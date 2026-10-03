# SalesIA Enterprise - Frontend

Frontend React + TypeScript de SalesIA Enterprise.

## Configuracion

Copiar `.env.example` a `.env` solo si se necesita cambiar la URL de la API:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

## Desarrollo

```powershell
npm install
npm run dev
```

Abrir `http://localhost:5173/login`.

El backend debe estar disponible en el puerto configurado. El frontend nunca se
conecta directamente a Supabase; todas las operaciones pasan por FastAPI.

## Calidad

```powershell
npm run lint
npm run build
```

La autenticacion, las rutas protegidas, Usuarios, Clientes y Productos utilizan
datos reales. Ventas e Inventario se conectaran en la fase 08.
