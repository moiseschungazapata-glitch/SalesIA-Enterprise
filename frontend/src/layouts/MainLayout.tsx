import Sidebar from '../components/Sidebar'

interface MainLayoutProps {
  children: React.ReactNode
}

function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="main-layout">
      <Sidebar />

      <main className="main-content">
        {children}
      </main>
    </div>
  )
}

export default MainLayout