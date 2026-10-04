import { useMemo, useState } from 'react'
import type { UserRole } from '../../app/navigation'
import FormModal from '../../components/FormModal'
import PageHeader from '../../components/PageHeader'
import StateMessage from '../../components/StateMessage'
import { useInventory, useInventoryMovements } from '../../hooks/useOperations'
import { createInventoryMovement } from '../../services/operations'
import type { ManualInventoryMovementType } from '../../types/api'

interface InventoryProps {
  role: UserRole
}

const movementLabels: Record<string, string> = {
  initial: 'Stock inicial',
  entry: 'Entrada',
  adjustment_in: 'Ajuste de entrada',
  adjustment_out: 'Ajuste de salida',
  sale: 'Venta',
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('es-PE', {
    dateStyle: 'short', timeStyle: 'short',
  }).format(new Date(value))
}

function Inventory({ role }: InventoryProps) {
  const canManage = role === 'administrator'
  const canAudit = role !== 'seller'
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<'active' | 'inactive' | ''>('')
  const [showForm, setShowForm] = useState(false)
  const [productId, setProductId] = useState('')
  const [movementType, setMovementType] =
    useState<ManualInventoryMovementType>('entry')
  const [quantity, setQuantity] = useState('1')
  const [reason, setReason] = useState('')
  const [saving, setSaving] = useState(false)
  const [feedback, setFeedback] = useState('')
  const [formError, setFormError] = useState('')

  const inventory = useInventory({
    page: 1, pageSize: 100, search, status,
  })
  const movements = useInventoryMovements(canAudit)
  const items = inventory.data.items
  const totalUnits = useMemo(
    () => items.reduce((sum, item) => sum + item.stock, 0), [items],
  )
  const outOfStock = items.filter((item) => item.stock === 0).length

  const handleMovement = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setFormError('')
    setFeedback('')
    const parsedQuantity = Number(quantity)
    if (!productId || !reason.trim() || parsedQuantity < 1) {
      setFormError('Completa producto, cantidad y motivo.')
      return
    }
    setSaving(true)
    try {
      const created = await createInventoryMovement({
        product_id: Number(productId),
        movement_type: movementType,
        quantity: parsedQuantity,
        reason: reason.trim(),
      })
      setFeedback(`Movimiento guardado. Nuevo stock: ${created.stock_after}.`)
      setProductId('')
      setMovementType('entry')
      setQuantity('1')
      setReason('')
      setShowForm(false)
      inventory.reload()
      movements.reload()
    } catch (error) {
      setFormError(
        error instanceof Error ? error.message : 'No se pudo guardar el movimiento.',
      )
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="page">
      <PageHeader
        eyebrow="CONTROL OPERATIVO"
        title="Inventario"
        description="Existencias reales y trazabilidad de cada cambio de stock."
        action={canManage ? (
          <button
            type="button"
            className="primary-button compact"
            onClick={() => {
              setShowForm(true)
              setFormError('')
            }}
          >
            + Movimiento
          </button>
        ) : undefined}
      />

      <section className="kpi-grid compact-grid">
        <article className="mini-stat"><span>Unidades disponibles</span><strong>{totalUnits}</strong></article>
        <article className="mini-stat"><span>Productos registrados</span><strong>{inventory.data.total}</strong></article>
        <article className="mini-stat"><span>Productos agotados</span><strong>{outOfStock}</strong></article>
        <article className="mini-stat"><span>Movimientos visibles</span><strong>{canAudit ? movements.data.total : '—'}</strong></article>
      </section>

      {feedback && (
        <StateMessage type="success" title="Inventario actualizado" description={feedback} />
      )}

      {canManage && showForm && (
        <FormModal
          eyebrow="MOVIMIENTO AUTORIZADO"
          title="Registrar movimiento"
          description="La cantidad siempre es positiva; el tipo define si suma o resta."
          onClose={() => setShowForm(false)}
          closeDisabled={saving}
        >
          {formError && (
            <StateMessage type="error" title="No se pudo guardar" description={formError} />
          )}
          <form className="entity-form" onSubmit={handleMovement}>
            <label>
              Producto
              <select value={productId} onChange={(event) => setProductId(event.target.value)}>
                <option value="">Seleccionar producto</option>
                {items.filter((item) => item.active).map((item) => (
                  <option key={item.product_id} value={item.product_id}>
                    {item.sku} · {item.product_name} · Stock {item.stock}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Tipo
              <select
                value={movementType}
                onChange={(event) => setMovementType(
                  event.target.value as ManualInventoryMovementType,
                )}
              >
                <option value="initial">Stock inicial</option>
                <option value="entry">Entrada</option>
                <option value="adjustment_in">Ajuste de entrada</option>
                <option value="adjustment_out">Ajuste de salida</option>
              </select>
            </label>
            <label>
              Cantidad
              <input type="number" min="1" value={quantity} onChange={(event) => setQuantity(event.target.value)} />
            </label>
            <label>
              Motivo
              <input value={reason} maxLength={500} onChange={(event) => setReason(event.target.value)} placeholder="Ej. Reposición de mercadería" />
            </label>
            <div className="form-actions">
              <button type="button" className="secondary-button" onClick={() => setShowForm(false)}>Cancelar</button>
              <button type="submit" className="primary-button" disabled={saving}>{saving ? 'Guardando...' : 'Guardar movimiento'}</button>
            </div>
          </form>
        </FormModal>
      )}

      <section className="panel">
        <div className="panel-toolbar">
          <input className="search-input" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar por SKU, producto o categoría..." />
          <select className="select-input" value={status} onChange={(event) => setStatus(event.target.value as typeof status)}>
            <option value="">Todos los estados</option>
            <option value="active">Activos</option>
            <option value="inactive">Inactivos</option>
          </select>
        </div>
        {inventory.loading ? (
          <StateMessage type="loading" title="Cargando inventario" />
        ) : inventory.error ? (
          <StateMessage type="error" title="No se pudo cargar" description={inventory.error} actionLabel="Reintentar" onAction={inventory.reload} />
        ) : (
          <div className="table-wrapper">
            <table>
              <thead><tr><th>Producto</th><th>Categoría</th><th>Stock</th><th>Actualizado</th><th>Estado</th></tr></thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.product_id}>
                    <td><strong>{item.product_name}</strong><br /><span className="muted-text">{item.sku}</span></td>
                    <td>{item.category_name}</td>
                    <td><strong className={item.stock === 0 ? 'danger-text' : ''}>{item.stock}</strong></td>
                    <td>{formatDate(item.updated_at)}</td>
                    <td><span className={`status-pill ${item.active ? 'success' : 'danger'}`}>{item.active ? 'Activo' : 'Inactivo'}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
            {items.length === 0 && <div className="empty-state">No hay productos para mostrar.</div>}
          </div>
        )}
      </section>

      {canAudit && (
        <section className="panel">
          <div className="panel-header"><div><span className="eyebrow">TRAZABILIDAD</span><h2>Historial de movimientos</h2><p>Incluye ajustes manuales y salidas automáticas por venta.</p></div></div>
          {movements.loading ? (
            <StateMessage type="loading" title="Cargando movimientos" />
          ) : movements.error ? (
            <StateMessage type="error" title="No se pudo cargar" description={movements.error} actionLabel="Reintentar" onAction={movements.reload} />
          ) : (
            <div className="table-wrapper">
              <table>
                <thead><tr><th>Fecha</th><th>Producto</th><th>Tipo</th><th>Cantidad</th><th>Stock</th><th>Usuario</th><th>Referencia</th></tr></thead>
                <tbody>
                  {movements.data.items.map((movement) => (
                    <tr key={movement.id}>
                      <td>{formatDate(movement.created_at)}</td>
                      <td><strong>{movement.product_name}</strong><br /><span className="muted-text">{movement.sku}</span></td>
                      <td>{movementLabels[movement.movement_type]}</td>
                      <td className={['adjustment_out', 'sale'].includes(movement.movement_type) ? 'danger-text' : 'success-text'}>{['adjustment_out', 'sale'].includes(movement.movement_type) ? '−' : '+'}{movement.quantity}</td>
                      <td>{movement.stock_before} → {movement.stock_after}</td>
                      <td>{movement.user_name}</td>
                      <td>{movement.sale_number ?? movement.reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {movements.data.items.length === 0 && <div className="empty-state">Todavía no hay movimientos registrados.</div>}
            </div>
          )}
        </section>
      )}
    </div>
  )
}

export default Inventory
