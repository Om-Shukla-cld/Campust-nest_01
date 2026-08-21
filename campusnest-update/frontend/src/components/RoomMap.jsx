import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import { api } from '../utils/api'

// Leaflet's default marker icons don't bundle correctly with Vite — point at CDN assets instead
const defaultIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

const campusIcon = L.divIcon({
  className: '',
  html: '<div style="font-size:26px;line-height:1;filter:drop-shadow(0 1px 2px rgba(0,0,0,.4))">🎓</div>',
  iconSize: [26, 26],
  iconAnchor: [13, 26],
})

function BoundsWatcher({ onBoundsChange }) {
  const map = useMapEvents({
    moveend: () => {
      const b = map.getBounds()
      onBoundsChange({ minLat: b.getSouth(), maxLat: b.getNorth(), minLng: b.getWest(), maxLng: b.getEast() })
    },
  })
  useEffect(() => {
    const b = map.getBounds()
    onBoundsChange({ minLat: b.getSouth(), maxLat: b.getNorth(), minLng: b.getWest(), maxLng: b.getEast() })
  }, [])
  return null
}

/**
 * OpenStreetMap view of approved listings. Fetches only the pins inside the
 * current viewport (bounding-box query on GET /properties).
 */
export default function RoomMap({ center = [23.0776, 76.8516], zoom = 13, onSelectProperty, filters = {}, height = '70vh' }) {
  // default center: VIT Bhopal (matches the seeded demo data) — change to your campus
  const [properties, setProperties] = useState([])
  const [bounds, setBounds] = useState(null)

  async function load(b) {
    try {
      const data = await api.listProperties(b, filters)
      setProperties(data.filter(p => p.lat != null && p.lng != null))
    } catch (e) {
      console.error('Failed to load properties', e)
    }
  }
  useEffect(() => { if (bounds) load(bounds) }, [JSON.stringify(filters)])

  return (
    <div className="w-full rounded-2xl overflow-hidden border border-slate-100 shadow-sm relative" style={{ height }}>
      <MapContainer center={center} zoom={zoom} style={{ height: '100%', width: '100%' }} scrollWheelZoom>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <BoundsWatcher onBoundsChange={(b) => { setBounds(b); load(b) }} />
        <Marker position={center} icon={campusIcon}><Popup>Campus</Popup></Marker>
        {properties.map((p) => (
          <Marker key={p.id} position={[p.lat, p.lng]} icon={defaultIcon}>
            <Popup>
              <div className="text-sm min-w-[160px]">
                <p className="font-semibold">{p.name}</p>
                <p>{p.type} · ₹{p.rent}/mo · ★ {p.avg_rating || '—'}</p>
                <p className="text-xs text-slate-500">{p.area} · {p.distance_km} km · {p.available_slots} slots free</p>
                <button className="text-brand-600 underline mt-1 font-medium" onClick={() => onSelectProperty?.(p)}>
                  View details
                </button>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
      <div className="absolute bottom-3 left-3 z-[1000] chip bg-white/90 shadow">{properties.length} listings in view</div>
    </div>
  )
}
