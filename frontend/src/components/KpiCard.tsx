interface KpiCardProps {
  label: string
  value: string
  change: string
  detail: string
}

function KpiCard({
  label,
  value,
  change,
  detail,
}: KpiCardProps) {
  return (
    <article className="kpi-card">
      <div className="kpi-top">
        <span>{label}</span>
        <span className="kpi-badge">{change}</span>
      </div>

      <strong className="kpi-value">{value}</strong>

      <span className="kpi-detail">{detail}</span>
    </article>
  )
}

export default KpiCard
