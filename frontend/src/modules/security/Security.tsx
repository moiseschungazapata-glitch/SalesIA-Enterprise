import { lazy, Suspense, useCallback, useEffect, useState } from 'react'
import PageHeader from '../../components/PageHeader'
import StateMessage from '../../components/StateMessage'
import {
  getAccessLocations,
  getAuditLogs,
  getSessions,
  revokeOtherSessions,
  revokeSession,
} from '../../services/security'
import type {
  AccessLocation,
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

const AccessMap = lazy(() => import('../../components/AccessMap'))

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
  const [accesses, setAccesses] = useState<AccessLocation[]>([])
  const [selectedAccessId, setSelectedAccessId] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [success, setSuccess] = useState('')

  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true)
    setError('')
    try {
      const [sessionData, auditData, locationData] = await Promise.all([
        getSessions(signal),
        user.role === 'administrator'
          ? getAuditLogs(signal)
          : Promise.resolve({ items: [] }),
        getAccessLocations(signal),
      ])
      setSessions(sessionData.items)
      setAuditLogs(auditData.items)
      setAccesses(locationData.items)
      setSelectedAccessId((current) => current ?? locationData.items.find((item) => item.current)?.id ?? locationData.items[0]?.id ?? null)
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

  const selectedAccess = accesses.find((item) => item.id === selectedAccessId) ?? null
  const locatedAccesses = accesses.filter(
    (item) => item.latitude !== null && item.longitude !== null,
  )
  const locatedUsers = new Set(locatedAccesses.map((item) => item.user_id)).size

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
        <section className="panel security-location-section">
          <div className="panel-header security-location-heading">
            <div>
              <span className="eyebrow">MAPA DE ACCESOS</span>
              <h2>Ubicaciones aproximadas de inicio de sesión</h2>
              <p>Calculadas mediante IP pública. No se solicita GPS ni se muestran direcciones exactas.</p>
            </div>
            <span className="location-privacy-badge">Estimación por IP</span>
          </div>

          <div className="security-location-layout">
            <div className="security-map-shell">
              <Suspense fallback={<div className="access-map-empty"><strong>Cargando mapa…</strong></div>}>
                <AccessMap
                  items={accesses}
                  selectedId={selectedAccessId}
                  onSelect={(item) => setSelectedAccessId(item.id)}
                />
              </Suspense>
              <div className="security-map-legend">
                <span><i className="legend-dot known" /> Acceso ubicado</span>
                <span><i className="legend-radius" /> Radio orientativo</span>
              </div>
            </div>

            <aside className="security-location-summary">
              <div className="location-kpis">
                <div><span>Accesos</span><strong>{locatedAccesses.length}</strong></div>
                <div><span>Usuarios</span><strong>{locatedUsers}</strong></div>
              </div>
              {selectedAccess ? (
                <div className="selected-access-card">
                  <span className="eyebrow">ACCESO SELECCIONADO</span>
                  <div className="selected-access-user">
                    <div className="profile-avatar">{selectedAccess.user_name.charAt(0).toUpperCase()}</div>
                    <div><strong>{selectedAccess.user_name}</strong><span>{selectedAccess.user_email}</span></div>
                  </div>
                  <dl>
                    <div><dt>Zona aproximada</dt><dd>{[selectedAccess.city, selectedAccess.region, selectedAccess.country].filter(Boolean).join(', ') || 'No disponible'}</dd></div>
                    <div><dt>Inicio</dt><dd>{new Date(selectedAccess.created_at).toLocaleString('es-PE')}</dd></div>
                    <div><dt>Dispositivo</dt><dd>{deviceLabel(selectedAccess.user_agent)}</dd></div>
                    <div><dt>IP pública</dt><dd>{selectedAccess.ip_address || 'No disponible'}</dd></div>
                    <div><dt>Proveedor</dt><dd>{selectedAccess.isp || 'No disponible'}</dd></div>
                    <div><dt>Confianza</dt><dd>Orientativa · nivel ciudad/región</dd></div>
                  </dl>
                </div>
              ) : (
                <p className="location-empty-copy">Inicia sesión nuevamente para registrar la primera ubicación aproximada.</p>
              )}
            </aside>
          </div>

          {accesses.length > 0 && (
            <div className="table-wrapper access-location-table">
              <table>
                <thead><tr><th>Usuario</th><th>Fecha</th><th>Zona aproximada</th><th>IP</th><th>Dispositivo</th><th>Estado</th></tr></thead>
                <tbody>{accesses.map((item) => (
                  <tr key={item.id} className={item.id === selectedAccessId ? 'selected-row' : ''} onClick={() => setSelectedAccessId(item.id)}>
                    <td><strong>{item.user_name}</strong><small>{item.user_email}</small></td>
                    <td>{new Date(item.created_at).toLocaleString('es-PE')}</td>
                    <td>{[item.city, item.region, item.country].filter(Boolean).join(', ') || 'Sin estimación'}</td>
                    <td>{item.ip_address || '—'}</td>
                    <td>{deviceLabel(item.user_agent)}</td>
                    <td><span className={`access-status ${item.revoked_at ? 'revoked' : 'known'}`}>{item.revoked_at ? 'Revocada' : item.latitude === null ? 'Sin ubicar' : 'Conocida'}</span></td>
                  </tr>
                ))}</tbody>
              </table>
            </div>
          )}
        </section>
      )}

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
