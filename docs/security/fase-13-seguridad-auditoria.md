# Fase 13 - Seguridad y auditoria

## Alcance cerrado

La fase refuerza la autenticacion implementada en la fase 05 sin cambiar el
modelo de roles del producto. Los permisos efectivos son comprobados tanto en
React como, de forma obligatoria, en FastAPI.

| Control | Implementacion |
| --- | --- |
| Roles y permisos | Administrador, gerente y vendedor con matriz por endpoint y pantalla. |
| Proteccion de endpoints | JWT firmado, usuario/empresa/rol activos y sesion central vigente. |
| Validacion de entrada | Schemas Pydantic, limites de longitud, tipos y errores uniformes 422. |
| Acciones criticas | Tabla `audit_logs` para accesos, usuarios, catalogos, ventas, inventario, insights y reportes. |
| Control de sesiones | Tabla `auth_sessions`, JTI almacenado como SHA-256, cierre individual y cierre de otras sesiones. |
| Mapa de accesos | Ubicacion aproximada por IP publica, sin permiso GPS, con mapa interactivo y detalle por sesion. |
| Secretos | `SECRET_KEY` fuera de Git, longitud minima, CORS restringido y SSL obligatorio en produccion. |

## Proteccion de acceso

- Cada inicio correcto crea una sesion revocable en PostgreSQL.
- El JWT solo es valido si su JTI coincide con una sesion activa y no vencida.
- Cerrar sesion revoca el token en el servidor; eliminarlo del navegador ya no
  es el unico control.
- Cambiar correo, rol, estado o contrasena de un usuario revoca sus sesiones.
- Cinco intentos fallidos consecutivos bloquean temporalmente la cuenta durante
  quince minutos. Ambos valores se configuran por variables de entorno.
- Las respuestas de autenticacion usan `Cache-Control: no-store`.

No se incorporaron refresh tokens porque el acceso actual dura 30 minutos y el
producto aun no requiere sesiones de larga duracion. La recuperacion de
contrasena necesita un proveedor de correo y queda fuera de los seis entregables
obligatorios de esta fase.

## Auditoria

Los registros son de solo adicion para la aplicacion. No se guarda el cuerpo
completo de las solicitudes ni contrasenas. Cada evento conserva usuario,
accion, tipo e identificador del recurso, fecha, IP observada por la API y un
`request_id` para correlacionar logs.

Acciones cubiertas:

- inicio correcto, intento rechazado y cierre de sesion;
- revocacion de sesiones;
- alta y cambios sensibles de usuarios;
- altas/cambios de clientes, categorias y productos;
- ajustes de inventario y registro de ventas;
- generacion de insights y reportes.

## API

| Metodo | Endpoint | Acceso |
| --- | --- | --- |
| POST | `/api/v1/auth/logout` | Usuario autenticado |
| GET | `/api/v1/security/sessions` | Usuario autenticado |
| POST | `/api/v1/security/sessions/{id}/revoke` | Propietario de la sesion |
| POST | `/api/v1/security/sessions/revoke-others` | Usuario autenticado |
| POST | `/api/v1/security/sessions/current/location` | Usuario autenticado; solo su sesion actual |
| GET | `/api/v1/security/access-locations` | Administrador: empresa; otros roles: accesos propios |
| GET | `/api/v1/security/audit-logs` | Solo administrador |

La pantalla `/seguridad` permite a cualquier usuario gestionar sus sesiones.
El historial de auditoria solo aparece para administradores.

## Ubicacion aproximada de accesos

Despues de un inicio de sesion correcto, el navegador consulta la ubicacion
general asociada a su IP publica y la guarda en la sesion activa. Este proceso
no utiliza la API GPS del dispositivo, no abre una solicitud de permisos y no
obtiene una direccion domiciliaria.

La pantalla de Seguridad muestra:

- mapa ampliable y desplazable con OpenStreetMap y Leaflet;
- un radio orientativo alrededor de cada estimacion;
- usuario, fecha, dispositivo, IP, proveedor y ciudad o region;
- historial de accesos ubicados, sin ubicar y revocados;
- vista adaptable para escritorio, tablet y celular.

La ubicacion por IP puede corresponder al nodo del proveedor de internet, variar
con redes moviles, VPN o proxy y no debe usarse como prueba de presencia fisica.
Por esa razon la interfaz siempre la identifica como estimacion a nivel de
ciudad o region y nunca como ubicacion exacta.

## Variables de entorno

```text
SECRET_KEY=<valor aleatorio de al menos 32 caracteres>
ACCESS_TOKEN_EXPIRE_MINUTES=30
LOGIN_MAX_FAILED_ATTEMPTS=5
LOGIN_LOCK_MINUTES=15
DATABASE_SSL_MODE=require
CORS_ORIGINS=https://tu-frontend.example
```

Los secretos reales nunca se documentan ni se envian al frontend.

## Migracion

La revision `20261004_0004` agrega:

- `users.failed_login_attempts`;
- `users.locked_until`;
- `auth_sessions` e indices para usuario, vigencia y empresa.

La revision `20261004_0005` agrega a `auth_sessions` las coordenadas aproximadas,
ciudad, region, pais, ISP, zona horaria, fuente y fecha de estimacion.

## Criterios de aceptacion

- Un token sin sesion, vencido o revocado devuelve `401`.
- Un rol sin permiso devuelve `403`.
- Un usuario solo puede revocar sus propias sesiones.
- La auditoria solo puede consultarla un administrador de la misma empresa.
- Una operacion critica confirmada crea su evento en la misma transaccion.
- Las contrasenas, hashes, tokens y secretos no aparecen en auditoria.
