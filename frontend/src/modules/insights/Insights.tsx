import { useMemo, useState } from 'react'
import PageHeader from '../../components/PageHeader'
import StateMessage from '../../components/StateMessage'
import { useInsights } from '../../hooks/useInsights'
import { generateInsights } from '../../services/insights'
import type {
  InsightCategory,
  InsightRecord,
  InsightSeverity,
} from '../../types/api'

type HistoryFilter = 'all' | 'active' | 'history'

const categoryLabels: Record<InsightCategory, string> = {
  sales: 'Ventas',
  products: 'Productos',
  sellers: 'Vendedores',
  customers: 'Clientes',
  statistics: 'Estadística',
}

const severityLabels: Record<InsightSeverity, string> = {
  info: 'Informativo',
  warning: 'Requiere atención',
  critical: 'Crítico',
}

function localIsoDate(date: Date) {
  const offset = date.getTimezoneOffset() * 60_000
  return new Date(date.getTime() - offset).toISOString().slice(0, 10)
}

function initialDates() {
  const today = new Date()
  return {
    dateFrom: localIsoDate(new Date(today.getFullYear(), today.getMonth(), 1)),
    dateTo: localIsoDate(today),
  }
}

function evidenceValue(insight: InsightRecord) {
  const value = insight.evidence.value
  const unit = insight.evidence.unit
  if (value === undefined || value === null) return 'Dato disponible'
  if (unit === 'PEN') return `S/ ${Number(value).toLocaleString('es-PE')}`
  if (unit === 'percent') return `${value} %`
  return `${value}${unit ? ` ${String(unit)}` : ''}`
}

function formatPeriod(insight: InsightRecord) {
  if (!insight.period_start || !insight.period_end) return 'Periodo no especificado'
  return `${insight.period_start} al ${insight.period_end}`
}

function Insights() {
  const [defaults] = useState(initialDates)
  const { data, loading, error, reload } = useInsights()
  const [dateFrom, setDateFrom] = useState(defaults.dateFrom)
  const [dateTo, setDateTo] = useState(defaults.dateTo)
  const [category, setCategory] = useState<'all' | InsightCategory>('all')
  const [severity, setSeverity] = useState<'all' | InsightSeverity>('all')
  const [history, setHistory] = useState<HistoryFilter>('active')
  const [generating, setGenerating] = useState(false)
  const [actionError, setActionError] = useState('')
  const [success, setSuccess] = useState('')

  const filteredInsights = useMemo(
    () =>
      data.items.filter((insight) => {
        const matchesCategory = category === 'all' || insight.category === category
        const matchesSeverity = severity === 'all' || insight.severity === severity
        const matchesHistory =
          history === 'all' ||
          (history === 'active' ? insight.active : !insight.active)
        return matchesCategory && matchesSeverity && matchesHistory
      }),
    [category, data.items, history, severity],
  )

  const activeCount = data.items.filter((item) => item.active).length
  const warningCount = data.items.filter(
    (item) => item.active && item.severity !== 'info',
  ).length
  const categoriesCount = new Set(
    data.items.filter((item) => item.active).map((item) => item.category),
  ).size

  const handleGenerate = async () => {
    if (dateTo < dateFrom) {
      setActionError('La fecha final no puede ser anterior a la fecha inicial.')
      return
    }
    setGenerating(true)
    setActionError('')
    setSuccess('')
    try {
      const result = await generateInsights({
        date_from: dateFrom,
        date_to: dateTo,
        branch: 'main',
      })
      setSuccess(
        `Se generaron ${result.generated_count} insights con el dataset #${result.dataset_id}.`,
      )
      setHistory('active')
      reload()
    } catch (requestError) {
      setActionError(
        requestError instanceof Error
          ? requestError.message
          : 'No fue posible generar los insights.',
      )
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="page">
      <PageHeader
        eyebrow="FASE 11 · INTELIGENCIA EMPRESARIAL"
        title="Insights explicables"
        description="Reglas determinísticas que convierten tus ventas en observaciones con evidencia numérica e historial verificable."
      />

      <section className="panel insight-generator">
        <div className="panel-header">
          <div>
            <span className="eyebrow">NUEVO ANÁLISIS</span>
            <h2>Analizar un periodo</h2>
            <p>Se utiliza únicamente la información real guardada en tu base de datos.</p>
          </div>
        </div>
        <div className="form-grid insight-generation-form">
          <label>
            Desde
            <input type="date" value={dateFrom} onChange={(event) => setDateFrom(event.target.value)} />
          </label>
          <label>
            Hasta
            <input type="date" value={dateTo} onChange={(event) => setDateTo(event.target.value)} />
          </label>
          <button type="button" className="primary-button" disabled={generating || !dateFrom || !dateTo} onClick={() => void handleGenerate()}>
            {generating ? 'Analizando…' : 'Generar insights'}
          </button>
        </div>
        {actionError && <p className="form-error insight-feedback">{actionError}</p>}
        {success && <p className="form-success insight-feedback">{success}</p>}
      </section>

      <section className="kpi-grid compact-grid">
        <article className="mini-stat"><span>Historial total</span><strong>{data.total}</strong></article>
        <article className="mini-stat"><span>Insights vigentes</span><strong>{activeCount}</strong></article>
        <article className="mini-stat"><span>Alertas vigentes</span><strong>{warningCount}</strong></article>
        <article className="mini-stat"><span>Categorías analizadas</span><strong>{categoriesCount}</strong></article>
      </section>

      <section className="panel">
        <div className="insight-toolbar">
          <div>
            <span className="eyebrow">CONSULTAR RESULTADOS</span>
            <h2>Observaciones e historial</h2>
          </div>
          <div className="insight-selects">
            <select className="select-input" value={history} onChange={(event) => setHistory(event.target.value as HistoryFilter)}>
              <option value="active">Vigentes</option>
              <option value="history">Anteriores</option>
              <option value="all">Todo el historial</option>
            </select>
            <select className="select-input" value={category} onChange={(event) => setCategory(event.target.value as 'all' | InsightCategory)}>
              <option value="all">Todas las categorías</option>
              {Object.entries(categoryLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
            <select className="select-input" value={severity} onChange={(event) => setSeverity(event.target.value as 'all' | InsightSeverity)}>
              <option value="all">Todas las severidades</option>
              {Object.entries(severityLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </div>
        </div>
      </section>

      {loading && <StateMessage type="loading" title="Cargando insights" description="Consultando el historial guardado en Supabase." />}
      {!loading && error && <StateMessage type="error" title="No se pudieron cargar los insights" description={error} actionLabel="Reintentar" onAction={reload} />}
      {!loading && !error && filteredInsights.length === 0 && (
        <StateMessage type="empty" title="No hay insights para estos filtros" description="Genera un análisis o cambia los filtros de consulta." />
      )}

      {!loading && !error && filteredInsights.length > 0 && (
        <section className="insight-grid">
          {filteredInsights.map((insight) => (
            <article key={insight.id} className={`insight-card ${insight.severity} ${insight.active ? '' : 'archived'}`}>
              <div className="insight-top">
                <span className="status-pill neutral">{categoryLabels[insight.category]}</span>
                <strong>{evidenceValue(insight)}</strong>
              </div>
              <h2>{insight.title}</h2>
              <p>{insight.description}</p>
              <div className="insight-evidence">
                <span>Regla: {insight.rule_code}</span>
                <span>Dataset #{insight.dataset_id} · Análisis #{insight.analysis_id}</span>
                <span>{formatPeriod(insight)}</span>
              </div>
              <div className="insight-indicator">
                <span className={`insight-dot ${insight.severity}`} />
                <span>{severityLabels[insight.severity]} · {insight.active ? 'Vigente' : 'Histórico'}</span>
                <time dateTime={insight.generated_at}>{new Date(insight.generated_at).toLocaleString('es-PE')}</time>
              </div>
            </article>
          ))}
        </section>
      )}
    </div>
  )
}

export default Insights
