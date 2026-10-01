import {
  navigationItems,
  type PageKey,
} from '../app/navigation'

interface HeaderProps {
  activePage: PageKey
}

function Header({ activePage }: HeaderProps) {
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
        <button type="button" className="icon-button">
          ?
        </button>

        <button type="button" className="icon-button">
          !
        </button>

        <div className="profile">
          <div className="profile-avatar">CR</div>
          <div>
            <strong>Carlos Rivera</strong>
            <span>Administrador</span>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
