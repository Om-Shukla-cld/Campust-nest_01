import { useEffect, useState } from 'react'
import { api } from '../utils/api'
import { useAuth } from '../App'
import { useToast } from './Toast'
import { Modal, Spinner, Empty, StatusBadge, inr } from './shared'

const ICON = { cab: '🚕', auto: '🛺', bike: '🏍️', bus: '🚌' }

export default function SmartTransport() {
  const { user } = useAuth()
  const toast = useToast()
  const [rides, setRides] = useState(null)
  const [filters, setFilters] = useState({ origin: '', destination: '', mode: '' })
  const [form, setForm] = useState(null)

  const load = () => api.getRides(filters).then(setRides).catch(e => toast(e.message, 'error'))
  useEffect(() => { const t = setTimeout(load, 250); return () => clearTimeout(t) }, [filters])

  const need = () => { toast('Log in as a student to join or post rides', 'error'); return false }
  const join = async (r) => { if (!user) return need(); try { await api.joinRide(r.id); toast('Seat reserved 🎉', 'success'); load() } catch (e) { toast(e.message, 'error') } }
  const leave = async (r) => { try { await api.leaveRide(r.id); toast('Left ride'); load() } catch (e) { toast(e.message, 'error') } }
  const cancel = async (r) => { try { await api.cancelRide(r.id); toast('Ride cancelled'); load() } catch (e) { toast(e.message, 'error') } }
  const create = async (e) => {
    e.preventDefault()
    try { await api.createRide({ ...form, seats_total: +form.seats_total, cost_per_head: +form.cost_per_head, depart_at: new Date(form.depart_at).toISOString() }); toast('Ride posted', 'success'); setForm(null); load() }
    catch (err) { toast(err.message, 'error') }
  }
  const f = (k) => ({ value: form?.[k] ?? '', onChange: e => setForm(x => ({ ...x, [k]: e.target.value })) })

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div><h1 className="text-2xl font-extrabold">Smart Transport 🚕</h1><p className="text-sm text-slate-500">Share cabs and autos with other students — split the fare.</p></div>
        <button className="btn-primary" onClick={() => user ? setForm({ origin: 'VIT Bhopal Main Gate', destination: '', depart_at: '', mode: 'cab', seats_total: 3, cost_per_head: 0, notes: '' }) : need()}>+ Post a ride</button>
      </div>
      <div className="card grid md:grid-cols-3 gap-3">
        <input className="input" placeholder="From" value={filters.origin} onChange={e => setFilters(s => ({ ...s, origin: e.target.value }))} />
        <input className="input" placeholder="To" value={filters.destination} onChange={e => setFilters(s => ({ ...s, destination: e.target.value }))} />
        <select className="input" value={filters.mode} onChange={e => setFilters(s => ({ ...s, mode: e.target.value }))}><option value="">Any mode</option>{Object.keys(ICON).map(m => <option key={m}>{m}</option>)}</select>
      </div>
      {!rides ? <Spinner /> : rides.length === 0 ? <Empty>No upcoming rides. Post one!</Empty> : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">{rides.map(r => (
          <div key={r.id} className="card flex flex-col gap-2">
            <div className="flex justify-between items-start"><div className="text-3xl">{ICON[r.mode]}</div><StatusBadge status={r.status} /></div>
            <div className="font-bold">{r.origin} → {r.destination}</div>
            <div className="text-sm text-slate-600">🕒 {new Date(r.depart_at).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })}</div>
            <div className="text-sm">💺 {r.seats_left} of {r.seats_total} seats left · 💰 {inr(r.cost_per_head)}/head</div>
            {r.notes && <div className="text-xs text-slate-500 italic">“{r.notes}”</div>}
            <div className="text-xs text-slate-500">Host: {r.host?.name}</div>
            <div className="mt-auto pt-2 flex gap-2">
              {user && r.host?.id === user.id ? <button className="btn-danger flex-1" onClick={() => cancel(r)}>Cancel ride</button>
                : r.is_joined ? <button className="btn-ghost flex-1" onClick={() => leave(r)}>Leave</button>
                : <button className="btn-primary flex-1" disabled={r.seats_left === 0} onClick={() => join(r)}>{r.seats_left === 0 ? 'Full' : 'Join'}</button>}
            </div>
          </div>))}</div>
      )}
      <Modal open={!!form} onClose={() => setForm(null)} title="Post a shared ride">
        {form && (
          <form onSubmit={create} className="grid md:grid-cols-2 gap-3">
            <div><label className="label">From</label><input className="input" required {...f('origin')} /></div>
            <div><label className="label">To</label><input className="input" required {...f('destination')} placeholder="Bhopal Junction" /></div>
            <div><label className="label">Departure</label><input className="input" type="datetime-local" required {...f('depart_at')} /></div>
            <div><label className="label">Mode</label><select className="input" {...f('mode')}>{Object.keys(ICON).map(m => <option key={m}>{m}</option>)}</select></div>
            <div><label className="label">Seats available</label><input className="input" type="number" min="1" max="8" {...f('seats_total')} /></div>
            <div><label className="label">Cost per head ₹</label><input className="input" type="number" {...f('cost_per_head')} /></div>
            <div className="md:col-span-2"><label className="label">Notes</label><input className="input" {...f('notes')} /></div>
            <div className="md:col-span-2 flex justify-end gap-2"><button type="button" className="btn-ghost" onClick={() => setForm(null)}>Cancel</button><button className="btn-primary">Post ride</button></div>
          </form>
        )}
      </Modal>
    </div>
  )
}
