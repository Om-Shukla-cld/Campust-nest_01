import { useState } from 'react'
import { motion } from 'framer-motion'
import PaymentButton from './PaymentButton'

export const inr = (n) => '₹' + Number(n || 0).toLocaleString('en-IN')

export function Stars({ value = 0, count }) {
  const v = Math.round(value * 2) / 2
  return (
    <span className="inline-flex items-center gap-1 text-amber-500 text-sm">
      <span>{'★'.repeat(Math.floor(v))}{v % 1 ? '½' : ''}{'☆'.repeat(5 - Math.ceil(v))}</span>
      <span className="text-slate-500 text-xs">{value ? value.toFixed(1) : '—'}{count !== undefined ? ` (${count})` : ''}</span>
    </span>
  )
}

export function Spinner({ label = 'Loading…' }) {
  return <div className="py-10 text-center text-slate-400 text-sm animate-pulse">{label}</div>
}

export function Empty({ children }) {
  return <div className="py-10 text-center text-slate-400 text-sm">{children}</div>
}

export function StatCard({ label, value, hint, accent = 'brand' }) {
  const map = { brand: 'text-brand-700 bg-brand-50', green: 'text-emerald-700 bg-emerald-50', amber: 'text-amber-700 bg-amber-50', rose: 'text-rose-700 bg-rose-50' }
  return (
    <div className="card">
      <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</div>
      <div className={`mt-2 text-2xl font-extrabold rounded-xl inline-block px-2 ${map[accent]}`}>{value}</div>
      {hint && <div className="text-xs text-slate-400 mt-1">{hint}</div>}
    </div>
  )
}

export function Modal({ open, onClose, title, children, wide }) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={onClose}>
      <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
        onClick={e => e.stopPropagation()}
        className={`bg-white rounded-2xl shadow-xl w-full ${wide ? 'max-w-4xl' : 'max-w-2xl'} max-h-[90vh] overflow-y-auto`}>
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <h3 className="font-bold text-lg">{title}</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700 text-xl leading-none">×</button>
        </div>
        <div className="p-6">{children}</div>
      </motion.div>
    </div>
  )
}

export function StatusBadge({ status }) {
  const map = { approved: 'bg-emerald-100 text-emerald-700', pending: 'bg-amber-100 text-amber-700', rejected: 'bg-rose-100 text-rose-700',
    paid: 'bg-emerald-100 text-emerald-700', due: 'bg-amber-100 text-amber-700', overdue: 'bg-rose-100 text-rose-700',
    open: 'bg-emerald-100 text-emerald-700', full: 'bg-slate-200 text-slate-600' }
  return <span className={`chip ${map[status] || ''} capitalize`}>{status}</span>
}

export function PropertyCard({ p, onOpen, selected, onToggleCompare, actions }) {
  return (
    <motion.div layout initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
      className={`card p-0 overflow-hidden flex flex-col ${selected ? 'ring-2 ring-brand-500' : ''}`}>
      <div className="relative h-40 bg-gradient-to-br from-amber-100 to-orange-200 flex items-center justify-center text-5xl">
        {p.images?.[0] ? <img src={p.images[0]} alt="" className="w-full h-full object-cover" loading="lazy" /> : <span>🏠</span>}
        {p.is_featured && <span className="absolute top-2 left-2 chip bg-amber-400 text-amber-900">⭐ Featured</span>}
        <span className="absolute top-2 right-2 chip bg-white/90">{p.type}</span>
      </div>
      <div className="p-4 flex-1 flex flex-col gap-2">
        <div className="flex items-start justify-between gap-2">
          <div>
            <h3 className="font-bold leading-tight">{p.name}</h3>
            <div className="text-xs text-slate-500">{p.area} · {p.distance_km} km from campus</div>
          </div>
          <div className="text-right">
            <div className="font-extrabold text-brand-700">{inr(p.rent)}</div>
            <div className="text-[10px] text-slate-400">/month</div>
          </div>
        </div>
        <div className="flex items-center justify-between">
          <Stars value={p.avg_rating} count={p.review_count} />
          <span className="text-xs text-slate-500">🛡 {p.safety_score?.toFixed(1)} · 🛏 {p.available_slots} free</span>
        </div>
        <div className="flex flex-wrap gap-1">
          {(p.amenities || []).slice(0, 5).map(a => <span key={a} className="chip">{a}</span>)}
          {p.amenities?.length > 5 && <span className="chip">+{p.amenities.length - 5}</span>}
        </div>
        <div className="mt-auto flex gap-2 pt-2">
          {onOpen && <button onClick={() => onOpen(p)} className="btn-primary flex-1">Details</button>}
          {onToggleCompare && (
            <button onClick={() => onToggleCompare(p)} className={selected ? 'btn bg-brand-100 text-brand-700' : 'btn-ghost'}>
              {selected ? '✓ Compare' : '+ Compare'}
            </button>
          )}
          {actions}
        </div>
      </div>
    </motion.div>
  )
}

export function PropertyDetail({ p, onReview, canReview, user, paymentsEnabled = false, onPaid }) {
  const [stars, setStars] = useState(5)
  const [comment, setComment] = useState('')
  const [anon, setAnon] = useState(false)
  if (!p) return null
  return (
    <div className="space-y-5">
      {p.images?.[0] && <img src={p.images[0]} alt="" className="w-full h-56 object-cover rounded-xl" />}
      <div className="grid sm:grid-cols-3 gap-3 text-sm">
        <div className="card py-3"><div className="label">Rent</div><div className="font-bold text-lg">{inr(p.rent)}<span className="text-xs text-slate-400">/mo</span></div></div>
        <div className="card py-3"><div className="label">Deposit</div><div className="font-bold text-lg">{inr(p.deposit)}</div></div>
        <div className="card py-3"><div className="label">Other charges</div><div className="font-bold text-lg">{inr(p.other_price)}</div></div>
      </div>
      <p className="text-slate-600 text-sm">{p.description}</p>
      <div className="text-sm text-slate-600">📍 {p.address} · {p.distance_km} km from campus · 🛡 Safety {p.safety_score} · 👥 {p.gender}</div>
      <div className="flex flex-wrap gap-1">{(p.amenities || []).map(a => <span key={a} className="chip">{a}</span>)}</div>
      {p.owner && <div className="text-sm">Owner: <b>{p.owner.name}</b> {p.owner.is_verified && <span className="chip bg-emerald-100 text-emerald-700">verified</span>} · {p.owner.phone}</div>}
      {p.slots && (
        <div>
          <div className="label">Slots ({p.available_slots} of {p.total_slots} available)</div>
          <div className="flex flex-wrap gap-1">{p.slots.map(s => <span key={s.id} className={`chip ${s.is_occupied ? 'bg-slate-200 line-through' : 'bg-emerald-100 text-emerald-700'}`}>{s.label}</span>)}</div>
          {user?.role === 'student' && p.available_slots > 0 && (() => {
            const free = p.slots.find(s => !s.is_occupied)
            return (
              <div className="mt-3 card bg-brand-50 border-brand-100">
                <div className="font-semibold text-sm">Book {free.label} — {inr(free.rent_per_slot || p.rent)}/month</div>
                {paymentsEnabled
                  ? <PaymentButton className="mt-2 max-w-xs" slotId={free.id} slotRent={free.rent_per_slot || p.rent} userName={user.name} userEmail={user.email} onPaid={onPaid} />
                  : <div className="mt-2 text-xs text-slate-500">💳 Online booking via Razorpay is disabled on this server (set <code>RAZORPAY_KEY_ID/SECRET</code> in <code>backend/.env</code>). Contact the owner at {p.owner?.phone || '—'} to book.</div>}
              </div>
            )
          })()}
        </div>
      )}
      <div>
        <div className="label">Reviews ({p.reviews?.length || 0})</div>
        <div className="space-y-2">
          {(p.reviews || []).map(r => (
            <div key={r.id} className="bg-slate-50 rounded-xl p-3 text-sm">
              <div className="flex justify-between"><b>{r.author_name}</b><Stars value={r.stars} /></div>
              <div className="text-slate-600">{r.comment}</div>
            </div>
          ))}
          {!p.reviews?.length && <Empty>No reviews yet.</Empty>}
        </div>
      </div>
      {canReview && (
        <form className="card space-y-2" onSubmit={e => { e.preventDefault(); onReview({ property_id: p.id, stars, comment, is_anonymous: anon }); setComment('') }}>
          <div className="font-semibold text-sm">Write a review</div>
          <div className="flex gap-2 items-center">
            {[1, 2, 3, 4, 5].map(n => <button type="button" key={n} onClick={() => setStars(n)} className={`text-2xl ${n <= stars ? 'text-amber-500' : 'text-slate-300'}`}>★</button>)}
            <label className="ml-auto text-xs flex items-center gap-1"><input type="checkbox" checked={anon} onChange={e => setAnon(e.target.checked)} /> Anonymous</label>
          </div>
          <textarea className="input" rows={2} placeholder="Share your experience…" value={comment} onChange={e => setComment(e.target.value)} />
          <button className="btn-primary">Submit review</button>
        </form>
      )}
    </div>
  )
}
