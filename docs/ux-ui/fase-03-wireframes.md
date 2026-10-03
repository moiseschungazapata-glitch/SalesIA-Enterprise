# Fase 03 - Wireframes y especificacion de pantallas

## 1. Control del documento

| Campo | Valor |
| --- | --- |
| Proyecto | SalesIA Enterprise |
| Fase | 03 - UX/UI empresarial |
| Entregable | Wireframes de la primera version |
| Estado | Completo y validado para cierre |
| Fuente | Requisitos, contratos API, permisos y formularios aprobados |

## 2. Convenciones

Los wireframes son estructurales. No representan datos reales ni sustituyen la
implementacion de las fases 04 a 08.

- `[Primario]` representa la accion principal.
- `[Secundario]` representa una accion alternativa.
- Los controles entre parentesis son campos o filtros.
- Una accion marcada por rol no aparece para perfiles sin permiso.
- Las tablas incluyen desplazamiento horizontal en tableta cuando sea necesario.

## 3. Estructura global autenticada

```text
+------------------+--------------------------------------------------+
| SALESIA          | Contexto de pagina                 Usuario / Rol  |
|                  +--------------------------------------------------+
| Navegacion       | Cabecera de pagina                 [Accion]       |
| permitida        | Descripcion                                       |
| por rol          +--------------------------------------------------+
|                  | Indicadores / filtros / contenido                 |
|                  |                                                  |
| Cerrar sesion    |                                                  |
+------------------+--------------------------------------------------+
```

Navegacion por rol:

| Rol | Inicio | Opciones visibles |
| --- | --- | --- |
| Administrador | Dashboard | Dashboard, Ventas, Clientes, Productos, Inventario, Usuarios. |
| Vendedor | Ventas | Ventas, Clientes, Productos, Inventario. |
| Gerente | Dashboard | Dashboard, Ventas, Clientes, Productos, Inventario. |

## 4. Acceso y estados

### AU-01 - Inicio de sesion

```text
+------------------------------------------+
| SalesIA Enterprise                       |
| Bienvenido de nuevo                      |
| (Correo electronico)                     |
| (Contraseña)                             |
| [Iniciar sesion]                         |
| Mensaje de error cuando corresponda      |
+------------------------------------------+
```

No incluye registro, recuperacion ni seleccion de rol. El selector de perfil
visible despues del acceso es una herramienta temporal de revision del
prototipo y se retirara al integrar la autenticacion real.

### AU-02 - Sesion vencida y acceso denegado

Ambos estados utilizan `StateMessage`: icono, etiqueta, titulo, explicacion y
una accion para iniciar sesion o volver a una pantalla permitida.

## 5. Dashboard

### DA-01 - Resumen comercial

```text
+----------------------------------------------------------------+
| Resumen comercial                      (Desde) (Hasta) [Aplicar]|
+---------------+---------------+---------------+----------------+
| Ventas        | Ingresos      | Ticket medio  | Productos      |
+---------------+---------------+---------------+----------------+
| Ventas del periodo            | Productos por revisar           |
+-------------------------------+--------------------------------+
| Ventas recientes              | Accesos operativos              |
+-------------------------------+--------------------------------+
```

Solo Administrador y Gerente. No presenta estadistica avanzada ni insights.

## 6. Patron de listas y mantenimiento

Clientes, productos, categorias y usuarios comparten este patron:

```text
+----------------------------------------------------------------+
| Titulo y descripcion                         [+ Nuevo registro] |
| (Buscar) (Filtro principal) (Estado)                            |
| Mostrando X de Y                                                |
+----------------------------------------------------------------+
| Columna 1 | Columna 2 | Columna 3 | Estado | Accion            |
| registro  | dato      | dato      | Activo | Ver / Editar      |
+----------------------------------------------------------------+
| Estado vacio o paginacion                                       |
+----------------------------------------------------------------+
```

La accion de alta o edicion solo aparece para Administrador. Vendedor y
Gerente reciben vistas de consulta segun la matriz de permisos.

### Clientes

- CL-01: lista y filtros.
- CL-02: formulario de persona o empresa.
- CL-03: detalle con datos e historial reservado para fase funcional.
- CL-04: edicion y cambio de estado sin eliminar.

### Productos y categorias

- PR-01: lista con SKU, categoria, precio, existencia y estado.
- PR-02: alta; stock inicial se expresa como movimiento.
- PR-03: detalle de producto.
- PR-04: edicion sin modificar stock directamente.
- CA-01: panel de categorias dentro de Productos, con lista, alta y estado.

### Usuarios

- US-01: lista y filtros por rol y estado.
- US-02: alta con contraseña inicial y confirmacion.
- US-03: edicion, cambio de rol/estado y asignacion de contraseña.

## 7. Ventas

### VE-01 - Historial

```text
+----------------------------------------------------------------+
| Ventas                                     [+ Nueva venta]*     |
| (Numero) (Desde) (Hasta) (Cliente) (Vendedor)**                |
| Venta | Cliente | Vendedor | Fecha | Items | Total | Estado     |
+----------------------------------------------------------------+
* Administrador y Vendedor
** Solo Administrador y Gerente
```

El Vendedor consulta unicamente sus ventas. El Gerente no ve la accion de
registro.

### VE-02, VE-04 y VE-05 - Registro

```text
+--------------------------------------+-------------------------+
| 1. Cliente                           | Resumen                 |
| (Buscar cliente activo)              | Cliente                 |
| 2. Productos                         | Lineas                  |
| (Buscar producto) (Cantidad) [Agregar]| Metodo de pago         |
| Lineas: producto, stock, precio      | Total estimado PEN      |
| [Quitar]                             | [Revisar venta]         |
+--------------------------------------+-------------------------+
| Confirmacion: consecuencia, volver y [Confirmar venta]          |
| Resultado: numero de venta o error recuperable                  |
+----------------------------------------------------------------+
```

En tableta el resumen se coloca despues de las lineas. No hay descuento,
impuesto, credito ni pago parcial.

### VE-03 - Detalle

Presenta numero, estado, cliente, vendedor, fecha, lineas, precios aplicados,
pago y total. Una venta confirmada no ofrece editar ni eliminar.

## 8. Inventario

### IN-01 - Existencias

Lista SKU, producto, categoria, existencia y estado. Todos los roles pueden
consultarla. El Vendedor no visualiza el historial de movimientos.

### IN-02 e IN-04 - Movimientos

Administrador y Gerente consultan producto, tipo, cantidad, fecha,
responsable, motivo y venta relacionada.

### IN-03 - Nuevo movimiento

```text
+------------------------------------------------------+
| Registrar movimiento                                 |
| (Producto)       Existencia actual                   |
| (Tipo permitido) (Cantidad)                          |
| (Motivo)         Existencia resultante               |
| [Cancelar] [Revisar movimiento]                      |
+------------------------------------------------------+
| Confirmacion y [Confirmar movimiento]                |
+------------------------------------------------------+
```

Solo Administrador. No ofrece una salida manual de tipo venta.

## 9. Estados transversales

Cada lista y formulario contempla:

| Estado | Contenido minimo |
| --- | --- |
| Cargando | Indicador, titulo y contexto. |
| Sin datos | Explicacion y accion permitida si existe. |
| Error | Descripcion y reintento. |
| Exito | Confirmacion y siguiente paso. |
| Sin permiso | Motivo y retorno seguro. |
| Sesion vencida | Aviso y regreso al login. |
| Formulario invalido | Resumen y errores junto a campos. |

## 10. Correspondencia completa

| Area | Pantallas cubiertas | Evidencia de prototipo |
| --- | --- | --- |
| Acceso | AU-01, AU-02 | `modules/auth`, `StateMessage` |
| Dashboard | DA-01 | `modules/dashboard` |
| Ventas | VE-01 a VE-05 | `modules/sales` |
| Clientes | CL-01 a CL-04 | `modules/customers` |
| Productos | PR-01 a PR-04 | `modules/products` |
| Categorias | CA-01 | Panel dentro de `modules/products` |
| Inventario | IN-01 a IN-04 | `modules/inventory` |
| Usuarios | US-01 a US-03 | `modules/users` |

El prototipo demuestra arquitectura visual, visibilidad y patrones. Las
pantallas de detalle y edicion se especifican en este documento y en el diseño
de formularios; su navegacion real corresponde a la fase 06 y su operacion a
las fases 07 y 08.

## 11. Validacion responsive

- Computadora: sidebar completa y formularios de hasta dos columnas.
- Tableta horizontal: paneles reducidos y tablas desplazables.
- Tableta estrecha: acciones y formularios apilados.
- Los controles mantienen una zona de interaccion minima y foco visible.
- La informacion prioritaria aparece antes que los datos secundarios.

## 12. Criterios de aceptacion

- Todas las pantallas del inventario aprobado tienen estructura definida.
- Los tres roles cuentan con inicio y navegacion permitida.
- Las acciones modificables solo aparecen donde corresponde.
- Usuarios y Categorias forman parte del diseño.
- Los estados de carga, vacio, error, exito y permisos estan definidos.
- Computadora y tableta tienen una adaptacion documentada.
- Los modulos de fases futuras no aparecen en la navegacion activa.

