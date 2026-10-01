# Fase 03 - Diseño de formularios

## 1. Control del documento

| Campo | Valor |
| --- | --- |
| Proyecto | SalesIA Enterprise |
| Fase | 03 - UX/UI |
| Entregable | Especificacion de formularios |
| Alcance | Primera version del sistema |
| Estado | Definido |
| Origen | Requisitos de fase 01, contratos y permisos de fase 02 |

## 2. Objetivo

Definir los campos, controles, validaciones, acciones y respuestas visuales de
los formularios de la primera version antes de implementarlos en React.

Los nombres visibles se presentan en español. Los nombres enviados a la API
mantienen el formato `snake_case` definido en los contratos. El backend vuelve
a validar todos los datos y conserva la decision final sobre cada operacion.

## 3. Reglas comunes

### 3.1 Presentacion

- Cada campo tiene una etiqueta visible; el texto de ejemplo no reemplaza la
  etiqueta.
- Los campos obligatorios se identifican con `*` y se explican al inicio.
- En computadora se permiten dos columnas para campos cortos relacionados.
- En tableta los campos se colocan en una sola columna cuando falte espacio.
- Los formularios de mantenimiento usan una cabecera con titulo, descripcion y
  accion para regresar.
- Los formularios no muestran identificadores internos al usuario, salvo el
  numero comercial de una venta.
- Los importes se presentan en soles con dos decimales, por ejemplo `S/ 150.00`.

### 3.2 Validacion

- Se eliminan espacios accidentales al principio y al final de textos.
- Al enviar, el foco se mueve al primer campo invalido.
- El error aparece junto al campo y explica como corregirlo.
- Un error general aparece encima de las acciones cuando no pertenece a un
  campo concreto.
- Las validaciones simples pueden ejecutarse al salir del campo; las reglas de
  negocio se confirman con el backend.
- Los datos escritos se conservan cuando la API responde con un error.
- El boton principal se deshabilita mientras se procesa la solicitud para
  evitar envios repetidos.

### 3.3 Acciones

Los formularios de creacion y edicion utilizan:

- **Guardar:** accion principal.
- **Cancelar:** vuelve a la lista o al detalle sin guardar.
- **Desactivar o activar:** accion separada en la edicion cuando corresponda.

Si el usuario intenta salir con cambios sin guardar, se muestra una confirmacion
con `Seguir editando` y `Descartar cambios`.

Las acciones de desactivacion y confirmacion de venta requieren una confirmacion
explicita. No se utilizan botones de eliminacion definitiva.

### 3.4 Estados de envio

| Estado | Comportamiento |
| --- | --- |
| Inicial | Campos disponibles y accion principal visible. |
| Invalido | Mensajes junto a los campos; no se envia la solicitud. |
| Enviando | Controles bloqueados y boton con texto de progreso. |
| Exito | Mensaje claro y redireccion al detalle o a la lista. |
| Error recuperable | Se conserva la captura y se permite corregir o reintentar. |
| Sesion vencida | Se informa el vencimiento y se regresa al inicio de sesion. |
| Sin permiso | Se informa que la accion no esta disponible para el rol. |

## 4. Inicio de sesion

**Formulario:** FO-AU-01  
**Pantalla relacionada:** AU-01  
**Acceso:** publico

| Campo visible | Control | API | Regla |
| --- | --- | --- | --- |
| Correo electronico | `email` con teclado de correo | `email` | Obligatorio y con formato valido. |
| Contraseña | Contraseña con accion mostrar u ocultar | `password` | Obligatoria. |

Acciones:

- `Iniciar sesion` envia el formulario.
- La tecla Enter ejecuta la misma accion.

Mensajes:

- Credenciales incorrectas: `El correo o la contraseña son incorrectos.`
- Usuario desactivado: `Tu usuario esta desactivado. Contacta al administrador.`
- Error de conexion: `No pudimos conectar con el sistema. Intenta nuevamente.`

No se incluyen registro, recuperacion de contraseña ni opcion para mantener la
sesion abierta.

## 5. Usuarios

### 5.1 Crear usuario

**Formulario:** FO-US-01  
**Pantalla relacionada:** US-02  
**Acceso:** administrador

| Campo visible | Control | API | Regla |
| --- | --- | --- | --- |
| Nombre completo | Texto | `name` | Obligatorio. |
| Correo electronico | Correo | `email` | Obligatorio, formato valido y unico. |
| Rol | Selector | `role` | Administrador, Vendedor o Gerente. |
| Contraseña inicial | Contraseña | `password` | Obligatoria, entre 12 y 128 caracteres. |
| Confirmar contraseña | Contraseña | No se envia | Debe coincidir con la contraseña inicial. |

El usuario se crea activo. Un correo duplicado se informa junto al campo de
correo. El boton principal usa el texto `Crear usuario`.

### 5.2 Editar usuario

**Formulario:** FO-US-02  
**Pantalla relacionada:** US-03  
**Acceso:** administrador

Campos editables: nombre, correo, rol y estado activo. La contraseña no se
muestra. La accion `Asignar nueva contraseña` despliega dos campos:

- Nueva contraseña, entre 12 y 128 caracteres.
- Confirmar nueva contraseña, solo para validacion visual.

Si los campos de contraseña permanecen cerrados o vacios, `new_password` no se
envia. Desactivar un usuario solicita confirmacion y explica que ya no podra
iniciar sesion.

### 5.3 Filtros de usuarios

**Formulario:** FI-US-01  
**Pantalla relacionada:** US-01

| Filtro | Control | Comportamiento |
| --- | --- | --- |
| Buscar | Texto | Busca por nombre o correo. |
| Rol | Selector | Todos, Administrador, Vendedor o Gerente. |
| Estado | Selector | Todos, Activos o Inactivos. |

Incluye `Limpiar filtros`. El cambio de filtros regresa a la primera pagina.

## 6. Clientes

### 6.1 Crear cliente

**Formulario:** FO-CL-01  
**Pantalla relacionada:** CL-02  
**Acceso:** administrador

| Campo visible | Control | API | Regla |
| --- | --- | --- | --- |
| Tipo de cliente | Opciones Persona o Empresa | `customer_type` | Obligatorio. |
| Tipo de documento | Valor automatico | `document_type` | DNI para persona y RUC para empresa. |
| Numero de documento | Texto numerico | `document_number` | DNI de 8 digitos o RUC de 11 digitos; unico. |
| Nombre completo o razon social | Texto | `name` | Obligatorio; la etiqueta cambia segun el tipo. |
| Telefono | Texto | `phone` | Opcional. |
| Correo electronico | Correo | `email` | Opcional; si se escribe, debe ser valido. |
| Direccion | Texto de varias lineas | `address` | Opcional. |

Al cambiar Persona por Empresa se actualizan el tipo de documento, la longitud
esperada y la etiqueta del nombre. Si ya se escribio un documento, se solicita
confirmacion antes de limpiarlo.

El cliente se crea activo. Un DNI o RUC duplicado se informa junto al numero de
documento.

### 6.2 Editar cliente

**Formulario:** FO-CL-02  
**Pantalla relacionada:** CL-04  
**Acceso:** administrador

El tipo y numero de documento se muestran como datos de solo lectura. Se pueden
editar nombre o razon social, telefono, correo, direccion y estado.

Al desactivar, la confirmacion explica que el cliente conservara su historial y
dejara de estar disponible para ventas nuevas.

### 6.3 Filtros de clientes

**Formulario:** FI-CL-01  
**Pantalla relacionada:** CL-01

| Filtro | Control | Comportamiento |
| --- | --- | --- |
| Buscar | Texto | Busca por nombre, razon social, DNI o RUC. |
| Estado | Selector | Todos, Activos o Inactivos. |

Para vendedores, la vista usada al registrar una venta muestra unicamente
clientes activos.

## 7. Categorias

### 7.1 Crear categoria

**Formulario:** FO-CA-01  
**Pantalla relacionada:** CA-01  
**Acceso:** administrador

| Campo visible | Control | API | Regla |
| --- | --- | --- | --- |
| Nombre | Texto | `name` | Obligatorio y unico. |
| Descripcion | Texto de varias lineas | `description` | Opcional. |

El formulario puede presentarse en un panel lateral desde la gestion de
categorias para conservar visible la lista. El boton principal dice `Crear
categoria`.

### 7.2 Editar categoria

**Formulario:** FO-CA-02  
**Pantalla relacionada:** CA-01  
**Acceso:** administrador

Permite cambiar nombre, descripcion y estado. Al desactivar, se informa que la
categoria no podra asignarse a productos activos nuevos. Un nombre duplicado se
muestra junto al campo `Nombre`.

### 7.3 Filtros de categorias

**Formulario:** FI-CA-01

Incluye busqueda por nombre y selector de estado. La lista de categorias usada
en formularios de producto muestra solamente categorias activas.

## 8. Productos

### 8.1 Crear producto

**Formulario:** FO-PR-01  
**Pantalla relacionada:** PR-02  
**Acceso:** administrador

| Campo visible | Control | API | Regla |
| --- | --- | --- | --- |
| Codigo SKU | Texto | `sku` | Obligatorio y unico. |
| Nombre | Texto | `name` | Obligatorio. |
| Descripcion | Texto de varias lineas | `description` | Opcional. |
| Categoria | Selector con busqueda | `category_id` | Obligatoria, existente y activa. |
| Precio de venta | Importe en PEN | `unit_price` | Obligatorio, mayor que cero y con hasta dos decimales. |
| Stock inicial | Numero entero | `initial_stock` | Opcional; cero o un entero positivo. Valor inicial: cero. |

El campo de precio presenta el prefijo `S/`, pero la API recibe el decimal sin
el simbolo. Si el stock inicial es mayor que cero, el sistema creara el
movimiento inicial junto con el producto.

El boton principal dice `Crear producto`.

### 8.2 Editar producto

**Formulario:** FO-PR-02  
**Pantalla relacionada:** PR-04  
**Acceso:** administrador

Permite editar SKU, nombre, descripcion, categoria, precio y estado. La
existencia se muestra como dato de solo lectura con la accion `Registrar
movimiento`, que abre el formulario de inventario.

El formulario nunca envia `stock`. Al desactivar, la confirmacion indica que el
producto no podra agregarse a ventas nuevas.

### 8.3 Filtros de productos

**Formulario:** FI-PR-01  
**Pantalla relacionada:** PR-01

| Filtro | Control | Comportamiento |
| --- | --- | --- |
| Buscar | Texto | Busca por SKU o nombre. |
| Categoria | Selector | Todas o una categoria concreta. |
| Estado | Selector | Todos, Activos o Inactivos. |

Para vendedores, la seleccion durante una venta incluye solamente productos
activos.

## 9. Inventario

### 9.1 Registrar movimiento

**Formulario:** FO-IN-01  
**Pantalla relacionada:** IN-03  
**Acceso:** administrador

| Campo visible | Control | API | Regla |
| --- | --- | --- | --- |
| Producto | Selector con busqueda | `product_id` | Obligatorio, existente y activo. |
| Existencia actual | Solo lectura | No se envia | Se actualiza al elegir el producto. |
| Tipo de movimiento | Selector | `movement_type` | Stock inicial, Entrada, Ajuste de entrada o Ajuste de salida. |
| Cantidad | Numero entero | `quantity` | Obligatoria y mayor que cero. |
| Motivo | Texto de varias lineas | `reason` | Obligatorio para explicar el movimiento manual. |
| Existencia resultante | Vista previa | No se envia | Calculada para ayudar a revisar la operacion. |

Reglas de interaccion:

- `Stock inicial` solo aparece para un producto sin movimientos anteriores.
- `Entrada` y `Ajuste de entrada` aumentan la existencia.
- `Ajuste de salida` la reduce y no puede producir stock negativo.
- `Salida por venta` no aparece como opcion manual.
- La vista previa no reemplaza la validacion final del backend.

Antes de enviar, una confirmacion resume producto, tipo, cantidad, existencia
actual, resultado esperado y motivo. El boton final dice `Confirmar movimiento`.

### 9.2 Filtros de existencias

**Formulario:** FI-IN-01  
**Pantalla relacionada:** IN-01

Incluye busqueda por SKU o producto y selector de estado. No incluye filtro de
alerta de stock bajo porque las alertas automaticas estan fuera del alcance.

### 9.3 Filtros de movimientos

**Formulario:** FI-IN-02  
**Pantalla relacionada:** IN-02

| Filtro | Control | Comportamiento |
| --- | --- | --- |
| Producto | Selector con busqueda | Todos o un producto. |
| Tipo | Selector | Todos, Inicial, Entrada, Ajuste de entrada, Ajuste de salida o Venta. |
| Desde | Fecha | Inicio opcional del periodo. |
| Hasta | Fecha | Fin opcional del periodo. |

Si se indican ambas fechas, `Desde` no puede ser posterior a `Hasta`.

## 10. Ventas

### 10.1 Registrar venta

**Formulario:** FO-VE-01  
**Pantallas relacionadas:** VE-02, VE-04 y VE-05  
**Acceso:** administrador y vendedor

Se presenta como una sola pagina dividida en cuatro bloques. En computadora, el
resumen permanece visible al lado derecho; en tableta aparece despues de los
productos.

#### Bloque 1 - Cliente

| Campo visible | Control | API | Regla |
| --- | --- | --- | --- |
| Cliente | Busqueda y seleccion | `customer_id` | Obligatorio, registrado y activo. |

El resultado muestra nombre o razon social y DNI o RUC. No se permite crear un
cliente dentro de la venta porque esa accion corresponde al administrador.

#### Bloque 2 - Productos

| Campo visible | Control | API | Regla |
| --- | --- | --- | --- |
| Producto | Busqueda por SKU o nombre | `items[].product_id` | Activo y no repetido en la venta. |
| Cantidad | Numero entero | `items[].quantity` | Mayor que cero y no superior al stock disponible. |

Cada linea muestra SKU, nombre, stock disponible, precio unitario vigente,
cantidad, subtotal calculado y accion `Quitar`. Al seleccionar el mismo producto
otra vez, se enfoca la linea existente en lugar de crear un duplicado.

Debe existir al menos una linea. El frontend muestra precios y subtotales para
la revision, pero no los envia a la API.

#### Bloque 3 - Pago y resumen

| Campo visible | Control | API | Regla |
| --- | --- | --- | --- |
| Metodo de pago | Selector | `payment_method` | Efectivo, Tarjeta o Transferencia bancaria. |
| Moneda | Solo lectura | No se envia | PEN. |
| Total | Solo lectura | No se envia | Suma visual de subtotales. |

No existen campos para descuento, impuesto, pago parcial, credito ni importe
pagado. El backend obtiene los precios vigentes, calcula el total y registra un
unico pago completo.

#### Bloque 4 - Confirmacion

El boton `Revisar venta` abre un resumen con:

- Cliente.
- Productos, cantidades y precios mostrados.
- Metodo de pago.
- Total estimado en PEN.
- Aviso de que la confirmacion descontara existencias y no podra editarse.

Acciones de la confirmacion:

- `Volver a editar` cierra el resumen sin perder datos.
- `Confirmar venta` realiza un unico envio y queda bloqueado mientras espera.

El frontend genera una clave de idempotencia para el envio. Esta clave no se
muestra ni se solicita al usuario.

#### Resultado

En caso de exito se muestra el numero de venta y la accion `Ver detalle`. La
captura se limpia solamente despues de recibir la confirmacion.

Si cambia el stock, un producto queda inactivo o el cliente deja de estar
disponible, se conserva el formulario y se marca la parte que debe corregirse.
Una respuesta repetida con la misma clave no crea una segunda venta.

### 10.2 Filtros del historial

**Formulario:** FI-VE-01  
**Pantalla relacionada:** VE-01

| Filtro | Control | Disponibilidad |
| --- | --- | --- |
| Numero de venta | Texto | Todos los roles. |
| Desde | Fecha | Todos los roles. |
| Hasta | Fecha | Todos los roles. |
| Cliente | Selector con busqueda | Todos los roles. |
| Vendedor | Selector con busqueda | Administrador y gerente. |
| Estado | Selector | Todos; inicialmente solo Confirmada. |

Para el vendedor no aparece el filtro de vendedor y la consulta siempre queda
limitada a sus propias ventas. Las fechas deben formar un rango valido.

## 11. Dashboard

### 11.1 Filtro de periodo

**Formulario:** FI-DA-01  
**Pantalla relacionada:** DA-01  
**Acceso:** administrador y gerente

| Campo | Control | Regla |
| --- | --- | --- |
| Desde | Fecha | Opcional. |
| Hasta | Fecha | Opcional; no puede ser anterior a Desde. |

Si no se selecciona un periodo se usa el mes actual en `America/Lima`. El
filtro actualiza el resumen comercial basico; no activa calculos estadisticos
avanzados.

## 12. Confirmaciones

| Accion | Titulo | Accion principal |
| --- | --- | --- |
| Descartar cambios | `¿Descartar los cambios?` | Descartar cambios |
| Desactivar cliente | `¿Desactivar este cliente?` | Desactivar cliente |
| Desactivar producto | `¿Desactivar este producto?` | Desactivar producto |
| Desactivar categoria | `¿Desactivar esta categoria?` | Desactivar categoria |
| Desactivar usuario | `¿Desactivar este usuario?` | Desactivar usuario |
| Registrar movimiento | `Confirma el movimiento de inventario` | Confirmar movimiento |
| Registrar venta | `Revisa y confirma la venta` | Confirmar venta |

Las confirmaciones indican el efecto concreto y permiten cancelar sin perder la
captura. La confirmacion de una accion sensible no se cierra con Enter de forma
accidental; el usuario debe activar el boton correspondiente.

## 13. Correspondencia con la API

| Formulario | Operacion prevista |
| --- | --- |
| FO-AU-01 | `POST /api/v1/auth/login` |
| FO-US-01 | `POST /api/v1/users` |
| FO-US-02 | `PATCH /api/v1/users/{id}` |
| FO-CL-01 | `POST /api/v1/customers` |
| FO-CL-02 | `PATCH /api/v1/customers/{id}` |
| FO-CA-01 | `POST /api/v1/categories` |
| FO-CA-02 | `PATCH /api/v1/categories/{id}` |
| FO-PR-01 | `POST /api/v1/products` |
| FO-PR-02 | `PATCH /api/v1/products/{id}` |
| FO-IN-01 | `POST /api/v1/inventory/movements` |
| FO-VE-01 | `POST /api/v1/sales` |

Los filtros corresponden a parametros de consulta de los endpoints `GET`. Los
formularios no agregan operaciones `DELETE` ni envian campos calculados que la
API no acepta.

## 14. Limites de esta fase

Este documento no implementa componentes React, llamadas HTTP, validaciones de
backend ni persistencia. Las longitudes maximas de nombres, descripciones,
telefonos, direcciones y codigos se concretaran con el modelo de datos de la
fase 04 y se reflejaran despues en la interfaz.

No se diseñan formularios de descuentos, impuestos, devoluciones, credito,
facturacion, exportacion, analitica, probabilidad, insights o reportes
avanzados.

## 15. Criterios de aceptacion

- Cada operacion modificable de la primera version tiene un formulario.
- Los campos coinciden con los contratos de la API.
- Crear y editar respetan las diferencias de cada recurso.
- El stock no se edita directamente desde el producto.
- El formulario de inventario no permite una salida manual de tipo venta.
- La venta exige cliente registrado, al menos un producto y un solo pago
  completo.
- El frontend no envia precios ni totales calculados al registrar una venta.
- Los permisos determinan que formularios y filtros aparecen para cada rol.
- Los errores conservan la captura y permiten corregirla.
- Ningun formulario adelanta funciones reservadas para otras fases.

## 16. Siguiente paso de la fase 03

Con la navegacion y los formularios definidos, el siguiente trabajo es crear el
sistema visual: colores, tipografia, espaciado y componentes base. Ese sistema
se aplicara despues a los wireframes de estas pantallas.
