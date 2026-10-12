"""Seller profile and monthly performance service."""

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.identity import Employee, Role, User
from app.models.sales import Sale
from app.schemas.sellers import SellerProfileUpdate


class SellerService:
    def __init__(self, session: Session, company_id: int) -> None:
        self.session = session
        self.company_id = company_id

    def list(self) -> list[dict]:
        now = datetime.now(UTC)
        month_start = datetime(now.year, now.month, 1, tzinfo=UTC)
        rows = self.session.execute(
            select(
                User,
                Employee,
                func.count(Sale.id),
                func.coalesce(func.sum(Sale.total), 0),
            )
            .join(Role, Role.id == User.role_id)
            .outerjoin(Employee, Employee.user_id == User.id)
            .outerjoin(
                Sale,
                (Sale.seller_id == User.id) & (Sale.created_at >= month_start),
            )
            .where(User.company_id == self.company_id, Role.code == "seller")
            .group_by(User.id, Employee.id)
            .order_by(User.name, User.id)
        ).all()
        return [
            self._record(user, employee, int(count), Decimal(total))
            for user, employee, count, total in rows
        ]

    def update(self, user_id: int, payload: SellerProfileUpdate) -> dict:
        row = self.session.execute(
            select(User, Employee)
            .join(Role, Role.id == User.role_id)
            .outerjoin(Employee, Employee.user_id == User.id)
            .where(User.id == user_id, User.company_id == self.company_id, Role.code == "seller")
        ).one_or_none()
        if row is None:
            raise AppError("SELLER_NOT_FOUND", "El vendedor no existe", status_code=404)
        user, employee = row
        if employee is None:
            employee = Employee(
                company_id=self.company_id,
                user_id=user.id,
                employee_code=payload.employee_code.strip().upper(),
                name=user.name,
                email=user.email,
            )
            self.session.add(employee)
        employee.employee_code = payload.employee_code.strip().upper()
        employee.name = user.name
        employee.email = user.email
        employee.phone = payload.phone
        employee.document_number = payload.document_number
        employee.hire_date = payload.hire_date
        employee.zone = payload.zone
        employee.monthly_target = payload.monthly_target
        employee.commission_percent = payload.commission_percent
        employee.employment_status = payload.employment_status
        employee.active = payload.employment_status == "active"
        try:
            self.session.flush()
        except IntegrityError as exc:
            raise AppError(
                "EMPLOYEE_CODE_EXISTS", "El código de empleado ya está registrado", status_code=409
            ) from exc
        sales_count, sales_total = self.session.execute(
            select(func.count(Sale.id), func.coalesce(func.sum(Sale.total), 0)).where(
                Sale.seller_id == user.id,
                Sale.created_at
                >= datetime(datetime.now(UTC).year, datetime.now(UTC).month, 1, tzinfo=UTC),
            )
        ).one()
        return self._record(user, employee, int(sales_count), Decimal(sales_total))

    @staticmethod
    def _record(user: User, employee: Employee | None, count: int, total: Decimal) -> dict:
        target = employee.monthly_target if employee else Decimal("0")
        rate = employee.commission_percent if employee else Decimal("0")
        progress = (total / target * 100).quantize(Decimal("0.01")) if target else Decimal("0")
        return {
            "user_id": user.id,
            "employee_id": employee.id if employee else None,
            "employee_code": employee.employee_code if employee else None,
            "name": user.name,
            "email": user.email,
            "phone": employee.phone if employee else None,
            "document_number": employee.document_number if employee else None,
            "hire_date": employee.hire_date if employee else None,
            "zone": employee.zone if employee else None,
            "monthly_target": target,
            "commission_percent": rate,
            "employment_status": employee.employment_status if employee else "active",
            "active": user.active and (employee.active if employee else True),
            "sales_count": count,
            "sales_total": total.quantize(Decimal("0.01")),
            "commission_estimate": (total * rate / 100).quantize(Decimal("0.01")),
            "target_progress_percent": progress,
            "created_at": user.created_at,
        }
