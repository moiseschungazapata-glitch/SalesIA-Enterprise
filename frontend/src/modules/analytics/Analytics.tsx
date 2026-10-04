import { useState, type FormEvent } from 'react'
import PageHeader from '../../components/PageHeader'
import StateMessage from '../../components/StateMessage'
import { useAnalyticsMetadata } from '../../hooks/useAnalytics'
import { compareSalesStatistics } from '../../services/analytics'
import type {
  AnalysisExecutionRecord,
  StatisticalAnalysisType,
  StatisticalVariableType,
} from '../../types/api'

const variableTypeLabels: Record<StatisticalVariableType, string> = {
  qualitative: 'Cualitativa',
  quantitative_discrete: 'Cuantitativa discreta',
  quantitative_continuous: 'Cuantitativa continua',
}

const analysisLabels: Record<StatisticalAnalysisType, string> = {
  mean: 'Media',
  median: 'Mediana',
  comparison: 'Media vs. mediana',
  frequency: 'Probabilidad de evento',
  random_variable: 'Variable aleatoria',
  bayes: 'Teorema de Bayes',
  insight: 'Insights empresariales',
}

function numericMetric(
  analysis: AnalysisExecutionRecord | null,
  metric: string,
) {
  const value = analysis?.results.find(
    (result) => result.metric === metric,
  )?.numeric_value
  return value === null || value === undefined ? null : Number(value)
}

function textMetric(
  analysis: AnalysisExecutionRecord | null,
  metric: string,
) {
  return (
    analysis?.results.find((result) => result.metric === metric)
      ?.text_value || ''
  )
}

function formatMetric(value: number | null, currency: boolean) {
  if (value === null || !Number.isFinite(value)) return '—'
  return currency
    ? `S/ ${value.toLocaleString('es-PE', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })}`
    : value.toLocaleString('es-PE', { maximumFractionDigits: 2 })
}

function Analytics() {
  const { variables, history, loading, error: loadError, reload } =
    useAnalyticsMetadata()
  const [metric, setMetric] = useState<'sale_total' | 'items_per_sale'>(
    'sale_total',
  )
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [result, setResult] = useState<AnalysisExecutionRecord | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [executionError, setExecutionError] = useState('')

  const executeAnalysis = async (event: FormEvent) => {
    event.preventDefault()
    setSubmitting(true)
    setExecutionError('')
    try {
      const analysis = await compareSalesStatistics({
        metric,
        date_from: dateFrom || null,
        date_to: dateTo || null,
      })
      setResult(analysis)
      reload()
    } catch (requestError) {
      setExecutionError(
        requestError instanceof Error
          ? requestError.message
          : 'No se pudo ejecutar el análisis.',
      )
    } finally {
      setSubmitting(false)
    }
  }

  const currency = result?.variable_name === 'sale_total'
  const mean = numericMetric(result, 'mean')
  const median = numericMetric(result, 'median')
  const difference = numericMetric(result, 'difference')
  const sampleSize = numericMetric(result, 'sample_size')

  return (
    <div className="page">
      <PageHeader
        eyebrow="MOTOR ESTADÍSTICO · FASE 09"
        title="Analytics"
        description="Media, mediana y clasificación calculadas por la API sobre tus ventas reales."
      />

      <section className="panel analytics-control-panel">
        <div className="panel-header">
          <div>
            <span className="eyebrow">NUEVO ANÁLISIS</span>
            <h2>Analizar ventas confirmadas</h2>
            <p>
              Crea un dataset inmutable, guarda sus observaciones y registra el
              resultado para consultas posteriores.
            </p>
          </div>
        </div>

        <form className="analytics-filter-form" onSubmit={executeAnalysis}>
          <label>
            Variable
            <select
              value={metric}
              onChange={(event) =>
                setMetric(
                  event.target.value as 'sale_total' | 'items_per_sale',
                )
              }
            >
              <option value="sale_total">Monto total de venta</option>
              <option value="items_per_sale">Unidades por venta</option>
            </select>
          </label>

          <label>
            Desde
            <input
              type="date"
              value={dateFrom}
              onChange={(event) => setDateFrom(event.target.value)}
            />
          </label>

          <label>
            Hasta
            <input
              type="date"
              value={dateTo}
              onChange={(event) => setDateTo(event.target.value)}
            />
          </label>

          <button className="primary-button" type="submit" disabled={submitting}>
            {submitting ? 'Analizando…' : 'Ejecutar análisis'}
          </button>
        </form>
      </section>

      {executionError && (
        <StateMessage
          type="error"
          title="No se pudo completar el análisis"
          description={executionError}
        />
      )}

      {result ? (
        <>
          <section className="kpi-grid">
            <article className="kpi-card">
              <div className="kpi-top"><span>Media</span></div>
              <strong className="kpi-value">
                {formatMetric(mean, currency)}
              </strong>
              <span className="kpi-detail">promedio aritmético</span>
            </article>
            <article className="kpi-card">
              <div className="kpi-top"><span>Mediana</span></div>
              <strong className="kpi-value">
                {formatMetric(median, currency)}
              </strong>
              <span className="kpi-detail">valor central ordenado</span>
            </article>
            <article className="kpi-card">
              <div className="kpi-top"><span>Diferencia</span></div>
              <strong className="kpi-value">
                {formatMetric(difference, currency)}
              </strong>
              <span className="kpi-detail">media menos mediana</span>
            </article>
            <article className="kpi-card">
              <div className="kpi-top"><span>Observaciones</span></div>
              <strong className="kpi-value">{sampleSize ?? 0}</strong>
              <span className="kpi-detail">ventas del dataset</span>
            </article>
          </section>

          <section className="panel probability-note">
            <span className="eyebrow">INTERPRETACIÓN</span>
            <h2>{result.variable_label}</h2>
            <p>{textMetric(result, 'interpretation')}</p>
            <small className="analysis-dataset-reference">
              Dataset #{result.dataset_id}: {result.dataset_name}
            </small>
          </section>
        </>
      ) : (
        <StateMessage
          type="empty"
          title="Aún no ejecutaste un análisis en esta sesión"
          description="Selecciona una variable y usa las ventas registradas para calcular media y mediana."
        />
      )}

      <section className="panel">
        <div className="panel-header">
          <div>
            <span className="eyebrow">VARIABLES ESTADÍSTICAS</span>
            <h2>Clasificación disponible</h2>
            <p>Definiciones utilizadas por el motor para interpretar los datos.</p>
          </div>
        </div>

        {loading ? (
          <StateMessage type="loading" title="Cargando variables" />
        ) : loadError ? (
          <StateMessage type="error" title="No se pudieron cargar" description={loadError} />
        ) : (
          <div className="variable-catalog">
            {variables.map((variable) => (
              <article className="variable-card" key={variable.name}>
                <div className="variable-card-top">
                  <span className="status-pill neutral">
                    {variableTypeLabels[variable.variable_type]}
                  </span>
                </div>
                <h3>{variable.label}</h3>
                <p>{variable.description}</p>
                <small>{variable.unit || 'Sin unidad'}</small>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <span className="eyebrow">TRAZABILIDAD</span>
            <h2>Historial de análisis</h2>
            <p>Cada cálculo queda guardado en Supabase con su dataset y resultado.</p>
          </div>
        </div>

        {!loading && history.items.length === 0 ? (
          <StateMessage type="empty" title="No hay análisis guardados" />
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Análisis</th>
                  <th>Dataset</th>
                  <th>Observaciones</th>
                  <th>Fecha</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {history.items.map((analysis) => (
                  <tr key={analysis.analysis_id}>
                    <td><strong>#{analysis.analysis_id}</strong></td>
                    <td>{analysisLabels[analysis.analysis_type]}</td>
                    <td>{analysis.dataset_name}</td>
                    <td>{analysis.observation_count}</td>
                    <td>{new Date(analysis.created_at).toLocaleString('es-PE')}</td>
                    <td><span className="status-pill success">Completado</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}

export default Analytics
