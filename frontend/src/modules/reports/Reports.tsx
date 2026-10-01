import { useState } from 'react'
import PageHeader from '../../components/PageHeader'

type ReportType =
  | 'Todos'
  | 'Comercial'
  | 'Analytics'
  | 'Inventario'
  | 'Estadístico'

interface Report {
  id: number
  title: string
  type: Exclude<ReportType, 'Todos'>
  date: string
  status: 'Disponible' | 'Pendiente'
  description: string
}

const initialReports: Report[] = [
  {
    id: 1,
    title: 'Resumen comercial septiembre',
    type: 'Comercial',
    date: '30/09/2026',
    status: 'Disponible',
    description:
      'Resumen de ventas, ingresos y comportamiento comercial.',
  },
  {
    id: 2,
    title: 'Análisis estadístico mensual',
    type: 'Analytics',
    date: '30/09/2026',
    status: 'Disponible',
    description:
      'Resultados de media, mediana y variables analizadas.',
  },
  {
    id: 3,
    title: 'Estado de inventario',
    type: 'Inventario',
    date: '30/09/2026',
    status: 'Disponible',
    description:
      'Situación del stock y productos que requieren revisión.',
  },
  {
    id: 4,
    title: 'Reporte de probabilidad',
    type: 'Estadístico',
    date: '29/09/2026',
    status: 'Pendiente',
    description:
      'Resultados de eventos, variables aleatorias y Bayes.',
  },
]

function Reports() {
  const [reports] =
    useState<Report[]>(initialReports)

  const [filter, setFilter] =
    useState<ReportType>('Todos')

  const filteredReports =
    filter === 'Todos'
      ? reports
      : reports.filter(
          (report) => report.type === filter,
        )

  const generateReport = (title: string) => {
    window.alert(
      `Preparación del reporte "${title}". La generación final se conectará al backend.`,
    )
  }

  return (
    <div className="page">
      <PageHeader
        eyebrow="DOCUMENTACIÓN EMPRESARIAL"
        title="Reportes"
        description="Consulta, filtra y prepara reportes derivados de la información del sistema."
      />

      <section className="report-grid">
        <article className="report-card featured">
          <div className="report-icon">R</div>

          <span className="eyebrow">
            REPORTE PRINCIPAL
          </span>

          <h2>Resumen ejecutivo</h2>

          <p>
            Vista consolidada de ventas, clientes,
            productos e indicadores generales.
          </p>

          <button
            type="button"
            className="primary-button"
            onClick={() =>
              generateReport('Resumen ejecutivo')
            }
          >
            Preparar reporte
          </button>
        </article>

        <article className="report-card featured">
          <div className="report-icon">A</div>

          <span className="eyebrow">
            ANÁLISIS
          </span>

          <h2>Reporte estadístico</h2>

          <p>
            Resultados de media, mediana, variables y
            análisis probabilístico.
          </p>

          <button
            type="button"
            className="secondary-button"
            onClick={() =>
              generateReport('Reporte estadístico')
            }
          >
            Preparar análisis
          </button>
        </article>
      </section>

      <section className="panel">
        <div className="insight-toolbar">
          <div>
            <span className="eyebrow">
              HISTORIAL
            </span>

            <h2>Reportes disponibles</h2>
          </div>

          <div className="insight-filters">
            {[
              'Todos',
              'Comercial',
              'Analytics',
              'Inventario',
              'Estadístico',
            ].map((item) => (
              <button
                key={item}
                type="button"
                className={
                  filter === item
                    ? 'insight-filter active'
                    : 'insight-filter'
                }
                onClick={() =>
                  setFilter(
                    item as ReportType,
                  )
                }
              >
                {item}
              </button>
            ))}
          </div>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Reporte</th>
                <th>Tipo</th>
                <th>Fecha</th>
                <th>Estado</th>
                <th>Acción</th>
              </tr>
            </thead>

            <tbody>
              {filteredReports.map((report) => (
                <tr key={report.id}>
                  <td>
                    <div className="report-table-title">
                      <strong>{report.title}</strong>
                      <span>
                        {report.description}
                      </span>
                    </div>
                  </td>

                  <td>{report.type}</td>

                  <td>{report.date}</td>

                  <td>
                    <span
                      className={`status-pill ${
                        report.status ===
                        'Disponible'
                          ? 'success'
                          : 'warning'
                      }`}
                    >
                      {report.status}
                    </span>
                  </td>

                  <td>
                    <button
                      type="button"
                      className="text-button"
                      onClick={() =>
                        generateReport(
                          report.title,
                        )
                      }
                    >
                      Generar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="panel report-info-panel">
        <div>
          <span className="eyebrow">
            FLUJO
          </span>

          <h2>
            Datos → análisis → reporte
          </h2>

          <p>
            Los reportes de la versión integrada se
            alimentarán posteriormente con los resultados
            reales provenientes de FastAPI y PostgreSQL.
          </p>
        </div>

        <div className="report-flow">
          <span>Datos</span>
          <strong>→</strong>
          <span>Analytics</span>
          <strong>→</strong>
          <span>Insights</span>
          <strong>→</strong>
          <span>Reporte</span>
        </div>
      </section>
    </div>
  )
}

export default Reports
