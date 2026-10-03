import {
  navigationItems,
  roleLabels,
  type PageKey,
} from '../app/navigation'
import type { AuthUser } from '../types/api'

interface HeaderProps {
  activePage: PageKey
  user: AuthUser
}

function getInitials(name: string) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part.charAt(0).toUpperCase())
    .join('')
}

function Header({ activePage, user }: HeaderProps) {
  const current = navigationItems.find(
    (item) => item.key === activePage,
  )

  return (
    <header className="topbar">
      <div>
        <div className="breadcrumb">
          SalesIA Enterprise <span>/</span> {current?.label}
        </div>

        <p className="topbar-description">
          {current?.description}
        </p>
      </div>

      <div className="topbar-actions">
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
