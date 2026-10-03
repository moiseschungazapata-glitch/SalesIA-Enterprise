# Migraciones de SalesIA Enterprise

Alembic es la unica fuente de verdad para crear o modificar el esquema. No se
deben crear tablas manualmente desde Supabase.

Los comandos se ejecutan desde `backend/`:

```powershell
uv sync --dev
uv run alembic -c alembic.ini upgrade head
uv run alembic -c alembic.ini current
```

Para comprobar el SQL sin conectarse a una base:

```powershell
uv run alembic -c alembic.ini upgrade head --sql
```
