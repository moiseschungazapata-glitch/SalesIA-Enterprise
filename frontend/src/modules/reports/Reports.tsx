import { useMemo, useState } from 'react'
import PageHeader from '../../components/PageHeader'
import StateMessage from '../../components/StateMessage'
import { useReports } from '../../hooks/useReports'
import {
  downloadReport,
  generateReport,
  getReport,
} from '../../services/reports'
import type {
  ReportColumn,
  ReportDetail,
  ReportType,
} from '../../types/api'

const reportTypes: Array<{
  type: ReportType
  label: string
  description: string
}> = [
  {
    type: 'sales',
    label: 'Ventas',
    description: 'Operaciones, clientes, vendedores, unidades y facturación.',
  },
  {
    type: 'statistical',
    label: 'Estadístico',
    description: 'Datasets, análisis ejecutados y resultados calculados.',
  },
  {
    type: 'products',
    label: 'Productos',
    description: 'Catálogo, stock, unidades vendidas e ingresos por producto.',
  },
  {
    type: 'customers',
    label: 'Clientes',
    description: 'Compras, gasto acumulado y última actividad comercial.',
  },
  {
    type: 'sellers',
    label: 'Vendedores',
    description: 'Cantidad de ventas, facturación y última operación.',
  },
]

const summaryLabels: Record<string, string> = {
  transactions: 'Transacciones',
  revenue: 'Facturación',
  ticket_average: 'Ticket promedio',
  products: 'Productos',
  active_products: 'Productos activos',
  units_sold: 'Unidades vendidas',
  customers: 'Clientes',
  buyers: 'Clientes compradores',
  sellers: 'Vendedores',
  active_sellers: 'Vendedores activos',
  analyses: 'Análisis',
  completed: 'Completados',
  datasets: 'Datasets',
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

function typeLabel(type: ReportType) {
  return reportTypes.find((item) => item.type === type)?.label || type
}

function formatValue(value: unknown, column: ReportColumn) {
  if (value === null || value === undefined || value === '') return '—'
  if (column.format === 'money') {
    return `S/ ${Number(value).toLocaleString('es-PE', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`
  }
  if (column.format === 'datetime') {
    return new Date(String(value)).toLocaleString('es-PE')
  }
  if (column.format === 'date') {
    return new Date(`${String(value)}T00:00:00`).toLocaleDateString('es-PE')
  }
  return String(value)
}

function formatSummary(key: string, value: unknown) {
  if (key === 'revenue' || key === 'ticket_average') {
    return `S/ ${Number(value).toLocaleString('es-PE', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`
  }
  return String(value)
}

function Reports() {
  const [defaults] = useState(initialDates)
  const [filter, setFilter] = useState<'all' | ReportType>('all')
  const { data, loading, error, reload } = useReports(
    filter === 'all' ? undefined : filter,
  )
  const [reportType, setReportType] = useState<ReportType>('sales')
  const [title, setTitle] = useState('')
  const [dateFrom, setDateFrom] = useState(defaults.dateFrom)
  const [dateTo, setDateTo] = useState(defaults.dateTo)
  const [selectedReport, setSelectedReport] = useState<ReportDetail | null>(null)
  const [busy, setBusy] = useState(false)
  const [actionError, setActionError] = useState('')
  const [success, setSuccess] = useState('')

  const selectedType = useMemo(
    () => reportTypes.find((item) => item.type === reportType),
    [reportType],
  )

  const handleGenerate = async () => {
    if (dateTo < dateFrom) {
      setActionError('La fecha final no puede ser anterior a la fecha inicial.')
      return
    }
    setBusy(true)
    setActionError('')
    setSuccess('')
    try {
      const report = await generateReport({
        report_type: reportType,
        title: title.trim() || null,
        date_from: dateFrom,
        date_to: dateTo,
      })
      setSelectedReport(report)
      setSuccess(`Reporte #${report.id} generado con ${report.row_count} filas.`)
      reload()
    } catch (requestError) {
      setActionError(
        requestError instanceof Error
          ? requestError.message
          : 'No se pudo generar el reporte.',
      )
    } finally {
      setBusy(false)
    }
  }

  const handleView = async (reportId: number) => {
    setBusy(true)
    setActionError('')
    try {
      setSelectedReport(await getReport(reportId))
    } catch (requestError) {
      setActionError(
        requestError instanceof Error
          ? requestError.message
          : 'No se pudo abrir el reporte.',
      )
    } finally {
      setBusy(false)
    }
  }

  const handleDownload = async (reportId: number) => {
    setActionError('')
    try {
      await downloadReport(reportId)
    } catch (requestError) {
      setActionError(
        requestError instanceof Error
          ? requestError.message
          : 'No se pudo descargar el reporte.',
      )
    }
  }

  return (
    <div className="page reports-page">
      <PageHeader
        eyebrow="FASE 12 · DOCUMENTACIÓN EMPRESARIAL"
        title="Reportes"
        description="Genera, consulta, exporta e imprime reportes basados en los datos reales de SalesIA."
      />

      <section className="report-type-grid print-hidden">
        {reportTypes.map((item) => (
          <button
            key={item.type}
            type="button"
            className={reportType === item.type ? 'report-type-card active' : 'report-type-card'}
            onClick={() => setReportType(item.type)}
          >
            <span>{item.label.slice(0, 1)}</span>
            <strong>{item.label}</strong>
            <small>{item.description}</small>
          </button>
        ))}
      </section>

      <section className="panel report-generator print-hidden">
        <div className="panel-header">
          <div>
            <span className="eyebrow">GENERAR REPORTE</span>
            <h2>{selectedType?.label}</h2>
            <p>{selectedType?.description}</p>
          </div>
        </div>
        <div className="form-grid report-generation-form">
          <label>
            Título opcional
            <input
              value={title}
              maxLength={180}
              placeholder={`Reporte de ${selectedType?.label.toLowerCase()}`}
              onChange={(event) => setTitle(event.target.value)}
            />
          </label>
          <label>
            Desde
            <input type="date" value={dateFrom} onChange={(event) => setDateFrom(event.target.value)} />
          </label>
          <label>
            Hasta
            <input type="date" value={dateTo} onChange={(event) => setDateTo(event.target.value)} />
          </label>
          <button type="button" className="primary-button" disabled={busy} onClick={() => void handleGenerate()}>
            {busy ? 'Procesando…' : 'Generar reporte'}
          </button>
        </div>
        {actionError && <p className="form-error report-feedback">{actionError}</p>}
        {success && <p className="form-success report-feedback">{success}</p>}
      </section>

      <section className="panel print-hidden">
        <div className="insight-toolbar">
          <div>
            <span className="eyebrow">CONSULTAS HISTÓRICAS</span>
            <h2>Reportes guardados</h2>
          </div>
          <select className="select-input" value={filter} onChange={(event) => setFilter(event.target.value as 'all' | ReportType)}>
            <option value="all">Todos los tipos</option>
            {reportTypes.map((item) => <option key={item.type} value={item.type}>{item.label}</option>)}
          </select>
        </div>
        {loading && <StateMessage type="loading" title="Cargando reportes" />}
        {!loading && error && <StateMessage type="error" title="No se pudo cargar el historial" description={error} actionLabel="Reintentar" onAction={reload} />}
        {!loading && !error && data.items.length === 0 && <StateMessage type="empty" title="Todavía no hay reportes" description="Elige un tipo y genera el primer reporte." />}
        {!loading && !error && data.items.length > 0 && (
          <div className="table-wrapper">
            <table>
              <thead><tr><th>Reporte</th><th>Tipo</th><th>Periodo</th><th>Filas</th><th>Estado</th><th>Acciones</th></tr></thead>
              <tbody>
                {data.items.map((report) => (
                  <tr key={report.id}>
                    <td><div className="report-table-title"><strong>{report.title}</strong><span>#{report.id} · {new Date(report.created_at).toLocaleString('es-PE')}</span></div></td>
                    <td>{typeLabel(report.report_type)}</td>
                    <td>{String(report.parameters.date_from)} al {String(report.parameters.date_to)}</td>
                    <td>{report.row_count}</td>
                    <td><span className={`status-pill ${report.status === 'completed' ? 'success' : 'warning'}`}>{report.status === 'completed' ? 'Disponible' : report.status}</span></td>
                    <td><div className="table-actions"><button type="button" className="text-button" onClick={() => void handleView(report.id)}>Ver</button><button type="button" className="text-button" onClick={() => void handleDownload(report.id)}>CSV</button></div></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {selectedReport && (
        <section className="panel report-print-area">
          <div className="report-print-header">
            <div>
              <span className="eyebrow">SALESIA ENTERPRISE · REPORTE #{selectedReport.id}</span>
              <h2>{selectedReport.title}</h2>
              <p>{typeLabel(selectedReport.report_type)} · {String(selectedReport.parameters.date_from)} al {String(selectedReport.parameters.date_to)}</p>
            </div>
            <div className="report-detail-actions print-hidden">
              <button type="button" className="secondary-button" onClick={() => void handleDownload(selectedReport.id)}>Descargar CSV</button>
              <button type="button" className="primary-button" onClick={() => window.print()}>Imprimir</button>
            </div>
          </div>
          <div className="report-summary-grid">
            {Object.entries(selectedReport.content.summary).map(([key, value]) => (
              <div key={key}><span>{summaryLabels[key] || key}</span><strong>{formatSummary(key, value)}</strong></div>
            ))}
          </div>
          <div className="table-wrapper report-result-table">
            <table>
              <thead><tr>{selectedReport.content.columns.map((column) => <th key={column.key}>{column.label}</th>)}</tr></thead>
              <tbody>
                {selectedReport.content.rows.map((row, index) => (
                  <tr key={index}>{selectedReport.content.columns.map((column) => <td key={column.key}>{formatValue(row[column.key], column)}</td>)}</tr>
                ))}
              </tbody>
            </table>
          </div>
          {selectedReport.content.rows.length === 0 && <StateMessage type="empty" title="El periodo no contiene datos para este reporte" />}
          <footer className="report-print-footer">Generado el {selectedReport.generated_at ? new Date(selectedReport.generated_at).toLocaleString('es-PE') : '—'} · Datos históricos guardados en SalesIA</footer>
        </section>
      )}
    </div>
  )
}

export default Reports
