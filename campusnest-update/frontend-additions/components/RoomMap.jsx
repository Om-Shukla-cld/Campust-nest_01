import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap, useMapEvents } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import { api } from '../lib/api'

// Leaflet's default marker icons don't bundle correctly with Vite — point at CDN assets instead
const defaultIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
})

function BoundsWatcher({ onBoundsChange }) {
  const map = useMapEvents({
    moveend: () => {
      const b = map.getBounds()
      onBoundsChange({
        minLat: b.getSouth(), maxLat: b.getNorth(),
        minLng: b.getWest(), maxLng: b.getEast(),
      })
    },
  })
  useEffect(() => {
    const b = map.getBounds()
    onBoundsChange({
      minLat: b.getSouth(), maxLat: b.getNorth(),
      minLng: b.getWest(), maxLng: b.getEast(),
    })
  }, [])
  return null
}

export default function RoomMap({ center = [23.0776, 76.8516], onSelectProperty }) {
  // default center: VIT Bhopal (matches the seeded demo data) — change to your campus
  const [properties, setProperties] = useState([])

  async function loadForBounds(bounds) {
    try {
      const data = await api.listProperties(bounds)
      setProperties(data)
    } catch (e) {
      console.error('Failed to load properties', e)
    }
  }

  return (
    <div className="w-full h-[70vh] rounded-2xl overflow-hidden">
      <MapContainer center={center} zoom={13} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <BoundsWatcher onBoundsChange={loadForBounds} />

        {properties.map((p) => (
          <Marker key={p.id} position={[p.lat, p.lng]} icon={defaultIcon}>
            <Popup>
              <div className="text-sm">
                <p className="font-semibold">{p.name}</p>
                <p>{p.type} · ₹{p.rent}/mo</p>
                <button
                  className="text-blue-600 underline mt-1"
                  onClick={() => onSelectProperty?.(p)}
                >
                  View details
                </button>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  )
}
