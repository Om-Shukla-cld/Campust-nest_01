import { useEffect, useState } from 'react'
import { api } from '../utils/api'
import { useToast } from './Toast'
import { StatCard, StatusBadge, Modal, PropertyDetail, Spinner, Empty, inr, Stars } from './shared'

export default function ModeratorDashboard() {
  const toast = useToast()
  const [dash, setDash] = useState(null)
  const [tab, setTab] = useState('pending')
  const [props, setProps] = useState(null)
  const [owners, setOwners] = useState(null)
  const [reviews, setReviews] = useState(null)
  const [posts, setPosts] = useState(null)
  const [open, setOpen] = useState(null)
  const [reject, setReject] = useState(null)

  const loadAll = () => {
    api.moderatorDashboard().then(setDash)
    const status = ['pending', 'approved', 'rejected'].includes(tab) ? tab : 'all'
    if (['pending', 'approved', 'rejected'].includes(tab)) api.moderationQueue(status).then(setProps).catch(e => toast(e.message, 'error'))
    if (tab === 'owners') api.listOwners().then(setOwners)
    if (tab === 'reviews') api.flaggedReviews().then(setReviews)
    if (tab === 'posts') api.flaggedPosts().then(setPosts)
  }
  useEffect(() => { loadAll() }, [tab])

  const act = async (fn, msg) => { try { await fn(); toast(msg, 'success'); loadAll() } catch (e) { toast(e.message, 'error') } }

  const tabs = [['pending', '⏳ Pending'], ['approved', '✅ Approved'], ['rejected', '❌ Rejected'], ['owners', '🏠 Owners'], ['reviews', '⚠️ Flagged reviews'], ['posts', '🚩 Flagged posts']]
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-extrabold">Moderator console 🛡️</h1>
      {dash && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <StatCard label="Pending listings" value={dash.properties.pending} accent="amber" />
          <StatCard label="Live listings" value={dash.properties.approved} accent="green" />
          <StatCard label="Owners to verify" value={dash.owners.pending} accent={dash.owners.pending ? 'amber' : 'green'} hint={`${dash.owners.verified} verified`} />
          <StatCard label="Students" value={dash.students} />
          <StatCard label="Flagged" value={dash.flagged_reviews + dash.flagged_posts} accent={dash.flagged_reviews + dash.flagged_posts ? 'rose' : 'green'} hint="reviews + posts" />
        </div>
      )}
      <div className="flex gap-1 bg-slate-100 rounded-xl p-1 w-fit flex-wrap">{tabs.map(([k, l]) => <button key={k} onClick={() => setTab(k)} className={`tab ${tab === k ? 'tab-active' : ''}`}>{l}</button>)}</div>

      {['pending', 'approved', 'rejected'].includes(tab) && (!props ? <Spinner /> : props.length === 0 ? <Empty>Nothing here.</Empty> : (
        <div className="card p-0 overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500"><tr><th className="p-3">Property</th><th className="p-3">Owner</th><th className="p-3">Rent</th><th className="p-3">Status</th><th className="p-3 text-right">Actions</th></tr></thead>
            <tbody>{props.map(p => (
              <tr key={p.id} className="border-t border-slate-100">
                <td className="p-3"><button className="font-semibold text-brand-700 hover:underline" onClick={() => api.getProperty(p.id).then(setOpen)}>{p.name}</button><div className="text-xs text-slate-500">{p.type} · {p.area} · {p.total_slots} slots</div></td>
                <td className="p-3">{p.owner?.name}{p.owner?.is_verified ? ' ✅' : ' ⏳'}</td><td className="p-3">{inr(p.rent)}</td>
                <td className="p-3"><StatusBadge status={p.status} />{p.is_featured && ' ⭐'}</td>
                <td className="p-3 text-right whitespace-nowrap space-x-1">
                  {p.status !== 'approved' && <button className="btn bg-emerald-600 text-white py-1" onClick={() => act(() => api.moderateProperty(p.id, 'approved'), 'Listing approved')}>Approve</button>}
                  {p.status !== 'rejected' && <button className="btn-danger py-1" onClick={() => setReject({ id: p.id, reason: '' })}>Reject</button>}
                  {p.status === 'approved' && <button className="btn-ghost py-1" onClick={() => act(() => api.toggleFeatured(p.id), 'Featured toggled')}>{p.is_featured ? 'Unfeature' : 'Feature'}</button>}
                </td>
              </tr>))}</tbody>
          </table>
        </div>
      ))}

      {tab === 'owners' && (!owners ? <Spinner /> : (
        <div className="card p-0 overflow-x-auto"><table className="w-full text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500"><tr><th className="p-3">Owner</th><th className="p-3">Phone</th><th className="p-3">Status</th><th className="p-3 text-right">Actions</th></tr></thead>
          <tbody>{owners.map(o => (
            <tr key={o.id} className="border-t border-slate-100">
              <td className="p-3 font-semibold">{o.name}</td><td className="p-3">{o.phone}</td>
              <td className="p-3">{o.is_verified ? <span className="chip bg-emerald-100 text-emerald-700">verified</span> : <span className="chip bg-amber-100 text-amber-700">pending</span>}</td>
              <td className="p-3 text-right"><button className={o.is_verified ? 'btn-ghost py-1' : 'btn-primary py-1'} onClick={() => act(() => api.verifyOwner(o.id, !o.is_verified), o.is_verified ? 'Verification revoked' : 'Owner verified')}>{o.is_verified ? 'Revoke' : 'Verify'}</button></td>
            </tr>))}</tbody></table></div>
      ))}

      {tab === 'reviews' && (!reviews ? <Spinner /> : reviews.length === 0 ? <Empty>No flagged reviews 🎉</Empty> : (
        <div className="space-y-2">{reviews.map(r => (
          <div key={r.id} className="card flex items-center gap-4">
            <div className="flex-1"><div className="flex gap-2 items-center"><b>{r.author_name}</b><Stars value={r.stars} />{r.is_hidden && <span className="chip">hidden</span>}</div><div className="text-sm text-slate-600">{r.comment}</div></div>
            <button className="btn-ghost py-1" onClick={() => act(() => api.moderateReview(r.id, { is_hidden: !r.is_hidden }), r.is_hidden ? 'Review restored' : 'Review hidden')}>{r.is_hidden ? 'Unhide' : 'Hide'}</button>
            <button className="btn-primary py-1" onClick={() => act(() => api.moderateReview(r.id, { is_flagged: false }), 'Flag cleared')}>Clear flag</button>
          </div>))}</div>
      ))}

      {tab === 'posts' && (!posts ? <Spinner /> : posts.length === 0 ? <Empty>No flagged posts 🎉</Empty> : (
        <div className="space-y-2">{posts.map(p => (
          <div key={p.id} className="card flex items-center gap-4">
            <div className="flex-1"><b>{p.title || '(untitled)'}</b> <span className="text-xs text-slate-500">by {p.author?.name}</span><div className="text-sm text-slate-600">{p.content}</div></div>
            <button className="btn-ghost py-1" onClick={() => act(() => api.moderatePost(p.id, { is_hidden: true }), 'Post hidden')}>Hide</button>
            <button className="btn-primary py-1" onClick={() => act(() => api.moderatePost(p.id, { is_flagged: false }), 'Flag cleared')}>Clear flag</button>
          </div>))}</div>
      ))}

      <Modal open={!!open} onClose={() => setOpen(null)} title={open?.name} wide><PropertyDetail p={open} /></Modal>
      <Modal open={!!reject} onClose={() => setReject(null)} title="Reject listing">
        {reject && (
          <form onSubmit={e => { e.preventDefault(); act(() => api.moderateProperty(reject.id, 'rejected', reject.reason), 'Listing rejected'); setReject(null) }} className="space-y-3">
            <textarea className="input" rows={3} placeholder="Reason shown to the owner" value={reject.reason} onChange={e => setReject(r => ({ ...r, reason: e.target.value }))} />
            <div className="flex justify-end gap-2"><button type="button" className="btn-ghost" onClick={() => setReject(null)}>Cancel</button><button className="btn-danger">Reject</button></div>
          </form>
        )}
      </Modal>
    </div>
  )
}
