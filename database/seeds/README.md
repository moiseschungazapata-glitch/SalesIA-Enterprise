# Datos semilla

El script `seed_reference_data.py` crea registros seguros e idempotentes:

- una empresa inicial configurable;
- los roles `administrator`, `seller` y `manager`;
- la categoria `General`.

No crea un usuario administrador con contraseña predeterminada. Ese usuario se
creara en la fase 05 con un hash Argon2id y una contraseña elegida por el
propietario.

Despues de aplicar las migraciones, ejecutar desde `backend/`:

```powershell
uv run python ../database/seeds/seed_reference_data.py `
  --company-name "Mi Empresa" `
  --company-slug "mi-empresa"
```

El comando se puede repetir sin duplicar los registros.
