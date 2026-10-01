import { useState } from 'react'

function Probability() {
  const [prior, setPrior] = useState('0.40')
  const [likelihood, setLikelihood] = useState('0.70')
  const [evidence, setEvidence] = useState('0.50')

  const result =
    (Number(prior) * Number(likelihood)) /
    (Number(evidence) || 1)

  const percentage = Math.min(
    100,
    Math.max(0, result * 100),
  )

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">PROBABILIDAD</span>
          <h1>Probabilidad y Bayes</h1>
          <p>
            Espacio para análisis probabilístico sobre datos
            comerciales.
          </p>
        </div>
      </div>

      <section className="probability-layout">
        <article className="panel">
          <div className="panel-header">
            <div>
              <h2>Teorema de Bayes</h2>
              <p>
                Configura los valores para obtener una
                probabilidad posterior.
              </p>
            </div>
          </div>

          <div className="form-grid">
            <label>
              Probabilidad previa P(A)
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
              Verosimilitud P(B|A)
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={likelihood}
                onChange={(event) =>
                  setLikelihood(event.target.value)
                }
              />
            </label>

            <label>
              Evidencia P(B)
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={evidence}
                onChange={(event) =>
                  setEvidence(event.target.value)
                }
              />
            </label>
          </div>
        </article>

        <article className="probability-result">
          <span className="eyebrow">
            RESULTADO CALCULADO
          </span>

          <strong>
            {percentage.toFixed(2)}%
          </strong>

          <p>
            Probabilidad posterior P(A|B)
          </p>

          <div className="result-meter">
            <div
              style={{
                width: `${Math.min(100, percentage)}%`,
              }}
            />
          </div>
        </article>
      </section>

      <section className="analytics-cards">
        <article className="analysis-card">
          <span className="eyebrow">EVENTOS</span>
          <h3>Definición</h3>
          <p>
            Permite representar eventos y probabilidades
            asociadas a situaciones comerciales.
          </p>
        </article>

        <article className="analysis-card">
          <span className="eyebrow">BAYES</span>
          <h3>Probabilidad posterior</h3>
          <p>
            Permite actualizar una probabilidad utilizando
            nueva evidencia.
          </p>
        </article>

        <article className="analysis-card">
          <span className="eyebrow">VARIABLES</span>
          <h3>Datos aleatorios</h3>
          <p>
            Los datos operativos pueden utilizarse como base
            para variables aleatorias y análisis probabilísticos.
          </p>
        </article>
      </section>
    </div>
  )
}

export default Probability
