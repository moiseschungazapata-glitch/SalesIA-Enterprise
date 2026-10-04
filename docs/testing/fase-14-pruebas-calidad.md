# Fase 14 - Pruebas y calidad

## Objetivo

Cerrar la verificación integral de SalesIA Enterprise antes del despliegue. La
estrategia combina pruebas unitarias, de API, integración, reglas de interfaz y
aceptación del flujo comercial, siempre sobre bases aisladas o dobles de prueba.
Las pruebas automatizadas no escriben en el proyecto real de Supabase.

## Matriz de cobertura

| Requisito del plan | Evidencia automatizada | Resultado |
| --- | --- | --- |
| Motor estadístico | `backend/tests/unit/test_statistics_engine.py` y `backend/tests/api/test_statistics.py` | Media, mediana, comparación, probabilidad, variable aleatoria y Bayes verificados, incluidos límites inválidos. |
| Endpoints | `backend/tests/api/` | Autenticación, usuarios, catálogo, operaciones, dashboard, estadísticas, insights y reportes verificados con permisos y contratos OpenAPI. |
| Integración | `backend/tests/api/test_operations.py` | Venta atómica, precios del servidor, idempotencia, pago, movimiento y reducción de inventario. |
| Formularios y navegación | `frontend/tests/login.test.tsx`, `frontend/tests/interface.test.tsx` y `frontend/tests/navigation.test.ts` | Validación de acceso, ojo de contraseña, tema persistente, modales, cierre seguro, menú y páginas por rol. |
| Cálculos y casos límite | Pruebas estadísticas, dashboard, inventario, reportes y seguridad del backend | Series vacías, Bayes inconsistente, stock insuficiente, duplicados, sesión vencida y bloqueo temporal. |
| Aceptación | Suite API de operaciones más pruebas de interfaz y cliente HTTP | Acceso seguro, navegación autorizada, operación comercial persistente y tratamiento uniforme de errores. |

## Resultados del cierre

Fecha de validación: 4 de octubre de 2026.

- Backend: **53 pruebas aprobadas**.
- Frontend: **13 pruebas aprobadas** en 4 archivos.
- Total automatizado: **66 pruebas aprobadas**.
- Análisis Python: Ruff sin errores.
- Análisis TypeScript/React: ESLint sin errores.
- Compilación de producción: completada correctamente con Vite.
- Auditoría de dependencias frontend: 0 vulnerabilidades reportadas por npm al instalar el entorno de pruebas.
- Cobertura focal: acceso 95.45 %, modal 95 %, tema 100 %, navegación lateral 71.42 % y cliente HTTP 68.62 % por líneas/declaraciones según corresponda.

La cobertura global del frontend es menor porque las pantallas de negocio se
validan principalmente mediante sus endpoints e integraciones del backend. El
objetivo de esta fase fue proteger los recorridos de mayor riesgo y establecer
una base repetible, no inflar la métrica con pruebas superficiales.

## Comandos reproducibles

Backend:

```powershell
cd C:\SalesIA-Enterprise\backend
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check app tests
```

Frontend:

```powershell
cd C:\SalesIA-Enterprise\frontend
npm test
npm run test:coverage
npm run lint
npm run build
```

El informe HTML local de cobertura se genera en `frontend/coverage/index.html`
y se excluye del repositorio por ser un artefacto regenerable.

## Criterios de aceptación

- Todas las suites terminan sin fallos.
- La compilación de producción termina sin errores.
- Los permisos impiden acceder a páginas y operaciones no autorizadas.
- Las ventas son transaccionales e idempotentes y no permiten stock negativo.
- Los cálculos estadísticos rechazan entradas vacías o inconsistentes.
- Un token rechazado elimina la sesión local y notifica a la aplicación.
- Los formularios principales son accesibles como diálogos y soportan teclado.
- Existe evidencia repetible y documentada para volver a validar el sistema.

## Conclusión

La fase 14 queda cerrada. El sistema cumple el plan de pruebas definido para
esta etapa y está listo para iniciar la fase 15, documentación de usuario y
técnica, sin asuntos de calidad bloqueantes conocidos.
