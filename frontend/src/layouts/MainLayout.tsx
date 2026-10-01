import type { ReactNode } from 'react'
import type { PageKey } from '../app/navigation'
import Header from '../components/Header'
import Sidebar from '../components/Sidebar'

interface MainLayoutProps {
  children: ReactNode
  activePage: PageKey
  onNavigate: (page: PageKey) => void
  onLogout: () => void
}

function MainLayout({
  children,
  activePage,
  onNavigate,
  onLogout,
}: MainLayoutProps) {
  return (
    <div className="main-layout">
      <Sidebar
        activePage={activePage}
        onNavigate={onNavigate}
        onLogout={onLogout}
      />

      <div className="main-area">
        <Header activePage={activePage} />

        <main className="content-area">
          {children}
        </main>
      </div>
    </div>
  )
}

export default MainLayout
