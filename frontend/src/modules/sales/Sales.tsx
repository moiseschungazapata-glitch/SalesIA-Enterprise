import { useMemo, useState } from 'react'
import PageHeader from '../../components/PageHeader'
import {
  customers,
  products,
  sales as initialSales,
} from '../../services/mockData'
import type { Sale } from '../../types'

interface CartItem {
  id: number
  productId: number
  product: string
  price: number
  quantity: number
  subtotal: number
}

function Sales() {
  const [saleList, setSaleList] =
    useState<Sale[]>(initialSales)

  const [selectedCustomer, setSelectedCustomer] =
    useState('')

  const [selectedProduct, setSelectedProduct] =
    useState('')

  const [quantity, setQuantity] = useState('1')

  const [payment, setPayment] =
    useState<'Completado' | 'Pendiente'>('Completado')

  const [cart, setCart] = useState<CartItem[]>([])

  const [search, setSearch] = useState('')

  const selectedProductData = products.find(
    (product) =>
      product.id === Number(selectedProduct),
  )

  const addToCart = () => {
    if (
      !selectedProductData ||
      Number(quantity) <= 0
    ) {
      return
    }

    const requestedQuantity = Number(quantity)

    if (
      requestedQuantity >
      selectedProductData.stock
    ) {
      return
    }

    const existingItem = cart.find(
      (item) =>
        item.productId === selectedProductData.id,
    )

    if (existingItem) {
      const newQuantity =
        existingItem.quantity + requestedQuantity

      if (newQuantity > selectedProductData.stock) {
        return
      }

      setCart((current) =>
        current.map((item) =>
          item.productId === selectedProductData.id
            ? {
                ...item,
                quantity: newQuantity,
                subtotal:
                  newQuantity *
                  item.price,
              }
            : item,
        ),
      )
    } else {
      setCart((current) => [
        ...current,
        {
          id: Date.now(),
          productId: selectedProductData.id,
          product: selectedProductData.name,
          price: selectedProductData.price,
          quantity: requestedQuantity,
          subtotal:
            requestedQuantity *
            selectedProductData.price,
        },
      ])
    }

    setSelectedProduct('')
    setQuantity('1')
  }

  const removeFromCart = (id: number) => {
    setCart((current) =>
      current.filter((item) => item.id !== id),
    )
  }

  const total = useMemo(
    () =>
      cart.reduce(
        (sum, item) => sum + item.subtotal,
        0,
      ),
    [cart],
  )

  const filteredSales = saleList.filter(
    (sale) =>
      sale.id
        .toLowerCase()
        .includes(search.toLowerCase()) ||
      sale.customer
        .toLowerCase()
        .includes(search.toLowerCase()) ||
      sale.seller
        .toLowerCase()
        .includes(search.toLowerCase()),
  )

  const averageTicket =
    saleList.length > 0
      ? saleList.reduce(
          (sum, sale) => sum + sale.total,
          0,
        ) / saleList.length
      : 0

  const registerSale = () => {
    if (!selectedCustomer || cart.length === 0) {
      return
    }

    const customer = customers.find(
      (item) =>
        item.id === Number(selectedCustomer),
    )

    if (!customer) {
      return
    }

    const newSale: Sale = {
      id: `V-${String(153 + saleList.length).padStart(5, '0')}`,
      customer: customer.name,
      seller: 'Carlos Rivera',
      date: new Date().toLocaleDateString('es-PE'),
      items: cart.reduce(
        (sum, item) => sum + item.quantity,
        0,
      ),
      total,
      payment,
    }

    setSaleList((current) => [
      newSale,
      ...current,
    ])

    setCart([])
    setSelectedCustomer('')
    setPayment('Completado')
  }

  return (
    <div className="page">
      <PageHeader
        eyebrow="OPERACIÓN COMERCIAL"
        title="Ventas"
        description="Registra operaciones, productos, cantidades y pagos."
      />

      <section className="kpi-grid">
        <article className="kpi-card">
          <div className="kpi-top">
            <span>Ventas registradas</span>
          </div>
          <strong className="kpi-value">
            {saleList.length}
          </strong>
          <span className="kpi-detail">
            operaciones en el frontend
          </span>
        </article>

        <article className="kpi-card">
          <div className="kpi-top">
            <span>Ingresos mostrados</span>
          </div>
          <strong className="kpi-value">
            S/{' '}
            {saleList
              .reduce(
                (sum, sale) => sum + sale.total,
                0,
              )
              .toLocaleString('es-PE')}
          </strong>
          <span className="kpi-detail">
            total de ventas mock
          </span>
        </article>

        <article className="kpi-card">
          <div className="kpi-top">
            <span>Ticket promedio</span>
          </div>
          <strong className="kpi-value">
            S/ {averageTicket.toFixed(0)}
          </strong>
          <span className="kpi-detail">
            promedio por venta
          </span>
        </article>

        <article className="kpi-card">
          <div className="kpi-top">
            <span>Pagos pendientes</span>
          </div>
          <strong className="kpi-value">
            {
              saleList.filter(
                (sale) =>
                  sale.payment === 'Pendiente',
              ).length
            }
          </strong>
          <span className="kpi-detail">
            operaciones pendientes
          </span>
        </article>
      </section>

      <section className="sales-workspace">
        <article className="panel sale-form-panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">
                NUEVA OPERACIÓN
              </span>
              <h2>Registrar venta</h2>
              <p>
                Selecciona cliente y agrega productos al
                pedido.
              </p>
            </div>
          </div>

          <div className="sale-form">
            <label>
              Cliente
              <select
                value={selectedCustomer}
                onChange={(event) =>
                  setSelectedCustomer(
                    event.target.value,
                  )
                }
              >
                <option value="">
                  Seleccionar cliente
                </option>

                {customers
                  .filter(
                    (customer) =>
                      customer.status === 'Activo',
                  )
                  .map((customer) => (
                    <option
                      key={customer.id}
                      value={customer.id}
                    >
                      {customer.name}
                    </option>
                  ))}
              </select>
            </label>

            <label>
              Producto
              <select
                value={selectedProduct}
                onChange={(event) =>
                  setSelectedProduct(
                    event.target.value,
                  )
                }
              >
                <option value="">
                  Seleccionar producto
                </option>

                {products
                  .filter(
                    (product) =>
                      product.stock > 0,
                  )
                  .map((product) => (
                    <option
                      key={product.id}
                      value={product.id}
                    >
                      {product.name} · S/{' '}
                      {product.price}
                    </option>
                  ))}
              </select>
            </label>

            <label>
              Cantidad
              <input
                type="number"
                min="1"
                value={quantity}
                onChange={(event) =>
                  setQuantity(
                    event.target.value,
                  )
                }
              />
            </label>

            <div className="sale-add-row">
              <div className="selected-product-info">
                {selectedProductData ? (
                  <>
                    <strong>
                      {selectedProductData.name}
                    </strong>

                    <span>
                      Stock disponible:{' '}
                      {selectedProductData.stock}
                    </span>
                  </>
                ) : (
                  <>
                    <strong>
                      Selecciona un producto
                    </strong>

                    <span>
                      Aquí aparecerá su disponibilidad.
                    </span>
                  </>
                )}
              </div>

              <button
                type="button"
                className="primary-button"
                onClick={addToCart}
              >
                Agregar
              </button>
            </div>
          </div>

          <div className="cart-section">
            <div className="cart-header">
              <div>
                <strong>
                  Productos de la venta
                </strong>

                <span>
                  {cart.length} productos
                </span>
              </div>
            </div>

            {cart.length === 0 ? (
              <div className="empty-state cart-empty">
                Agrega al menos un producto para registrar
                la venta.
              </div>
            ) : (
              <div className="cart-list">
                {cart.map((item) => (
                  <div
                    className="cart-row"
                    key={item.id}
                  >
                    <div>
                      <strong>
                        {item.product}
                      </strong>

                      <span>
                        {item.quantity} × S/{' '}
                        {item.price.toFixed(2)}
                      </span>
                    </div>

                    <strong>
                      S/{' '}
                      {item.subtotal.toLocaleString(
                        'es-PE',
                      )}
                    </strong>

                    <button
                      type="button"
                      className="remove-button"
                      onClick={() =>
                        removeFromCart(item.id)
                      }
                    >
                      Quitar
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="sale-summary">
            <div>
              <span>Total</span>
              <strong>
                S/ {total.toLocaleString('es-PE')}
              </strong>
            </div>

            <label>
              Estado del pago
              <select
                value={payment}
                onChange={(event) =>
                  setPayment(
                    event.target.value as
                      | 'Completado'
                      | 'Pendiente',
                  )
                }
              >
                <option value="Completado">
                  Completado
                </option>

                <option value="Pendiente">
                  Pendiente
                </option>
              </select>
            </label>

            <button
              type="button"
              className="primary-button"
              disabled={
                !selectedCustomer ||
                cart.length === 0
              }
              onClick={registerSale}
            >
              Registrar venta
            </button>
          </div>
        </article>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <span className="eyebrow">
              HISTORIAL
            </span>

            <h2>Ventas registradas</h2>

            <p>
              Consulta las operaciones disponibles.
            </p>
          </div>
        </div>

        <div className="panel-toolbar">
          <input
            className="search-input"
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
            placeholder="Buscar por ID, cliente o vendedor..."
          />

          <button
            type="button"
            className="secondary-button"
          >
            Exportar
          </button>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Venta</th>
                <th>Cliente</th>
                <th>Vendedor</th>
                <th>Fecha</th>
                <th>Items</th>
                <th>Total</th>
                <th>Pago</th>
              </tr>
            </thead>

            <tbody>
              {filteredSales.map((sale) => (
                <tr key={sale.id}>
                  <td>
                    <strong>{sale.id}</strong>
                  </td>

                  <td>{sale.customer}</td>

                  <td>{sale.seller}</td>

                  <td>{sale.date}</td>

                  <td>{sale.items}</td>

                  <td>
                    S/{' '}
                    {sale.total.toLocaleString(
                      'es-PE',
                    )}
                  </td>

                  <td>
                    <span
                      className={`status-pill ${
                        sale.payment ===
                        'Completado'
                          ? 'success'
                          : 'warning'
                      }`}
                    >
                      {sale.payment}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {filteredSales.length === 0 && (
            <div className="empty-state">
              No se encontraron ventas.
            </div>
          )}
        </div>
      </section>
    </div>
  )
}

export default Sales
