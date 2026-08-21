import { useEffect, useState } from 'react'
import { api } from '../lib/api'

const FIELD_OPTIONS = {
  veg: ['Veg', 'Non-veg', 'Either'],
  smoker: ['Non-smoker', 'Smoker', "Doesn't matter"],
  sleep: ['Early bird', 'Night owl', 'Flexible'],
  cleanliness: ['Very tidy', 'Average', 'Relaxed'],
  study: ['Silent study', 'Music while studying', 'Group study'],
}

export default function ProfileBuilder() {
  const [profile, setProfile] = useState(null)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    api.getMyProfile().then(setProfile).catch(console.error)
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
        phone: profile.phone,
        reg_no: profile.reg_no,
        veg: profile.veg,
        smoker: profile.smoker,
        sleep: profile.sleep,
        cleanliness: profile.cleanliness,
        study: profile.study,
        about_me: profile.about_me,
      })
      setProfile(updated)
      setSaved(true)
    } finally {
      setSaving(false)
    }
  }

  if (!profile) return <p className="text-white text-center mt-24">Loading your nest profile…</p>

  return (
    <div className="max-w-2xl mx-auto mt-16 p-8 bg-secondary rounded-2xl space-y-6">
      <h2 className="text-2xl font-bold text-white">Your Nest Profile</h2>
      <p className="text-slate-400 text-sm">
        This is what future roommates and owners see about you when matching rooms.
      </p>

      <div className="grid grid-cols-2 gap-4">
        <input
          value={profile.name || ''} placeholder="Full name"
          onChange={(e) => update('name', e.target.value)}
          className="p-3 rounded-lg bg-primary text-white outline-none"
        />
        <input
          value={profile.phone || ''} placeholder="Phone"
          onChange={(e) => update('phone', e.target.value)}
          className="p-3 rounded-lg bg-primary text-white outline-none"
        />
        <input
          value={profile.reg_no || ''} placeholder="Registration No."
          onChange={(e) => update('reg_no', e.target.value)}
          className="p-3 rounded-lg bg-primary text-white outline-none col-span-2"
        />
      </div>

      {Object.entries(FIELD_OPTIONS).map(([field, options]) => (
        <div key={field}>
          <label className="text-slate-300 text-sm capitalize block mb-1">{field}</label>
          <div className="flex gap-2 flex-wrap">
            {options.map((opt) => (
              <button
                key={opt} type="button"
                onClick={() => update(field, opt)}
                className={`px-3 py-1.5 rounded-full text-sm border ${
                  profile[field] === opt
                    ? 'bg-accentGold text-primary border-accentGold'
                    : 'text-slate-300 border-slate-600'
                }`}
              >
                {opt}
              </button>
            ))}
          </div>
        </div>
      ))}

      <textarea
        value={profile.about_me || ''} placeholder="About me — hobbies, routine, what you're looking for in a flat…"
        onChange={(e) => update('about_me', e.target.value)}
        rows={4}
        className="w-full p-3 rounded-lg bg-primary text-white outline-none"
      />

      <button
        onClick={handleSave} disabled={saving}
        className="px-6 py-3 rounded-lg bg-accentGold text-primary font-semibold disabled:opacity-50"
      >
        {saving ? 'Saving…' : saved ? 'Saved ✓' : 'Save profile'}
      </button>
    </div>
  )
}
