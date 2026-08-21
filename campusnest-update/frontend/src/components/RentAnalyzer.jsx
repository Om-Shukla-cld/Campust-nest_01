import { useEffect, useState } from 'react'
import { api } from '../utils/api'
import { useToast } from './Toast'
import { inr, Spinner, StatCard } from './shared'

function TrendChart({ series }) {
  if (!series?.points?.length) return null
  const pts = series.points, W = 520, H = 160, pad = 28
  const ys = pts.map(p => p.avg_rent), min = Math.min(...ys) * 0.97, max = Math.max(...ys) * 1.03
  const x = i => pad + (i / (pts.length - 1)) * (W - pad * 2), y = v => H - pad - ((v - min) / (max - min || 1)) * (H - pad * 2)
  const d = pts.map((p, i) => `${i ? 'L' : 'M'}${x(i)},${y(p.avg_rent)}`).join(' ')
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-44">
      <path d={`${d} L${x(pts.length - 1)},${H - pad} L${x(0)},${H - pad} Z`} fill="#f59e0b" opacity="0.1" />
      <path d={d} fill="none" stroke="#d97706" strokeWidth="2.5" />
      {pts.map((p, i) => <g key={p.month}><circle cx={x(i)} cy={y(p.avg_rent)} r="3.5" fill="#d97706" /><text x={x(i)} y={H - 8} fontSize="10" textAnchor="middle" fill="#64748b">{p.month.slice(2)}</text><text x={x(i)} y={y(p.avg_rent) - 8} fontSize="9" textAnchor="middle" fill="#334155">{p.avg_rent}</text></g>)}
    </svg>
  )
}

export default function RentAnalyzer() {
  const toast = useToast()
  const [areas, setAreas] = useState([])
  const [summary, setSummary] = useState(null)
  const [area, setArea] = useState('Kothri Kalan')
  const [type, setType] = useState('PG')
  const [trends, setTrends] = useState(null)
  const [rent, setRent] = useState(7000)
  const [analysis, setAnalysis] = useState(null)

  useEffect(() => { api.propertyAreas().then(setAreas); api.areaSummary().then(setSummary) }, [])
  useEffect(() => { api.rentTrends(area, type, 12).then(setTrends).catch(e => toast(e.message, 'error')) }, [area, type])
  const analyze = (e) => { e?.preventDefault(); api.analyzeRent(rent, area, type).then(setAnalysis).catch(e => toast(e.message, 'error')) }
  useEffect(() => { analyze() }, [area, type])

  const verdictColor = { 'great deal': 'green', fair: 'brand', 'slightly high': 'amber', overpriced: 'rose', unknown: 'brand' }
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-extrabold">Rent Analyzer 📊</h1>
      <div className="card flex flex-wrap gap-3 items-end">
        <div><label className="label">Area</label><select className="input" value={area} onChange={e => setArea(e.target.value)}>{[...new Set([area, ...areas])].map(a => <option key={a}>{a}</option>)}</select></div>
        <div><label className="label">Type</label><select className="input" value={type} onChange={e => setType(e.target.value)}>{['PG', 'Hostel', 'Shared Room', '1BHK', '2BHK', 'Studio'].map(t => <option key={t}>{t}</option>)}</select></div>
        <form onSubmit={analyze} className="flex gap-2 items-end"><div><label className="label">Quoted rent ₹</label><input className="input w-36" type="number" value={rent} onChange={e => setRent(+e.target.value)} /></div><button className="btn-primary">Is it fair?</button></form>
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="card lg:col-span-2">
          <div className="flex justify-between items-center"><div className="font-bold">{area} · {type} — 12-month trend</div>{trends?.[0] && <span className={`chip ${trends[0].change_pct > 0 ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700'}`}>{trends[0].change_pct > 0 ? '▲' : '▼'} {Math.abs(trends[0].change_pct)}%</span>}</div>
          {!trends ? <Spinner /> : trends.length ? <TrendChart series={trends[0]} /> : <div className="py-10 text-center text-slate-400 text-sm">No trend data for this combination.</div>}
        </div>
        <div className="card space-y-3">
          <div className="font-bold">Verdict</div>
          {!analysis ? <Spinner /> : (
            <>
              <StatCard label={`₹${rent} is`} value={analysis.verdict} accent={verdictColor[analysis.verdict]} />
              {analysis.market_avg && <div className="text-sm text-slate-600">Market average: <b>{inr(analysis.market_avg)}</b> ({analysis.diff_pct > 0 ? '+' : ''}{analysis.diff_pct}%) · cheaper than {100 - analysis.percentile}% of listings</div>}
              <div className="text-sm bg-brand-50 text-brand-800 rounded-xl p-3">💡 {analysis.suggestion}</div>
            </>
          )}
        </div>
      </div>

      <div>
        <h2 className="font-bold mb-2">Live market snapshot (approved listings)</h2>
        {!summary ? <Spinner /> : (
          <div className="grid sm:grid-cols-3 gap-3">{summary.map(s => (
            <button key={s.area} onClick={() => setArea(s.area)} className={`card text-left hover:shadow-md ${s.area === area ? 'ring-2 ring-brand-500' : ''}`}>
              <div className="font-bold">{s.area}</div>
              <div className="text-2xl font-extrabold text-brand-700">{inr(s.avg_rent)}<span className="text-xs text-slate-400">/mo avg</span></div>
              <div className="text-xs text-slate-500">{inr(s.min_rent)} – {inr(s.max_rent)} · {s.listings} listings · 🛡 {s.avg_safety}</div>
            </button>))}</div>
        )}
      </div>
    </div>
  )
}
