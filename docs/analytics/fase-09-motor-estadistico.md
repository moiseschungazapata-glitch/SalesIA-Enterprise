# Fase 09 - Motor estadistico Semana 07

## Estado

Completada el 3 de octubre de 2026.

La fase convierte datos comerciales en datasets persistentes y ejecuta los
calculos en Python/FastAPI. El navegador solo captura parametros y presenta los
resultados; no contiene la logica estadistica oficial.

## Alcance implementado

- Clasificacion de variables cualitativas, cuantitativas discretas y
  cuantitativas continuas.
- Media aritmetica con precision decimal.
- Mediana para series pares e impares.
- Comparacion media-mediana con diferencia e interpretacion explicable.
- Creacion de snapshots de ventas confirmadas por empresa y periodo.
- Probabilidad de eventos a partir de casos favorables y observaciones.
- Variables aleatorias discretas o continuas, con distribucion de frecuencias,
  media, mediana, minimo y maximo.
- Teorema de Bayes con validacion de probabilidades consistentes.
- Persistencia de datasets, variables, observaciones, analisis y resultados.
- Historial de analisis aislado por empresa.
- Acceso para administrador y gerente; el vendedor no accede al modulo.

## Flujo operativo

1. El usuario abre `Analytics` y selecciona monto total o unidades por venta.
2. La API consulta solamente las ventas confirmadas de su empresa.
3. Se crea un snapshot en `datasets`.
4. La variable queda clasificada en `dataset_variables`.
5. Cada venta se conserva como una observacion del snapshot.
6. Python calcula media y mediana y genera una interpretacion.
7. La ejecucion se registra en `statistical_analyses` y sus valores en
   `statistical_results`.
8. El historial puede consultarse posteriormente sin recalcular ni alterar el
   snapshot original.

Los calculos manuales, de probabilidad, variables aleatorias y Bayes siguen el
mismo principio: cada ejecucion genera un dataset y un analisis trazable.

## API

| Metodo | Endpoint | Funcion |
| --- | --- | --- |
| GET | `/api/v1/statistics/variables` | Clasificacion de variables comerciales |
| POST | `/api/v1/statistics/sales/compare` | Media y mediana de ventas reales |
| POST | `/api/v1/statistics/mean` | Media de una serie persistida |
| POST | `/api/v1/statistics/median` | Mediana de una serie persistida |
| POST | `/api/v1/statistics/compare` | Comparacion media-mediana |
| GET | `/api/v1/statistics/analyses` | Historial de analisis de la empresa |
| POST | `/api/v1/probability/events` | Probabilidad de un evento |
| POST | `/api/v1/probability/bayes` | Probabilidad posterior mediante Bayes |
| POST | `/api/v1/random-variables/analyze` | Analisis de una variable aleatoria |

Todos requieren JWT. Los endpoints de escritura responden `201` y registran el
resultado en PostgreSQL.

## Interfaz

- `Analytics`: ejecuta analisis sobre ventas reales, presenta media, mediana,
  diferencia, cantidad de observaciones, clasificacion e historial.
- `Probabilidad`: ofrece formularios funcionales para eventos, variables
  aleatorias y Bayes, mostrando los identificadores persistidos.
- Ambas pantallas estan disponibles para administrador y gerente desde el
  menu principal.

## Validaciones importantes

- No se aceptan series vacias, valores no finitos ni series con mas de 1000
  observaciones manuales.
- Los casos favorables no pueden superar el total de observaciones.
- Las probabilidades se limitan al intervalo `[0, 1]` y `P(B)` debe ser mayor
  que cero.
- Bayes rechaza combinaciones inconsistentes cuyo posterior quede fuera de
  `[0, 1]`.
- Un analisis de ventas sin operaciones en el periodo responde con un error de
  negocio claro y no crea registros parciales.

## Evidencias de verificacion

- Motor unitario: media, mediana par/impar, comparacion, frecuencia y Bayes.
- Persistencia aislada: datasets, observaciones, analisis, resultados, variable
  aleatoria e historial.
- Contrato OpenAPI: rutas de estadistica, probabilidad y variables aleatorias.
- Backend: `ruff` sin errores.
- Frontend: TypeScript/Vite compila y ESLint no reporta errores.
- Supabase: 22 tablas, revision Alembic correcta y RLS activo.
- Prueba transaccional real: escritura completa en las tablas analiticas y
  rollback confirmado, sin conservar datos de prueba.

## Criterios de aceptacion de la fase

- [x] El sistema identifica y clasifica variables estadisticas.
- [x] Calcula correctamente media y mediana.
- [x] Explica la comparacion entre media y mediana.
- [x] Analiza variables aleatorias definidas.
- [x] Calcula probabilidades simples.
- [x] Bayes produce un resultado reproducible y validado.
- [x] Cada analisis y sus resultados quedan almacenados.
- [x] Los datos comerciales reales pueden alimentar el motor.
- [x] El historial respeta el aislamiento por empresa.
- [x] La interfaz consume la API real.

La visualizacion de tendencias, graficos, participacion y KPIs por filtros
corresponde a la fase 10.
