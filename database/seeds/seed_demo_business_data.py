"""Load idempotent fictional business data for end-to-end SalesIA testing."""

from argparse import ArgumentParser
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import engine
from app.models.catalog import Category, Product
from app.models.company import Company
from app.models.customer import Customer
from app.models.identity import Role, User
from app.models.inventory import Inventory, InventoryMovement

CATEGORIES = (
    ("Computación", "Equipos y accesorios informáticos."),
    ("Oficina", "Artículos para trabajo administrativo."),
    ("Conectividad", "Equipos para redes y comunicaciones."),
    ("Audio y video", "Accesorios audiovisuales empresariales."),
)

CUSTOMERS = (
    (
        "person",
        "DNI",
        "71000001",
        "Ana Torres Mendoza",
        "987100001",
        "ana.torres@example.com",
        "Miraflores, Lima",
    ),
    (
        "person",
        "DNI",
        "71000002",
        "Carlos Rivera Soto",
        "987100002",
        "carlos.rivera@example.com",
        "San Miguel, Lima",
    ),
    (
        "person",
        "DNI",
        "71000003",
        "Lucía Vega Ramos",
        "987100003",
        "lucia.vega@example.com",
        "Santiago de Surco, Lima",
    ),
    (
        "person",
        "DNI",
        "71000004",
        "María Paredes León",
        "987100004",
        "maria.paredes@example.com",
        "Los Olivos, Lima",
    ),
    (
        "company",
        "RUC",
        "20990000001",
        "Innovación Andina SAC",
        "014001001",
        "compras@innovacion-andina.example",
        "San Isidro, Lima",
    ),
    (
        "company",
        "RUC",
        "20990000002",
        "Comercial Nova EIRL",
        "014001002",
        "ventas@comercial-nova.example",
        "Ate, Lima",
    ),
)

PRODUCTS = (
    (
        "Computación",
        "CMP-LAP-001",
        "Laptop empresarial 14 pulgadas",
        "Equipo portátil para trabajo empresarial.",
        "2899.90",
        8,
    ),
    (
        "Computación",
        "CMP-MON-001",
        "Monitor IPS 24 pulgadas",
        "Monitor Full HD para oficina.",
        "649.90",
        15,
    ),
    (
        "Computación",
        "CMP-TEC-001",
        "Teclado inalámbrico",
        "Teclado compacto en español.",
        "129.90",
        30,
    ),
    ("Computación", "CMP-MOU-001", "Mouse ergonómico", "Mouse óptico inalámbrico.", "79.90", 35),
    (
        "Oficina",
        "OFI-SIL-001",
        "Silla ergonómica",
        "Silla regulable con soporte lumbar.",
        "589.00",
        12,
    ),
    (
        "Oficina",
        "OFI-ESC-001",
        "Escritorio modular",
        "Escritorio de melamina para oficina.",
        "749.00",
        10,
    ),
    (
        "Oficina",
        "OFI-PAP-001",
        "Papel A4 caja",
        "Caja de cinco millares de papel A4.",
        "124.50",
        25,
    ),
    (
        "Conectividad",
        "RED-ROU-001",
        "Router Wi-Fi 6",
        "Router de doble banda para pequeñas empresas.",
        "399.90",
        14,
    ),
    (
        "Conectividad",
        "RED-SWI-001",
        "Switch de 8 puertos",
        "Switch Gigabit no administrable.",
        "189.90",
        18,
    ),
    (
        "Audio y video",
        "AV-AUD-001",
        "Audífonos con micrófono",
        "Audífonos USB para videollamadas.",
        "159.90",
        22,
    ),
    (
        "Audio y video",
        "AV-CAM-001",
        "Cámara web Full HD",
        "Cámara 1080p con micrófono.",
        "219.90",
        16,
    ),
    (
        "Audio y video",
        "AV-PRO-001",
        "Proyector empresarial",
        "Proyector portátil para presentaciones.",
        "1849.00",
        6,
    ),
)


def seed(company_slug: str, apply: bool) -> dict[str, int]:
    counters = {"categories": 0, "customers": 0, "products": 0, "inventories": 0}
    with Session(engine) as session:
        company = session.scalar(select(Company).where(Company.slug == company_slug))
        if company is None:
            raise RuntimeError(f"No existe una empresa con slug '{company_slug}'")
        admin = session.scalar(
            select(User)
            .join(Role, Role.id == User.role_id)
            .where(
                User.company_id == company.id,
                User.active.is_(True),
                Role.code == "administrator",
            )
            .order_by(User.id)
        )
        if admin is None:
            raise RuntimeError("La empresa necesita un administrador activo")

        categories: dict[str, Category] = {}
        for name, description in CATEGORIES:
            category = session.scalar(
                select(Category).where(
                    Category.company_id == company.id,
                    Category.name == name,
                )
            )
            if category is None:
                category = Category(
                    company_id=company.id,
                    name=name,
                    description=description,
                    active=True,
                )
                session.add(category)
                session.flush()
                counters["categories"] += 1
            categories[name] = category

        for customer_type, document_type, document, name, phone, email, address in CUSTOMERS:
            exists = session.scalar(
                select(Customer.id).where(
                    Customer.company_id == company.id,
                    Customer.document_number == document,
                )
            )
            if exists is None:
                session.add(
                    Customer(
                        company_id=company.id,
                        customer_type=customer_type,
                        document_type=document_type,
                        document_number=document,
                        name=name,
                        phone=phone,
                        email=email,
                        address=address,
                        active=True,
                    )
                )
                counters["customers"] += 1

        for category_name, sku, name, description, price, stock in PRODUCTS:
            product = session.scalar(
                select(Product).where(
                    Product.company_id == company.id,
                    Product.sku == sku,
                )
            )
            if product is None:
                product = Product(
                    company_id=company.id,
                    category_id=categories[category_name].id,
                    sku=sku,
                    name=name,
                    description=description,
                    unit_price=Decimal(price),
                    active=True,
                )
                session.add(product)
                session.flush()
                counters["products"] += 1
            inventory = session.scalar(select(Inventory).where(Inventory.product_id == product.id))
            if inventory is None:
                session.add(
                    Inventory(
                        company_id=company.id,
                        product_id=product.id,
                        quantity=stock,
                        version=1,
                    )
                )
                session.add(
                    InventoryMovement(
                        company_id=company.id,
                        product_id=product.id,
                        user_id=admin.id,
                        movement_type="initial",
                        quantity=stock,
                        stock_before=0,
                        stock_after=stock,
                        reason="Carga inicial de datos ficticios para pruebas",
                    )
                )
                counters["inventories"] += 1

        if apply:
            session.commit()
        else:
            session.rollback()
    return counters


def parse_args():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--company-slug", default="salesia-enterprise")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Confirma la escritura. Sin esta opción solo muestra una vista previa.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    result = seed(arguments.company_slug, arguments.apply)
    mode = "APLICADOS" if arguments.apply else "VISTA PREVIA (sin cambios)"
    print(mode)
    print(f"Categorías nuevas: {result['categories']}")
    print(f"Clientes nuevos: {result['customers']}")
    print(f"Productos nuevos: {result['products']}")
    print(f"Inventarios iniciales: {result['inventories']}")
