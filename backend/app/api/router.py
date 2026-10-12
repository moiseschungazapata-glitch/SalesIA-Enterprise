"""Central router for the SalesIA HTTP API."""

from fastapi import APIRouter

from app.api.routes import (
    auth,
    categories,
    customers,
    dashboard,
    insights,
    inventory,
    orders,
    payments,
    probability,
    products,
    public,
    random_variables,
    reports,
    sales,
    security,
    sellers,
    settings,
    statistics,
    users,
)

api_router = APIRouter()
api_router.include_router(public.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(customers.router)
api_router.include_router(categories.router)
api_router.include_router(products.router)
api_router.include_router(inventory.router)
api_router.include_router(orders.router)
api_router.include_router(payments.router)
api_router.include_router(sales.router)
api_router.include_router(dashboard.router)
api_router.include_router(insights.router)
api_router.include_router(statistics.router)
api_router.include_router(probability.router)
api_router.include_router(random_variables.router)
api_router.include_router(reports.router)
api_router.include_router(security.router)
api_router.include_router(sellers.router)
api_router.include_router(settings.router)
