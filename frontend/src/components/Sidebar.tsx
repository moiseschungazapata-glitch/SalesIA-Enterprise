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
}

function Sidebar({
  activePage,
  role,
  onNavigate,
  onLogout,
}: SidebarProps) {
  const items = getNavigationItems(role)

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-mark">S</div>

        <div>
          <strong>SalesIA</strong>
          <span>Enterprise</span>
        </div>
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
            onClick={() => onNavigate(item.key)}
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
          Prototipo UX activo
        </div>

        <button
          type="button"
          className="logout-button"
          onClick={onLogout}
        >
          Cerrar sesión
        </button>
      </div>
    </aside>
  )
}

export default Sidebar
