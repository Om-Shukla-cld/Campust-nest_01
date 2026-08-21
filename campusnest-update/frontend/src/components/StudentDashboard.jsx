import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../utils/api'
import { useAuth } from '../App'
import { useToast } from './Toast'
import PropertyBrowser from './PropertyBrowser'
import { Spinner, Empty, Modal } from './shared'
import ProfileBuilder from './ProfileBuilder'

function Roommates() {
  const toast = useToast()
  const [matches, setMatches] = useState(null)
  const [view, setView] = useState(null)
  const load = () => api.roommateMatches().then(setMatches).catch(e => toast(e.message, 'error'))
  useEffect(() => { load() }, [])
  if (!matches) return <Spinner />
  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {matches.length === 0 && <Empty>No matches yet — fill in your profile.</Empty>}
      {matches.map(m => (
        <div key={m.user.id} className="card flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <div><div className="font-bold">{m.user.name}</div><div className="text-xs text-slate-500">{m.user.reg_no} · budget ₹{m.user.budget}</div></div>
            <div className={`text-2xl font-extrabold ${m.score >= 75 ? 'text-emerald-600' : m.score >= 50 ? 'text-amber-600' : 'text-rose-600'}`}>{m.score}%</div>
          </div>
          <div className="h-2 rounded-full bg-slate-100"><div className="h-2 rounded-full bg-brand-500" style={{ width: `${m.score}%` }} /></div>
          <p className="text-xs text-slate-600 line-clamp-2">{m.user.about_me}</p>
          <div className="flex flex-wrap gap-1">
            {m.matched_on.map(f => <span key={f} className="chip bg-emerald-100 text-emerald-700">✓ {f}</span>)}
            {m.differs_on.map(f => <span key={f} className="chip bg-rose-50 text-rose-600">✗ {f}</span>)}
          </div>
          <button className="btn-ghost mt-auto" onClick={() => setView(m.user)}>View profile</button>
        </div>
      ))}
      <Modal open={!!view} onClose={() => setView(null)} title={view?.name}>
        {view && (
          <div className="space-y-2 text-sm">
            <p className="text-slate-600">{view.about_me}</p>
            <div className="grid grid-cols-2 gap-2">
              {['veg', 'smoker', 'sleep', 'cleanliness', 'study', 'budget'].map(k => <div key={k} className="bg-slate-50 rounded-xl p-2"><div className="label">{k}</div><div className="font-semibold">{view[k] ?? '—'}</div></div>)}
            </div>
            <div className="text-slate-500">📞 {view.phone || 'hidden'} · ✉️ {view.email || '—'}</div>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default function StudentDashboard() {
  const { user } = useAuth()
  const [tab, setTab] = useState('browse')
  const tabs = [['browse', '🔍 Browse'], ['roommates', '🤝 Roommates'], ['profile', '👤 My profile']]
  return (
    <div className="space-y-4">
      <div className="flex items-end justify-between flex-wrap gap-2">
        <div><h1 className="text-2xl font-extrabold">Hi {user.name?.split(' ')[0]} 👋</h1><p className="text-sm text-slate-500">{user.reg_no} · {user.college}</p></div>
        <div className="flex gap-2 flex-wrap">
          <Link to="/compare" className="btn-ghost">⚖️ Compare</Link>
          <Link to="/rent-analyzer" className="btn-ghost">📊 Rent Analyzer</Link>
          <Link to="/community" className="btn-ghost">💬 Community</Link>
          <Link to="/transport" className="btn-ghost">🚕 Transport</Link>
        </div>
      </div>
      <div className="flex gap-1 bg-slate-100 rounded-xl p-1 w-fit">{tabs.map(([k, l]) => <button key={k} onClick={() => setTab(k)} className={`tab ${tab === k ? 'tab-active' : ''}`}>{l}</button>)}</div>
      {tab === 'browse' && <PropertyBrowser canReview />}
      {tab === 'roommates' && <Roommates />}
      {tab === 'profile' && <ProfileBuilder />}
    </div>
  )
}
