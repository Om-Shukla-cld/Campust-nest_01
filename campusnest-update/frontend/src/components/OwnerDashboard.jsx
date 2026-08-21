import { useEffect, useState } from 'react'
import { api } from '../utils/api'
import { useAuth } from '../App'
import { useToast } from './Toast'
import { StatCard, StatusBadge, Modal, Spinner, Empty, inr } from './shared'

const EMPTY = { name: '', type: 'PG', gender: 'any', area: '', address: '', rent: '', deposit: '', other_price: '', distance_km: '', total_slots: 1, amenities: '', description: '', lat: 23.0776, lng: 76.8516 }

export default function OwnerDashboard() {
  const { user } = useAuth()
  const toast = useToast()
  const [dash, setDash] = useState(null)
  const [props, setProps] = useState(null)
  const [tenants, setTenants] = useState(null)
  const [form, setForm] = useState(null)       // property form (null=closed)
  const [tenantForm, setTenantForm] = useState(null)

  const load = () => Promise.all([api.ownerDashboard(), api.myProperties(), api.getTenants()])
    .then(([d, p, t]) => { setDash(d); setProps(p); setTenants(t) }).catch(e => toast(e.message, 'error'))
  useEffect(() => { load() }, [])

  const saveProperty = async (e) => {
    e.preventDefault()
    const body = { ...form, rent: +form.rent, deposit: +form.deposit || 0, other_price: +form.other_price || 0, distance_km: +form.distance_km || 0, total_slots: +form.total_slots || 1,
      lat: +form.lat, lng: +form.lng, amenities: String(form.amenities).split(',').map(s => s.trim()).filter(Boolean) }
    try {
      if (form.id) { const { id, ...rest } = body; await api.updateProperty(id, rest); toast('Listing updated (re-queued for approval if key fields changed)', 'success') }
      else { await api.createProperty(body); toast('Listing submitted — awaiting moderator approval', 'success') }
      setForm(null); load()
    } catch (err) { toast(err.message, 'error') }
  }
  const del = async (p) => { if (!confirm(`Delete "${p.name}"?`)) return; try { await api.deleteProperty(p.id); toast('Deleted'); load() } catch (e) { toast(e.message, 'error') } }
  const edit = (p) => setForm({ ...p, amenities: (p.amenities || []).join(', ') })

  const saveTenant = async (e) => {
    e.preventDefault()
    try { await api.addTenant({ ...tenantForm, property_id: +tenantForm.property_id, rent: tenantForm.rent ? +tenantForm.rent : undefined }); toast('Tenant added', 'success'); setTenantForm(null); load() }
    catch (err) { toast(err.message, 'error') }
  }
  const setRent = async (t, rent_status) => { try { await api.updateTenant(t.id, { rent_status }); load() } catch (e) { toast(e.message, 'error') } }
  const endTenancy = async (t) => { try { await api.updateTenant(t.id, { end_date: new Date().toISOString() }); toast('Tenancy ended, slot freed'); load() } catch (e) { toast(e.message, 'error') } }

  if (!dash || !props || !tenants) return <Spinner />
  const s = dash.stats
  const f = (k) => ({ value: form?.[k] ?? '', onChange: e => setForm(x => ({ ...x, [k]: e.target.value })) })
  const tf = (k) => ({ value: tenantForm?.[k] ?? '', onChange: e => setTenantForm(x => ({ ...x, [k]: e.target.value })) })

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between flex-wrap gap-2">
        <div><h1 className="text-2xl font-extrabold">Owner dashboard 🏠</h1>
          <p className="text-sm text-slate-500">{user.name} · {user.phone} {user.is_verified ? <span className="chip bg-emerald-100 text-emerald-700">verified owner</span> : <span className="chip bg-amber-100 text-amber-700">verification pending</span>}</p></div>
        <button className="btn-primary" onClick={() => setForm({ ...EMPTY })}>+ Add property</button>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        <StatCard label="Properties" value={s.total_properties} hint={`${s.approved} live · ${s.pending} pending`} />
        <StatCard label="Slots" value={`${s.occupied_slots}/${s.total_slots}`} hint="occupied" accent="green" />
        <StatCard label="Active tenants" value={s.active_tenants} accent="green" />
        <StatCard label="Monthly revenue" value={inr(s.monthly_revenue)} accent="brand" />
        <StatCard label="Rent due" value={inr(s.rent_due)} accent={s.rent_due ? 'rose' : 'green'} />
        <StatCard label="Rejected" value={s.rejected} accent={s.rejected ? 'rose' : 'brand'} />
      </div>

      <section>
        <h2 className="font-bold text-lg mb-2">My listings</h2>
        {props.length === 0 ? <Empty>No listings yet.</Empty> : (
          <div className="card p-0 overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500"><tr><th className="p-3">Property</th><th className="p-3">Type</th><th className="p-3">Rent</th><th className="p-3">Slots free</th><th className="p-3">Rating</th><th className="p-3">Status</th><th className="p-3"></th></tr></thead>
              <tbody>
                {props.map(p => (
                  <tr key={p.id} className="border-t border-slate-100">
                    <td className="p-3"><div className="font-semibold">{p.name}</div><div className="text-xs text-slate-500">{p.area}</div>{p.rejection_reason && <div className="text-xs text-rose-600">Reason: {p.rejection_reason}</div>}</td>
                    <td className="p-3">{p.type}</td><td className="p-3">{inr(p.rent)}</td><td className="p-3">{p.available_slots}/{p.total_slots}</td>
                    <td className="p-3">★ {p.avg_rating} ({p.review_count})</td><td className="p-3"><StatusBadge status={p.status} /></td>
                    <td className="p-3 text-right whitespace-nowrap"><button className="btn-ghost py-1" onClick={() => edit(p)}>Edit</button> <button className="btn-danger py-1" onClick={() => del(p)}>Delete</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section>
        <div className="flex items-center justify-between mb-2"><h2 className="font-bold text-lg">Tenants</h2><button className="btn-ghost" onClick={() => setTenantForm({ property_id: props[0]?.id || '', name: '', phone: '', reg_no: '', rent: '' })} disabled={!props.length}>+ Add tenant</button></div>
        {tenants.length === 0 ? <Empty>No tenants yet.</Empty> : (
          <div className="card p-0 overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500"><tr><th className="p-3">Tenant</th><th className="p-3">Property</th><th className="p-3">Rent</th><th className="p-3">Since</th><th className="p-3">Rent status</th><th className="p-3"></th></tr></thead>
              <tbody>
                {tenants.map(t => (
                  <tr key={t.id} className={`border-t border-slate-100 ${t.end_date ? 'opacity-50' : ''}`}>
                    <td className="p-3"><div className="font-semibold">{t.name}</div><div className="text-xs text-slate-500">{t.reg_no} · {t.phone}</div></td>
                    <td className="p-3">{props.find(p => p.id === t.property_id)?.name}</td><td className="p-3">{inr(t.rent)}</td>
                    <td className="p-3">{t.start_date?.slice(0, 10)}{t.end_date && ` → ${t.end_date.slice(0, 10)}`}</td>
                    <td className="p-3"><StatusBadge status={t.rent_status} /></td>
                    <td className="p-3 text-right whitespace-nowrap">
                      {!t.end_date && <>
                        <select className="input inline w-auto py-1 mr-1" value={t.rent_status} onChange={e => setRent(t, e.target.value)}><option>paid</option><option>due</option><option>overdue</option></select>
                        <button className="btn-ghost py-1" onClick={() => endTenancy(t)}>End</button></>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <Modal open={!!form} onClose={() => setForm(null)} title={form?.id ? 'Edit listing' : 'Add property'} wide>
        {form && (
          <form onSubmit={saveProperty} className="grid md:grid-cols-3 gap-3">
            <div className="md:col-span-2"><label className="label">Name</label><input className="input" required {...f('name')} /></div>
            <div><label className="label">Type</label><select className="input" {...f('type')}>{['PG', 'Hostel', 'Shared Room', '1BHK', '2BHK', 'Studio'].map(t => <option key={t}>{t}</option>)}</select></div>
            <div><label className="label">For</label><select className="input" {...f('gender')}><option value="any">any</option><option value="boys">boys</option><option value="girls">girls</option></select></div>
            <div><label className="label">Area</label><input className="input" required {...f('area')} placeholder="Kothri Kalan" /></div>
            <div><label className="label">Distance from campus (km)</label><input className="input" type="number" step="0.1" {...f('distance_km')} /></div>
            <div className="md:col-span-3"><label className="label">Address</label><input className="input" {...f('address')} /></div>
            <div><label className="label">Rent ₹/month</label><input className="input" type="number" required {...f('rent')} /></div>
            <div><label className="label">Deposit ₹</label><input className="input" type="number" {...f('deposit')} /></div>
            <div><label className="label">Other charges ₹</label><input className="input" type="number" {...f('other_price')} /></div>
            <div><label className="label">Total slots / beds</label><input className="input" type="number" min="1" {...f('total_slots')} /></div>
            <div><label className="label">Latitude</label><input className="input" type="number" step="0.0001" {...f('lat')} /></div>
            <div><label className="label">Longitude</label><input className="input" type="number" step="0.0001" {...f('lng')} /></div>
            <div className="md:col-span-3"><label className="label">Amenities (comma separated)</label><input className="input" {...f('amenities')} placeholder="wifi, mess, ac, laundry" /></div>
            <div className="md:col-span-3"><label className="label">Description</label><textarea className="input" rows={2} {...f('description')} /></div>
            <div className="md:col-span-3 flex gap-2 justify-end"><button type="button" className="btn-ghost" onClick={() => setForm(null)}>Cancel</button><button className="btn-primary">{form.id ? 'Save changes' : 'Submit for approval'}</button></div>
          </form>
        )}
      </Modal>

      <Modal open={!!tenantForm} onClose={() => setTenantForm(null)} title="Add tenant">
        {tenantForm && (
          <form onSubmit={saveTenant} className="grid md:grid-cols-2 gap-3">
            <div className="md:col-span-2"><label className="label">Property</label><select className="input" {...tf('property_id')}>{props.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}</select></div>
            <div><label className="label">Name</label><input className="input" required {...tf('name')} /></div>
            <div><label className="label">Reg no (links student account)</label><input className="input" {...tf('reg_no')} /></div>
            <div><label className="label">Phone</label><input className="input" {...tf('phone')} /></div>
            <div><label className="label">Rent ₹ (default: listing rent)</label><input className="input" type="number" {...tf('rent')} /></div>
            <div className="md:col-span-2 flex justify-end gap-2"><button type="button" className="btn-ghost" onClick={() => setTenantForm(null)}>Cancel</button><button className="btn-primary">Add tenant</button></div>
          </form>
        )}
      </Modal>
    </div>
  )
}
