import {
  navigationItems,
  roleLabels,
  type PageKey,
} from '../app/navigation'
import type { AuthUser } from '../types/api'
import ThemeToggle from './ThemeToggle'

interface HeaderProps {
  activePage: PageKey
  user: AuthUser
  onOpenMenu: () => void
}

function getInitials(name: string) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part.charAt(0).toUpperCase())
    .join('')
}

function Header({ activePage, user, onOpenMenu }: HeaderProps) {
  const current = navigationItems.find(
    (item) => item.key === activePage,
  )

  return (
    <header className="topbar">
      <button
        type="button"
        className="mobile-menu-button"
        onClick={onOpenMenu}
        aria-label="Mostrar u ocultar menú principal"
        title="Mostrar u ocultar menú"
        aria-controls="salesia-sidebar"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M4 7h16M4 12h16M4 17h16" />
        </svg>
      </button>

      <div className="topbar-copy">
        <div className="breadcrumb">
          SalesIA Enterprise <span>/</span> {current?.label}
        </div>

        <p className="topbar-description">
          {current?.description}
        </p>
      </div>

      <div className="topbar-actions">
        <ThemeToggle />
        <div className="profile">
          <div className="profile-avatar">
            {getInitials(user.name)}
          </div>
          <div>
            <strong>{user.name}</strong>
            <span>{roleLabels[user.role]}</span>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
