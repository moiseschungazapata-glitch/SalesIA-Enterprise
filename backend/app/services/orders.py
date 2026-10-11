"""Order lifecycle and sale conversion services."""

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.core.security import SELLER_ROLE
from app.models.catalog import Category, Product
from app.models.customer import Customer
from app.models.identity import User
from app.models.orders import Order, OrderDetail
from app.schemas.orders import OrderCreate
from app.schemas.sales import SaleCreate
from app.services.operations import SalesService


class OrderService:
    def __init__(self, session: Session, company_id: int, user_id: int, role: str) -> None:
        self.session, self.company_id, self.user_id, self.role = session, company_id, user_id, role

    def list(
        self, page: int, page_size: int, status: str | None
    ) -> tuple[list[dict[str, Any]], int]:
        filters = [Order.company_id == self.company_id]
        if self.role == SELLER_ROLE:
            filters.append(Order.seller_id == self.user_id)
        if status:
            filters.append(Order.status == status)
        orders = self.session.scalars(
            select(Order)
            .where(*filters)
            .order_by(Order.created_at.desc(), Order.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        total = self.session.scalar(select(func.count(Order.id)).where(*filters))
        return [self._record(order) for order in orders], int(total or 0)

    def get(self, order_id: int) -> dict[str, Any]:
        return self._record(self._get_owned(order_id))

    def create(self, payload: OrderCreate) -> dict[str, Any]:
        order = Order(
            company_id=self.company_id,
            customer_id=payload.customer_id,
            seller_id=self.user_id,
            number="TMP",
            status="pending",
            currency="PEN",
            total=Decimal("0.01"),
        )
        self.session.add(order)
        self.session.flush()
        order.number = f"P-{order.id:06d}"
        self._replace_details(order, payload)
        return self._record(order)

    def update(self, order_id: int, payload: OrderCreate) -> dict[str, Any]:
        order = self._get_owned(order_id)
        if order.status not in {"draft", "pending"}:
            raise AppError(
                "ORDER_NOT_EDITABLE", "Solo puede editar pedidos pendientes", status_code=409
            )
        order.customer_id = payload.customer_id
        self.session.execute(delete(OrderDetail).where(OrderDetail.order_id == order.id))
        self._replace_details(order, payload)
        return self._record(order)

    def change_status(self, order_id: int, status: str) -> dict[str, Any]:
        order = self._get_owned(order_id)
        if status == "approved" and order.status == "pending":
            order.status, order.approved_at = "approved", datetime.now(UTC)
        elif status == "cancelled" and order.status in {"draft", "pending", "approved"}:
            order.status, order.cancelled_at = "cancelled", datetime.now(UTC)
        else:
            raise AppError(
                "INVALID_ORDER_TRANSITION", "El cambio de estado no es válido", status_code=409
            )
        self.session.flush()
        return self._record(order)

    def convert(self, order_id: int, payment_method: str, key: UUID) -> tuple[dict[str, Any], Any]:
        order = self._get_owned(order_id)
        if order.status != "approved":
            raise AppError("ORDER_NOT_APPROVED", "El pedido debe estar aprobado", status_code=409)
        details = self.session.scalars(
            select(OrderDetail).where(OrderDetail.order_id == order.id).order_by(OrderDetail.id)
        ).all()
        sale = SalesService(self.session, self.company_id, self.user_id, self.role).create(
            SaleCreate(
                customer_id=order.customer_id,
                payment_method=payment_method,
                items=[
                    {"product_id": item.product_id, "quantity": item.quantity} for item in details
                ],
            ),
            key,
        )
        order.status, order.sale_id, order.converted_at = "converted", sale.id, datetime.now(UTC)
        self.session.flush()
        return self._record(order), sale

    def _get_owned(self, order_id: int) -> Order:
        order = self.session.scalar(
            select(Order).where(Order.id == order_id, Order.company_id == self.company_id)
        )
        if order is None:
            raise AppError("ORDER_NOT_FOUND", "El pedido no existe", status_code=404)
        if self.role == SELLER_ROLE and order.seller_id != self.user_id:
            raise AppError(
                "ORDER_ACCESS_DENIED",
                "No puede acceder al pedido de otro vendedor",
                status_code=403,
            )
        return order

    def _replace_details(self, order: Order, payload: OrderCreate) -> None:
        customer = self.session.scalar(
            select(Customer).where(
                Customer.id == payload.customer_id,
                Customer.company_id == self.company_id,
                Customer.active.is_(True),
            )
        )
        if customer is None:
            raise AppError(
                "CUSTOMER_NOT_FOUND", "El cliente no existe o está inactivo", status_code=404
            )
        quantities = {item.product_id: item.quantity for item in payload.items}
        rows = self.session.execute(
            select(Product, Category.name)
            .join(Category, Category.id == Product.category_id)
            .where(
                Product.company_id == self.company_id,
                Product.id.in_(quantities),
                Product.active.is_(True),
            )
        ).all()
        if len(rows) != len(quantities):
            raise AppError(
                "PRODUCT_NOT_FOUND",
                "Uno o más productos no existen o están inactivos",
                status_code=404,
            )
        total = Decimal("0")
        for product, category_name in rows:
            subtotal = (product.unit_price * quantities[product.id]).quantize(Decimal("0.01"))
            total += subtotal
            self.session.add(
                OrderDetail(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantities[product.id],
                    unit_price=product.unit_price,
                    subtotal=subtotal,
                    sku_snapshot=product.sku,
                    product_name_snapshot=product.name,
                    category_name_snapshot=category_name,
                )
            )
        order.total = total.quantize(Decimal("0.01"))
        self.session.flush()

    def _record(self, order: Order) -> dict[str, Any]:
        customer = self.session.scalar(
            select(Customer.name).where(Customer.id == order.customer_id)
        )
        seller = self.session.scalar(select(User.name).where(User.id == order.seller_id))
        details = self.session.scalars(
            select(OrderDetail).where(OrderDetail.order_id == order.id).order_by(OrderDetail.id)
        ).all()
        return {
            "id": order.id,
            "number": order.number,
            "status": order.status,
            "customer_id": order.customer_id,
            "customer_name": str(customer),
            "seller_id": order.seller_id,
            "seller_name": str(seller),
            "sale_id": order.sale_id,
            "currency": order.currency,
            "total": order.total,
            "items": [
                {
                    "product_id": item.product_id,
                    "sku": item.sku_snapshot,
                    "product_name": item.product_name_snapshot,
                    "category_name": item.category_name_snapshot,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "subtotal": item.subtotal,
                }
                for item in details
            ],
            "created_at": order.created_at,
            "updated_at": order.updated_at,
        }
