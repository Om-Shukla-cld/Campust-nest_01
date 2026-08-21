import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api } from '../utils/api'
import { useToast } from './Toast'
import { inr, Stars, Spinner, Empty } from './shared'

export default function CompareProperties() {
  const toast = useToast()
  const [params, setParams] = useSearchParams()
  const [all, setAll] = useState([])
  const [ids, setIds] = useState((params.get('ids') || '').split(',').filter(Boolean).map(Number))
  const [res, setRes] = useState(null)

  useEffect(() => { api.searchProperties({ page_size: 100 }).then(d => setAll(d.items)).catch(e => toast(e.message, 'error')) }, [])
  useEffect(() => {
    setParams(ids.length ? { ids: ids.join(',') } : {})
    if (ids.length >= 2) api.compareProperties(ids).then(setRes).catch(e => toast(e.message, 'error'))
    else setRes(null)
  }, [ids])

  const toggle = (id) => setIds(s => s.includes(id) ? s.filter(x => x !== id) : s.length < 4 ? [...s, id] : (toast('Max 4 properties', 'error'), s))
  const badge = (key, id, label) => res?.[key] === id && <span className="chip bg-emerald-100 text-emerald-700 mr-1">{label}</span>

  const rows = [
    ['Rent / month', p => inr(p.rent)], ['Deposit', p => inr(p.deposit)], ['Other charges', p => inr(p.other_price)],
    ['Total monthly', p => inr(p.rent + (p.other_price || 0))], ['Type · For', p => `${p.type} · ${p.gender}`], ['Area', p => p.area],
    ['Distance', p => `${p.distance_km} km`], ['Safety score', p => `🛡 ${p.safety_score}`], ['Rating', p => <Stars value={p.avg_rating} count={p.review_count} />],
    ['Free slots', p => `${p.available_slots}/${p.total_slots}`], ['Amenities', p => <div className="flex flex-wrap gap-1">{p.amenities.map(a => <span key={a} className={`chip ${res?.summary.common_amenities.includes(a) ? 'bg-brand-100 text-brand-700' : ''}`}>{a}</span>)}</div>],
    ['Owner', p => `${p.owner?.name}${p.owner?.is_verified ? ' ✅' : ''}`],
  ]

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-extrabold">Compare properties ⚖️</h1>
      <div className="card">
        <div className="label">Pick 2–4 listings</div>
        <div className="flex flex-wrap gap-2">
          {all.map(p => <button key={p.id} onClick={() => toggle(p.id)} className={`btn text-xs ${ids.includes(p.id) ? 'bg-brand-600 text-white' : 'bg-slate-100 text-slate-700'}`}>{p.name} · {inr(p.rent)}</button>)}
          {all.length === 0 && <Spinner />}
        </div>
      </div>
      {!res ? <Empty>Select at least two properties to compare.</Empty> : (
        <>
          <div className="grid sm:grid-cols-4 gap-3">
            {[['🏆 Best value', res.best_value_id], ['💸 Cheapest', res.cheapest_id], ['📍 Closest', res.closest_id], ['🛡 Safest', res.safest_id]].map(([l, id]) => (
              <div key={l} className="card py-3"><div className="label">{l}</div><div className="font-bold">{res.properties.find(p => p.id === id)?.name}</div></div>
            ))}
          </div>
          <div className="card p-0 overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="bg-slate-50"><th className="p-3 text-left text-xs uppercase text-slate-500 w-40">Criteria</th>
                {res.properties.map(p => <th key={p.id} className="p-3 text-left align-top"><div className="font-bold">{p.name}</div><div className="mt-1">{badge('best_value_id', p.id, '🏆 best value')}{badge('cheapest_id', p.id, '💸')}{badge('closest_id', p.id, '📍')}{badge('safest_id', p.id, '🛡')}{badge('top_rated_id', p.id, '⭐')}</div></th>)}</tr></thead>
              <tbody>{rows.map(([label, fn]) => <tr key={label} className="border-t border-slate-100"><td className="p-3 text-slate-500">{label}</td>{res.properties.map(p => <td key={p.id} className="p-3">{fn(p)}</td>)}</tr>)}</tbody>
            </table>
          </div>
          <p className="text-xs text-slate-500">Average rent of selection: {inr(res.summary.avg_rent)} · Range {inr(res.summary.rent_range[0])}–{inr(res.summary.rent_range[1])} · Common amenities: {res.summary.common_amenities.join(', ') || 'none'}</p>
        </>
      )}
    </div>
  )
}
