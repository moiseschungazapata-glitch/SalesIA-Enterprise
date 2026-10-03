import { useState } from 'react'
import './App.css'
import {
  canAccessPage,
  getDefaultPage,
  type PageKey,
  type UserRole,
} from './app/navigation'
import MainLayout from './layouts/MainLayout'
import Login from './modules/auth/Login'
import Customers from './modules/customers/Customers'
import Dashboard from './modules/dashboard/Dashboard'
import Inventory from './modules/inventory/Inventory'
import Products from './modules/products/Products'
import Sales from './modules/sales/Sales'
import Users from './modules/users/Users'

function App() {
  const [authenticated, setAuthenticated] = useState(false)
  const [role, setRole] =
    useState<UserRole>('administrator')
  const [activePage, setActivePage] =
    useState<PageKey>('dashboard')

  const changeRole = (nextRole: UserRole) => {
    setRole(nextRole)
    setActivePage(getDefaultPage(nextRole))
  }

  if (!authenticated) {
    return (
      <Login
        onLogin={() => {
          setAuthenticated(true)
          setActivePage(getDefaultPage(role))
        }}
      />
    )
  }

  const safePage = canAccessPage(role, activePage)
    ? activePage
    : getDefaultPage(role)

  const renderPage = () => {
    switch (safePage) {
      case 'dashboard':
        return (
          <Dashboard
            role={role}
            onNavigate={setActivePage}
          />
        )

      case 'sales':
        return <Sales role={role} />

      case 'customers':
        return <Customers role={role} />

      case 'products':
        return <Products role={role} />

      case 'inventory':
        return <Inventory role={role} />

      case 'users':
        return <Users />

      default:
        return (
          <Dashboard
            role={role}
            onNavigate={setActivePage}
          />
        )
    }
  }

  return (
    <MainLayout
      activePage={safePage}
      role={role}
      onRoleChange={changeRole}
      onNavigate={setActivePage}
      onLogout={() => {
        setAuthenticated(false)
        setRole('administrator')
        setActivePage('dashboard')
      }}
    >
      {renderPage()}
    </MainLayout>
  )
}

export default App
