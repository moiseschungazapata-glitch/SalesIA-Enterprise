import { useMemo, useState, type FormEvent } from 'react'
import type { PageKey, UserRole } from '../../app/navigation'
import KpiCard from '../../components/KpiCard'
import PageHeader from '../../components/PageHeader'
import StateMessage from '../../components/StateMessage'
import { useDashboard } from '../../hooks/useDashboard'
import type { DashboardFilters } from '../../services/dashboard'
import type { DashboardBreakdownPoint, DashboardGranularity } from '../../types/api'

interface DashboardProps { role: UserRole; onNavigate: (page: PageKey) => void }
const chartColors = ['#155eef', '#13b8a6', '#f59e0b', '#8b5cf6', '#ef4444']

function localDateValue(value: Date) {
  return `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, '0')}-${String(value.getDate()).padStart(2, '0')}`
}

function defaultFilters(): DashboardFilters {
  const today = new Date()
  return { dateFrom: localDateValue(new Date(today.getFullYear(), today.getMonth(), 1)), dateTo: localDateValue(today), branch: 'main', sellerId: '', categoryId: '' }
}

function money(value: string | number) {
  return new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN', maximumFractionDigits: 2 }).format(Number(value))
}

function shortMoney(value: string | number) {
  const number = Number(value)
  if (number >= 1_000_000) return `S/ ${(number / 1_000_000).toFixed(1)} M`
  if (number >= 1_000) return `S/ ${(number / 1_000).toFixed(1)} mil`
  return money(value)
}

function periodLabel(value: string, granularity: DashboardGranularity) {
  const date = new Date(`${value}T12:00:00`)
  return new Intl.DateTimeFormat('es-PE', granularity === 'month'
    ? { month: 'short', year: 'numeric' }
    : { day: '2-digit', month: 'short' }).format(date)
}

function CompactRanking({ items, emptyLabel }: { items: DashboardBreakdownPoint[]; emptyLabel: string }) {
  if (!items.length) return <p className="dashboard-compact-empty">{emptyLabel}</p>
  return <div className="dashboard-compact-ranking">{items.slice(0, 5).map((item, index) => (
    <div className="dashboard-compact-row" key={item.id}>
      <span className="dashboard-rank-number">{index + 1}</span>
      <div><strong>{item.label}</strong><span>{item.transactions} ventas · {item.units} unidades</span></div>
      <strong>{shortMoney(item.revenue)}</strong>
    </div>
  ))}</div>
}

function Dashboard({ role, onNavigate }: DashboardProps) {
  const canRegisterSale = role === 'administrator'
  const initialFilters = defaultFilters()
  const [draftFilters, setDraftFilters] = useState(initialFilters)
  const [filters, setFilters] = useState(initialFilters)
  const { data, loading, error, reload } = useDashboard(filters)

  const applyFilters = (event: FormEvent) => { event.preventDefault(); setFilters(draftFilters) }
  const resetFilters = () => { const next = defaultFilters(); setDraftFilters(next); setFilters(next) }

  const chart = useMemo(() => {
    if (!data?.sales_by_period.length) return null
    const values = data.sales_by_period.map((item) => Number(item.revenue))
    const maximum = Math.max(...values, 1)
    const width = 720; const startX = 24; const usableWidth = width - startX * 2
    const points = values.map((value, index) => ({
      x: values.length === 1 ? width / 2 : startX + index * usableWidth / (values.length - 1),
      y: 28 + (1 - value / maximum) * 154,
      value,
    }))
    const line = points.map((point) => `${point.x},${point.y}`).join(' ')
    return { points, line, area: `${startX},190 ${line} ${width - startX},190`, maximum }
  }, [data])

  const donutBackground = useMemo(() => {
    if (!data) return 'conic-gradient(#e7edf5 0 100%)'
    let current = 0
    return `conic-gradient(${data.ticket_distribution.map((item, index) => {
      const start = current; current += Number(item.percentage)
      return `${chartColors[index % chartColors.length]} ${start}% ${current}%`
    }).join(', ')})`
  }, [data])

  return <div className="page dashboard-page">
    <PageHeader eyebrow="RESUMEN EJECUTIVO" title="Dashboard" description="Una vista clara de los resultados principales de tu negocio." action={
      <div className="dashboard-header-actions">
        {canRegisterSale && <button className="primary-button compact" type="button" onClick={() => onNavigate('sales')}>+ Nueva venta</button>}
        <button className="secondary-button compact" type="button" onClick={() => onNavigate('orders')}>Nuevo pedido</button>
        <button className="secondary-button compact" type="button" onClick={() => onNavigate('payments')}>Registrar pago</button>
      </div>
    } />

    <details className="panel dashboard-filter-panel">
      <summary><div><strong>Periodo y filtros</strong><span>{filters.dateFrom} — {filters.dateTo}</span></div><span>{loading ? 'Actualizando…' : 'Ajustar'}</span></summary>
      <form className="dashboard-filter-form" onSubmit={applyFilters}>
        <label>Desde<input type="date" value={draftFilters.dateFrom} max={draftFilters.dateTo} onChange={(event) => setDraftFilters({ ...draftFilters, dateFrom: event.target.value })} required /></label>
        <label>Hasta<input type="date" value={draftFilters.dateTo} min={draftFilters.dateFrom} onChange={(event) => setDraftFilters({ ...draftFilters, dateTo: event.target.value })} required /></label>
        <label>Sucursal<select value={draftFilters.branch} onChange={(event) => setDraftFilters({ ...draftFilters, branch: event.target.value as 'main' })}>
          {(data?.filter_options.branches ?? [{ id: 'main' as const, label: 'Sucursal principal' }]).map((branch) => <option key={branch.id} value={branch.id}>{branch.label}</option>)}
        </select></label>
        <label>Vendedor<select value={draftFilters.sellerId} onChange={(event) => setDraftFilters({ ...draftFilters, sellerId: event.target.value })}>
          <option value="">Todos</option>{data?.filter_options.sellers.map((seller) => <option key={seller.id} value={seller.id}>{seller.label}</option>)}
        </select></label>
        <label>Categoría<select value={draftFilters.categoryId} onChange={(event) => setDraftFilters({ ...draftFilters, categoryId: event.target.value })}>
          <option value="">Todas</option>{data?.filter_options.categories.map((category) => <option key={category.id} value={category.id}>{category.label}</option>)}
        </select></label>
        <div className="dashboard-filter-actions"><button className="secondary-button compact" type="button" onClick={resetFilters}>Limpiar</button><button className="primary-button compact" type="submit" disabled={loading}>Aplicar</button></div>
      </form>
    </details>

    {error && !data && <section className="panel"><StateMessage type="error" title="No se pudo cargar el dashboard" description={error} actionLabel="Reintentar" onAction={reload} /></section>}
    {loading && !data && <section className="panel"><StateMessage type="loading" title="Calculando indicadores" description="Estamos preparando el resumen del periodo seleccionado." /></section>}

    {data && <>
      {error && <div className="form-error dashboard-inline-error">{error} Se muestran los últimos datos válidos.</div>}
      <section className="dashboard-kpi-grid">
        <KpiCard label="Ventas" value={money(data.kpis.sales_total)} detail="facturación del periodo" />
        <KpiCard label="Operaciones" value={data.kpis.transactions.toLocaleString('es-PE')} detail="ventas confirmadas" />
        <KpiCard label="Clientes activos" value={data.kpis.active_customers.toLocaleString('es-PE')} detail="clientes con compras" />
        <KpiCard label="Ticket promedio" value={money(data.kpis.ticket_average)} detail="importe promedio por venta" />
      </section>

      <section className="dashboard-main-grid">
        <article className="panel dashboard-chart-panel">
          <div className="panel-header dashboard-panel-heading"><div><span className="eyebrow">TENDENCIA</span><h2>Evolución de ventas</h2></div><span className="panel-period">{data.period.granularity === 'day' ? 'Diaria' : data.period.granularity === 'week' ? 'Semanal' : 'Mensual'}</span></div>
          {data.kpis.transactions === 0 || !chart ? <StateMessage type="empty" title="No hay ventas en este periodo" description="Amplía el intervalo o registra una nueva venta." /> :
            <div className="dashboard-line-chart">
              <div className="dashboard-chart-scale"><span>{shortMoney(chart.maximum)}</span><span>{shortMoney(chart.maximum / 2)}</span><span>S/ 0</span></div>
              <div className="dashboard-chart-canvas">
                <svg viewBox="0 0 720 210" role="img" aria-label="Evolución de ingresos del periodo" preserveAspectRatio="none">
                  <defs><linearGradient id="dashboardArea" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#155eef" stopOpacity=".25" /><stop offset="100%" stopColor="#155eef" stopOpacity="0" /></linearGradient></defs>
                  <line x1="24" y1="28" x2="696" y2="28" /><line x1="24" y1="105" x2="696" y2="105" /><line x1="24" y1="182" x2="696" y2="182" />
                  <polygon points={chart.area} fill="url(#dashboardArea)" /><polyline points={chart.line} className="dashboard-chart-line" />
                  {chart.points.map((point, index) => <circle key={data.sales_by_period[index].period} cx={point.x} cy={point.y} r="4"><title>{periodLabel(data.sales_by_period[index].period, data.period.granularity)}: {money(point.value)}</title></circle>)}
                </svg>
                <div className="dashboard-chart-labels">{data.sales_by_period.map((item) => <span key={item.period}>{periodLabel(item.period, data.period.granularity)}</span>)}</div>
              </div>
            </div>}
        </article>

        <article className="panel dashboard-donut-panel">
          <div className="panel-header dashboard-panel-heading"><div><span className="eyebrow">COMPOSICIÓN</span><h2>Rangos de ticket</h2></div></div>
          <div className="dashboard-donut-wrap">
            <div className="dashboard-donut" style={{ background: donutBackground }}><div><strong>{data.kpis.transactions}</strong><span>ventas</span></div></div>
            <div className="dashboard-donut-legend">{data.ticket_distribution.slice(0, 5).map((item, index) => <div key={item.label}><i style={{ background: chartColors[index] }} /><span>{item.label}</span><strong>{Number(item.percentage).toFixed(0)}%</strong></div>)}</div>
          </div>
        </article>
      </section>

      <section className="dashboard-summary-grid">
        <article className="panel dashboard-compact-panel">
          <div className="panel-header dashboard-panel-heading"><div><span className="eyebrow">EQUIPO</span><h2>Vendedores destacados</h2></div><button className="text-button" onClick={() => onNavigate('sellers')}>Ver todo</button></div>
          <CompactRanking items={data.sales_by_seller} emptyLabel="Sin ventas por vendedor" />
        </article>
        <article className="panel dashboard-compact-panel">
          <div className="panel-header dashboard-panel-heading"><div><span className="eyebrow">CATÁLOGO</span><h2>Productos destacados</h2></div><button className="text-button" onClick={() => onNavigate('products')}>Ver todo</button></div>
          <CompactRanking items={data.sales_by_product} emptyLabel="Sin productos vendidos" />
        </article>
        <article className="panel dashboard-compact-panel dashboard-period-summary">
          <div className="panel-header dashboard-panel-heading"><div><span className="eyebrow">PERIODO</span><h2>Resumen comercial</h2></div></div>
          <dl>
            <div><dt>Unidades vendidas</dt><dd>{data.kpis.units_sold.toLocaleString('es-PE')}</dd></div>
            <div><dt>Media de ventas</dt><dd>{money(data.kpis.sales_mean)}</dd></div>
            <div><dt>Mediana de ventas</dt><dd>{money(data.kpis.sales_median)}</dd></div>
            <div><dt>Resultados generados</dt><dd>{new Intl.DateTimeFormat('es-PE', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(data.generated_at))}</dd></div>
          </dl>
        </article>
      </section>
    </>}
  </div>
}

export default Dashboard
