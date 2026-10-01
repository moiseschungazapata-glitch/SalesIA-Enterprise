import { useMemo, useState } from 'react'
import PageHeader from '../../components/PageHeader'

type ProbabilitySection =
  | 'events'
  | 'random'
  | 'bayes'

function Probability() {
  const [section, setSection] =
    useState<ProbabilitySection>('events')

  const [successes, setSuccesses] =
    useState('7')

  const [total, setTotal] =
    useState('10')

  const [prior, setPrior] =
    useState('0.40')

  const [likelihood, setLikelihood] =
    useState('0.70')

  const [evidence, setEvidence] =
    useState('0.50')

  const [randomValues, setRandomValues] =
    useState('120, 150, 180, 200, 240, 260, 300')

  const eventProbability = useMemo(() => {
    const favorable = Number(successes)
    const observations = Number(total)

    if (
      !Number.isFinite(favorable) ||
      !Number.isFinite(observations) ||
      observations <= 0
    ) {
      return 0
    }

    return Math.min(
      1,
      Math.max(0, favorable / observations),
    )
  }, [successes, total])

  const parsedRandomValues = useMemo(() => {
    return randomValues
      .split(',')
      .map((value) => Number(value.trim()))
      .filter((value) => Number.isFinite(value))
  }, [randomValues])

  const randomMean = useMemo(() => {
    if (parsedRandomValues.length === 0) {
      return 0
    }

    return (
      parsedRandomValues.reduce(
        (sum, value) => sum + value,
        0,
      ) / parsedRandomValues.length
    )
  }, [parsedRandomValues])

  const randomMin = useMemo(() => {
    if (parsedRandomValues.length === 0) {
      return 0
    }

    return Math.min(...parsedRandomValues)
  }, [parsedRandomValues])

  const randomMax = useMemo(() => {
    if (parsedRandomValues.length === 0) {
      return 0
    }

    return Math.max(...parsedRandomValues)
  }, [parsedRandomValues])

  const bayesProbability = useMemo(() => {
    const pA = Number(prior)
    const pBgivenA = Number(likelihood)
    const pB = Number(evidence)

    if (
      !Number.isFinite(pA) ||
      !Number.isFinite(pBgivenA) ||
      !Number.isFinite(pB) ||
      pB <= 0
    ) {
      return 0
    }

    return Math.min(
      1,
      Math.max(
        0,
        (pA * pBgivenA) / pB,
      ),
    )
  }, [prior, likelihood, evidence])

  const percentage = (value: number) =>
    `${(value * 100).toFixed(2)}%`

  return (
    <div className="page">
      <PageHeader
        eyebrow="PROBABILIDAD"
        title="Probabilidad y Bayes"
        description="Herramientas para análisis probabilístico sobre datos comerciales."
      />

      <div className="probability-navigation">
        <button
          type="button"
          className={
            section === 'events'
              ? 'analytics-tab active'
              : 'analytics-tab'
          }
          onClick={() => setSection('events')}
        >
          Eventos
        </button>

        <button
          type="button"
          className={
            section === 'random'
              ? 'analytics-tab active'
              : 'analytics-tab'
          }
          onClick={() => setSection('random')}
        >
          Variable aleatoria
        </button>

        <button
          type="button"
          className={
            section === 'bayes'
              ? 'analytics-tab active'
              : 'analytics-tab'
          }
          onClick={() => setSection('bayes')}
        >
          Bayes
        </button>
      </div>

      {section === 'events' && (
        <section className="probability-layout">
          <article className="panel">
            <div className="panel-header">
              <div>
                <span className="eyebrow">
                  EVENTOS
                </span>

                <h2>Probabilidad básica</h2>

                <p>
                  Define casos favorables y observaciones
                  para obtener una probabilidad.
                </p>
              </div>
            </div>

            <div className="probability-form">
              <label>
                Casos favorables
                <input
                  type="number"
                  min="0"
                  value={successes}
                  onChange={(event) =>
                    setSuccesses(event.target.value)
                  }
                />
              </label>

              <label>
                Total de observaciones
                <input
                  type="number"
                  min="1"
                  value={total}
                  onChange={(event) =>
                    setTotal(event.target.value)
                  }
                />
              </label>
            </div>

            <div className="probability-equation">
              <span>
                P(A) = casos favorables / observaciones
              </span>

              <strong>
                P(A) = {successes} / {total}
              </strong>
            </div>
          </article>

          <article className="probability-result">
            <span className="eyebrow">
              RESULTADO
            </span>

            <strong>
              {percentage(eventProbability)}
            </strong>

            <p>
              Probabilidad estimada del evento A.
            </p>

            <div className="result-meter">
              <div
                style={{
                  width: `${eventProbability * 100}%`,
                }}
              />
            </div>
          </article>
        </section>
      )}

      {section === 'random' && (
        <>
          <section className="panel">
            <div className="panel-header">
              <div>
                <span className="eyebrow">
                  VARIABLE ALEATORIA
                </span>

                <h2>Serie de observaciones</h2>

                <p>
                  Introduce valores numéricos separados
                  por comas para analizar la variable.
                </p>
              </div>
            </div>

            <div className="random-variable-form">
              <label>
                Valores observados
                <textarea
                  value={randomValues}
                  onChange={(event) =>
                    setRandomValues(
                      event.target.value,
                    )
                  }
                  placeholder="120, 150, 180, 200"
                  rows={4}
                />
              </label>
            </div>
          </section>

          <section className="kpi-grid">
            <article className="kpi-card">
              <div className="kpi-top">
                <span>Observaciones</span>
              </div>

              <strong className="kpi-value">
                {parsedRandomValues.length}
              </strong>

              <span className="kpi-detail">
                valores válidos
              </span>
            </article>

            <article className="kpi-card">
              <div className="kpi-top">
                <span>Media</span>
              </div>

              <strong className="kpi-value">
                {randomMean.toFixed(2)}
              </strong>

              <span className="kpi-detail">
                promedio de la variable
              </span>
            </article>

            <article className="kpi-card">
              <div className="kpi-top">
                <span>Mínimo</span>
              </div>

              <strong className="kpi-value">
                {randomMin}
              </strong>

              <span className="kpi-detail">
                valor menor
              </span>
            </article>

            <article className="kpi-card">
              <div className="kpi-top">
                <span>Máximo</span>
              </div>

              <strong className="kpi-value">
                {randomMax}
              </strong>

              <span className="kpi-detail">
                valor mayor
              </span>
            </article>
          </section>

          <section className="panel">
            <div className="panel-header">
              <div>
                <span className="eyebrow">
                  DISTRIBUCIÓN
                </span>

                <h2>Valores observados</h2>

                <p>
                  Representación visual de los valores
                  ingresados.
                </p>
              </div>
            </div>

            <div className="random-bars">
              {parsedRandomValues.map(
                (value, index) => {
                  const base =
                    Math.max(randomMax, 1)

                  return (
                    <div
                      className="random-bar-column"
                      key={`${value}-${index}`}
                    >
                      <span>{value}</span>

                      <div
                        className="random-bar"
                        style={{
                          height: `${
                            (value / base) * 100
                          }%`,
                        }}
                      />

                      <small>
                        X{index + 1}
                      </small>
                    </div>
                  )
                },
              )}
            </div>
          </section>
        </>
      )}

      {section === 'bayes' && (
        <>
          <section className="probability-layout">
            <article className="panel">
              <div className="panel-header">
                <div>
                  <span className="eyebrow">
                    TEOREMA DE BAYES
                  </span>

                  <h2>Probabilidad posterior</h2>

                  <p>
                    Configura las probabilidades para
                    calcular P(A|B).
                  </p>
                </div>
              </div>

              <div className="probability-form three">
                <label>
                  P(A) · Probabilidad previa
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    value={prior}
                    onChange={(event) =>
                      setPrior(event.target.value)
                    }
                  />
                </label>

                <label>
                  P(B|A) · Verosimilitud
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    value={likelihood}
                    onChange={(event) =>
                      setLikelihood(
                        event.target.value,
                      )
                    }
                  />
                </label>

                <label>
                  P(B) · Evidencia
                  <input
                    type="number"
                    step="0.01"
                    min="0.01"
                    max="1"
                    value={evidence}
                    onChange={(event) =>
                      setEvidence(
                        event.target.value,
                      )
                    }
                  />
                </label>
              </div>

              <div className="bayes-formula">
                <span>
                  P(A|B) = P(B|A) × P(A) / P(B)
                </span>
              </div>
            </article>

            <article className="probability-result">
              <span className="eyebrow">
                POSTERIOR
              </span>

              <strong>
                {percentage(bayesProbability)}
              </strong>

              <p>
                Resultado calculado para P(A|B).
              </p>

              <div className="result-meter">
                <div
                  style={{
                    width: `${
                      bayesProbability * 100
                    }%`,
                  }}
                />
              </div>
            </article>
          </section>

          <section className="analytics-cards">
            <article className="analysis-card">
              <span className="eyebrow">
                P(A)
              </span>

              <h3>Probabilidad previa</h3>

              <strong>
                {percentage(Number(prior))}
              </strong>

              <p>
                Representa la probabilidad inicial del
                evento antes de considerar nueva evidencia.
              </p>
            </article>

            <article className="analysis-card">
              <span className="eyebrow">
                P(B|A)
              </span>

              <h3>Verosimilitud</h3>

              <strong>
                {percentage(Number(likelihood))}
              </strong>

              <p>
                Representa la probabilidad de observar B
                cuando A ocurre.
              </p>
            </article>

            <article className="analysis-card">
              <span className="eyebrow">
                P(A|B)
              </span>

              <h3>Posterior</h3>

              <strong>
                {percentage(bayesProbability)}
              </strong>

              <p>
                Resultado actualizado utilizando la
                evidencia disponible.
              </p>
            </article>
          </section>
        </>
      )}

      <section className="panel probability-note">
        <div>
          <span className="eyebrow">
            ESTADO
          </span>

          <h2>Interfaz de demostración</h2>

          <p>
            Los cálculos mostrados actualmente se
            realizan en el frontend con datos introducidos
            por el usuario. La conexión con el motor Python
            se realizará mediante FastAPI.
          </p>
        </div>
      </section>
    </div>
  )
}

export default Probability
