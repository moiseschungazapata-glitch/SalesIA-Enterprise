# Fase 01 - Analisis y levantamiento

## 1. Control del documento

| Campo | Valor |
| --- | --- |
| Proyecto | SalesIA Enterprise |
| Fase | 01 - Analisis y levantamiento |
| Estado | Aprobado para continuar con la fase 02 |
| Alcance | Primera version del sistema |
| Empresa | Una sola empresa |
| Operacion | Un solo local o almacen |
| Moneda | Sol peruano (PEN) |

## 2. Problema

La empresa necesita registrar clientes, productos, existencias y ventas en un
solo sistema. Tambien necesita conservar datos confiables de cada operacion para
consultar resultados comerciales y realizar analisis estadisticos en fases
posteriores.

## 3. Objetivo de la primera version

Construir una aplicacion web que permita autenticar usuarios, administrar
clientes y productos, controlar las existencias de un unico almacen, registrar
ventas pagadas completamente y consultar un resumen comercial basico.

La informacion registrada sera la fuente de datos para los futuros modulos de
estadistica, probabilidad, insights y reportes.

## 4. Alcance incluido

La primera version incluye:

- Inicio de sesion.
- Gestion de usuarios por parte del administrador.
- Gestion de clientes de tipo persona y empresa.
- Gestion de productos y categorias.
- Registro de stock inicial y entradas de inventario.
- Salida automatica de inventario al confirmar una venta.
- Registro de ventas para clientes previamente registrados.
- Un pago completo por venta.
- Consulta del historial y detalle de ventas.
- Resumen basico de ventas, ingresos, ticket promedio y productos vendidos.
- Trazabilidad de los movimientos de inventario.

## 5. Fuera del alcance inicial

Las siguientes funciones se reservan para versiones o fases posteriores:

- Pedidos y cotizaciones.
- Descuentos e impuestos.
- Pagos parciales, ventas a credito y pasarelas de pago.
- Devoluciones y anulaciones.
- Facturacion electronica.
- Multiples empresas, locales, sucursales o almacenes.
- Multiples monedas.
- Transferencias entre almacenes.
- Alertas automaticas de stock.
- Exportacion de reportes.
- Media, mediana, probabilidad, Teorema de Bayes e insights.
- Analitica avanzada y modelos predictivos.

## 6. Actores y permisos

### 6.1 Administrador

- Crear, consultar, actualizar y desactivar usuarios.
- Asignar roles.
- Gestionar clientes, productos y categorias.
- Registrar entradas y ajustes autorizados de inventario.
- Registrar ventas.
- Consultar todas las ventas, existencias y resumen comercial.

### 6.2 Vendedor

- Consultar clientes activos.
- Consultar productos activos y sus existencias.
- Registrar ventas.
- Consultar sus propias ventas.

### 6.3 Gerente

- Consultar todas las ventas.
- Consultar clientes, productos e inventario.
- Consultar el resumen comercial.
- No modificar operaciones comerciales desde el resumen.

Los roles de analista y almacen se reservan para fases posteriores.

## 7. Flujo principal de venta

1. El vendedor inicia sesion.
2. Abre la opcion de nueva venta.
3. Busca y selecciona un cliente registrado y activo.
4. Agrega uno o mas productos activos.
5. Indica una cantidad entera mayor que cero para cada producto.
6. El sistema muestra precio unitario, cantidad, subtotal y total.
7. El vendedor selecciona un metodo de pago permitido.
8. El vendedor confirma la venta.
9. El sistema vuelve a comprobar la disponibilidad de stock.
10. El sistema registra la venta, sus detalles, el pago y los movimientos de
    inventario como una sola operacion.
11. La venta queda confirmada y aparece en el historial.

Si una validacion o escritura falla, la operacion completa se cancela y no se
guardan datos parciales.

## 8. Casos de uso principales

### CU-01 - Iniciar sesion

**Actor:** administrador, vendedor o gerente.

**Resultado esperado:** un usuario activo con credenciales validas accede a las
funciones permitidas para su rol. Un usuario inactivo o con credenciales
incorrectas no obtiene acceso.

### CU-02 - Gestionar clientes

**Actor:** administrador.

**Resultado esperado:** el administrador puede crear, consultar, actualizar y
desactivar clientes. Los clientes con historial comercial se conservan.

### CU-03 - Gestionar productos

**Actor:** administrador.

**Resultado esperado:** el administrador puede crear, consultar, actualizar y
desactivar productos y categorias. Los productos usados en ventas se conservan.

### CU-04 - Registrar movimiento de inventario

**Actor:** administrador.

**Resultado esperado:** toda variacion manual del stock genera un movimiento
con producto, cantidad, tipo, fecha, usuario responsable y motivo.

### CU-05 - Registrar venta

**Actor:** administrador o vendedor.

**Resultado esperado:** se registra una venta confirmada con cliente, vendedor,
productos, cantidades, precios, pago y movimientos de inventario relacionados.

### CU-06 - Consultar historial de ventas

**Actor:** administrador, vendedor o gerente.

**Resultado esperado:** el administrador y el gerente consultan todas las
ventas; el vendedor consulta solamente las ventas que registro. La consulta
permite filtrar por numero, cliente, vendedor, fecha y estado, segun el rol.

### CU-07 - Consultar resumen comercial

**Actor:** administrador o gerente.

**Resultado esperado:** el usuario consulta total vendido, numero de ventas,
ticket promedio, productos mas vendidos y ventas recientes dentro de un rango
de fechas.

## 9. Requisitos funcionales

- **RF-01:** el sistema debe autenticar usuarios mediante sus credenciales.
- **RF-02:** el sistema debe limitar las funciones segun el rol del usuario.
- **RF-03:** el administrador debe poder gestionar usuarios y sus estados.
- **RF-04:** el administrador debe poder gestionar clientes.
- **RF-05:** el administrador debe poder gestionar productos y categorias.
- **RF-06:** el sistema debe conservar el stock actual de cada producto.
- **RF-07:** todo cambio de stock debe generar un movimiento de inventario.
- **RF-08:** el vendedor y el administrador deben poder registrar ventas.
- **RF-09:** toda venta debe registrar sus productos, cantidades y precios.
- **RF-10:** toda venta inicial debe registrar un unico pago por el total.
- **RF-11:** confirmar una venta debe descontar el stock correspondiente.
- **RF-12:** el sistema debe permitir consultar el historial y detalle de ventas.
- **RF-13:** el sistema debe mostrar un resumen comercial por rango de fechas.
- **RF-14:** las ventas confirmadas deben quedar disponibles como fuente para
  futuros analisis.

## 10. Reglas de negocio

- **RN-01:** el sistema pertenece a una sola empresa.
- **RN-02:** la primera version administra un solo local o almacen.
- **RN-03:** todas las operaciones monetarias se registran en PEN.
- **RN-04:** toda venta debe pertenecer a un cliente registrado y activo.
- **RN-05:** un cliente puede ser persona, identificada por DNI, o empresa,
  identificada por RUC.
- **RN-06:** el DNI o RUC de un cliente debe ser unico.
- **RN-07:** un cliente con ventas no puede eliminarse; solamente desactivarse.
- **RN-08:** cada producto debe tener un codigo unico, nombre, categoria, precio
  de venta, stock y estado.
- **RN-09:** el precio de venta debe ser mayor que cero.
- **RN-10:** solo pueden venderse productos activos.
- **RN-11:** una venta debe incluir al menos un producto.
- **RN-12:** la cantidad vendida debe ser un numero entero mayor que cero.
- **RN-13:** no se puede vender una cantidad superior al stock disponible.
- **RN-14:** el stock nunca puede quedar negativo.
- **RN-15:** el stock se descuenta cuando la venta queda confirmada.
- **RN-16:** el precio aplicado se guarda en el detalle de la venta y no cambia
  si posteriormente se modifica el precio del producto.
- **RN-17:** el subtotal de una linea es precio unitario multiplicado por cantidad.
- **RN-18:** el total es la suma de los subtotales.
- **RN-19:** la primera version no calcula descuentos ni impuestos.
- **RN-20:** cada venta se paga completamente con un solo metodo de pago.
- **RN-21:** el importe pagado debe ser igual al total de la venta.
- **RN-22:** venta, detalles, pago y movimientos de inventario deben guardarse en
  una unica operacion; si una parte falla, no se conserva ningun cambio.
- **RN-23:** una venta confirmada no se edita ni elimina.
- **RN-24:** solo las ventas confirmadas participan en el resumen comercial y en
  futuros calculos analiticos.
- **RN-25:** confirmar dos veces la misma solicitud no debe crear ventas duplicadas.

## 11. Datos necesarios para analitica futura

Cada venta debe conservar como minimo:

- Identificador y numero de venta.
- Fecha y hora.
- Cliente.
- Vendedor.
- Estado.
- Moneda.
- Metodo e importe del pago.
- Total.
- Productos vendidos.
- Categoria de cada producto.
- Cantidades, precios unitarios y subtotales.

Estos datos permitiran calcular ventas por periodo, ingresos, numero de
transacciones, ticket promedio, productos mas vendidos y resultados por
vendedor, sin diseñar todavia el motor estadistico.

## 12. Requisitos no funcionales iniciales

- **RNF-01:** la aplicacion debe separar presentacion, logica de negocio y acceso
  a datos.
- **RNF-02:** las entradas deben validarse antes de modificar datos.
- **RNF-03:** las operaciones relacionadas con una venta deben ser atomicas.
- **RNF-04:** las contrasenas nunca deben almacenarse en texto plano.
- **RNF-05:** los secretos y configuraciones deben proporcionarse mediante
  variables de entorno.
- **RNF-06:** la API debe usar respuestas y errores consistentes.
- **RNF-07:** las acciones que afectan ventas e inventario deben conservar la
  identidad del usuario y la fecha.
- **RNF-08:** la interfaz debe funcionar inicialmente en computadoras y tabletas.
- **RNF-09:** la estructura debe permitir incorporar los modulos analiticos sin
  cambiar el flujo comercial principal.

## 13. Criterios de aceptacion de la primera version

1. Un usuario activo puede iniciar sesion y acceder solamente a las funciones
   permitidas para su rol.
2. El administrador puede registrar clientes persona y empresa sin duplicar DNI
   o RUC.
3. El administrador puede registrar productos con precio y stock validos.
4. Todo cambio de stock queda representado por un movimiento de inventario.
5. Un vendedor puede seleccionar un cliente activo y agregar productos activos.
6. El sistema calcula correctamente los subtotales y el total de una venta.
7. El sistema rechaza cantidades invalidas o superiores al stock disponible.
8. Al confirmar una venta, se guardan la cabecera, los detalles, el pago y los
   movimientos de inventario.
9. Si falla una parte del registro, no queda una venta parcial ni cambia el stock.
10. El stock se reduce exactamente en las cantidades vendidas.
11. El historial conserva el precio aplicado aunque cambie el precio del producto.
12. Los permisos de consulta del historial se respetan segun el rol.
13. El resumen comercial utiliza solamente ventas confirmadas.

## 14. Cierre de la fase

La fase 01 se considera cerrada porque se definieron el problema, el objetivo,
el alcance, los actores, los casos de uso, las reglas de negocio, los datos
necesarios y los criterios de aceptacion de la primera version.

Las decisiones tecnicas para implementar estos requisitos corresponden a la
fase 02. El modelo de datos, la API, la interfaz y las pruebas se desarrollaran
en sus fases respectivas.
