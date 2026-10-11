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

## Datos ficticios para pruebas integrales

`seed_demo_business_data.py` agrega a una empresa existente:

- 4 categorías;
- 6 clientes ficticios (personas y empresas);
- 12 productos ficticios;
- inventario inicial y su movimiento trazable para cada producto nuevo.

No crea usuarios, pedidos, ventas ni pagos y no modifica existencias ya creadas.
Todos los correos usan el dominio reservado `example.com` y los documentos están
reservados exclusivamente para demostración.

Vista previa, sin escribir:

```powershell
cd C:\SalesIA-Enterprise\backend
.\.venv\Scripts\python.exe ..\database\seeds\seed_demo_business_data.py
```

Aplicación confirmada:

```powershell
cd C:\SalesIA-Enterprise\backend
.\.venv\Scripts\python.exe ..\database\seeds\seed_demo_business_data.py --apply
```

El script usa `DATABASE_URL` del backend y se puede repetir sin duplicar datos.
