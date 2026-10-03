# Fase 04 - Verificacion y cierre

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

## 3. Limite de la verificacion local

La migracion se ha compilado y validado sin una credencial externa. Para cerrar
la fase contra infraestructura real falta crear el proyecto Supabase, configurar
`backend/.env`, aplicar la migracion y ejecutar la semilla. Esos pasos no
requieren cambios manuales en las tablas.

## 4. Criterios de aceptacion

| Criterio del plan | Estado |
| --- | --- |
| Esquema de usuarios, roles, clientes, productos, ventas e inventario | Implementado |
| Entidades analiticas y relaciones | Implementado |
| Indices para busquedas frecuentes | Implementado |
| Constraints y claves foraneas | Implementado |
| Migracion y seed inicial | Implementado y validado sin conexion |
| Ejecucion sobre Supabase | Pendiente de configurar credencial privada |

## 5. Condicion final de cierre

La fase 04 quedara cerrada cuando `alembic current` muestre
`20261002_0001 (head)` en el proyecto Supabase y la semilla haya creado sus
cuatro grupos de datos de referencia: empresa, tres roles y categoria general.

