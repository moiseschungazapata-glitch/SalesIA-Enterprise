import { useCallback, useEffect, useMemo, useState } from 'react'
import type { UserRole } from '../../app/navigation'
import FormModal from '../../components/FormModal'
import PageHeader from '../../components/PageHeader'
import StateMessage from '../../components/StateMessage'
import { listSellers, updateSeller } from '../../services/sellers'
import type { EmploymentStatus, SellerRecord, SellerUpdateRequest } from '../../types/api'

const money = (value: string | number) => Number(value).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const statusLabels: Record<EmploymentStatus, string> = { active: 'Activo', leave: 'Licencia', terminated: 'Finalizado' }

export default function Sellers({ role }: { role: UserRole }) {
  const [items, setItems] = useState<SellerRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [editing, setEditing] = useState<SellerRecord | null>(null)
  const [form, setForm] = useState<SellerUpdateRequest>({ employee_code: '', phone: '', document_number: '', hire_date: '', zone: '', monthly_target: '0', commission_percent: '0', employment_status: 'active' })
  const canEdit = role === 'administrator'
  const load = useCallback(async () => {
    setLoading(true); setError('')
    try { setItems((await listSellers()).items) }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'No se pudieron cargar los vendedores.') }
    finally { setLoading(false) }
  }, [])
  useEffect(() => { const timer = window.setTimeout(() => void load(), 0); return () => window.clearTimeout(timer) }, [load])
  const totalSales = useMemo(() => items.reduce((sum, item) => sum + Number(item.sales_total), 0), [items])
  const totalCommission = useMemo(() => items.reduce((sum, item) => sum + Number(item.commission_estimate), 0), [items])

  const open = (item: SellerRecord) => {
    setEditing(item)
    setForm({ employee_code: item.employee_code ?? `VEN-${String(item.user_id).padStart(6, '0')}`, phone: item.phone ?? '', document_number: item.document_number ?? '', hire_date: item.hire_date ?? '', zone: item.zone ?? '', monthly_target: item.monthly_target, commission_percent: item.commission_percent, employment_status: item.employment_status })
  }
  const save = async () => {
    if (!editing || !form.employee_code.trim()) return
    try { await updateSeller(editing.user_id, { ...form, phone: form.phone || null, document_number: form.document_number || null, hire_date: form.hire_date || null, zone: form.zone || null }); setEditing(null); setSuccess('Perfil del vendedor actualizado.'); await load() }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'No se pudo actualizar el vendedor.') }
  }

  return <div className="page">
    <PageHeader eyebrow="EQUIPO COMERCIAL" title="Vendedores" description="Administra perfiles laborales, zonas, metas, comisiones y rendimiento mensual." />
    {success && <StateMessage type="success" title={success} />}{error && <StateMessage type="error" title="No se pudo completar" description={error} />}
    <section className="kpi-grid"><article className="kpi-card"><span>Vendedores</span><strong className="kpi-value">{items.length}</strong></article><article className="kpi-card"><span>Ventas del mes</span><strong className="kpi-value">S/ {money(totalSales)}</strong></article><article className="kpi-card"><span>Comisiones estimadas</span><strong className="kpi-value">S/ {money(totalCommission)}</strong></article></section>
    <section className="panel">{loading ? <StateMessage type="loading" title="Cargando vendedores" /> : <div className="table-wrapper"><table><thead><tr><th>Vendedor</th><th>Código</th><th>Zona</th><th>Ventas del mes</th><th>Meta</th><th>Avance</th><th>Comisión</th><th>Estado</th><th>Acción</th></tr></thead><tbody>{items.map((item) => <tr key={item.user_id}><td><strong>{item.name}</strong><small>{item.email}</small></td><td>{item.employee_code ?? 'Sin ficha'}</td><td>{item.zone || 'Sin asignar'}</td><td>{item.sales_count} · S/ {money(item.sales_total)}</td><td>S/ {money(item.monthly_target)}</td><td>{money(item.target_progress_percent)}%</td><td>{money(item.commission_percent)}% · S/ {money(item.commission_estimate)}</td><td><span className={`status-pill ${item.employment_status === 'active' ? 'success' : item.employment_status === 'terminated' ? 'danger' : 'neutral'}`}>{statusLabels[item.employment_status]}</span></td><td>{canEdit && <button className="secondary-button compact" onClick={() => open(item)}>Editar ficha</button>}</td></tr>)}</tbody></table>{!items.length && <div className="empty-state">Crea un usuario con rol Vendedor para comenzar.</div>}</div>}</section>
    {editing && <FormModal eyebrow="FICHA COMERCIAL" title={editing.name} description="La meta y comisión se calculan sobre las ventas confirmadas del mes actual." onClose={() => setEditing(null)} size="wide"><div className="form-grid"><label>Código de empleado<input value={form.employee_code} maxLength={30} onChange={(e) => setForm({...form, employee_code: e.target.value})} /></label><label>Documento<input value={form.document_number ?? ''} maxLength={30} onChange={(e) => setForm({...form, document_number: e.target.value})} /></label><label>Teléfono<input value={form.phone ?? ''} maxLength={30} onChange={(e) => setForm({...form, phone: e.target.value})} /></label><label>Fecha de ingreso<input type="date" value={form.hire_date ?? ''} onChange={(e) => setForm({...form, hire_date: e.target.value})} /></label><label>Zona o sucursal<input value={form.zone ?? ''} maxLength={120} onChange={(e) => setForm({...form, zone: e.target.value})} /></label><label>Meta mensual (S/)<input type="number" min="0" step="0.01" value={form.monthly_target} onChange={(e) => setForm({...form, monthly_target: e.target.value})} /></label><label>Comisión (%)<input type="number" min="0" max="100" step="0.01" value={form.commission_percent} onChange={(e) => setForm({...form, commission_percent: e.target.value})} /></label><label>Estado laboral<select value={form.employment_status} onChange={(e) => setForm({...form, employment_status: e.target.value as EmploymentStatus})}>{Object.entries(statusLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label><div className="sale-modal-actions"><button className="secondary-button" onClick={() => setEditing(null)}>Cancelar</button><button className="primary-button" onClick={() => void save()}>Guardar ficha</button></div></div></FormModal>}
  </div>
}
