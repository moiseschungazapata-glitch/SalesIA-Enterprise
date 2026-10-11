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
import { accessColor, accessDisplayName } from '../utils/accessIdentity'
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
        <span>La ubicación aproximada aparecerá cuando alguien abra el enlace público.</span>
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
        const precise = item.location_source === 'device_location'
        const markerColor = accessColor(item)
        return (
          <Fragment key={item.id}>
            <Circle
              center={center}
              radius={precise ? Math.max(item.accuracy_m ?? 30, 15) : 5000}
              pathOptions={{ color: selected ? '#f59e0b' : markerColor, fillColor: markerColor, fillOpacity: precise ? 0.16 : 0.025, weight: selected ? 3 : 1, dashArray: precise ? undefined : '6 7' }}
            />
            <CircleMarker
              center={center}
              radius={selected ? 11 : 8}
              eventHandlers={{ click: () => onSelect(item) }}
              pathOptions={{ color: selected ? '#f59e0b' : '#fff', fillColor: markerColor, fillOpacity: 1, weight: selected ? 4 : 3 }}
            >
              <Popup>
                <strong>{accessDisplayName(item)}</strong><br />
                {item.city || item.region || 'Zona no identificada'}<br />
                <small>{precise ? `${item.is_anonymous ? 'Visita anónima precisa' : 'Ubicación del dispositivo'} · ± ${Math.round(item.accuracy_m ?? 0)} m` : item.is_anonymous ? 'Visita anónima · estimación por IP' : 'Estimación por IP pública'}</small>
              </Popup>
            </CircleMarker>
          </Fragment>
        )
      })}
    </MapContainer>
  )
}

export default AccessMap
