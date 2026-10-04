# SalesIA Enterprise

Sistema web de gestión de ventas y analítica estadística.

- Frontend: React + TypeScript
- Backend: Python + FastAPI
- Base de datos: PostgreSQL

Desarrollo basado en las 16 fases del Plan Integral de Desarrollo.

## Documentacion

- [Fase 01 - Analisis y levantamiento](docs/requirements/fase-01-requisitos.md)
- [Fase 02 - Arquitectura tecnica](docs/architecture/fase-02-arquitectura.md)
- [Fase 02 - Contratos iniciales de la API](docs/api/fase-02-contratos-api.md)
- [Fase 02 - Autenticacion y permisos](docs/architecture/fase-02-autenticacion-permisos.md)
- [Fase 02 - Configuracion y ambientes](docs/architecture/fase-02-configuracion-ambientes.md)
- [Fase 02 - Decisiones tecnologicas](docs/architecture/fase-02-decisiones-tecnicas.md)
- [Fase 02 - Cierre](docs/architecture/fase-02-cierre.md)
- [Fase 03 - Mapa de pantallas y navegacion](docs/ux-ui/fase-03-navegacion-pantallas.md)
- [Fase 03 - Diseno de formularios](docs/ux-ui/fase-03-formularios.md)
- [Fase 03 - Sistema visual](docs/ux-ui/fase-03-sistema-visual.md)
- [Fase 03 - Wireframes](docs/ux-ui/fase-03-wireframes.md)
- [Fase 03 - Cierre](docs/ux-ui/fase-03-cierre.md)
- [Fase 04 - Modelo entidad-relacion](docs/database/fase-04-modelo-entidad-relacion.md)
- [Fase 04 - Diccionario de datos](docs/database/fase-04-diccionario-datos.md)
- [Fase 04 - Activacion en Supabase](docs/database/fase-04-supabase.md)
- [Fase 04 - Verificacion y cierre](docs/database/fase-04-cierre.md)
- [Fase 05 - Backend y API](docs/backend/fase-05-api.md)
- [Fase 05 - Administrador inicial](docs/backend/fase-05-administrador.md)
- [Fase 05 - Verificacion y cierre](docs/backend/fase-05-cierre.md)
- [Fase 06 - Frontend React](docs/frontend/fase-06-frontend-react.md)
- [Fase 07 - Clientes y productos](docs/catalog/fase-07-clientes-productos.md)
- [Fase 08 - Ventas e inventario](docs/operations/fase-08-ventas-inventario.md)
- [Fase 09 - Motor estadistico](docs/analytics/fase-09-motor-estadistico.md)
- [Fase 10 - Dashboard Analytics](docs/analytics/fase-10-dashboard-analytics.md)
- [Fase 11 - Insights empresariales](docs/analytics/fase-11-insights-empresariales.md)
- [Fase 12 - Reportes](docs/reports/fase-12-reportes.md)

## Estado actual

- Fase 01: completa.
- Fase 02: completa.
- Fase 03: completa.
- Fase 04: completa y verificada en Supabase.
- Fase 05: completada y verificada con el administrador inicial activo en Supabase.
- Fase 06: completada; autenticacion, rutas y usuarios conectados a la API real.
- Fase 07: completada; clientes, categorias y productos conectados a Supabase.
- Fase 08: completada; ventas, pagos e inventario operan de forma transaccional.
- Fase 09: completada; media, mediana, variables, probabilidad y Bayes operan
  mediante FastAPI y conservan datasets, observaciones e historial en Supabase.
- Fase 10: completada; el dashboard calcula KPIs, series, distribuciones y
  desgloses desde ventas reales con filtros comerciales.
- Fase 11: completada; genera insights determinísticos con evidencia numérica,
  trazabilidad hacia datasets y análisis, e historial consultable.
- Fase 12: completada; genera reportes de ventas, estadística, productos,
  clientes y vendedores con historial, CSV y vista imprimible.
- Siguiente fase: 13 - Seguridad y auditoría.

El frontend utiliza datos reales para la sesion, usuarios, clientes, categorias,
productos, ventas, inventario, estadistica, probabilidad y dashboard ejecutivo.
Los insights empresariales también se generan y consultan desde la API real.
Los reportes se guardan como copias históricas y se exportan desde la API real.
