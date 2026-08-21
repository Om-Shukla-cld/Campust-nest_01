import { useEffect, useState } from 'react'
import { api } from '../utils/api'
import { useToast } from './Toast'
import { Spinner, Empty, Stars } from './shared'

const ICON = { tiffin: '🍱', laundry: '🧺', medical: '🏥', repair: '🔧', mess: '🍛', stationery: '📚', grocery: '🛒', transport: '🚖', fitness: '🏋️' }

export default function GetServices() {
  const toast = useToast()
  const [cats, setCats] = useState([])
  const [cat, setCat] = useState('')
  const [q, setQ] = useState('')
  const [items, setItems] = useState(null)
  useEffect(() => { api.serviceCategories().then(setCats) }, [])
  useEffect(() => { const t = setTimeout(() => api.getServices({ category: cat, q }).then(setItems).catch(e => toast(e.message, 'error')), 200); return () => clearTimeout(t) }, [cat, q])
  return (
    <div className="space-y-4">
      <div><h1 className="text-2xl font-extrabold">Local services 🛠️</h1><p className="text-sm text-slate-500">Verified services near campus — tiffin, laundry, doctors, repairs and more.</p></div>
      <div className="card flex flex-wrap gap-2 items-center">
        <input className="input max-w-xs" placeholder="🔍 Search services" value={q} onChange={e => setQ(e.target.value)} />
        <button onClick={() => setCat('')} className={`btn text-xs ${!cat ? 'bg-brand-600 text-white' : 'bg-slate-100'}`}>All</button>
        {cats.map(c => <button key={c.category} onClick={() => setCat(c.category)} className={`btn text-xs capitalize ${cat === c.category ? 'bg-brand-600 text-white' : 'bg-slate-100'}`}>{ICON[c.category] || '•'} {c.category} ({c.count})</button>)}
      </div>
      {!items ? <Spinner /> : items.length === 0 ? <Empty>No services found.</Empty> : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">{items.map(s => (
          <div key={s.id} className="card flex gap-3">
            <div className="text-3xl">{ICON[s.category] || '•'}</div>
            <div className="flex-1">
              <div className="flex justify-between items-start"><div className="font-bold">{s.name}</div>{s.is_verified && <span className="chip bg-emerald-100 text-emerald-700">✓</span>}</div>
              <div className="text-xs text-slate-500 capitalize">{s.category} · {s.area}</div>
              <p className="text-sm text-slate-600 mt-1">{s.description}</p>
              <div className="flex items-center justify-between mt-2 text-xs"><Stars value={s.rating} /><span className="text-slate-500">{s.price_range}</span></div>
              <div className="text-xs text-slate-500 mt-1">🕒 {s.open_hours}</div>
              <a href={`tel:${s.phone}`} className="btn-ghost w-full mt-2 py-1">📞 {s.phone}</a>
            </div>
          </div>))}</div>
      )}
    </div>
  )
}
