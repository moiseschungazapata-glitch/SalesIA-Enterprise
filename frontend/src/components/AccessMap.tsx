import { Fragment, useEffect } from 'react'
import {
  Circle,
  CircleMarker,
  MapContainer,
  Popup,
  TileLayer,
  useMap,
} from 'react-leaflet'
import type { LatLngBoundsExpression } from 'leaflet'
import type { AccessLocation } from '../types/api'
import 'leaflet/dist/leaflet.css'

interface AccessMapProps {
  items: AccessLocation[]
  selectedId: number | null
  onSelect: (item: AccessLocation) => void
}

function FitAccesses({ items }: { items: AccessLocation[] }) {
  const map = useMap()
  useEffect(() => {
    const bounds = items
      .filter((item) => item.latitude !== null && item.longitude !== null)
      .map((item) => [item.latitude!, item.longitude!] as [number, number])
    if (bounds.length === 1) map.setView(bounds[0], 11)
    else if (bounds.length > 1) map.fitBounds(bounds as LatLngBoundsExpression, { padding: [32, 32] })
  }, [items, map])
  return null
}

function AccessMap({ items, selectedId, onSelect }: AccessMapProps) {
  const located = items.filter(
    (item) => item.latitude !== null && item.longitude !== null,
  )

  if (located.length === 0) {
    return (
      <div className="access-map-empty">
        <strong>Aún no hay accesos ubicados</strong>
        <span>La ubicación aproximada aparecerá después del próximo inicio de sesión.</span>
      </div>
    )
  }

  return (
    <MapContainer
      className="access-map-canvas"
      center={[-12.0464, -77.0428]}
      zoom={10}
      scrollWheelZoom
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <FitAccesses items={located} />
      {located.map((item) => {
        const center: [number, number] = [item.latitude!, item.longitude!]
        const selected = item.id === selectedId
        return (
          <Fragment key={item.id}>
            <Circle
              center={center}
              radius={12000}
              pathOptions={{ color: selected ? '#f59e0b' : '#0ea5e9', fillOpacity: 0.08, weight: 1 }}
            />
            <CircleMarker
              center={center}
              radius={selected ? 11 : 8}
              eventHandlers={{ click: () => onSelect(item) }}
              pathOptions={{ color: '#fff', fillColor: selected ? '#f59e0b' : '#087cf0', fillOpacity: 1, weight: 3 }}
            >
              <Popup>
                <strong>{item.user_name}</strong><br />
                {item.city || item.region || 'Zona no identificada'}<br />
                <small>Estimación por IP pública</small>
              </Popup>
            </CircleMarker>
          </Fragment>
        )
      })}
    </MapContainer>
  )
}

export default AccessMap
