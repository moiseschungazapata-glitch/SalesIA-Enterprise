import type { ReactNode } from 'react'
import type {
  PageKey,
  UserRole,
} from '../app/navigation'
import Header from '../components/Header'
import Sidebar from '../components/Sidebar'

interface MainLayoutProps {
  children: ReactNode
  activePage: PageKey
  role: UserRole
  onRoleChange: (role: UserRole) => void
  onNavigate: (page: PageKey) => void
  onLogout: () => void
}

function MainLayout({
  children,
  activePage,
  role,
  onRoleChange,
  onNavigate,
  onLogout,
}: MainLayoutProps) {
  return (
    <div className="main-layout">
      <Sidebar
        activePage={activePage}
        role={role}
        onNavigate={onNavigate}
        onLogout={onLogout}
      />

      <div className="main-area">
        <Header
          activePage={activePage}
          role={role}
          onRoleChange={onRoleChange}
        />

        <div className="prototype-banner" role="status">
          Prototipo de fase 03: los datos y el cambio de rol son
          demostrativos. La autenticación real corresponde a la fase 05.
        </div>

        <main className="content-area">
          {children}
        </main>
      </div>
    </div>
  )
}

export default MainLayout
