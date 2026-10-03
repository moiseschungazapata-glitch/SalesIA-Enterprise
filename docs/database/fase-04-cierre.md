# Fase 04 - Verificacion y cierre

**Estado:** completa y verificada en Supabase el 2 de octubre de 2026.

## 1. Resultado implementado

- Registro SQLAlchemy con convencion uniforme de nombres.
- 22 modelos PostgreSQL organizados por dominio.
- Conexion sincronica con psycopg 3 y pool reducido para Supabase.
- Migracion Alembic inicial reversible.
- Restricciones de dinero, documentos, inventario, ventas y probabilidades.
- Indices para filtros frecuentes de clientes, productos, inventario y ventas.
- Semilla idempotente de empresa, roles y categoria inicial.
- RLS habilitado sin politicas publicas en todas las tablas.
- Modelo entidad-relacion y diccionario de datos.
- Pruebas estructurales sin requerir credenciales reales.

## 2. Evidencia automatizada

La implementacion se valida con:

```powershell
uv run ruff check app tests ../database/migrations ../database/seeds
uv run pytest -q
uv run python scripts/verify_database.py --company-slug "salesia-enterprise"
uv run alembic -c alembic.ini upgrade head --sql
uv run alembic -c alembic.ini downgrade 20261002_0001:base --sql
```

Las validaciones comprueban:

- presencia de las 22 tablas;
- resolucion de todas las claves foraneas;
- compilacion del DDL para PostgreSQL;
- correspondencia entre modelos y migracion;
- uso de tipos decimales para dinero;
- presencia de restricciones criticas;
- normalizacion de la URI de Supabase para psycopg 3.

## 3. Verificacion en infraestructura real

La migracion se aplico correctamente al proyecto Supabase configurado mediante
el Session Pooler y SSL. La comprobacion posterior obtuvo:

- PostgreSQL 17.11.
- Revision Alembic `20261002_0001 (head)`.
- 22 tablas de aplicacion.
- Empresa `SalesIA Enterprise` con slug `salesia-enterprise`.
- Roles `administrator`, `manager` y `seller`.
- Una categoria inicial `General`.
- RLS activo en las 22 tablas de aplicacion.
- Cero politicas publicas de acceso directo.
- Semilla ejecutada dos veces sin duplicar registros.

## 4. Criterios de aceptacion

| Criterio del plan | Estado |
| --- | --- |
| Esquema de usuarios, roles, clientes, productos, ventas e inventario | Implementado |
| Entidades analiticas y relaciones | Implementado |
| Indices para busquedas frecuentes | Implementado |
| Constraints y claves foraneas | Implementado |
| Migracion y seed inicial | Implementado y verificado |
| Ejecucion sobre Supabase | Verificada |

## 5. Condicion final de cierre

La condicion se cumplio: `alembic current` corresponde a
`20261002_0001 (head)` y la semilla creo empresa, tres roles y categoria general
sin duplicados. La fase 05 puede comenzar sobre este esquema.
