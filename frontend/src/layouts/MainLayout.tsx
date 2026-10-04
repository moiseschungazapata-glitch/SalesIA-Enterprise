import { useEffect, useState, type ReactNode } from 'react'
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
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => (
    window.localStorage.getItem('salesia.sidebar-collapsed') === 'true'
  ))

  useEffect(() => {
    window.localStorage.setItem(
      'salesia.sidebar-collapsed',
      String(sidebarCollapsed),
    )
  }, [sidebarCollapsed])

  const toggleSidebar = () => {
    if (window.matchMedia('(max-width: 760px)').matches) {
      setMobileMenuOpen((current) => !current)
      return
    }

    setSidebarCollapsed((current) => !current)
  }

  return (
    <div
      className={`main-layout ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}
    >
      <button
        type="button"
        className={`sidebar-backdrop ${mobileMenuOpen ? 'visible' : ''}`}
        onClick={() => setMobileMenuOpen(false)}
        aria-label="Cerrar menú principal"
        tabIndex={mobileMenuOpen ? 0 : -1}
      />
      <Sidebar
        activePage={activePage}
        role={user.role}
        onNavigate={onNavigate}
        onLogout={onLogout}
        mobileOpen={mobileMenuOpen}
        onClose={() => setMobileMenuOpen(false)}
      />

      <div className="main-area">
        <Header
          activePage={activePage}
          user={user}
          onOpenMenu={toggleSidebar}
        />

        <div className="integration-banner" role="status">
          Sesión, usuarios, clientes, productos, inventario y ventas conectados
          a la API y a la base de datos.
        </div>

        <main className="content-area">
          {children}
        </main>
      </div>
    </div>
  )
}

export default MainLayout
