import {
  getNavigationItems,
  roleLabels,
  type PageKey,
  type UserRole,
} from '../app/navigation'

interface SidebarProps {
  activePage: PageKey
  role: UserRole
  onNavigate: (page: PageKey) => void
  onLogout: () => void
  mobileOpen: boolean
  onClose: () => void
}

function Sidebar({
  activePage,
  role,
  onNavigate,
  onLogout,
  mobileOpen,
  onClose,
}: SidebarProps) {
  const items = getNavigationItems(role)

  return (
    <aside
      id="salesia-sidebar"
      className={`sidebar ${mobileOpen ? 'mobile-open' : ''}`}
    >
      <div className="sidebar-brand">
        <div className="brand-mark">S</div>

        <div>
          <strong>SalesIA</strong>
          <span>Enterprise</span>
        </div>

        <button
          type="button"
          className="sidebar-close-button"
          onClick={onClose}
          aria-label="Cerrar menú principal"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="m6 6 12 12M18 6 6 18" />
          </svg>
        </button>
      </div>

      <div className="sidebar-section-label">
        {roleLabels[role]}
      </div>

      <nav className="sidebar-nav" aria-label="Navegación principal">
        {items.map((item) => (
          <button
            key={item.key}
            type="button"
            aria-label={item.label}
            title={item.label}
            className={`nav-item ${
              activePage === item.key ? 'active' : ''
            }`}
            onClick={() => {
              onNavigate(item.key)
              onClose()
            }}
          >
            <span className="nav-dot">
              {item.label.charAt(0)}
            </span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-status">
          <span className="status-indicator" />
          Sesión segura activa
        </div>

        <button
          type="button"
          className="logout-button"
          onClick={() => {
            onClose()
            onLogout()
          }}
        >
          Cerrar sesión
        </button>
      </div>
    </aside>
  )
}

export default Sidebar
