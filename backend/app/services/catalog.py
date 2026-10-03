"""Customer and product catalog business services."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.catalog import Category, Product
from app.models.customer import Customer
from app.models.inventory import Inventory, InventoryMovement
from app.schemas.catalog import CategoryCreate, CategoryUpdate, ProductCreate, ProductUpdate
from app.schemas.customers import CustomerCreate, CustomerUpdate


@dataclass(frozen=True)
class ProductRecord:
    id: int
    sku: str
    name: str
    description: str | None
    category_id: int
    category_name: str
    unit_price: Decimal
    stock: int
    active: bool
    created_at: datetime
    updated_at: datetime


def _product_record(product: Product, category_name: str, stock: int) -> ProductRecord:
    return ProductRecord(
        id=product.id,
        sku=product.sku,
        name=product.name,
        description=product.description,
        category_id=product.category_id,
        category_name=category_name,
        unit_price=product.unit_price,
        stock=stock,
        active=product.active,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


class CustomerService:
    def __init__(self, session: Session, company_id: int) -> None:
        self.session = session
        self.company_id = company_id

    def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
        active: bool | None = None,
    ) -> tuple[list[Customer], int]:
        filters = [Customer.company_id == self.company_id]
        if search:
            normalized = search.strip().lower()
            filters.append(
                or_(
                    func.lower(Customer.name).contains(normalized, autoescape=True),
                    func.lower(Customer.document_number).contains(normalized, autoescape=True),
                    func.lower(func.coalesce(Customer.email, "")).contains(
                        normalized, autoescape=True
                    ),
                    func.lower(func.coalesce(Customer.phone, "")).contains(
                        normalized, autoescape=True
                    ),
                )
            )
        if active is not None:
            filters.append(Customer.active.is_(active))

        items = list(
            self.session.scalars(
                select(Customer)
                .where(*filters)
                .order_by(Customer.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        total = self.session.scalar(select(func.count(Customer.id)).where(*filters))
        return items, int(total or 0)

    def get(self, customer_id: int) -> Customer:
        customer = self.session.scalar(
            select(Customer).where(
                Customer.id == customer_id,
                Customer.company_id == self.company_id,
            )
        )
        if customer is None:
            raise AppError("CUSTOMER_NOT_FOUND", "El cliente no existe", status_code=404)
        return customer

    def create(self, payload: CustomerCreate) -> Customer:
        self._validate_document(
            payload.customer_type.value,
            payload.document_type.value,
            payload.document_number,
        )
        if self._document_exists(payload.document_number):
            raise AppError(
                "DOCUMENT_ALREADY_EXISTS",
                "El documento ya esta registrado",
                status_code=409,
            )

        customer = Customer(
            company_id=self.company_id,
            customer_type=payload.customer_type.value,
            document_type=payload.document_type.value,
            document_number=payload.document_number,
            name=payload.name,
            phone=payload.phone,
            email=str(payload.email).lower() if payload.email is not None else None,
            address=payload.address,
            active=True,
        )
        self.session.add(customer)
        self._flush_document_conflict()
        return customer

    def update(self, customer_id: int, payload: CustomerUpdate) -> Customer:
        customer = self.get(customer_id)
        fields = payload.model_fields_set

        if payload.name is not None:
            customer.name = payload.name
        if "phone" in fields:
            customer.phone = payload.phone
        if "email" in fields:
            customer.email = str(payload.email).lower() if payload.email is not None else None
        if "address" in fields:
            customer.address = payload.address
        if payload.active is not None:
            customer.active = payload.active

        self.session.flush()
        return customer

    @staticmethod
    def _validate_document(customer_type: str, document_type: str, number: str) -> None:
        valid_person = (
            customer_type == "person"
            and document_type == "DNI"
            and len(number) == 8
            and number.isdigit()
        )
        valid_company = (
            customer_type == "company"
            and document_type == "RUC"
            and len(number) == 11
            and number.isdigit()
        )
        if not valid_person and not valid_company:
            raise AppError(
                "INVALID_DOCUMENT",
                "Una persona requiere DNI de 8 digitos y una empresa RUC de 11 digitos",
                status_code=422,
            )

    def _document_exists(self, document_number: str) -> bool:
        return (
            self.session.scalar(
                select(Customer.id).where(
                    Customer.company_id == self.company_id,
                    Customer.document_number == document_number,
                )
            )
            is not None
        )

    def _flush_document_conflict(self) -> None:
        try:
            self.session.flush()
        except IntegrityError as exc:
            self.session.rollback()
            raise AppError(
                "DOCUMENT_ALREADY_EXISTS",
                "El documento ya esta registrado",
                status_code=409,
            ) from exc


class CategoryService:
    def __init__(self, session: Session, company_id: int) -> None:
        self.session = session
        self.company_id = company_id

    def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
        active: bool | None = None,
    ) -> tuple[list[Category], int]:
        filters = [Category.company_id == self.company_id]
        if search:
            normalized = search.strip().lower()
            filters.append(func.lower(Category.name).contains(normalized, autoescape=True))
        if active is not None:
            filters.append(Category.active.is_(active))

        items = list(
            self.session.scalars(
                select(Category)
                .where(*filters)
                .order_by(Category.name, Category.id)
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        total = self.session.scalar(select(func.count(Category.id)).where(*filters))
        return items, int(total or 0)

    def get(self, category_id: int) -> Category:
        category = self.session.scalar(
            select(Category).where(
                Category.id == category_id,
                Category.company_id == self.company_id,
            )
        )
        if category is None:
            raise AppError("CATEGORY_NOT_FOUND", "La categoria no existe", status_code=404)
        return category

    def create(self, payload: CategoryCreate) -> Category:
        if self._name_exists(payload.name):
            self._raise_name_conflict()
        category = Category(
            company_id=self.company_id,
            name=payload.name,
            description=payload.description,
            active=True,
        )
        self.session.add(category)
        self._flush_name_conflict()
        return category

    def update(self, category_id: int, payload: CategoryUpdate) -> Category:
        category = self.get(category_id)
        if payload.name is not None:
            if self._name_exists(payload.name, exclude_category_id=category.id):
                self._raise_name_conflict()
            category.name = payload.name
        if "description" in payload.model_fields_set:
            category.description = payload.description
        if payload.active is not None:
            category.active = payload.active
        self._flush_name_conflict()
        return category

    def _name_exists(self, name: str, exclude_category_id: int | None = None) -> bool:
        statement = select(Category.id).where(
            Category.company_id == self.company_id,
            func.lower(Category.name) == name.lower(),
        )
        if exclude_category_id is not None:
            statement = statement.where(Category.id != exclude_category_id)
        return self.session.scalar(statement) is not None

    @staticmethod
    def _raise_name_conflict() -> None:
        raise AppError(
            "CATEGORY_ALREADY_EXISTS",
            "Ya existe una categoria con ese nombre",
            status_code=409,
        )

    def _flush_name_conflict(self) -> None:
        try:
            self.session.flush()
        except IntegrityError as exc:
            self.session.rollback()
            raise AppError(
                "CATEGORY_ALREADY_EXISTS",
                "Ya existe una categoria con ese nombre",
                status_code=409,
            ) from exc


class ProductService:
    def __init__(self, session: Session, company_id: int, user_id: int) -> None:
        self.session = session
        self.company_id = company_id
        self.user_id = user_id

    def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
        category_id: int | None = None,
        active: bool | None = None,
    ) -> tuple[list[ProductRecord], int]:
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
        if category_id is not None:
            filters.append(Product.category_id == category_id)
        if active is not None:
            filters.append(Product.active.is_(active))

        stock = func.coalesce(Inventory.quantity, 0)
        statement = (
            select(Product, Category.name, stock)
            .join(Category, Category.id == Product.category_id)
            .outerjoin(Inventory, Inventory.product_id == Product.id)
            .where(*filters)
            .order_by(Product.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = self.session.execute(statement).all()
        total = self.session.scalar(
            select(func.count(Product.id))
            .join(Category, Category.id == Product.category_id)
            .where(*filters)
        )
        return [
            _product_record(product, category_name, int(current_stock))
            for product, category_name, current_stock in rows
        ], int(total or 0)

    def get(self, product_id: int) -> ProductRecord:
        return self._get_product_row(product_id)

    def create(self, payload: ProductCreate) -> ProductRecord:
        category = self._get_category(payload.category_id, require_active=True)
        if self._sku_exists(payload.sku):
            self._raise_sku_conflict()

        product = Product(
            company_id=self.company_id,
            category_id=category.id,
            sku=payload.sku,
            name=payload.name,
            description=payload.description,
            unit_price=payload.unit_price,
            active=True,
        )
        self.session.add(product)
        self._flush_sku_conflict()

        inventory = Inventory(
            company_id=self.company_id,
            product_id=product.id,
            quantity=payload.initial_stock,
            version=1,
        )
        self.session.add(inventory)
        if payload.initial_stock > 0:
            self.session.add(
                InventoryMovement(
                    company_id=self.company_id,
                    product_id=product.id,
                    user_id=self.user_id,
                    sale_id=None,
                    movement_type="initial",
                    quantity=payload.initial_stock,
                    stock_before=0,
                    stock_after=payload.initial_stock,
                    reason="Stock inicial al crear el producto",
                )
            )
        self.session.flush()
        return _product_record(product, category.name, payload.initial_stock)

    def update(self, product_id: int, payload: ProductUpdate) -> ProductRecord:
        product = self._get_product(product_id)

        if payload.sku is not None:
            if self._sku_exists(payload.sku, exclude_product_id=product.id):
                self._raise_sku_conflict()
            product.sku = payload.sku
        if payload.name is not None:
            product.name = payload.name
        if "description" in payload.model_fields_set:
            product.description = payload.description
        if payload.category_id is not None:
            category = self._get_category(payload.category_id, require_active=True)
            product.category_id = category.id
        if payload.unit_price is not None:
            product.unit_price = payload.unit_price
        if payload.active is not None:
            if payload.active:
                self._get_category(product.category_id, require_active=True)
            product.active = payload.active

        self._flush_sku_conflict()
        return self._get_product_row(product.id)

    def _get_product(self, product_id: int) -> Product:
        product = self.session.scalar(
            select(Product).where(
                Product.id == product_id,
                Product.company_id == self.company_id,
            )
        )
        if product is None:
            raise AppError("PRODUCT_NOT_FOUND", "El producto no existe", status_code=404)
        return product

    def _get_product_row(self, product_id: int) -> ProductRecord:
        stock = func.coalesce(Inventory.quantity, 0)
        row = self.session.execute(
            select(Product, Category.name, stock)
            .join(Category, Category.id == Product.category_id)
            .outerjoin(Inventory, Inventory.product_id == Product.id)
            .where(
                Product.id == product_id,
                Product.company_id == self.company_id,
            )
        ).one_or_none()
        if row is None:
            raise AppError("PRODUCT_NOT_FOUND", "El producto no existe", status_code=404)
        return _product_record(row[0], row[1], int(row[2]))

    def _get_category(self, category_id: int, *, require_active: bool) -> Category:
        category = self.session.scalar(
            select(Category).where(
                Category.id == category_id,
                Category.company_id == self.company_id,
            )
        )
        if category is None:
            raise AppError("CATEGORY_NOT_FOUND", "La categoria no existe", status_code=404)
        if require_active and not category.active:
            raise AppError(
                "CATEGORY_INACTIVE",
                "La categoria esta inactiva",
                status_code=409,
            )
        return category

    def _sku_exists(self, sku: str, exclude_product_id: int | None = None) -> bool:
        statement = select(Product.id).where(
            Product.company_id == self.company_id,
            func.lower(Product.sku) == sku.lower(),
        )
        if exclude_product_id is not None:
            statement = statement.where(Product.id != exclude_product_id)
        return self.session.scalar(statement) is not None

    @staticmethod
    def _raise_sku_conflict() -> None:
        raise AppError("SKU_ALREADY_EXISTS", "El SKU ya esta registrado", status_code=409)

    def _flush_sku_conflict(self) -> None:
        try:
            self.session.flush()
        except IntegrityError as exc:
            self.session.rollback()
            raise AppError(
                "SKU_ALREADY_EXISTS",
                "El SKU ya esta registrado",
                status_code=409,
            ) from exc
