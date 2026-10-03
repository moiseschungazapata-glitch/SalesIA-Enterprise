# Fase 03 - Sistema visual y componentes base

## 1. Control del documento

| Campo | Valor |
| --- | --- |
| Proyecto | SalesIA Enterprise |
| Fase | 03 - UX/UI empresarial |
| Entregable | Sistema visual y componentes base |
| Alcance | Primera version para computadora y tableta |
| Estado | Completo y validado para cierre |
| Implementacion de referencia | `frontend/src/App.css` y `frontend/src/components` |

## 2. Objetivo

Definir un lenguaje visual consistente para las pantallas operativas de la
primera version. Este documento fija decisiones de presentacion e interaccion;
la persistencia, autorizacion efectiva y validacion de negocio corresponden a
fases posteriores.

## 3. Principios de diseño

- La operacion principal debe reconocerse antes que los datos secundarios.
- Cada pantalla presenta un solo titulo principal y una accion primaria clara.
- El color complementa al texto, pero nunca es la unica señal de estado.
- Las listas conservan encabezados, filtros y conteo de resultados.
- Los formularios usan etiquetas visibles y mensajes que indican como corregir.
- Las acciones no autorizadas no se muestran para el rol actual.
- No se utilizan acciones de eliminacion definitiva en la primera version.
- La interfaz se diseña para computadora y tableta sin agregar alcance movil.

## 4. Paleta de color

| Token | Valor | Uso |
| --- | --- | --- |
| Azul principal | `#155EEF` | Acciones primarias, seleccion y foco. |
| Azul oscuro | `#0B4ACB` | Interaccion y contraste de acciones. |
| Cyan | `#06B6D4` | Acentos de marca y visualizaciones simples. |
| Cyan suave | `#ECFEFF` | Fondos informativos de baja intensidad. |
| Texto principal | `#1F2937` | Texto general y controles. |
| Negro de titulos | `#111827` | Titulos y cifras principales. |
| Gris 50 | `#F8FAFC` | Fondo general. |
| Gris 100 | `#F1F5F9` | Fondos secundarios. |
| Gris 200 | `#E2E8F0` | Divisores y bordes. |
| Gris 300 | `#CBD5E1` | Bordes de controles. |
| Texto secundario | `#667085` | Descripciones y ayudas. |
| Exito | `#16A34A` | Operacion correcta o estado activo. |
| Advertencia | `#D97706` | Situacion que requiere revision. |
| Error | `#DC2626` | Error, dato invalido o riesgo. |
| Blanco | `#FFFFFF` | Superficies, tarjetas y controles. |

Los fondos suaves de exito, advertencia y error son `#ECFDF3`, `#FFF7ED` y
`#FEF2F2`. Cada estado incluye texto o icono ademas del color.

## 5. Tipografia

- Familia: fuente sans serif del sistema para evitar dependencias externas.
- Titulo de pagina: peso 700 u 800, entre 24 y 32 px segun el ancho disponible.
- Titulo de panel: peso 700, entre 16 y 20 px.
- Texto base: entre 13 y 16 px.
- Texto auxiliar: entre 11 y 13 px, sin bajar el contraste minimo.
- Etiquetas superiores: mayusculas, peso 800 y espaciado entre letras.
- Cifras KPI: peso 800 y jerarquia superior al texto descriptivo.

## 6. Espaciado, bordes y elevacion

La escala base es de 4 px. Los espacios habituales son 4, 8, 12, 16, 24 y
32 px. Los formularios y paneles usan separaciones mayores que los elementos
internos para conservar agrupaciones reconocibles.

| Elemento | Decision |
| --- | --- |
| Controles | Altura minima 40 px. |
| Botones | Altura minima 36 px; accion principal claramente diferenciada. |
| Tarjetas | Radio entre 10 y 16 px. |
| Campos | Radio de 8 px y borde visible. |
| Paneles | Borde gris y sombra discreta cuando mejora la separacion. |
| Foco | Contorno azul visible y no sustituido solo por sombra. |

## 7. Estructura de pagina

La aplicacion usa cuatro zonas:

1. Barra lateral con marca, navegacion permitida y cierre de sesion.
2. Cabecera con contexto, perfil y rol actual.
3. Aviso exclusivo del prototipo durante la fase 03.
4. Contenido con cabecera de pagina, indicadores y paneles.

El ancho de contenido se adapta al espacio disponible. Las tablas usan un
contenedor con desplazamiento horizontal antes de comprimir columnas hasta
volverlas ilegibles.

## 8. Componentes base

| Componente | Variantes y reglas |
| --- | --- |
| Sidebar | Opcion normal, activa y no visible por permiso. |
| Header | Contexto de pagina, identidad y rol; el selector de rol solo existe en el prototipo. |
| PageHeader | Etiqueta, titulo, descripcion y accion opcional. |
| Boton | Primario, secundario, compacto, deshabilitado y peligro controlado. |
| Campo | Texto, correo, contraseña, numero, fecha, selector y area de texto. |
| Tabla | Encabezado, filas, estado, accion contextual y resultado vacio. |
| KPI | Etiqueta, valor, detalle y tendencia opcional. |
| Estado | Cargando, vacio, error y exito con texto explicativo. |
| Confirmacion | Titulo directo, consecuencia, cancelar y accion explicita. |
| Etiqueta de estado | Exito, advertencia, error y neutral con texto visible. |

Los componentes implementados de referencia son `Sidebar`, `Header`,
`PageHeader`, `KpiCard` y `StateMessage`.

## 9. Formularios

- Una etiqueta visible identifica cada control.
- Los campos relacionados pueden ocupar dos columnas en computadora.
- En tableta se reorganizan en una columna cuando el espacio sea insuficiente.
- El primer error debe recibir foco cuando se implemente la logica funcional.
- Los botones de envio muestran estado deshabilitado durante el procesamiento.
- Un error recuperable conserva lo escrito.
- Cancelar o salir con cambios solicita confirmacion.
- Los importes se muestran en PEN con dos decimales.

## 10. Estados de experiencia

| Estado | Presentacion |
| --- | --- |
| Cargando | Indicador de progreso, titulo breve y contexto de la operacion. |
| Vacio | Explica que no existen resultados y ofrece una accion solo si el rol puede ejecutarla. |
| Error | Describe el problema sin culpar al usuario y ofrece reintentar cuando corresponda. |
| Exito | Confirma el resultado y presenta el siguiente paso. |
| Sin permiso | Explica que el perfil no puede usar la funcion y permite volver. |
| Sesion vencida | Informa el cierre y dirige al inicio de sesion. |
| Formulario invalido | Mensaje general y detalle junto a cada campo afectado. |

## 11. Responsive

| Ancho | Comportamiento |
| --- | --- |
| Mayor de 1050 px | Sidebar completa, paneles en varias columnas y formularios compactos. |
| 761 a 1050 px | Tableta horizontal; grillas reducidas y tablas desplazables. |
| Hasta 760 px | Tableta estrecha; sidebar compacta, acciones apiladas y formularios de una columna. |

Los puntos de cambio son una guia visual. En la fase 06 se validaran con los
dispositivos objetivo y pruebas de componentes.

## 12. Accesibilidad

- HTML semantico para navegacion, encabezados, formularios y tablas.
- Etiquetas asociadas visualmente a los controles.
- Navegacion operable con teclado.
- Foco visible y orden de tabulacion predecible.
- Texto alternativo para imagenes informativas cuando se incorporen.
- Contraste suficiente entre texto, fondo y estados.
- Mensajes que no dependen exclusivamente de color o posicion.
- Botones con nombres de accion y no solamente iconos ambiguos.

## 13. Limites de la fase

Los graficos estadisticos, exportaciones, reportes avanzados, predicciones e
insights automaticos no forman parte de la navegacion activa de esta version.
Sus archivos de prototipo pueden conservarse como referencia para las fases 09
a 12.

## 14. Criterios de aceptacion

- La paleta coincide con la identidad azul y cyan aprobada.
- Tipografia, espacios, bordes y estados tienen reglas reutilizables.
- Los componentes base cubren navegacion, formularios, tablas y mensajes.
- Computadora y tableta tienen comportamiento definido.
- Las acciones y estados se comprenden sin depender solo del color.
- El prototipo usa los tokens y patrones descritos.
- Los modulos reservados no aparecen en la navegacion activa.

