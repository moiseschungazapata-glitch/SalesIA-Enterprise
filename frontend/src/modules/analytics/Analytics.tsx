import { useMemo, useState } from 'react'
import PageHeader from '../../components/PageHeader'
import {
  customers,
  products,
  sales,
} from '../../services/mockData'

type AnalyticsSection =
  | 'overview'
  | 'sales'
  | 'products'
  | 'customers'
  | 'sellers'
  | 'variables'

const salesValues = sales.map((sale) => sale.total)

function calculateMean(values: number[]) {
  if (values.length === 0) {
    return 0
  }

  return (
    values.reduce((sum, value) => sum + value, 0) /
    values.length
  )
}

function calculateMedian(values: number[]) {
  if (values.length === 0) {
    return 0
  }

  const sorted = [...values].sort((a, b) => a - b)
  const middle = Math.floor(sorted.length / 2)

  if (sorted.length % 2 === 0) {
    return (
      (sorted[middle - 1] + sorted[middle]) / 2
    )
  }

  return sorted[middle]
}

function formatCurrency(value: number) {
  return `S/ ${value.toLocaleString('es-PE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`
}

function Analytics() {
  const [section, setSection] =
    useState<AnalyticsSection>('overview')

  const mean = calculateMean(salesValues)
  const median = calculateMedian(salesValues)

  const totalRevenue = sales.reduce(
    (sum, sale) => sum + sale.total,
    0,
  )

  const totalUnits = products.reduce(
    (sum, product) => sum + product.sold,
    0,
  )

  const sellerData = useMemo(() => {
    const sellers = new Map<
      string,
      {
        seller: string
        sales: number
        revenue: number
        average: number
      }
    >()

    for (const sale of sales) {
      const current = sellers.get(sale.seller)

      if (!current) {
        sellers.set(sale.seller, {
          seller: sale.seller,
          sales: 1,
          revenue: sale.total,
          average: sale.total,
        })
      } else {
        current.sales += 1
        current.revenue += sale.total
        current.average =
          current.revenue / current.sales
      }
    }

    return Array.from(sellers.values()).sort(
      (a, b) => b.revenue - a.revenue,
    )
  }, [])

  const productData = useMemo(() => {
    return [...products]
      .sort((a, b) => b.sold - a.sold)
      .map((product) => ({
        ...product,
        revenue: product.price * product.sold,
      }))
  }, [])

  const customerData = useMemo(() => {
    return [...customers].sort(
      (a, b) => b.purchases - a.purchases,
    )
  }, [])

  const categoryData = useMemo(() => {
    const categories = new Map<
      string,
      {
        category: string
        units: number
        revenue: number
      }
    >()

    for (const product of products) {
      const current = categories.get(product.category)

      const revenue =
        product.price * product.sold

      if (!current) {
        categories.set(product.category, {
          category: product.category,
          units: product.sold,
          revenue,
        })
      } else {
        current.units += product.sold
        current.revenue += revenue
      }
    }

    return Array.from(categories.values()).sort(
      (a, b) => b.revenue - a.revenue,
    )
  }, [])

  const variableData = [
    {
      name: 'total_venta',
      type: 'Cuantitativa',
      description:
        'Monto total de una operación comercial.',
    },
    {
      name: 'cantidad_items',
      type: 'Cuantitativa',
      description:
        'Cantidad de artículos incluidos en una venta.',
    },
    {
      name: 'precio',
      type: 'Cuantitativa',
      description:
        'Precio unitario del producto.',
    },
    {
      name: 'categoria',
      type: 'Cualitativa',
      description:
        'Categoría asociada a un producto.',
    },
    {
      name: 'ciudad',
      type: 'Cualitativa',
      description:
        'Ciudad registrada para el cliente.',
    },
    {
      name: 'frecuencia_compra',
      type: 'Cuantitativa',
      description:
        'Cantidad de compras realizadas por cliente.',
    },
  ]

  const maxRevenue = Math.max(
    ...categoryData.map((item) => item.revenue),
    1,
  )

  const renderOverview = () => (
    <>
      <section className="kpi-grid">
        <article className="kpi-card">
          <div className="kpi-top">
            <span>Ingresos analizados</span>
          </div>
          <strong className="kpi-value">
            {formatCurrency(totalRevenue)}
          </strong>
          <span className="kpi-detail">
            conjunto actual
          </span>
        </article>

        <article className="kpi-card">
          <div className="kpi-top">
            <span>Media</span>
          </div>
          <strong className="kpi-value">
            {formatCurrency(mean)}
          </strong>
          <span className="kpi-detail">
            promedio de la muestra
          </span>
        </article>

        <article className="kpi-card">
          <div className="kpi-top">
            <span>Mediana</span>
          </div>
          <strong className="kpi-value">
            {formatCurrency(median)}
          </strong>
          <span className="kpi-detail">
            valor central
          </span>
        </article>

        <article className="kpi-card">
          <div className="kpi-top">
            <span>Observaciones</span>
          </div>
          <strong className="kpi-value">
            {sales.length}
          </strong>
          <span className="kpi-detail">
            ventas disponibles para el análisis
          </span>
        </article>
      </section>

      <section className="dashboard-grid">
        <article className="panel panel-large">
          <div className="panel-header">
            <div>
              <span className="eyebrow">
                VENTAS
              </span>

              <h2>Ingresos por categoría</h2>

              <p>
                Participación económica de los productos
                vendidos.
              </p>
            </div>
          </div>

          <div className="analytics-bars">
            {categoryData.map((item) => (
              <div
                className="analytics-bar-row"
                key={item.category}
              >
                <div className="analytics-bar-label">
                  <strong>{item.category}</strong>
                  <span>
                    {formatCurrency(item.revenue)}
                  </span>
                </div>

                <div className="analytics-bar-track">
                  <div
                    className="analytics-bar-fill"
                    style={{
                      width: `${
                        (item.revenue / maxRevenue) *
                        100
                      }%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">
                VARIABLES
              </span>

              <h2>Datos disponibles</h2>

              <p>
                Variables identificadas para análisis.
              </p>
            </div>
          </div>

          <div className="variable-list">
            {variableData.map((variable) => (
              <div
                className="variable-row"
                key={variable.name}
              >
                <div>
                  <strong>{variable.name}</strong>
                  <small>{variable.description}</small>
                </div>

                <span>{variable.type}</span>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="analytics-cards">
        <article className="analysis-card">
          <span className="eyebrow">
            MEDIA
          </span>

          <h3>Promedio de ventas</h3>

          <strong>{formatCurrency(mean)}</strong>

          <p>
            Se obtiene sumando las observaciones y
            dividiendo entre su cantidad.
          </p>
        </article>

        <article className="analysis-card">
          <span className="eyebrow">
            MEDIANA
          </span>

          <h3>Valor central</h3>

          <strong>{formatCurrency(median)}</strong>

          <p>
            Divide el conjunto ordenado y permite
            observar el centro de los datos.
          </p>
        </article>

        <article className="analysis-card">
          <span className="eyebrow">
            VOLUMEN
          </span>

          <h3>Unidades vendidas</h3>

          <strong>{totalUnits}</strong>

          <p>
            Cantidad acumulada de unidades vendidas
            en los productos disponibles.
          </p>
        </article>
      </section>
    </>
  )

  const renderSales = () => (
    <section className="panel">
      <div className="panel-header">
        <div>
          <span className="eyebrow">
            ANÁLISIS DE VENTAS
          </span>

          <h2>Resultados comerciales</h2>

          <p>
            Estadísticas calculadas sobre las ventas
            disponibles.
          </p>
        </div>
      </div>

      <div className="analysis-summary-grid">
        <div>
          <span>Total de ventas</span>
          <strong>{sales.length}</strong>
        </div>

        <div>
          <span>Ingresos</span>
          <strong>
            {formatCurrency(totalRevenue)}
          </strong>
        </div>

        <div>
          <span>Media</span>
          <strong>{formatCurrency(mean)}</strong>
        </div>

        <div>
          <span>Mediana</span>
          <strong>
            {formatCurrency(median)}
          </strong>
        </div>
      </div>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Venta</th>
              <th>Cliente</th>
              <th>Vendedor</th>
              <th>Total</th>
              <th>Pago</th>
            </tr>
          </thead>

          <tbody>
            {sales.map((sale) => (
              <tr key={sale.id}>
                <td>
                  <strong>{sale.id}</strong>
                </td>

                <td>{sale.customer}</td>

                <td>{sale.seller}</td>

                <td>
                  {formatCurrency(sale.total)}
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
      </div>
    </section>
  )

  const renderProducts = () => (
    <section className="panel">
      <div className="panel-header">
        <div>
          <span className="eyebrow">
            ANÁLISIS DE PRODUCTOS
          </span>

          <h2>Productos vendidos</h2>

          <p>
            Cantidad, ingresos y participación por
            producto.
          </p>
        </div>
      </div>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Producto</th>
              <th>Categoría</th>
              <th>Unidades</th>
              <th>Precio</th>
              <th>Ingresos</th>
              <th>Stock</th>
            </tr>
          </thead>

          <tbody>
            {productData.map((product) => (
              <tr key={product.id}>
                <td>
                  <strong>{product.name}</strong>
                </td>

                <td>{product.category}</td>

                <td>{product.sold}</td>

                <td>
                  {formatCurrency(product.price)}
                </td>

                <td>
                  {formatCurrency(product.revenue)}
                </td>

                <td>{product.stock}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )

  const renderCustomers = () => (
    <section className="panel">
      <div className="panel-header">
        <div>
          <span className="eyebrow">
            ANÁLISIS DE CLIENTES
          </span>

          <h2>Comportamiento de clientes</h2>

          <p>
            Compras y frecuencia de actividad registrada.
          </p>
        </div>
      </div>

      <div className="analysis-summary-grid">
        <div>
          <span>Total clientes</span>
          <strong>{customers.length}</strong>
        </div>

        <div>
          <span>Activos</span>
          <strong>
            {
              customers.filter(
                (customer) =>
                  customer.status === 'Activo',
              ).length
            }
          </strong>
        </div>

        <div>
          <span>Compras registradas</span>
          <strong>
            {customers.reduce(
              (sum, customer) =>
                sum + customer.purchases,
              0,
            )}
          </strong>
        </div>

        <div>
          <span>Media de compras</span>
          <strong>
            {(
              customers.reduce(
                (sum, customer) =>
                  sum + customer.purchases,
                0,
              ) / customers.length
            ).toFixed(2)}
          </strong>
        </div>
      </div>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Cliente</th>
              <th>Ciudad</th>
              <th>Compras</th>
              <th>Estado</th>
            </tr>
          </thead>

          <tbody>
            {customerData.map((customer) => (
              <tr key={customer.id}>
                <td>
                  <strong>{customer.name}</strong>
                </td>

                <td>{customer.city}</td>

                <td>{customer.purchases}</td>

                <td>
                  <span
                    className={`status-pill ${
                      customer.status ===
                      'Activo'
                        ? 'success'
                        : 'neutral'
                    }`}
                  >
                    {customer.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )

  const renderSellers = () => (
    <section className="panel">
      <div className="panel-header">
        <div>
          <span className="eyebrow">
            ANÁLISIS DE VENDEDORES
          </span>

          <h2>Rendimiento comercial</h2>

          <p>
            Ventas, ingresos y promedio por vendedor.
          </p>
        </div>
      </div>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Vendedor</th>
              <th>Ventas</th>
              <th>Ingresos</th>
              <th>Promedio</th>
            </tr>
          </thead>

          <tbody>
            {sellerData.map((seller) => (
              <tr key={seller.seller}>
                <td>
                  <strong>{seller.seller}</strong>
                </td>

                <td>{seller.sales}</td>

                <td>
                  {formatCurrency(seller.revenue)}
                </td>

                <td>
                  {formatCurrency(seller.average)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )

  const renderVariables = () => (
    <section className="panel">
      <div className="panel-header">
        <div>
          <span className="eyebrow">
            VARIABLES ESTADÍSTICAS
          </span>

          <h2>Catálogo de variables</h2>

          <p>
            Clasificación de las variables utilizadas
            por el análisis.
          </p>
        </div>
      </div>

      <div className="variable-catalog">
        {variableData.map((variable) => (
          <article
            className="variable-card"
            key={variable.name}
          >
            <div className="variable-card-top">
              <span className="status-pill neutral">
                {variable.type}
              </span>
            </div>

            <h3>{variable.name}</h3>

            <p>{variable.description}</p>
          </article>
        ))}
      </div>
    </section>
  )

  return (
    <div className="page">
      <PageHeader
        eyebrow="MOTOR ANALÍTICO"
        title="Analytics"
        description="Análisis estadístico de los datos comerciales de SalesIA."
      />

      <div className="analytics-navigation">
        {[
          ['overview', 'Resumen'],
          ['sales', 'Ventas'],
          ['products', 'Productos'],
          ['customers', 'Clientes'],
          ['sellers', 'Vendedores'],
          ['variables', 'Variables'],
        ].map(([key, label]) => (
          <button
            type="button"
            key={key}
            className={
              section === key
                ? 'analytics-tab active'
                : 'analytics-tab'
            }
            onClick={() =>
              setSection(
                key as AnalyticsSection,
              )
            }
          >
            {label}
          </button>
        ))}
      </div>

      {section === 'overview' && renderOverview()}
      {section === 'sales' && renderSales()}
      {section === 'products' && renderProducts()}
      {section === 'customers' && renderCustomers()}
      {section === 'sellers' && renderSellers()}
      {section === 'variables' && renderVariables()}
    </div>
  )
}

export default Analytics
