import { useState, type FormEvent } from 'react'
import PageHeader from '../../components/PageHeader'
import StateMessage from '../../components/StateMessage'
import {
  analyzeRandomVariable,
  calculateAutomaticEventProbability,
  calculateBayes,
} from '../../services/analytics'
import type {
  AnalysisExecutionRecord,
  AutomaticEventType,
} from '../../types/api'

type ProbabilitySection = 'events' | 'random' | 'bayes'

const automaticEvents: Record<
  AutomaticEventType,
  { label: string; numerator: string; denominator: string }
> = {
  order_conversion: {
    label: 'Pedido convertido en venta',
    numerator: 'Pedidos con estado convertido',
    denominator: 'Pedidos registrados, excepto borradores',
  },
  fully_paid_sale: {
    label: 'Venta pagada completamente',
    numerator: 'Ventas con pago completo',
    denominator: 'Ventas confirmadas',
  },
  card_payment: {
    label: 'Pago realizado con tarjeta',
    numerator: 'Pagos completados con tarjeta',
    denominator: 'Todos los pagos completados',
  },
}

function resultNumber(result: AnalysisExecutionRecord | null, metric: string) {
  const value = result?.results.find((item) => item.metric === metric)
    ?.numeric_value
  return value === null || value === undefined ? null : Number(value)
}

function percentage(value: number | null) {
  return value === null ? '—' : `${(value * 100).toFixed(2)}%`
}

function Probability() {
  const [section, setSection] = useState<ProbabilitySection>('events')
  const [result, setResult] = useState<AnalysisExecutionRecord | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [automaticEvent, setAutomaticEvent] = useState<AutomaticEventType>(
    'order_conversion',
  )
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')

  const [randomName, setRandomName] = useState('Monto de venta')
  const [randomType, setRandomType] = useState<'discrete' | 'continuous'>(
    'continuous',
  )
  const [randomValues, setRandomValues] = useState(
    '120, 150, 180, 200, 240, 260, 300',
  )

  const [eventA, setEventA] = useState('Cliente recurrente')
  const [eventB, setEventB] = useState('Realiza una compra este mes')
  const [prior, setPrior] = useState('0.40')
  const [likelihood, setLikelihood] = useState('0.70')
  const [evidence, setEvidence] = useState('0.50')

  const changeSection = (nextSection: ProbabilitySection) => {
    setSection(nextSection)
    setResult(null)
    setError('')
  }

  const runRequest = async (request: () => Promise<AnalysisExecutionRecord>) => {
    setLoading(true)
    setError('')
    try {
      setResult(await request())
    } catch (requestError) {
      setResult(null)
      setError(
        requestError instanceof Error
          ? requestError.message
          : 'No se pudo completar el cálculo.',
      )
    } finally {
      setLoading(false)
    }
  }

  const submitAutomaticEvent = (event: FormEvent) => {
    event.preventDefault()
    void runRequest(() =>
      calculateAutomaticEventProbability({
        event_type: automaticEvent,
        date_from: dateFrom || null,
        date_to: dateTo || null,
      }),
    )
  }

  const submitRandom = (event: FormEvent) => {
    event.preventDefault()
    const values = randomValues
      .split(',')
      .map((value) => Number(value.trim()))
      .filter((value) => Number.isFinite(value))
    if (values.length === 0) {
      setError('Ingresa al menos un valor numérico válido.')
      return
    }
    void runRequest(() =>
      analyzeRandomVariable({
        name: randomName,
        variable_name: 'manual_random_variable',
        variable_label: randomName,
        variable_type:
          randomType === 'discrete'
            ? 'quantitative_discrete'
            : 'quantitative_continuous',
        random_variable_type: randomType,
        values,
      }),
    )
  }

  const submitBayes = (event: FormEvent) => {
    event.preventDefault()
    void runRequest(() =>
      calculateBayes({
        event_a: eventA,
        event_b: eventB,
        probability_a: prior,
        probability_b_given_a: likelihood,
        probability_b: evidence,
      }),
    )
  }

  const eventProbability = resultNumber(result, 'probability')
  const favorableCases = resultNumber(result, 'favorable_cases')
  const totalObservations = resultNumber(result, 'total_observations')
  const posterior = resultNumber(result, 'posterior')
  const selectedAutomaticEvent = automaticEvents[automaticEvent]

  return (
    <div className="page">
      <PageHeader
        eyebrow="MOTOR ESTADÍSTICO · FASE 09"
        title="Probabilidad y Bayes"
        description="Cálculos reproducibles ejecutados por Python y registrados en Supabase."
      />

      <div className="probability-navigation">
        <button
          type="button"
          className={section === 'events' ? 'analytics-tab active' : 'analytics-tab'}
          onClick={() => changeSection('events')}
        >
          Eventos
        </button>
        <button
          type="button"
          className={section === 'random' ? 'analytics-tab active' : 'analytics-tab'}
          onClick={() => changeSection('random')}
        >
          Variable aleatoria
        </button>
        <button
          type="button"
          className={section === 'bayes' ? 'analytics-tab active' : 'analytics-tab'}
          onClick={() => changeSection('bayes')}
        >
          Bayes
        </button>
      </div>

      {section === 'events' && (
        <section className="probability-layout">
          <article className="panel">
            <div className="panel-header">
              <div>
                <span className="eyebrow">EVENTOS</span>
                <h2>Probabilidad con datos reales</h2>
                <p>P(A) = casos favorables / observaciones.</p>
              </div>
            </div>
            <form
              className="probability-form probability-submit-form"
              onSubmit={submitAutomaticEvent}
            >
              <label>
                Evento empresarial
                <select
                  value={automaticEvent}
                  onChange={(event) =>
                    setAutomaticEvent(event.target.value as AutomaticEventType)
                  }
                >
                  {Object.entries(automaticEvents).map(([value, definition]) => (
                    <option value={value} key={value}>
                      {definition.label}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Desde (opcional)
                <input
                  type="date"
                  value={dateFrom}
                  max={dateTo || undefined}
                  onChange={(event) => setDateFrom(event.target.value)}
                />
              </label>
              <label>
                Hasta (opcional)
                <input
                  type="date"
                  value={dateTo}
                  min={dateFrom || undefined}
                  onChange={(event) => setDateTo(event.target.value)}
                />
              </label>
              <button className="primary-button" type="submit" disabled={loading}>
                {loading ? 'Consultando…' : 'Calcular con datos reales'}
              </button>
            </form>
            <div className="probability-data-definition">
              <span><strong>Casos favorables:</strong> {selectedAutomaticEvent.numerator}</span>
              <span><strong>Total observado:</strong> {selectedAutomaticEvent.denominator}</span>
              <small>Sin fechas se utiliza todo el historial disponible.</small>
            </div>
          </article>

          <article className="probability-result">
            <span className="eyebrow">RESULTADO</span>
            <strong>{percentage(eventProbability)}</strong>
            <p>Probabilidad estimada del evento.</p>
            {favorableCases !== null && totalObservations !== null && (
              <div className="probability-breakdown">
                <span>{favorableCases} casos favorables</span>
                <span>÷</span>
                <span>{totalObservations} observaciones</span>
              </div>
            )}
            <div className="result-meter">
              <div style={{ width: `${(eventProbability || 0) * 100}%` }} />
            </div>
          </article>
        </section>
      )}

      {section === 'random' && (
        <>
          <section className="panel">
            <div className="panel-header">
              <div>
                <span className="eyebrow">VARIABLE ALEATORIA</span>
                <h2>Analizar observaciones</h2>
                <p>Clasifica la variable y conserva su distribución y resultados.</p>
              </div>
            </div>
            <form className="random-variable-form" onSubmit={submitRandom}>
              <div className="probability-form random-metadata-form">
                <label>
                  Nombre
                  <input value={randomName} onChange={(event) => setRandomName(event.target.value)} required />
                </label>
                <label>
                  Naturaleza
                  <select value={randomType} onChange={(event) => setRandomType(event.target.value as 'discrete' | 'continuous')}>
                    <option value="continuous">Continua</option>
                    <option value="discrete">Discreta</option>
                  </select>
                </label>
              </div>
              <label>
                Valores separados por comas
                <textarea value={randomValues} onChange={(event) => setRandomValues(event.target.value)} rows={4} required />
              </label>
              <button className="primary-button" type="submit" disabled={loading}>
                {loading ? 'Analizando…' : 'Analizar y guardar'}
              </button>
            </form>
          </section>

          {result && (
            <section className="kpi-grid">
              {[
                ['Observaciones', 'sample_size'],
                ['Media', 'mean'],
                ['Mediana', 'median'],
                ['Mínimo', 'minimum'],
                ['Máximo', 'maximum'],
              ].map(([label, metric]) => (
                <article className="kpi-card" key={metric}>
                  <div className="kpi-top"><span>{label}</span></div>
                  <strong className="kpi-value">
                    {resultNumber(result, metric)?.toLocaleString('es-PE', {
                      maximumFractionDigits: 2,
                    }) ?? '—'}
                  </strong>
                  <span className="kpi-detail">resultado persistido</span>
                </article>
              ))}
            </section>
          )}
        </>
      )}

      {section === 'bayes' && (
        <section className="probability-layout">
          <article className="panel">
            <div className="panel-header">
              <div>
                <span className="eyebrow">TEOREMA DE BAYES</span>
                <h2>Probabilidad posterior</h2>
                <p>P(A|B) = P(B|A) × P(A) / P(B).</p>
              </div>
            </div>
            <form className="probability-form probability-submit-form" onSubmit={submitBayes}>
              <label>
                Evento A
                <input value={eventA} onChange={(event) => setEventA(event.target.value)} required />
              </label>
              <label>
                Evidencia B
                <input value={eventB} onChange={(event) => setEventB(event.target.value)} required />
              </label>
              <label>
                P(A) · Previa
                <input type="number" step="0.01" min="0" max="1" value={prior} onChange={(event) => setPrior(event.target.value)} required />
              </label>
              <label>
                P(B|A) · Verosimilitud
                <input type="number" step="0.01" min="0" max="1" value={likelihood} onChange={(event) => setLikelihood(event.target.value)} required />
              </label>
              <label>
                P(B) · Evidencia
                <input type="number" step="0.01" min="0.01" max="1" value={evidence} onChange={(event) => setEvidence(event.target.value)} required />
              </label>
              <button className="primary-button" type="submit" disabled={loading}>
                {loading ? 'Calculando…' : 'Calcular y guardar'}
              </button>
            </form>
          </article>

          <article className="probability-result">
            <span className="eyebrow">P(A|B)</span>
            <strong>{percentage(posterior)}</strong>
            <p>Probabilidad posterior con la evidencia indicada.</p>
            <div className="result-meter">
              <div style={{ width: `${(posterior || 0) * 100}%` }} />
            </div>
          </article>
        </section>
      )}

      {error && (
        <StateMessage
          type="error"
          title="No se pudo completar el cálculo"
          description={error}
        />
      )}

      {result && (
        <StateMessage
          type="success"
          title={`Análisis #${result.analysis_id} guardado`}
          description={`Dataset #${result.dataset_id}: ${result.dataset_name}`}
        />
      )}

      <section className="panel probability-note">
        <span className="eyebrow">ESTADO</span>
        <h2>Motor Python conectado</h2>
        <p>
          Los cálculos ya no se realizan en el navegador: la API valida,
          calcula y registra cada ejecución en la base de datos.
        </p>
      </section>
    </div>
  )
}

export default Probability
