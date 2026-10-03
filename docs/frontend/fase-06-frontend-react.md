# Fase 06 - Frontend React

## 1. Resultado

La aplicacion React dejo de utilizar autenticacion simulada. La sesion y la
administracion de usuarios consumen la API FastAPI conectada a Supabase.

Se implemento:

- React Router y rutas con URL real;
- proteccion de rutas para usuarios no autenticados;
- autorizacion visual segun el rol recibido desde la API;
- login real mediante `POST /api/v1/auth/login`;
- restauracion de sesion mediante `GET /api/v1/auth/me`;
- almacenamiento temporal del JWT en `sessionStorage`;
- cierre automatico al vencer o invalidarse el token;
- cliente API centralizado con errores uniformes;
- estados de carga, error, vacio y exito;
- listado, filtros y paginacion de usuarios reales;
- creacion y activacion/desactivacion de usuarios;
- proteccion para no desactivar la sesion actual desde la interfaz;
- formularios con validacion HTML y reglas equivalentes al backend.

## 2. Rutas

| URL | Acceso |
| --- | --- |
| `/login` | Publico |
| `/dashboard` | Administrador y gerente |
| `/ventas` | Todos los roles |
| `/clientes` | Todos los roles |
| `/productos` | Todos los roles |
| `/inventario` | Todos los roles |
| `/usuarios` | Solo administrador |

Las pantallas sin permiso redirigen a la pagina inicial permitida para el rol.

## 3. Flujo de datos

```text
React -> FastAPI -> Supabase PostgreSQL
```

El navegador no utiliza claves de Supabase ni accede directamente a sus tablas.
El JWT emitido por FastAPI se agrega como `Authorization: Bearer` en las
solicitudes protegidas.

## 4. Datos reales y demostrativos

Son reales:

- inicio y cierre de sesion;
- usuario actual y rol;
- listado, busqueda, filtros y paginacion de usuarios;
- creacion y cambio de estado de usuarios.

La fase 07 sustituyo posteriormente los datos demostrativos de clientes y
productos por datos reales. Siguen siendo demostrativos:

- ventas e inventario: fase 08;
- dashboard, estadistica, insights y reportes: fases 09 a 12.

## 5. Ejecucion local

Backend, desde `backend/`:

```powershell
uv run uvicorn app.main:app --reload
```

Frontend, desde `frontend/`:

```powershell
npm run dev
```

Abrir `http://localhost:5173/login` e ingresar con un usuario real.

## 6. Verificacion de cierre

```powershell
npm run lint
npm run build
```

La verificacion manual confirmo:

- redireccion de `/usuarios` a `/login` sin sesion;
- error seguro para credenciales incorrectas;
- inicio con el administrador real;
- carga del usuario real desde Supabase;
- restauracion de la sesion al recargar `/usuarios`;
- ausencia de errores o advertencias en la consola del navegador.
