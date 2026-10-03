import {
  navigationItems,
  roleLabels,
  roleProfiles,
  type PageKey,
  type UserRole,
} from '../app/navigation'

interface HeaderProps {
  activePage: PageKey
  role: UserRole
  onRoleChange: (role: UserRole) => void
}

function Header({
  activePage,
  role,
  onRoleChange,
}: HeaderProps) {
  const current = navigationItems.find(
    (item) => item.key === activePage,
  )
  const profile = roleProfiles[role]

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
        <label className="prototype-role-control">
          <span>Vista del prototipo</span>
          <select
            value={role}
            onChange={(event) =>
              onRoleChange(event.target.value as UserRole)
            }
          >
            <option value="administrator">Administrador</option>
            <option value="seller">Vendedor</option>
            <option value="manager">Gerente</option>
          </select>
        </label>

        <div className="profile">
          <div className="profile-avatar">
            {profile.initials}
          </div>
          <div>
            <strong>{profile.name}</strong>
            <span>{roleLabels[role]}</span>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
