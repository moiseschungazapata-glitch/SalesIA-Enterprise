import {
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from 'react-router-dom'
import './App.css'
import {
  canAccessPage,
  getDefaultPage,
  getPageByPath,
  pagePaths,
  type PageKey,
} from './app/navigation'
import StateMessage from './components/StateMessage'
import { useAuth } from './hooks/useAuth'
import MainLayout from './layouts/MainLayout'
import Analytics from './modules/analytics/Analytics'
import Login from './modules/auth/Login'
import Customers from './modules/customers/Customers'
import Dashboard from './modules/dashboard/Dashboard'
import Inventory from './modules/inventory/Inventory'
import Insights from './modules/insights/Insights'
import Products from './modules/products/Products'
import Probability from './modules/probability/Probability'
import Reports from './modules/reports/Reports'
import Sales from './modules/sales/Sales'
import Security from './modules/security/Security'
import Users from './modules/users/Users'
import type { AuthUser } from './types/api'

interface AuthenticatedApplicationProps {
  user: AuthUser
  onLogout: () => void
}

function AuthenticatedApplication({
  user,
  onLogout,
}: AuthenticatedApplicationProps) {
  const location = useLocation()
  const navigate = useNavigate()
  const defaultPage = getDefaultPage(user.role)
  const requestedPage = getPageByPath(location.pathname)
  const activePage =
    requestedPage && canAccessPage(user.role, requestedPage)
      ? requestedPage
      : defaultPage

  const goToPage = (page: PageKey) => {
    if (canAccessPage(user.role, page)) {
      navigate(pagePaths[page])
    }
  }

  const guarded = (page: PageKey, content: React.ReactNode) =>
    canAccessPage(user.role, page) ? (
      content
    ) : (
      <Navigate to={pagePaths[defaultPage]} replace />
    )

  return (
    <MainLayout
      activePage={activePage}
      user={user}
      onNavigate={goToPage}
      onLogout={onLogout}
    >
      <Routes>
        <Route
          path="/"
          element={<Navigate to={pagePaths[defaultPage]} replace />}
        />
        <Route
          path={pagePaths.dashboard}
          element={guarded(
            'dashboard',
            <Dashboard role={user.role} onNavigate={goToPage} />,
          )}
        />
        <Route
          path={pagePaths.sales}
          element={guarded('sales', <Sales role={user.role} />)}
        />
        <Route
          path={pagePaths.customers}
          element={guarded(
            'customers',
            <Customers role={user.role} />,
          )}
        />
        <Route
          path={pagePaths.products}
          element={guarded(
            'products',
            <Products role={user.role} />,
          )}
        />
        <Route
          path={pagePaths.inventory}
          element={guarded(
            'inventory',
            <Inventory role={user.role} />,
          )}
        />
        <Route
          path={pagePaths.users}
          element={guarded(
            'users',
            <Users currentUserId={user.id} />,
          )}
        />
        <Route
          path={pagePaths.analytics}
          element={guarded('analytics', <Analytics />)}
        />
        <Route
          path={pagePaths.probability}
          element={guarded('probability', <Probability />)}
        />
        <Route
          path={pagePaths.insights}
          element={guarded('insights', <Insights />)}
        />
        <Route
          path={pagePaths.reports}
          element={guarded('reports', <Reports />)}
        />
        <Route
          path={pagePaths.security}
          element={guarded('security', <Security user={user} onLogout={onLogout} />)}
        />
        <Route
          path="/login"
          element={<Navigate to={pagePaths[defaultPage]} replace />}
        />
        <Route
          path="*"
          element={<Navigate to={pagePaths[defaultPage]} replace />}
        />
      </Routes>
    </MainLayout>
  )
}

function App() {
  const { status, user, logout } = useAuth()

  if (status === 'loading') {
    return (
      <main className="login-page">
        <section className="login-panel session-loader">
          <StateMessage
            type="loading"
            title="Restaurando tu sesión"
            description="Estamos validando de forma segura tu acceso con la API."
          />
        </section>
      </main>
    )
  }

  if (status === 'anonymous' || !user) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    )
  }

  return <AuthenticatedApplication user={user} onLogout={logout} />
}

export default App
