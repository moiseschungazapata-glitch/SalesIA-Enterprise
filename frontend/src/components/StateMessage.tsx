interface StateMessageProps {
  type: 'loading' | 'empty' | 'error' | 'success'
  title: string
  description?: string
  actionLabel?: string
  onAction?: () => void
}

function StateMessage({
  type,
  title,
  description,
  actionLabel,
  onAction,
}: StateMessageProps) {
  const labels = {
    loading: 'Cargando',
    empty: 'Sin datos',
    error: 'Error',
    success: 'Completado',
  }

  return (
    <div className={`state-message ${type}`}>
      <div className="state-message-icon">
        {type === 'loading' && <span className="loading-spinner" />}
        {type === 'empty' && '○'}
        {type === 'error' && '!'}
        {type === 'success' && '✓'}
      </div>

      <span className="state-message-label">
        {labels[type]}
      </span>

      <h3>{title}</h3>

      {description && (
        <p>{description}</p>
      )}

      {actionLabel && onAction && (
        <button
          type="button"
          className="secondary-button compact"
          onClick={onAction}
        >
          {actionLabel}
        </button>
      )}
    </div>
  )
}

export default StateMessage
