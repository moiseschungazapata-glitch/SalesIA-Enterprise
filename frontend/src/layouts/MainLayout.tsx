import type { ReactNode } from 'react'
import type { PageKey } from '../app/navigation'
import Header from '../components/Header'
import Sidebar from '../components/Sidebar'
import type { AuthUser } from '../types/api'

interface MainLayoutProps {
  children: ReactNode
  activePage: PageKey
  user: AuthUser
  onNavigate: (page: PageKey) => void
  onLogout: () => void
}

function MainLayout({
  children,
  activePage,
  user,
  onNavigate,
  onLogout,
}: MainLayoutProps) {
  return (
    <div className="main-layout">
      <Sidebar
        activePage={activePage}
        role={user.role}
        onNavigate={onNavigate}
        onLogout={onLogout}
      />

      <div className="main-area">
        <Header activePage={activePage} user={user} />

        <div className="integration-banner" role="status">
          Sesión y usuarios conectados a la API. Los datos comerciales
          siguen siendo demostrativos hasta las fases 07 y 08.
        </div>

        <main className="content-area">
          {children}
        </main>
      </div>
    </div>
  )
}

export default MainLayout
