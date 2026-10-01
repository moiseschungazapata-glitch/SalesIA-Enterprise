import { useMemo, useState } from 'react'
import PageHeader from '../../components/PageHeader'
import {
  inventory as initialInventory,
} from '../../services/mockData'
import type { InventoryItem } from '../../types'

type MovementType = 'Entrada' | 'Salida'

function Inventory() {
  const [inventoryList, setInventoryList] =
    useState<InventoryItem[]>(initialInventory)

  const [search, setSearch] = useState('')
  const [showMovementForm, setShowMovementForm] =
    useState(false)

  const [selectedProduct, setSelectedProduct] =
    useState('')

  const [movementType, setMovementType] =
    useState<MovementType>('Entrada')

  const [quantity, setQuantity] = useState('1')

  const filteredInventory = useMemo(() => {
    return inventoryList.filter(
      (item) =>
        item.product
          .toLowerCase()
          .includes(search.toLowerCase()) ||
        item.category
          .toLowerCase()
          .includes(search.toLowerCase()),
    )
  }, [inventoryList, search])

  const criticalProducts = inventoryList.filter(
    (item) => item.stock <= item.minimum,
  )

  const totalUnits = inventoryList.reduce(
    (sum, item) => sum + item.stock,
    0,
  )

  const handleMovement = (
    event: React.FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()

    const amount = Number(quantity)

    if (
      !selectedProduct ||
      amount <= 0
    ) {
      return
    }

    const productId = Number(selectedProduct)

    const currentProduct = inventoryList.find(
      (item) => item.id === productId,
    )

    if (!currentProduct) {
      return
    }

    if (
      movementType === 'Salida' &&
      amount > currentProduct.stock
    ) {
      return
    }

    const newStock =
      movementType === 'Entrada'
        ? currentProduct.stock + amount
        : currentProduct.stock - amount

    const movementLabel =
      movementType === 'Entrada'
        ? `+${amount}`
        : `-${amount}`

    setInventoryList((current) =>
      current.map((item) =>
        item.id === productId
          ? {
              ...item,
              stock: newStock,
              movement: movementLabel,
              updated: 'Ahora',
            }
          : item,
      ),
    )

    setSelectedProduct('')
    setMovementType('Entrada')
    setQuantity('1')
    setShowMovementForm(false)
  }

  return (
    <div className="page">
      <PageHeader
        eyebrow="CONTROL OPERATIVO"
        title="Inventario"
        description="Seguimiento del stock y movimientos de productos."
        action={
          <button
            type="button"
            className="primary-button compact"
            onClick={() =>
              setShowMovementForm(
                (value) => !value,
              )
            }
          >
            {showMovementForm
              ? 'Cerrar'
              : '+ Movimiento'}
          </button>
        }
      />

      <section className="kpi-grid compact-grid">
        <article className="mini-stat">
          <span>Unidades disponibles</span>
          <strong>{totalUnits}</strong>
        </article>

        <article className="mini-stat">
          <span>Productos críticos</span>
          <strong>
            {criticalProducts.length}
          </strong>
        </article>

        <article className="mini-stat">
          <span>Productos agotados</span>
          <strong>
            {
              inventoryList.filter(
                (item) => item.stock === 0,
              ).length
            }
          </strong>
        </article>

        <article className="mini-stat">
          <span>Movimientos visibles</span>
          <strong>
            {inventoryList.length}
          </strong>
        </article>
      </section>

      {showMovementForm && (
        <section className="panel form-panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">
                MOVIMIENTO DE INVENTARIO
              </span>

              <h2>
                Registrar movimiento
              </h2>

              <p>
                Actualiza temporalmente el stock del
                producto.
              </p>
            </div>
          </div>

          <form
            className="entity-form"
            onSubmit={handleMovement}
          >
            <label>
              Producto
              <select
                value={selectedProduct}
                onChange={(event) =>
                  setSelectedProduct(
                    event.target.value,
                  )
                }
              >
                <option value="">
                  Seleccionar producto
                </option>

                {inventoryList.map((item) => (
                  <option
                    key={item.id}
                    value={item.id}
                  >
                    {item.product} · Stock {item.stock}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Tipo de movimiento
              <select
                value={movementType}
                onChange={(event) =>
                  setMovementType(
                    event.target.value as MovementType,
                  )
                }
              >
                <option value="Entrada">
                  Entrada
                </option>

                <option value="Salida">
                  Salida
                </option>
              </select>
            </label>

            <label>
              Cantidad
              <input
                type="number"
                min="1"
                value={quantity}
                onChange={(event) =>
                  setQuantity(
                    event.target.value,
                  )
                }
              />
            </label>

            <div className="form-actions">
              <button
                type="button"
                className="secondary-button"
                onClick={() =>
                  setShowMovementForm(false)
                }
              >
                Cancelar
              </button>

              <button
                type="submit"
                className="primary-button"
              >
                Guardar movimiento
              </button>
            </div>
          </form>
        </section>
      )}

      <section className="panel">
        <div className="panel-toolbar">
          <input
            className="search-input"
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
            placeholder="Buscar producto o categoría..."
          />

          <select className="select-input">
            <option>Todos los estados</option>
            <option>Normal</option>
            <option>Revisar</option>
          </select>
        </div>

        <div className="results-info">
          Mostrando {filteredInventory.length} de{' '}
          {inventoryList.length} productos
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Producto</th>
                <th>Categoría</th>
                <th>Stock actual</th>
                <th>Mínimo</th>
                <th>Movimiento</th>
                <th>Actualizado</th>
                <th>Estado</th>
              </tr>
            </thead>

            <tbody>
              {filteredInventory.map((item) => {
                const critical =
                  item.stock <= item.minimum

                return (
                  <tr key={item.id}>
                    <td>
                      <strong>
                        {item.product}
                      </strong>
                    </td>

                    <td>{item.category}</td>

                    <td>
                      <strong
                        className={
                          item.stock === 0
                            ? 'danger-text'
                            : critical
                              ? 'warning-text'
                              : ''
                        }
                      >
                        {item.stock}
                      </strong>
                    </td>

                    <td>{item.minimum}</td>

                    <td
                      className={
                        item.movement.startsWith('+')
                          ? 'success-text'
                          : 'danger-text'
                      }
                    >
                      {item.movement}
                    </td>

                    <td>{item.updated}</td>

                    <td>
                      <span
                        className={`status-pill ${
                          critical
                            ? item.stock === 0
                              ? 'danger'
                              : 'warning'
                            : 'success'
                        }`}
                      >
                        {critical
                          ? item.stock === 0
                            ? 'Agotado'
                            : 'Revisar'
                          : 'Normal'}
                      </span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>

          {filteredInventory.length === 0 && (
            <div className="empty-state">
              No se encontraron productos.
            </div>
          )}
        </div>
      </section>

      <section className="dashboard-grid">
        <article className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">
                ALERTAS
              </span>

              <h2>Stock crítico</h2>

              <p>
                Productos que requieren atención.
              </p>
            </div>
          </div>

          <div className="list">
            {criticalProducts.map((item) => (
              <div
                className="list-row"
                key={item.id}
              >
                <div>
                  <strong>
                    {item.product}
                  </strong>

                  <span>
                    Mínimo: {item.minimum} unidades
                  </span>
                </div>

                <strong className="danger-text">
                  {item.stock} uds.
                </strong>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">
                CONTROL
              </span>

              <h2>Estado del inventario</h2>

              <p>
                Resumen de disponibilidad actual.
              </p>
            </div>
          </div>

          <div className="inventory-health">
            <div>
              <span>Productos normales</span>
              <strong>
                {
                  inventoryList.filter(
                    (item) =>
                      item.stock > item.minimum,
                  ).length
                }
              </strong>
            </div>

            <div>
              <span>Requieren revisión</span>
              <strong>
                {criticalProducts.length}
              </strong>
            </div>

            <div>
              <span>Unidades totales</span>
              <strong>{totalUnits}</strong>
            </div>
          </div>
        </article>
      </section>
    </div>
  )
}

export default Inventory
