"""Payment collection, cancellation and refund workflow."""

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.core.security import SELLER_ROLE
from app.models.customer import Customer
from app.models.sales import Payment, Sale
from app.schemas.payments import PaymentCreate


class PaymentService:
    def __init__(self, session: Session, company_id: int, user_id: int, role: str) -> None:
        self.session = session
        self.company_id = company_id
        self.user_id = user_id
        self.role = role

    def list(self, page: int, page_size: int, status: str | None) -> tuple[list[dict], int]:
        filters = [Sale.company_id == self.company_id]
        if self.role == SELLER_ROLE:
            filters.append(Sale.seller_id == self.user_id)
        if status:
            filters.append(Payment.status == status)
        rows = self.session.execute(
            select(Payment, Sale, Customer.name)
            .join(Sale, Sale.id == Payment.sale_id)
            .join(Customer, Customer.id == Sale.customer_id)
            .where(*filters)
            .order_by(Payment.paid_at.desc(), Payment.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        total = self.session.scalar(
            select(func.count(Payment.id)).join(Sale, Sale.id == Payment.sale_id).where(*filters)
        )
        return [self._record(payment, sale, customer) for payment, sale, customer in rows], int(
            total or 0
        )

    def create(self, payload: PaymentCreate) -> dict:
        sale = self._sale(payload.sale_id, lock=True)
        balance = (sale.total - sale.paid_amount).quantize(Decimal("0.01"))
        if balance <= 0:
            raise AppError("SALE_ALREADY_PAID", "La venta ya está pagada", status_code=409)
        if payload.amount > balance:
            raise AppError(
                "PAYMENT_EXCEEDS_BALANCE",
                "El abono no puede superar el saldo pendiente",
                status_code=422,
                details={"balance_due": str(balance)},
            )
        payment = Payment(
            sale_id=sale.id,
            method=payload.method.value,
            amount=payload.amount,
            status="completed",
            reference=payload.reference,
            registered_by_id=self.user_id,
        )
        self.session.add(payment)
        sale.paid_amount = (sale.paid_amount + payload.amount).quantize(Decimal("0.01"))
        sale.payment_status = "paid" if sale.paid_amount == sale.total else "partial"
        self.session.flush()
        customer = self.session.get_one(Customer, sale.customer_id)
        return self._record(payment, sale, customer.name)

    def reverse(self, payment_id: int, *, refund: bool) -> dict:
        payment, sale, customer = self._payment(payment_id, lock=True)
        if payment.status != "completed":
            raise AppError("PAYMENT_NOT_REVERSIBLE", "El pago ya fue revertido", status_code=409)
        payment.status = "refunded" if refund else "cancelled"
        if refund:
            payment.refunded_at = datetime.now(UTC)
        else:
            payment.cancelled_at = datetime.now(UTC)
        sale.paid_amount = max(Decimal("0"), sale.paid_amount - payment.amount)
        if sale.paid_amount == 0:
            sale.payment_status = "refunded" if refund else "pending"
        elif sale.paid_amount < sale.total:
            sale.payment_status = "partial"
        else:
            sale.payment_status = "paid"
        self.session.flush()
        return self._record(payment, sale, customer)

    def _sale(self, sale_id: int, *, lock: bool) -> Sale:
        query = select(Sale).where(Sale.id == sale_id, Sale.company_id == self.company_id)
        if lock:
            query = query.with_for_update()
        sale = self.session.scalar(query)
        if sale is None:
            raise AppError("SALE_NOT_FOUND", "La venta no existe", status_code=404)
        if self.role == SELLER_ROLE and sale.seller_id != self.user_id:
            raise AppError(
                "PAYMENT_ACCESS_DENIED", "No puede gestionar esta venta", status_code=403
            )
        return sale

    def _payment(self, payment_id: int, *, lock: bool) -> tuple[Payment, Sale, str]:
        query = (
            select(Payment, Sale, Customer.name)
            .join(Sale, Sale.id == Payment.sale_id)
            .join(Customer, Customer.id == Sale.customer_id)
            .where(Payment.id == payment_id, Sale.company_id == self.company_id)
        )
        if lock:
            query = query.with_for_update()
        row = self.session.execute(query).one_or_none()
        if row is None:
            raise AppError("PAYMENT_NOT_FOUND", "El pago no existe", status_code=404)
        payment, sale, customer = row
        if self.role == SELLER_ROLE and sale.seller_id != self.user_id:
            raise AppError("PAYMENT_ACCESS_DENIED", "No puede gestionar este pago", status_code=403)
        return payment, sale, customer

    @staticmethod
    def _record(payment: Payment, sale: Sale, customer_name: str) -> dict:
        return {
            "id": payment.id,
            "sale_id": sale.id,
            "sale_number": sale.number,
            "customer_name": customer_name,
            "method": payment.method,
            "amount": payment.amount,
            "status": payment.status,
            "reference": payment.reference,
            "paid_at": payment.paid_at,
            "sale_total": sale.total,
            "paid_amount": sale.paid_amount,
            "balance_due": (sale.total - sale.paid_amount).quantize(Decimal("0.01")),
            "payment_status": sale.payment_status,
        }
