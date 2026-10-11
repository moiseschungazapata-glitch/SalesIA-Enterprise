import { useEffect, useState } from 'react'
import PageHeader from '../../components/PageHeader'
import StateMessage from '../../components/StateMessage'
import { getCommercialSettings, updateCommercialSettings } from '../../services/settings'
import type { CommercialSettings } from '../../types/api'

const initial: CommercialSettings = {
  tax_rate: '18.00',
  prices_include_tax: true,
  max_discount_percent: '30.00',
}

export default function Settings() {
  const [form, setForm] = useState(initial)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    const controller = new AbortController()
    getCommercialSettings(controller.signal)
      .then(setForm)
      .catch((reason: Error) => setError(reason.message))
      .finally(() => setLoading(false))
    return () => controller.abort()
  }, [])

  const save = async () => {
    setSaving(true); setError(''); setMessage('')
    try {
      setForm(await updateCommercialSettings(form))
      setMessage('Configuración comercial guardada.')
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'No se pudo guardar.')
    } finally { setSaving(false) }
  }

  return <section className="page-section">
    <PageHeader eyebrow="ADMINISTRACIÓN" title="Configuración comercial" description="Define el IGV y los límites de descuento que se aplican a nuevas ventas y pedidos." />
    {loading && <StateMessage type="loading" title="Cargando configuración" />}
    {error && <StateMessage type="error" title="No se pudo completar" description={error} />}
    {message && <StateMessage type="success" title={message} />}
    {!loading && <div className="form-card sale-form">
      <label>IGV (%)<input type="number" min="0" max="100" step="0.01" value={form.tax_rate} onChange={(e) => setForm({...form, tax_rate: e.target.value})} /></label>
      <label>Descuento máximo (%)<input type="number" min="0" max="100" step="0.01" value={form.max_discount_percent} onChange={(e) => setForm({...form, max_discount_percent: e.target.value})} /></label>
      <label>Tratamiento del precio<select value={String(form.prices_include_tax)} onChange={(e) => setForm({...form, prices_include_tax: e.target.value === 'true'})}><option value="true">El precio ya incluye IGV</option><option value="false">Agregar IGV al precio</option></select></label>
      <button className="primary-button" disabled={saving} onClick={() => void save()}>{saving ? 'Guardando…' : 'Guardar configuración'}</button>
    </div>}
  </section>
}
