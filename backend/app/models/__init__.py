"""Import every persistence model so Alembic can discover the full schema."""

from app.models.analytics import (
    BayesAnalysis,
    Dataset,
    DatasetVariable,
    Insight,
    Observation,
    RandomVariable,
    StatisticalAnalysis,
    StatisticalResult,
)
from app.models.catalog import Category, Product
from app.models.company import Company
from app.models.customer import Customer
from app.models.governance import AuditLog, Report
from app.models.identity import AnonymousVisit, AuthSession, Employee, Role, User
from app.models.inventory import Inventory, InventoryMovement
from app.models.orders import Order, OrderDetail
from app.models.sales import Payment, Sale, SaleDetail

__all__ = [
    "AuditLog",
    "AnonymousVisit",
    "AuthSession",
    "BayesAnalysis",
    "Category",
    "Company",
    "Customer",
    "Dataset",
    "DatasetVariable",
    "Employee",
    "Insight",
    "Inventory",
    "InventoryMovement",
    "Observation",
    "Order",
    "OrderDetail",
    "Payment",
    "Product",
    "RandomVariable",
    "Report",
    "Role",
    "Sale",
    "SaleDetail",
    "StatisticalAnalysis",
    "StatisticalResult",
    "User",
]
