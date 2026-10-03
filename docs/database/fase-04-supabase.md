# Fase 04 - Activacion en Supabase

## 1. Responsabilidades

Supabase aloja PostgreSQL. SQLAlchemy define el modelo y Alembic crea las
tablas. No se deben crear tablas manualmente en Table Editor.

La arquitectura es:

```text
React -> FastAPI -> SQLAlchemy/Alembic -> Supabase PostgreSQL
```

React no recibe `DATABASE_URL`, la contraseña de PostgreSQL ni una clave
`service_role`.

## 2. Crear el proyecto

1. Iniciar sesion en Supabase y seleccionar **New project**.
2. Elegir la organizacion, un nombre y una region cercana.
3. Generar una contraseña fuerte para PostgreSQL y guardarla en un gestor de
   contraseñas.
4. Esperar a que el proyecto termine de aprovisionarse.
5. Abrir **Connect** y seleccionar **Session pooler** para desarrollo desde una
   red IPv4. Una conexion directa tambien sirve si el equipo dispone de IPv6.
6. Copiar la URI de PostgreSQL y reemplazar el marcador de contraseña. Si la
   contraseña contiene caracteres reservados como `@`, `:` o `/`, deben estar
   codificados para una URL.

No publicar la URI en capturas, chats ni commits.

## 3. Configurar el backend

Desde PowerShell:

```powershell
cd C:\SalesIA-Enterprise\backend
Copy-Item .env.example .env
```

Editar `backend/.env` y cambiar solamente los valores locales necesarios:

```env
ENVIRONMENT=development
DATABASE_URL=postgresql+psycopg://USUARIO:CONTRASENA@HOST:5432/postgres
DATABASE_SSL_MODE=require
```

La aplicacion tambien acepta una URI que empiece por `postgresql://` y la
normaliza automaticamente al controlador psycopg 3.

## 4. Instalar y aplicar

Ejecutar desde `backend/`:

```powershell
uv sync --dev
uv run alembic -c alembic.ini upgrade head
uv run alembic -c alembic.ini current
```

Alembic creara las 22 tablas y activara RLS en todas. Despues cargar los datos
de referencia:

```powershell
uv run python ../database/seeds/seed_reference_data.py `
  --company-name "Nombre de mi empresa" `
  --company-slug "nombre-de-mi-empresa"
```

La semilla se puede ejecutar de nuevo sin duplicar datos.

## 5. Verificar en Supabase

1. Abrir **Table Editor** y comprobar que existen las 22 tablas.
2. Revisar `roles`: debe contener `administrator`, `seller` y `manager`.
3. Revisar `companies`: debe contener la empresa indicada en la semilla.
4. Revisar `categories`: debe existir `General`.
5. Abrir **Database > Migrations** o consultar `alembic_version`; el valor debe
   ser `20261002_0001`.
6. Comprobar que las tablas muestran RLS habilitado.

## 6. Comandos de diagnostico

```powershell
uv run alembic -c alembic.ini current
uv run alembic -c alembic.ini history
uv run pytest -q
```

Para revertir una base de desarrollo vacia:

```powershell
uv run alembic -c alembic.ini downgrade base
```

El downgrade elimina todas las tablas de SalesIA. No debe ejecutarse en una
base que contenga informacion que deba conservarse.

## 7. Referencias

- [Conectar con PostgreSQL en Supabase](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [SQLAlchemy con Supabase](https://supabase.com/docs/guides/troubleshooting/using-sqlalchemy-with-supabase-FUqebT)
- [Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security)

