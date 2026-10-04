import { useState, type FormEvent } from 'react'
import type { PageKey, UserRole } from '../../app/navigation'
import KpiCard from '../../components/KpiCard'
import PageHeader from '../../components/PageHeader'
import StateMessage from '../../components/StateMessage'
import { useDashboard } from '../../hooks/useDashboard'
import type { DashboardFilters } from '../../services/dashboard'
import type {
  DashboardBreakdownPoint,
  DashboardGranularity,
} from '../../types/api'

interface DashboardProps {
  role: UserRole
  onNavigate: (page: PageKey) => void
}

function localDateValue(value: Date) {
  const year = value.getFullYear()
  const month = String(value.getMonth() + 1).padStart(2, '0')
  const day = String(value.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function defaultFilters(): DashboardFilters {
  const today = new Date()
  return {
    dateFrom: localDateValue(new Date(today.getFullYear(), today.getMonth(), 1)),
    dateTo: localDateValue(today),
    branch: 'main',
    sellerId: '',
    categoryId: '',
  }
}

function money(value: string | number) {
  return new Intl.NumberFormat('es-PE', {
    style: 'currency',
    currency: 'PEN',
    maximumFractionDigits: 2,
  }).format(Number(value))
}

function shortMoney(value: string) {
  const number = Number(value)
  if (number >= 1_000_000) return `S/ ${(number / 1_000_000).toFixed(1)} M`
  if (number >= 1_000) return `S/ ${(number / 1_000).toFixed(1)} mil`
  return money(value)
}

function periodLabel(value: string, granularity: DashboardGranularity) {
  const date = new Date(`${value}T12:00:00`)
  if (granularity === 'month') {
    return new Intl.DateTimeFormat('es-PE', {
      month: 'short', year: 'numeric',
    }).format(date)
  }
  return new Intl.DateTimeFormat('es-PE', {
    day: '2-digit', month: 'short',
  }).format(date)
}

function BreakdownList({
  items,
  emptyLabel,
}: {
  items: DashboardBreakdownPoint[]
  emptyLabel: string
}) {
  if (items.length === 0) {
    return (
      <StateMessage
        type="empty"
        title={emptyLabel}
        description="Cambia los filtros o registra ventas para visualizar esta comparación."
      />
    )
  }
  return (
    <div className="dashboard-ranking">
      {items.map((item) => (
        <div className="dashboard-ranking-row" key={item.id}>
          <div className="dashboard-ranking-copy">
            <strong>{item.label}</strong>
            <span>{item.transactions} ventas · {item.units} unidades</span>
          </div>
          <strong>{money(item.revenue)}</strong>
          <div className="dashboard-progress" aria-hidden="true">
            <div style={{ width: `${Math.max(Number(item.share), 2)}%` }} />
          </div>
          <span>{Number(item.share).toFixed(1)}%</span>
        </div>
      ))}
    </div>
  )
}

function Dashboard({ role, onNavigate }: DashboardProps) {
  const canRegisterSale = role === 'administrator'
  const initialFilters = defaultFilters()
  const [draftFilters, setDraftFilters] = useState(initialFilters)
  const [filters, setFilters] = useState(initialFilters)
  const { data, loading, error, reload } = useDashboard(filters)

  const applyFilters = (event: FormEvent) => {
    event.preventDefault()
    setFilters(draftFilters)
  }

  const resetFilters = () => {
    const next = defaultFilters()
    setDraftFilters(next)
    setFilters(next)
  }

  const maximumRevenue = Math.max(
    1,
    ...(data?.sales_by_period.map((item) => Number(item.revenue)) ?? []),
  )
  const maximumFrequency = Math.max(
    1,
    ...(data?.ticket_distribution.map((item) => item.frequency) ?? []),
  )

  return (
    <div className="page">
      <PageHeader
        eyebrow="RESUMEN EJECUTIVO"
        title="Dashboard Analytics"
        description="Resultados comerciales reales calculados desde tus ventas confirmadas."
        action={canRegisterSale ? (
          <button
            className="primary-button compact"
            type="button"
            onClick={() => onNavigate('sales')}
          >
            + Nueva venta
          </button>
        ) : undefined}
      />

      <section className="panel dashboard-filter-panel">
        <div className="panel-header">
          <div>
            <span className="eyebrow">FILTROS</span>
            <h2>Periodo y segmentación</h2>
            <p>Combina fechas, sucursal, vendedor y categoría.</p>
          </div>
          {loading && <span className="dashboard-updating">Actualizando…</span>}
        </div>
        <form className="dashboard-filter-form" onSubmit={applyFilters}>
          <label>
            Desde
            <input
              type="date"
              value={draftFilters.dateFrom}
              max={draftFilters.dateTo}
              onChange={(event) => setDraftFilters({
                ...draftFilters, dateFrom: event.target.value,
              })}
              required
            />
          </label>
          <label>
            Hasta
            <input
              type="date"
              value={draftFilters.dateTo}
              min={draftFilters.dateFrom}
              onChange={(event) => setDraftFilters({
                ...draftFilters, dateTo: event.target.value,
              })}
              required
            />
          </label>
          <label>
            Sucursal
            <select
              value={draftFilters.branch}
              onChange={(event) => setDraftFilters({
                ...draftFilters,
                branch: event.target.value as 'main',
              })}
            >
              {(data?.filter_options.branches ?? [
                { id: 'main' as const, label: 'Sucursal principal' },
              ]).map((branch) => (
                <option key={branch.id} value={branch.id}>{branch.label}</option>
              ))}
            </select>
          </label>
          <label>
            Vendedor
            <select
              value={draftFilters.sellerId}
              onChange={(event) => setDraftFilters({
                ...draftFilters, sellerId: event.target.value,
              })}
            >
              <option value="">Todos</option>
              {data?.filter_options.sellers.map((seller) => (
                <option key={seller.id} value={seller.id}>{seller.label}</option>
              ))}
            </select>
          </label>
          <label>
            Categoría
            <select
              value={draftFilters.categoryId}
              onChange={(event) => setDraftFilters({
                ...draftFilters, categoryId: event.target.value,
              })}
            >
              <option value="">Todas</option>
              {data?.filter_options.categories.map((category) => (
                <option key={category.id} value={category.id}>{category.label}</option>
              ))}
            </select>
          </label>
          <div className="dashboard-filter-actions">
            <button className="secondary-button compact" type="button" onClick={resetFilters}>
              Limpiar
            </button>
            <button className="primary-button compact" type="submit" disabled={loading}>
              Aplicar filtros
            </button>
          </div>
        </form>
      </section>

      {error && !data && (
        <section className="panel">
          <StateMessage
            type="error"
            title="No se pudo cargar el dashboard"
            description={error}
            actionLabel="Reintentar"
            onAction={reload}
          />
        </section>
      )}

      {loading && !data && (
        <section className="panel">
          <StateMessage
            type="loading"
            title="Calculando indicadores"
            description="Estamos agrupando las ventas del periodo seleccionado."
          />
        </section>
      )}

      {data && (
        <>
          {error && (
            <div className="form-error dashboard-inline-error">
              {error} Los últimos resultados válidos continúan visibles.
            </div>
          )}

          <section className="dashboard-kpi-grid">
            <KpiCard
              label="Ventas del periodo"
              value={money(data.kpis.sales_total)}
              detail={`${data.period.date_from} al ${data.period.date_to}`}
            />
            <KpiCard
              label="Transacciones"
              value={data.kpis.transactions.toLocaleString('es-PE')}
              detail="ventas confirmadas"
            />
            <KpiCard
              label="Clientes activos"
              value={data.kpis.active_customers.toLocaleString('es-PE')}
              detail="clientes con compras"
            />
            <KpiCard
              label="Unidades vendidas"
              value={data.kpis.units_sold.toLocaleString('es-PE')}
              detail="productos del periodo"
            />
            <KpiCard
              label="Ticket promedio"
              value={money(data.kpis.ticket_average)}
              detail="importe promedio por venta"
            />
            <KpiCard
              label="Media"
              value={money(data.kpis.sales_mean)}
              detail="media aritmética de ventas"
            />
            <KpiCard
              label="Mediana"
              value={money(data.kpis.sales_median)}
              detail="valor central de las ventas"
            />
          </section>

          <section className="panel dashboard-series-panel">
            <div className="panel-header">
              <div>
                <span className="eyebrow">VENTAS POR PERIODO</span>
                <h2>Evolución de ingresos</h2>
                <p>Los periodos sin ventas se muestran en cero.</p>
              </div>
              <span className="panel-period">
                Agrupación: {data.period.granularity === 'day'
                  ? 'diaria'
                  : data.period.granularity === 'week' ? 'semanal' : 'mensual'}
              </span>
            </div>
            {data.kpis.transactions === 0 ? (
              <StateMessage
                type="empty"
                title="No hay ventas en este periodo"
                description="Registra una venta o amplía el intervalo para generar la gráfica."
                actionLabel={canRegisterSale ? 'Registrar venta' : undefined}
                onAction={canRegisterSale ? () => onNavigate('sales') : undefined}
              />
            ) : (
              <div className="dashboard-series" role="img" aria-label="Ventas por periodo">
                {data.sales_by_period.map((item) => (
                  <div className="dashboard-series-column" key={item.period}>
                    <span>{shortMoney(item.revenue)}</span>
                    <div className="dashboard-series-track">
                      <div style={{
                        height: `${Math.max(
                          Number(item.revenue) / maximumRevenue * 100,
                          item.transactions ? 4 : 0,
                        )}%`,
                      }} />
                    </div>
                    <strong>{periodLabel(item.period, data.period.granularity)}</strong>
                    <small>{item.transactions} ventas</small>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="dashboard-breakdown-grid">
            <article className="panel">
              <div className="panel-header">
                <div>
                  <span className="eyebrow">PRODUCTOS</span>
                  <h2>Ventas por producto</h2>
                  <p>Hasta 10 productos ordenados por facturación.</p>
                </div>
              </div>
              <BreakdownList
                items={data.sales_by_product}
                emptyLabel="Sin productos vendidos"
              />
            </article>

            <article className="panel">
              <div className="panel-header">
                <div>
                  <span className="eyebrow">EQUIPO COMERCIAL</span>
                  <h2>Ventas por vendedor</h2>
                  <p>Participación sobre el total filtrado.</p>
                </div>
              </div>
              <BreakdownList
                items={data.sales_by_seller}
                emptyLabel="Sin ventas por vendedor"
              />
            </article>
          </section>

          <section className="panel dashboard-distribution-panel">
            <div className="panel-header">
              <div>
                <span className="eyebrow">DISTRIBUCIÓN Y FRECUENCIA</span>
                <h2>Rangos de ticket de venta</h2>
                <p>Cantidad y proporción de operaciones en cada rango monetario.</p>
              </div>
            </div>
            <div className="dashboard-distribution">
              {data.ticket_distribution.map((item) => (
                <div className="dashboard-distribution-item" key={item.label}>
                  <strong>{item.frequency}</strong>
                  <div className="dashboard-distribution-track">
                    <div style={{
                      height: `${item.frequency / maximumFrequency * 100}%`,
                    }} />
                  </div>
                  <span>{item.label}</span>
                  <small>{Number(item.percentage).toFixed(1)}%</small>
                </div>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  )
}

export default Dashboard
