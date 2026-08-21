import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../utils/api'
import { useAuth } from '../App'
import { useToast } from './Toast'

const ROLES = {
  student: { icon: '🎓', title: 'Student Login', sub: 'Login with your registration number', field: 'Registration Number', placeholder: '21BCE0001', demo: '21BCE0001' },
  owner: { icon: '🏠', title: 'Owner Registration', sub: 'Login or register with your phone number', field: 'Phone Number', placeholder: '+91 98XXXXXXXX', demo: '+919800000001' },
  moderator: { icon: '🛡️', title: 'Moderator Access', sub: 'Restricted — moderators only', field: 'Moderator Phone', placeholder: '+910000000000', demo: '+910000000000' },
}

/** OTP login for all roles, styled like the CampusNest portal. Demo OTP is 1234 (DEBUG mode). */
export default function Login() {
  const { login } = useAuth()
  const toast = useToast()
  const [params, setParams] = useSearchParams()
  const role = ROLES[params.get('role')] ? params.get('role') : 'student'
  const R = ROLES[role]
  const [identifier, setIdentifier] = useState(R.demo)
  const [name, setName] = useState('')
  const [otp, setOtp] = useState('')
  const [sent, setSent] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => { setIdentifier(ROLES[role].demo); setOtp(''); setSent(false) }, [role])

  const sendOtp = async (e) => {
    e?.preventDefault(); setLoading(true)
    try {
      const r = await api.sendOtp(identifier, role)
      if (r.demo_otp) setOtp(r.demo_otp)
      setSent(true); toast(r.message, 'success')
    } catch (err) { toast(err.message, 'error') } finally { setLoading(false) }
  }
  const verify = async (e) => {
    e.preventDefault(); setLoading(true)
    try {
      const r = role === 'student' ? await api.studentLogin(identifier, otp, name || undefined)
        : role === 'owner' ? await api.ownerLogin(identifier, otp, name || undefined)
        : await api.moderatorLogin(identifier, otp)
      toast(`Welcome, ${r.user.name}!`, 'success'); login(r.user)
    } catch (err) { toast(err.message, 'error') } finally { setLoading(false) }
  }

  return (
    <div className="min-h-[calc(100vh-3rem)] flex items-center justify-center py-10">
      <div className="glass w-full max-w-md p-8 rise">
        <Link to="/" className="text-xs text-slate-300 hover:text-accentGold">← Back to home</Link>
        <div className="text-center mt-3">
          <div className="text-4xl">{R.icon}</div>
          <h1 className="font-display font-extrabold text-3xl mt-2">{R.title}</h1>
          <p className="text-slate-300 text-sm mt-1">{R.sub}</p>
        </div>

        <div className="grid grid-cols-3 gap-1 bg-white/10 rounded-xl p-1 mt-6">
          {Object.entries(ROLES).map(([k, v]) => (
            <button key={k} type="button" onClick={() => setParams({ role: k })}
              className={`rounded-lg py-1.5 text-xs font-semibold capitalize transition ${role === k ? 'bg-accentGold text-primary' : 'text-slate-200 hover:bg-white/10'}`}>
              {v.icon} {k}
            </button>
          ))}
        </div>

        <form onSubmit={sent ? verify : sendOtp} className="mt-6 space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wide text-slate-300 mb-1">{R.field}</label>
            <div className="flex gap-2">
              <input className="input-dark" value={identifier} onChange={e => { setIdentifier(e.target.value); setSent(false) }} placeholder={R.placeholder} required />
              {!sent && <button type="submit" disabled={loading} className="btn-primary whitespace-nowrap">{loading ? '…' : 'Send OTP'}</button>}
            </div>
          </div>
          {sent && (
            <>
              {role !== 'moderator' && (
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide text-slate-300 mb-1">Your name <span className="normal-case font-normal">(new accounts)</span></label>
                  <input className="input-dark" value={name} onChange={e => setName(e.target.value)} placeholder="Optional" />
                </div>
              )}
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wide text-slate-300 mb-1">OTP</label>
                <input className="input-dark tracking-[0.5em] text-center text-lg" value={otp} onChange={e => setOtp(e.target.value)} maxLength={6} required placeholder="••••" />
              </div>
              <button type="submit" disabled={loading} className="btn-primary w-full py-3">{loading ? 'Verifying…' : 'Login to Portal →'}</button>
              <button type="button" onClick={sendOtp} className="w-full text-xs text-slate-300 hover:text-accentGold">Resend OTP</button>
            </>
          )}
        </form>

        <p className="mt-6 text-center text-xs text-slate-300">Use OTP <b className="text-accentGold">1234</b> for demo access · New students/owners are created on first login</p>
      </div>
    </div>
  )
}
