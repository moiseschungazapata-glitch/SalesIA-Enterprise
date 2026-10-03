"""Transactional inventory and sales business services."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.core.security import SELLER_ROLE
from app.models.catalog import Category, Product
from app.models.customer import Customer
from app.models.identity import User
from app.models.inventory import Inventory, InventoryMovement
from app.models.sales import Payment, Sale, SaleDetail
from app.schemas.inventory import InventoryMovementCreate
from app.schemas.sales import SaleCreate


@dataclass(frozen=True)
class InventoryRecord:
    product_id: int
    sku: str
    product_name: str
    category_name: str
    stock: int
    active: bool
    updated_at: datetime


@dataclass(frozen=True)
class MovementRecord:
    id: int
    product_id: int
    sku: str
    product_name: str
    movement_type: str
    quantity: int
    stock_before: int
    stock_after: int
    reason: str
    user_id: int
    user_name: str
    sale_id: int | None
    sale_number: str | None
    created_at: datetime


@dataclass(frozen=True)
class PartyRecord:
    id: int
    name: str


@dataclass(frozen=True)
class SaleItemRecord:
    product_id: int
    sku: str
    product_name: str
    category_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


@dataclass(frozen=True)
class PaymentRecord:
    method: str
    amount: Decimal
    status: str
    paid_at: datetime


@dataclass(frozen=True)
class SaleRecord:
    id: int
    number: str
    status: str
    created_at: datetime
    customer: PartyRecord
    seller: PartyRecord
    items: list[SaleItemRecord]
    payment: PaymentRecord
    currency: str
    total: Decimal


@dataclass(frozen=True)
class SaleListRecord:
    id: int
    number: str
    status: str
    created_at: datetime
    customer: PartyRecord
    seller: PartyRecord
    items_count: int
    payment_method: str
    currency: str
    total: Decimal


class InventoryService:
    def __init__(self, session: Session, company_id: int, user_id: int) -> None:
        self.session = session
        self.company_id = company_id
        self.user_id = user_id

    def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        active: bool | None,
    ) -> tuple[list[InventoryRecord], int]:
        filters = [Product.company_id == self.company_id]
        if search:
            normalized = search.strip().lower()
            filters.append(
                or_(
                    func.lower(Product.sku).contains(normalized, autoescape=True),
                    func.lower(Product.name).contains(normalized, autoescape=True),
                    func.lower(Category.name).contains(normalized, autoescape=True),
                )
            )
        if active is not None:
            filters.append(Product.active.is_(active))

        rows = self.session.execute(
            select(Product, Category.name, Inventory)
            .join(Category, Category.id == Product.category_id)
            .join(Inventory, Inventory.product_id == Product.id)
            .where(*filters)
            .order_by(Product.name, Product.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        total = self.session.scalar(
            select(func.count(Product.id))
            .join(Category, Category.id == Product.category_id)
            .join(Inventory, Inventory.product_id == Product.id)
            .where(*filters)
        )
        return [
            InventoryRecord(
                product_id=product.id,
                sku=product.sku,
                product_name=product.name,
                category_name=category_name,
                stock=inventory.quantity,
                active=product.active,
                updated_at=inventory.updated_at,
            )
            for product, category_name, inventory in rows
        ], int(total or 0)

    def list_movements(
        self,
        *,
        page: int,
        page_size: int,
        product_id: int | None,
        movement_type: str | None,
        date_from: date | None,
        date_to: date | None,
    ) -> tuple[list[MovementRecord], int]:
        filters = [InventoryMovement.company_id == self.company_id]
        if product_id is not None:
            filters.append(InventoryMovement.product_id == product_id)
        if movement_type is not None:
            filters.append(InventoryMovement.movement_type == movement_type)
        if date_from is not None:
            filters.append(InventoryMovement.created_at >= datetime.combine(date_from, time.min))
        if date_to is not None:
            upper_bound = datetime.combine(date_to + timedelta(days=1), time.min)
            filters.append(InventoryMovement.created_at < upper_bound)

        rows = self.session.execute(
            select(InventoryMovement, Product.sku, Product.name, User.name, Sale.number)
            .join(Product, Product.id == InventoryMovement.product_id)
            .join(User, User.id == InventoryMovement.user_id)
            .outerjoin(Sale, Sale.id == InventoryMovement.sale_id)
            .where(*filters)
            .order_by(InventoryMovement.created_at.desc(), InventoryMovement.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        total = self.session.scalar(
            select(func.count(InventoryMovement.id)).where(*filters)
        )
        return [
            MovementRecord(
                id=movement.id,
                product_id=movement.product_id,
                sku=sku,
                product_name=product_name,
                movement_type=movement.movement_type,
                quantity=movement.quantity,
                stock_before=movement.stock_before,
                stock_after=movement.stock_after,
                reason=movement.reason,
                user_id=movement.user_id,
                user_name=user_name,
                sale_id=movement.sale_id,
                sale_number=sale_number,
                created_at=movement.created_at,
            )
            for movement, sku, product_name, user_name, sale_number in rows
        ], int(total or 0)

    def create_movement(self, payload: InventoryMovementCreate) -> MovementRecord:
        row = self.session.execute(
            select(Product, Inventory)
            .join(Inventory, Inventory.product_id == Product.id)
            .where(
                Product.id == payload.product_id,
                Product.company_id == self.company_id,
            )
            .with_for_update()
        ).one_or_none()
        if row is None:
            raise AppError("PRODUCT_NOT_FOUND", "El producto no existe", status_code=404)
        product, inventory = row
        if not product.active:
            raise AppError("PRODUCT_INACTIVE", "El producto esta inactivo", status_code=409)

        movement_type = payload.movement_type.value
        if movement_type == "initial":
            previous_movement = self.session.scalar(
                select(InventoryMovement.id).where(
                    InventoryMovement.product_id == product.id,
                    InventoryMovement.company_id == self.company_id,
                )
            )
            if previous_movement is not None or inventory.quantity != 0:
                raise AppError(
                    "INITIAL_STOCK_ALREADY_RECORDED",
                    "El stock inicial de este producto ya fue registrado",
                    status_code=409,
                )

        stock_before = inventory.quantity
        if movement_type == "adjustment_out":
            if payload.quantity > stock_before:
                raise AppError(
                    "INSUFFICIENT_STOCK",
                    "No hay stock suficiente para registrar la salida",
                    status_code=409,
                    details={"available": stock_before, "requested": payload.quantity},
                )
            stock_after = stock_before - payload.quantity
        else:
            stock_after = stock_before + payload.quantity

        inventory.quantity = stock_after
        inventory.version += 1
        movement = InventoryMovement(
            company_id=self.company_id,
            product_id=product.id,
            user_id=self.user_id,
            sale_id=None,
            movement_type=movement_type,
            quantity=payload.quantity,
            stock_before=stock_before,
            stock_after=stock_after,
            reason=payload.reason,
        )
        self.session.add(movement)
        self.session.flush()
        user_name = self.session.scalar(select(User.name).where(User.id == self.user_id))
        return MovementRecord(
            id=movement.id,
            product_id=product.id,
            sku=product.sku,
            product_name=product.name,
            movement_type=movement.movement_type,
            quantity=movement.quantity,
            stock_before=movement.stock_before,
            stock_after=movement.stock_after,
            reason=movement.reason,
            user_id=movement.user_id,
            user_name=str(user_name),
            sale_id=None,
            sale_number=None,
            created_at=movement.created_at,
        )


class SalesService:
    def __init__(self, session: Session, company_id: int, user_id: int, role: str) -> None:
        self.session = session
        self.company_id = company_id
        self.user_id = user_id
        self.role = role

    def list(
        self,
        *,
        page: int,
        page_size: int,
        number: str | None,
        customer_id: int | None,
        seller_id: int | None,
        status: str | None,
        date_from: date | None,
        date_to: date | None,
    ) -> tuple[list[SaleListRecord], int]:
        filters = [Sale.company_id == self.company_id]
        if self.role == SELLER_ROLE:
            filters.append(Sale.seller_id == self.user_id)
        elif seller_id is not None:
            filters.append(Sale.seller_id == seller_id)
        if number:
            normalized = number.strip().lower()
            filters.append(func.lower(Sale.number).contains(normalized, autoescape=True))
        if customer_id is not None:
            filters.append(Sale.customer_id == customer_id)
        if status is not None:
            filters.append(Sale.status == status)
        if date_from is not None:
            filters.append(Sale.created_at >= datetime.combine(date_from, time.min))
        if date_to is not None:
            upper_bound = datetime.combine(date_to + timedelta(days=1), time.min)
            filters.append(Sale.created_at < upper_bound)

        item_count = func.sum(SaleDetail.quantity)
        rows = self.session.execute(
            select(Sale, Customer.name, User.name, item_count, Payment.method)
            .join(Customer, Customer.id == Sale.customer_id)
            .join(User, User.id == Sale.seller_id)
            .join(SaleDetail, SaleDetail.sale_id == Sale.id)
            .join(Payment, Payment.sale_id == Sale.id)
            .where(*filters)
            .group_by(Sale.id, Customer.name, User.name, Payment.method)
            .order_by(Sale.created_at.desc(), Sale.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        total = self.session.scalar(select(func.count(Sale.id)).where(*filters))
        return [
            SaleListRecord(
                id=sale.id,
                number=sale.number,
                status=sale.status,
                created_at=sale.created_at,
                customer=PartyRecord(sale.customer_id, customer_name),
                seller=PartyRecord(sale.seller_id, seller_name),
                items_count=int(items_count),
                payment_method=payment_method,
                currency=sale.currency,
                total=sale.total,
            )
            for sale, customer_name, seller_name, items_count, payment_method in rows
        ], int(total or 0)

    def get(self, sale_id: int) -> SaleRecord:
        sale = self.session.scalar(
            select(Sale).where(Sale.id == sale_id, Sale.company_id == self.company_id)
        )
        if sale is None:
            raise AppError("SALE_NOT_FOUND", "La venta no existe", status_code=404)
        if self.role == SELLER_ROLE and sale.seller_id != self.user_id:
            raise AppError(
                "SALE_ACCESS_DENIED",
                "No puede consultar una venta registrada por otro vendedor",
                status_code=403,
            )
        return self._sale_record(sale)

    def create(self, payload: SaleCreate, idempotency_key: UUID) -> SaleRecord:
        request_hash = self._request_hash(payload)
        existing = self.session.scalar(
            select(Sale).where(
                Sale.company_id == self.company_id,
                Sale.idempotency_key == idempotency_key,
            )
        )
        if existing is not None:
            if existing.request_hash != request_hash:
                raise AppError(
                    "IDEMPOTENCY_KEY_REUSED",
                    "La clave de idempotencia ya fue usada con datos diferentes",
                    status_code=409,
                )
            return self._sale_record(existing)

        customer = self.session.scalar(
            select(Customer).where(
                Customer.id == payload.customer_id,
                Customer.company_id == self.company_id,
            )
        )
        if customer is None:
            raise AppError("CUSTOMER_NOT_FOUND", "El cliente no existe", status_code=404)
        if not customer.active:
            raise AppError("CUSTOMER_INACTIVE", "El cliente esta inactivo", status_code=409)

        requested = {item.product_id: item.quantity for item in payload.items}
        rows = self.session.execute(
            select(Product, Category.name, Inventory)
            .join(Category, Category.id == Product.category_id)
            .join(Inventory, Inventory.product_id == Product.id)
            .where(Product.company_id == self.company_id, Product.id.in_(requested))
            .order_by(Product.id)
            .with_for_update()
        ).all()
        found_ids = {product.id for product, _category, _inventory in rows}
        missing_ids = sorted(set(requested) - found_ids)
        if missing_ids:
            raise AppError(
                "PRODUCT_NOT_FOUND",
                "Uno o mas productos no existen",
                status_code=404,
                details={"product_ids": missing_ids},
            )

        for product, _category_name, inventory in rows:
            quantity = requested[product.id]
            if not product.active:
                raise AppError(
                    "PRODUCT_INACTIVE",
                    f"El producto {product.name} esta inactivo",
                    status_code=409,
                    details={"product_id": product.id},
                )
            if inventory.quantity < quantity:
                raise AppError(
                    "INSUFFICIENT_STOCK",
                    f"Stock insuficiente para {product.name}",
                    status_code=409,
                    details={
                        "product_id": product.id,
                        "available": inventory.quantity,
                        "requested": quantity,
                    },
                )

        total = sum(
            (product.unit_price * requested[product.id] for product, _category, _stock in rows),
            start=Decimal("0.00"),
        ).quantize(Decimal("0.01"))
        sale = Sale(
            company_id=self.company_id,
            customer_id=customer.id,
            seller_id=self.user_id,
            number=f"TMP-{idempotency_key.hex[:20]}",
            idempotency_key=idempotency_key,
            request_hash=request_hash,
            status="confirmed",
            currency="PEN",
            total=total,
        )
        self.session.add(sale)
        self.session.flush()
        sale.number = f"V-{sale.id:06d}"

        for product, category_name, inventory in rows:
            quantity = requested[product.id]
            subtotal = (product.unit_price * quantity).quantize(Decimal("0.01"))
            stock_before = inventory.quantity
            stock_after = stock_before - quantity
            inventory.quantity = stock_after
            inventory.version += 1
            self.session.add_all(
                [
                    SaleDetail(
                        sale_id=sale.id,
                        product_id=product.id,
                        quantity=quantity,
                        unit_price=product.unit_price,
                        subtotal=subtotal,
                        sku_snapshot=product.sku,
                        product_name_snapshot=product.name,
                        category_name_snapshot=category_name,
                    ),
                    InventoryMovement(
                        company_id=self.company_id,
                        product_id=product.id,
                        user_id=self.user_id,
                        sale_id=sale.id,
                        movement_type="sale",
                        quantity=quantity,
                        stock_before=stock_before,
                        stock_after=stock_after,
                        reason=f"Salida por venta {sale.number}",
                    ),
                ]
            )

        self.session.add(
            Payment(
                sale_id=sale.id,
                method=payload.payment_method.value,
                amount=total,
                status="completed",
            )
        )
        self.session.flush()
        return self._sale_record(sale)

    @staticmethod
    def _request_hash(payload: SaleCreate) -> str:
        canonical = {
            "customer_id": payload.customer_id,
            "payment_method": payload.payment_method.value,
            "items": sorted(
                (
                    {"product_id": item.product_id, "quantity": item.quantity}
                    for item in payload.items
                ),
                key=lambda item: item["product_id"],
            ),
        }
        encoded = json.dumps(canonical, separators=(",", ":"), sort_keys=True).encode()
        return hashlib.sha256(encoded).hexdigest()

    def _sale_record(self, sale: Sale) -> SaleRecord:
        customer_name = self.session.scalar(
            select(Customer.name).where(Customer.id == sale.customer_id)
        )
        seller_name = self.session.scalar(select(User.name).where(User.id == sale.seller_id))
        details = self.session.scalars(
            select(SaleDetail).where(SaleDetail.sale_id == sale.id).order_by(SaleDetail.id)
        ).all()
        payment = self.session.scalar(select(Payment).where(Payment.sale_id == sale.id))
        if payment is None:
            raise AppError("INTERNAL_ERROR", "La venta no tiene un pago asociado", status_code=500)
        return SaleRecord(
            id=sale.id,
            number=sale.number,
            status=sale.status,
            created_at=sale.created_at,
            customer=PartyRecord(sale.customer_id, str(customer_name)),
            seller=PartyRecord(sale.seller_id, str(seller_name)),
            items=[
                SaleItemRecord(
                    product_id=detail.product_id,
                    sku=detail.sku_snapshot,
                    product_name=detail.product_name_snapshot,
                    category_name=detail.category_name_snapshot,
                    quantity=detail.quantity,
                    unit_price=detail.unit_price,
                    subtotal=detail.subtotal,
                )
                for detail in details
            ],
            payment=PaymentRecord(
                method=payment.method,
                amount=payment.amount,
                status=payment.status,
                paid_at=payment.paid_at,
            ),
            currency=sale.currency,
            total=sale.total,
        )
