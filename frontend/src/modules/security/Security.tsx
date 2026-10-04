import { useCallback, useEffect, useState } from 'react'
import PageHeader from '../../components/PageHeader'
import StateMessage from '../../components/StateMessage'
import {
  getAuditLogs,
  getSessions,
  revokeOtherSessions,
  revokeSession,
} from '../../services/security'
import type {
  AuditLogRecord,
  AuthUser,
  SecuritySession,
} from '../../types/api'

interface SecurityProps {
  user: AuthUser
  onLogout: () => void
}

const actionLabels: Record<string, string> = {
  'auth.login': 'Inicio de sesión',
  'auth.login_failed': 'Acceso rechazado',
  'auth.logout': 'Cierre de sesión',
  'session.revoke': 'Sesión revocada',
  'session.revoke_others': 'Otras sesiones cerradas',
  'user.create': 'Usuario creado',
  'user.update': 'Usuario actualizado',
  'customer.create': 'Cliente creado',
  'customer.update': 'Cliente actualizado',
  'product.create': 'Producto creado',
  'product.update': 'Producto actualizado',
  'category.create': 'Categoría creada',
  'category.update': 'Categoría actualizada',
  'inventory.adjust': 'Inventario ajustado',
  'sale.create': 'Venta registrada',
  'insight.generate': 'Insights generados',
  'report.generate': 'Reporte generado',
}

function deviceLabel(userAgent: string | null) {
  if (!userAgent) return 'Dispositivo no identificado'
  if (/mobile|android|iphone/i.test(userAgent)) return 'Dispositivo móvil'
  if (/windows/i.test(userAgent)) return 'Equipo Windows'
  if (/macintosh|mac os/i.test(userAgent)) return 'Equipo Mac'
  if (/linux/i.test(userAgent)) return 'Equipo Linux'
  return 'Navegador web'
}

function Security({ user, onLogout }: SecurityProps) {
  const [sessions, setSessions] = useState<SecuritySession[]>([])
  const [auditLogs, setAuditLogs] = useState<AuditLogRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [success, setSuccess] = useState('')

  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true)
    setError('')
    try {
      const [sessionData, auditData] = await Promise.all([
        getSessions(signal),
        user.role === 'administrator'
          ? getAuditLogs(signal)
          : Promise.resolve({ items: [] }),
      ])
      setSessions(sessionData.items)
      setAuditLogs(auditData.items)
    } catch (requestError) {
      if (requestError instanceof DOMException && requestError.name === 'AbortError') return
      setError(requestError instanceof Error ? requestError.message : 'No se pudo cargar la seguridad.')
    } finally {
      setLoading(false)
    }
  }, [user.role])

  useEffect(() => {
    const controller = new AbortController()
    const timer = window.setTimeout(() => void load(controller.signal), 0)
    return () => {
      window.clearTimeout(timer)
      controller.abort()
    }
  }, [load])

  const closeOtherSessions = async () => {
    setBusy(true)
    setError('')
    try {
      const result = await revokeOtherSessions()
      setSuccess(`${result.revoked} sesión(es) adicional(es) cerrada(s).`)
      await load()
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'No se pudieron cerrar las sesiones.')
    } finally {
      setBusy(false)
    }
  }

  const closeSession = async (item: SecuritySession) => {
    setBusy(true)
    setError('')
    try {
      await revokeSession(item.id)
      if (item.current) {
        onLogout()
        return
      }
      setSuccess('La sesión seleccionada fue revocada.')
      await load()
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'No se pudo revocar la sesión.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page security-page">
      <PageHeader
        eyebrow="FASE 13 · PROTECCIÓN Y TRAZABILIDAD"
        title="Seguridad y auditoría"
        description="Controla tus accesos y consulta las acciones críticas registradas por el sistema."
        action={(
          <button type="button" className="secondary-button" disabled={busy} onClick={() => void closeOtherSessions()}>
            Cerrar otras sesiones
          </button>
        )}
      />

      {loading && <StateMessage type="loading" title="Verificando sesiones" />}
      {!loading && error && <StateMessage type="error" title="No se pudo cargar la seguridad" description={error} actionLabel="Reintentar" onAction={() => void load()} />}
      {success && <p className="form-success security-feedback">{success}</p>}

      {!loading && !error && (
        <section className="panel security-section">
          <div className="panel-header">
            <div><span className="eyebrow">CONTROL DE SESIONES</span><h2>Dispositivos con acceso</h2><p>Los tokens pueden revocarse desde el servidor sin esperar a que venzan.</p></div>
          </div>
          <div className="security-session-grid">
            {sessions.map((item) => (
              <article className={`security-session-card ${item.current ? 'current' : ''}`} key={item.id}>
                <div className="security-session-icon">{item.current ? '✓' : '•'}</div>
                <div>
                  <div className="security-session-title"><strong>{deviceLabel(item.user_agent)}</strong>{item.current && <span>Esta sesión</span>}</div>
                  <p>IP: {item.ip_address || 'No disponible'}</p>
                  <small>Inició {new Date(item.created_at).toLocaleString('es-PE')} · vence {new Date(item.expires_at).toLocaleString('es-PE')}</small>
                </div>
                <button type="button" className="text-button danger" disabled={busy || Boolean(item.revoked_at)} onClick={() => void closeSession(item)}>
                  {item.revoked_at ? 'Revocada' : item.current ? 'Cerrar aquí' : 'Revocar'}
                </button>
              </article>
            ))}
          </div>
        </section>
      )}

      {!loading && !error && user.role === 'administrator' && (
        <section className="panel security-section">
          <div className="panel-header"><div><span className="eyebrow">AUDITORÍA</span><h2>Acciones críticas recientes</h2><p>Historial inmutable de accesos y cambios empresariales.</p></div></div>
          {auditLogs.length === 0 ? <StateMessage type="empty" title="Aún no hay eventos de auditoría" /> : (
            <div className="table-wrapper">
              <table><thead><tr><th>Fecha</th><th>Acción</th><th>Usuario</th><th>Recurso</th><th>IP</th></tr></thead>
                <tbody>{auditLogs.map((entry) => (
                  <tr key={entry.id}><td>{new Date(entry.created_at).toLocaleString('es-PE')}</td><td><strong>{actionLabels[entry.action] || entry.action}</strong></td><td>{entry.user_name || 'Sistema'}</td><td>{entry.entity_type}{entry.entity_id ? ` #${entry.entity_id}` : ''}</td><td>{entry.ip_address || '—'}</td></tr>
                ))}</tbody>
              </table>
            </div>
          )}
        </section>
      )}
    </div>
  )
}

export default Security
