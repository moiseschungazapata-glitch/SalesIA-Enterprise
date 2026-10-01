interface KpiCardProps {
  label: string
  value: string
  change?: string
  detail: string
  trend?: 'positive' | 'negative' | 'neutral'
}

function KpiCard({
  label,
  value,
  change,
  detail,
  trend = 'positive',
}: KpiCardProps) {
  return (
    <article className="kpi-card">
      <div className="kpi-top">
        <span>{label}</span>

        {change && (
          <span className={`kpi-badge ${trend}`}>
            {change}
          </span>
        )}
      </div>

      <strong className="kpi-value">{value}</strong>

      <span className="kpi-detail">{detail}</span>
    </article>
  )
}

export default KpiCard
