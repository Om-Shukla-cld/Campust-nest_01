import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { api } from '../utils/api'
import { useToast } from './Toast'
import { PropertyCard, PropertyDetail, Modal, Spinner, Empty } from './shared'
import RoomMap from './RoomMap'
import { useAuth } from '../App'

const TYPES = ['', 'PG', 'Hostel', 'Shared Room', '1BHK', '2BHK', 'Studio']
const SORTS = [['recommended', 'Recommended'], ['rent_asc', 'Rent ↑'], ['rent_desc', 'Rent ↓'], ['distance', 'Nearest'], ['rating', 'Top rated'], ['newest', 'Newest']]

/** Shared property search used by Student & Guest dashboards. */
export default function PropertyBrowser({ canReview }) {
  const toast = useToast()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [searchParams, setSearchParams] = useSearchParams()
  const [view, setViewState] = useState(searchParams.get('view') === 'map' ? 'map' : 'grid')  // grid | map
  const setView = (v) => { setViewState(v); setSearchParams(v === 'map' ? { view: 'map' } : {}) }
  const [paymentsEnabled, setPaymentsEnabled] = useState(false)
  const [filters, setFilters] = useState({ q: '', type: '', area: '', max_rent: '', amenities: '', sort: 'recommended' })
  const [areas, setAreas] = useState([])
  const [data, setData] = useState(null)
  const [open, setOpen] = useState(null)
  const [compare, setCompare] = useState([])

  useEffect(() => { api.propertyAreas().then(setAreas).catch(() => {}); api.paymentsStatus().then(s => setPaymentsEnabled(!!s.enabled)).catch(() => {}) }, [])
  useEffect(() => {
    const t = setTimeout(() => {
      api.searchProperties({ ...filters, page_size: 50 }).then(setData).catch(e => toast(e.message, 'error'))
    }, 250)
    return () => clearTimeout(t)
  }, [filters])

  const set = (k) => (e) => setFilters(f => ({ ...f, [k]: e.target.value }))
  const openDetail = (p) => api.getProperty(p.id).then(setOpen).catch(e => toast(e.message, 'error'))
  const toggleCompare = (p) => setCompare(c => c.includes(p.id) ? c.filter(x => x !== p.id) : c.length < 4 ? [...c, p.id] : (toast('Compare up to 4 properties', 'error'), c))
  const review = async (body) => {
    try { await api.submitReview(body); toast('Review submitted', 'success'); openDetail({ id: body.property_id }) }
    catch (e) { toast(e.message, 'error') }
  }

  return (
    <div className="space-y-4">
      <div className="card grid md:grid-cols-6 gap-3">
        <input className="input md:col-span-2" placeholder="🔍 Search name, area…" value={filters.q} onChange={set('q')} />
        <select className="input" value={filters.type} onChange={set('type')}>{TYPES.map(t => <option key={t} value={t}>{t || 'All types'}</option>)}</select>
        <select className="input" value={filters.area} onChange={set('area')}><option value="">All areas</option>{areas.map(a => <option key={a}>{a}</option>)}</select>
        <input className="input" type="number" placeholder="Max rent ₹" value={filters.max_rent} onChange={set('max_rent')} />
        <select className="input" value={filters.sort} onChange={set('sort')}>{SORTS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}</select>
        <input className="input md:col-span-3" placeholder="Amenities (comma separated: wifi, mess, ac)" value={filters.amenities} onChange={set('amenities')} />
        <div className="md:col-span-3 flex items-center justify-end gap-2 text-sm text-slate-500">
          {data && <span>{data.total} listings</span>}
          <div className="flex bg-slate-100 rounded-xl p-0.5">
            <button onClick={() => setView('grid')} className={`tab py-1 ${view === 'grid' ? 'tab-active' : ''}`}>▦ Grid</button>
            <button onClick={() => setView('map')} className={`tab py-1 ${view === 'map' ? 'tab-active' : ''}`}>🗺 Map</button>
          </div>
          {compare.length > 0 && <button className="btn-primary" onClick={() => navigate(`/compare?ids=${compare.join(',')}`)}>Compare {compare.length} →</button>}
        </div>
      </div>

      {view === 'map' ? (
        <RoomMap filters={{ type: filters.type, area: filters.area, max_rent: filters.max_rent, amenities: filters.amenities, q: filters.q }} onSelectProperty={openDetail} />
      ) : !data ? <Spinner /> : data.items.length === 0 ? <Empty>No properties match these filters.</Empty> : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.items.map(p => <PropertyCard key={p.id} p={p} onOpen={openDetail} selected={compare.includes(p.id)} onToggleCompare={toggleCompare} />)}
        </div>
      )}

      <Modal open={!!open} onClose={() => setOpen(null)} title={open?.name} wide>
        <PropertyDetail p={open} canReview={canReview} onReview={review} user={user} paymentsEnabled={paymentsEnabled}
          onPaid={(r) => { toast(`Slot #${r.slot_id} booked 🎉`, 'success'); openDetail({ id: open.id }) }} />
      </Modal>
    </div>
  )
}
