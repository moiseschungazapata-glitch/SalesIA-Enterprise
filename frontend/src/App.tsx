import { useState } from 'react'
import './App.css'
import type { PageKey } from './app/navigation'
import MainLayout from './layouts/MainLayout'
import Login from './modules/auth/Login'
import Analytics from './modules/analytics/Analytics'
import Customers from './modules/customers/Customers'
import Dashboard from './modules/dashboard/Dashboard'
import Insights from './modules/insights/Insights'
import Inventory from './modules/inventory/Inventory'
import Probability from './modules/probability/Probability'
import Products from './modules/products/Products'
import Reports from './modules/reports/Reports'
import Sales from './modules/sales/Sales'

function App() {
  const [authenticated, setAuthenticated] = useState(false)
  const [activePage, setActivePage] =
    useState<PageKey>('dashboard')

  if (!authenticated) {
    return (
      <Login
        onLogin={() => setAuthenticated(true)}
      />
    )
  }

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard':
        return (
          <Dashboard
            onNavigate={setActivePage}
          />
        )

      case 'customers':
        return <Customers />

      case 'products':
        return <Products />

      case 'sales':
        return <Sales />

      case 'inventory':
        return <Inventory />

      case 'analytics':
        return <Analytics />

      case 'probability':
        return <Probability />

      case 'insights':
        return <Insights />

      case 'reports':
        return <Reports />

      default:
        return (
          <Dashboard
            onNavigate={setActivePage}
          />
        )
    }
  }

  return (
    <MainLayout
      activePage={activePage}
      onNavigate={setActivePage}
      onLogout={() => {
        setAuthenticated(false)
        setActivePage('dashboard')
      }}
    >
      {renderPage()}
    </MainLayout>
  )
}

export default App
