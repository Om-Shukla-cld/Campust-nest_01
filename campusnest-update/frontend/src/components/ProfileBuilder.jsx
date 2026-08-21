import { useEffect, useState } from 'react'
import { api } from '../utils/api'
import { useAuth } from '../App'
import { useToast } from './Toast'

// Label shown to the user  →  value stored (must match backend roommate-matching vocabulary)
const FIELD_OPTIONS = {
  veg: [['Veg', 'veg'], ['Non-veg', 'non-veg'], ['Eggetarian', 'eggetarian']],
  smoker: [['Non-smoker', 'no'], ['Occasionally', 'occasionally'], ['Smoker', 'yes']],
  sleep: [['Early bird', 'early-bird'], ['Night owl', 'night-owl'], ['Flexible', 'flexible']],
  cleanliness: [['Very tidy', 'tidy'], ['Average', 'average'], ['Relaxed', 'relaxed']],
  study: [['Silent study', 'quiet'], ['Music while studying', 'music'], ['Group study', 'group']],
}
const LABELS = { veg: 'Food', smoker: 'Smoking', sleep: 'Sleep schedule', cleanliness: 'Cleanliness', study: 'Study style' }

/** Lifestyle "Nest profile" — what roommates and owners see, and what powers /roommates/matches. */
export default function ProfileBuilder() {
  const { setUser } = useAuth()
  const toast = useToast()
  const [profile, setProfile] = useState(null)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    api.getMyProfile().then(setProfile).catch((e) => toast(e.message, 'error'))
  }, [])

  function update(field, value) {
    setProfile((p) => ({ ...p, [field]: value }))
    setSaved(false)
  }

  async function handleSave() {
    setSaving(true)
    try {
      const updated = await api.updateMyProfile({
        name: profile.name,
        email: profile.email,
        phone: profile.phone,
        veg: profile.veg,
        smoker: profile.smoker,
        sleep: profile.sleep,
        cleanliness: profile.cleanliness,
        study: profile.study,
        budget: profile.budget ? Number(profile.budget) : null,
        about_me: profile.about_me,
        looking_for_roommate: !!profile.looking_for_roommate,
      })
      setProfile(updated)
      setUser(updated)
      setSaved(true)
      toast('Nest profile saved', 'success')
    } catch (e) {
      toast(e.message, 'error')
    } finally {
      setSaving(false)
    }
  }

  if (!profile) return <p className="text-slate-400 text-center py-16 animate-pulse">Loading your nest profile…</p>

  const completed = ['veg', 'smoker', 'sleep', 'cleanliness', 'study', 'budget', 'about_me'].filter((k) => profile[k]).length
  const pct = Math.round((completed / 7) * 100)

  return (
    <div className="max-w-2xl card space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Your Nest Profile 🪺</h2>
        <p className="text-slate-500 text-sm">This is what future roommates and owners see about you when matching rooms.</p>
        <div className="mt-3 h-2 rounded-full bg-slate-100"><div className="h-2 rounded-full bg-brand-500 transition-all" style={{ width: `${pct}%` }} /></div>
        <div className="text-xs text-slate-400 mt-1">{pct}% complete — fuller profiles get better matches</div>
      </div>

      <div className="grid sm:grid-cols-2 gap-3">
        <input value={profile.name || ''} placeholder="Full name" onChange={(e) => update('name', e.target.value)} className="input" />
        <input value={profile.phone || ''} placeholder="Phone" onChange={(e) => update('phone', e.target.value)} className="input" />
        <input value={profile.email || ''} placeholder="Email" type="email" onChange={(e) => update('email', e.target.value)} className="input" />
        <input value={profile.reg_no || ''} placeholder="Registration No." readOnly className="input bg-slate-50 text-slate-500" title="Registration number is your login ID" />
      </div>

      {Object.entries(FIELD_OPTIONS).map(([field, options]) => (
        <div key={field}>
          <label className="label">{LABELS[field]}</label>
          <div className="flex gap-2 flex-wrap">
            {options.map(([label, value]) => (
              <button key={value} type="button" onClick={() => update(field, value)}
                className={`px-3 py-1.5 rounded-full text-sm border transition ${profile[field] === value ? 'bg-brand-600 text-white border-brand-600' : 'text-slate-600 border-slate-200 hover:border-brand-300'}`}>
                {label}
              </button>
            ))}
          </div>
        </div>
      ))}

      <div className="grid sm:grid-cols-2 gap-3 items-end">
        <div><label className="label">Monthly rent budget (₹)</label><input type="number" value={profile.budget || ''} onChange={(e) => update('budget', e.target.value)} className="input" placeholder="7000" /></div>
        <label className="text-sm flex items-center gap-2 pb-2"><input type="checkbox" checked={!!profile.looking_for_roommate} onChange={(e) => update('looking_for_roommate', e.target.checked)} /> I'm looking for a roommate</label>
      </div>

      <textarea value={profile.about_me || ''} placeholder="About me — hobbies, routine, what you're looking for in a flat…" onChange={(e) => update('about_me', e.target.value)} rows={4} className="input" />

      <button onClick={handleSave} disabled={saving} className="btn-primary">
        {saving ? 'Saving…' : saved ? 'Saved ✓' : 'Save profile'}
      </button>
    </div>
  )
}
