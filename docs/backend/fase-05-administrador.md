# Fase 05 - Creacion del administrador inicial

## 1. Principio

El proyecto no incluye credenciales predeterminadas. El primer administrador se
crea mediante un comando interactivo que oculta la contraseña y guarda solo su
hash Argon2id.

## 2. Comando

Desde `backend/`:

```powershell
uv run python scripts/create_admin.py `
  --name "Nombre del administrador" `
  --email "correo@empresa.com" `
  --company-slug "salesia-enterprise"
```

El comando solicita y confirma la contraseña sin mostrarla en pantalla. No se
debe incluir la contraseña como argumento, variable versionada, mensaje o
captura.

## 3. Verificacion

Iniciar el backend:

```powershell
uv run uvicorn app.main:app --reload
```

Abrir `http://127.0.0.1:8000/docs` y ejecutar:

```http
POST /api/v1/auth/login
```

con el correo y contraseña elegidos. La respuesta debe incluir un
`access_token`, nunca el hash ni la contraseña.

## 4. Recuperacion durante desarrollo

Si se olvida la contraseña, un administrador autenticado podra cambiarla con
`PATCH /api/v1/users/{id}`. Mientras solo exista un administrador y no pueda
iniciar sesion, se debe crear un comando controlado de recuperacion; nunca se
edita `password_hash` manualmente en Supabase.

