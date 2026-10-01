# Fase 02 - Decisiones tecnologicas

## 1. Objetivo

Este documento registra las herramientas seleccionadas, su responsabilidad y la
politica de versiones. Las dependencias del backend se instalaran en la fase 05
y las dependencias funcionales del frontend en la fase 06 o en la fase que las
necesite.

## 2. Linea base del entorno

Las versiones observadas en el entorno de desarrollo al cerrar la fase 02 son:

| Herramienta | Linea base |
| --- | --- |
| Python | 3.13 |
| Node.js | 24 |
| npm | 11 |
| FastAPI | 0.141 |
| Pydantic | 2.12 |
| React | 19 |
| TypeScript | 6 |
| Vite | 8 |

Las versiones exactas instaladas pueden recibir correcciones compatibles. Los
manifiestos y archivos lock seran la fuente de verdad durante la implementacion.

## 3. Backend seleccionado

| Herramienta | Responsabilidad | Momento de incorporacion |
| --- | --- | --- |
| Python 3.13 | Lenguaje del backend. | Base del proyecto. |
| FastAPI | API REST y OpenAPI. | Fase 05. |
| Uvicorn | Servidor ASGI local y de aplicacion. | Fase 05. |
| Pydantic 2 | Validacion de entradas y respuestas. | Fase 05. |
| pydantic-settings | Carga validada de variables de entorno. | Fase 05. |
| SQLAlchemy 2 | ORM y acceso sincronico a PostgreSQL. | Fase 04. |
| Alembic | Migraciones versionadas. | Fase 04. |
| psycopg 3 | Controlador PostgreSQL. | Fase 04. |
| PyJWT 2 | Firma y validacion de JWT. | Fase 05. |
| pwdlib con Argon2 | Hash de contraseñas. | Fase 05. |
| pytest | Pruebas de Python. | Fase 14. |
| HTTPX | Pruebas de endpoints FastAPI. | Fase 14. |

El backend utilizara un `pyproject.toml` para declarar dependencias y
configuracion de herramientas. La fase que inicialice las dependencias registrara
tambien una resolucion reproducible con versiones exactas.

## 4. Frontend seleccionado

El frontend ya contiene una base React/Vite. Mientras se completan las fases en
orden, esa base se considera un prototipo y no demuestra que las fases 03 o 06
esten cerradas.

| Herramienta | Responsabilidad | Estado o fase |
| --- | --- | --- |
| React 19 | Componentes y estado de interfaz. | Ya declarado. |
| React DOM 19 | Renderizado en navegador. | Ya declarado. |
| TypeScript 6 | Tipado estatico. | Ya declarado. |
| Vite 8 | Desarrollo y compilacion. | Ya declarado. |
| ESLint 10 | Analisis estatico. | Ya declarado. |
| React Router | Navegacion por URL. | Incorporar en fase 06. |
| React Hook Form | Estado y envio de formularios. | Incorporar en fase 06. |
| Zod | Validacion de formularios en el navegador. | Incorporar en fase 06. |
| Fetch API | Comunicacion HTTP. | Usar mediante un cliente central. |
| Recharts | Graficos de Analytics. | Incorporar en fase 10. |
| Vitest | Pruebas unitarias del frontend. | Fase 14. |
| Testing Library | Pruebas de componentes. | Fase 14. |
| Playwright | Flujos de aceptacion en navegador. | Fase 14. |

No se utilizara Redux en la primera version. El estado local se manejara con
React y hooks; si el volumen de datos remotos lo justifica, se evaluara una
herramienta de cache en la fase 06.

La primera version utilizara CSS propio. No se incorpora una biblioteca visual
antes de definir el sistema de diseño en la fase 03.

## 5. Base de datos

| Decision | Seleccion |
| --- | --- |
| Motor | PostgreSQL. |
| Acceso | SQLAlchemy 2 sincronico. |
| Migraciones | Alembic. |
| Identificadores | Enteros generados por la base en la primera version. |
| Dinero | Tipos decimales, nunca `float`. |
| Fechas | Marca temporal consistente y presentacion en `America/Lima`. |
| Integridad | Claves foraneas, restricciones e indices definidos en fase 04. |

No se añade Redis, una base documental ni un almacen analitico en la primera
version.

## 6. Dependencias y archivos lock

- `frontend/package.json` declara las dependencias directas de React.
- `frontend/package-lock.json` conserva la resolucion exacta y debe mantenerse.
- La instalacion reproducible del frontend utilizara `npm ci` cuando exista el
  lockfile actualizado.
- No existe un paquete Node en la raiz; por eso la raiz no debe tener
  `package-lock.json`.
- El backend tendra su propio manifiesto cuando comience la fase 04 o 05.
- No se comparten `node_modules` ni entornos virtuales entre aplicaciones.
- Toda dependencia nueva debe responder a una necesidad de la fase activa.

## 7. Politica de versiones

- Los runtimes mantienen la linea mayor acordada: Python 3.13 y Node.js 24.
- Las dependencias directas declaran una version compatible controlada.
- Los archivos lock conservan versiones exactas instaladas.
- Una actualizacion mayor se realiza de forma intencional y con verificacion de
  compilacion y pruebas.
- No se ejecuta una actualizacion general de dependencias durante otra fase sin
  una necesidad concreta.
- Las versiones se revisan antes del despliegue de la fase 15.

## 8. Herramientas descartadas por ahora

| Herramienta o enfoque | Motivo |
| --- | --- |
| Microservicios | Complejidad innecesaria para una empresa y un almacen. |
| Redux | El estado inicial no justifica otra capa global. |
| Axios | Fetch cubre las necesidades iniciales. |
| Docker obligatorio en desarrollo | Puede añadirse en despliegue sin bloquear el aprendizaje inicial. |
| Archivo OpenAPI manual | FastAPI generara la especificacion ejecutable. |
| ORM asincronico | La variante sincronica es mas sencilla para el alcance inicial. |

## 9. Responsabilidad por fase

| Fase | Uso de estas decisiones |
| --- | --- |
| 03 | Definir componentes, navegacion y sistema visual. |
| 04 | Incorporar PostgreSQL, SQLAlchemy, psycopg y Alembic. |
| 05 | Incorporar FastAPI, Pydantic, JWT, Argon2 y configuracion. |
| 06 | Completar enrutamiento, formularios y consumo de API en React. |
| 09 y 10 | Evaluar dependencias estadisticas y de graficos. |
| 14 | Incorporar herramientas de prueba. |
| 15 | Revisar versiones, builds y dependencias de produccion. |

## 10. Criterios de aceptacion

- Los runtimes y lineas principales estan definidos.
- Cada dependencia prevista tiene una responsabilidad y una fase.
- Frontend y backend mantienen manifiestos independientes.
- El lockfile valido del frontend se conserva.
- La raiz no simula ser un paquete Node.
- Las herramientas descartadas tienen una razon documentada.
- La seleccion no obliga a implementar fases posteriores.

## 11. Referencias tecnicas

- [SQLAlchemy 2 - Uso de sesiones](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [Alembic - Tutorial oficial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [FastAPI - Seguridad con JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [Vite - Variables de entorno](https://vite.dev/guide/env-and-mode)
