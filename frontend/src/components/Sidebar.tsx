import {
  navigationItems,
  type PageKey,
} from '../app/navigation'

interface SidebarProps {
  activePage: PageKey
  onNavigate: (page: PageKey) => void
  onLogout: () => void
}

function Sidebar({
  activePage,
  onNavigate,
  onLogout,
}: SidebarProps) {
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
        PRINCIPAL
      </div>

      <nav className="sidebar-nav">
        {navigationItems.map((item) => (
          <button
            key={item.key}
            type="button"
            className={`nav-item ${
              activePage === item.key ? 'active' : ''
            }`}
            onClick={() => onNavigate(item.key)}
          >
            <span className="nav-dot" />
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-status">
          <span className="status-indicator" />
          Sistema operativo
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
