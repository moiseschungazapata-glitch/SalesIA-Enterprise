# Fase 02 - Configuracion y ambientes

## 1. Objetivo

Este documento define como se separara la configuracion de desarrollo, pruebas
y produccion. La configuracion se implementara junto con cada aplicacion y el
despliegue se completara en la fase 15.

## 2. Principios

- El codigo no contiene credenciales ni direcciones propias de un ambiente.
- Los secretos se proporcionan mediante variables de entorno.
- Los archivos `.env` locales no se guardan en Git.
- Los archivos `.env.example` documentan nombres y valores seguros de ejemplo.
- Frontend y backend mantienen variables separadas.
- La base de datos de pruebas nunca comparte datos con desarrollo o produccion.
- Produccion obtiene sus secretos desde la plataforma de despliegue.

## 3. Archivos de referencia

| Archivo | Proposito |
| --- | --- |
| `backend/.env.example` | Variables esperadas por FastAPI. |
| `frontend/.env.example` | Variables publicas utilizadas por Vite. |
| `.gitignore` | Evitar que archivos `.env` y secretos entren a Git. |

Para trabajar localmente, cada ejemplo se copia como `.env` dentro de su misma
carpeta. Los archivos resultantes son locales y no se versionan.

## 4. Ambientes

### 4.1 Desarrollo

- Se ejecuta en la computadora del desarrollador.
- React utiliza el servidor local de Vite.
- FastAPI utiliza recarga automatica cuando se configure en la fase 05.
- PostgreSQL usa una base local llamada `salesia`.
- Los logs son legibles y pueden incluir detalles tecnicos sin secretos.

### 4.2 Pruebas

- Utiliza una base separada, por ejemplo `salesia_test`.
- No utiliza datos reales ni credenciales de produccion.
- Las pruebas pueden crear y limpiar sus propios datos.
- El ambiente se identifica como `test`.
- Los servicios externos se reemplazan por dobles de prueba cuando corresponda.

### 4.3 Produccion

- Usa HTTPS.
- No contiene archivos `.env` dentro de la imagen o repositorio.
- Las credenciales se inyectan desde el proveedor de despliegue.
- CORS permite solamente el dominio publicado del frontend.
- Los logs excluyen contraseñas, tokens y datos sensibles.
- La base de datos tiene credenciales distintas a desarrollo y pruebas.

El proveedor, dominio y proceso de despliegue se definiran en la fase 15.

## 5. Variables del backend

| Variable | Obligatoria | Ejemplo de desarrollo | Descripcion |
| --- | --- | --- | --- |
| `APP_NAME` | No | `SalesIA Enterprise` | Nombre mostrado por FastAPI. |
| `ENVIRONMENT` | Si | `development` | `development`, `test` o `production`. |
| `DATABASE_URL` | Si | `postgresql+psycopg://salesia:salesia@localhost:5432/salesia` | Conexion PostgreSQL. |
| `SECRET_KEY` | Si | Valor local aleatorio | Firma de los JWT. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | Duracion del token. |
| `CORS_ORIGINS` | Si | `http://localhost:5173` | Origenes permitidos separados por coma. |
| `LOG_LEVEL` | No | `INFO` | Nivel minimo de logs. |
| `TIMEZONE` | No | `America/Lima` | Zona usada para presentar fechas. |

Reglas:

- La aplicacion debe detenerse al iniciar si falta `DATABASE_URL` o `SECRET_KEY`.
- `SECRET_KEY` de produccion debe ser aleatoria y diferente en cada ambiente.
- `CORS_ORIGINS=*` no se permite en produccion cuando se usan credenciales.
- `DATABASE_URL` nunca se entrega al frontend.
- El prefijo `/api/v1` forma parte del contrato y no cambia por ambiente.

## 6. Variables del frontend

| Variable | Obligatoria | Ejemplo de desarrollo | Descripcion |
| --- | --- | --- | --- |
| `VITE_APP_NAME` | No | `SalesIA Enterprise` | Nombre visible de la aplicacion. |
| `VITE_API_BASE_URL` | Si | `http://127.0.0.1:8000/api/v1` | Direccion publica de la API. |

Todas las variables que comienzan con `VITE_` se incorporan al codigo enviado al
navegador. Nunca deben contener contraseñas, claves privadas, `SECRET_KEY` ni la
cadena de conexion a PostgreSQL.

## 7. Valores por ambiente

| Configuracion | Desarrollo | Pruebas | Produccion |
| --- | --- | --- | --- |
| `ENVIRONMENT` | `development` | `test` | `production` |
| Base de datos | `salesia` local | `salesia_test` aislada | Servicio PostgreSQL administrado o dedicado |
| API del frontend | API local | Servidor de prueba | URL HTTPS publica |
| CORS | `localhost:5173` | Cliente de pruebas | Dominio publicado |
| Logs | `INFO` o `DEBUG` controlado | `WARNING` o captura de pruebas | `INFO` |
| Secretos | Locales, fuera de Git | Exclusivos de pruebas | Gestor del proveedor |

## 8. Gestion de secretos

- Los ejemplos usan marcadores que no sirven en produccion.
- No se copian secretos en documentación, capturas, commits o mensajes de error.
- Un secreto expuesto debe reemplazarse, no solamente eliminarse del ultimo
  commit.
- Los tokens y contraseñas se ocultan en logs.
- La rotacion y administracion avanzada se completan en la fase 13.

## 9. Responsabilidad por fase

| Fase | Trabajo relacionado |
| --- | --- |
| 02 | Definir variables, ambientes y reglas. |
| 04 | Usar `DATABASE_URL` en SQLAlchemy y Alembic. |
| 05 | Cargar y validar la configuracion del backend. |
| 06 | Consumir `VITE_API_BASE_URL` desde React. |
| 14 | Ejecutar pruebas con ambiente y base aislados. |
| 15 | Configurar secretos, dominios, HTTPS y servicios reales. |

## 10. Criterios de aceptacion

- Desarrollo, pruebas y produccion estan separados.
- Cada variable tiene propietario, proposito y ejemplo seguro.
- El frontend no recibe secretos del backend.
- Las bases de desarrollo y pruebas son distintas.
- Los archivos `.env` permanecen fuera de Git.
- La configuracion de despliegue queda reservada para la fase 15.

## 11. Referencia tecnica

- [Vite - Variables de entorno y modos](https://vite.dev/guide/env-and-mode)
