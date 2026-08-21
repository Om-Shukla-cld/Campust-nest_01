import { useState } from 'react'
import { api } from '../lib/api'

/**
 * OTP login for all roles. Demo OTP is 1234 (DEBUG mode).
 *   Student   -> registration number (e.g. 21BCE0001)
 *   Owner     -> phone number
 *   Moderator -> phone +910000000000
 */
export default function Login({ onLoggedIn }) {
  const [role, setRole] = useState('student')
  const [identifier, setIdentifier] = useState('')
  const [otp, setOtp] = useState('')
  const [step, setStep] = useState('identify') // identify | verify
  const [hint, setHint] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const sendOtp = async (e) => {
    e.preventDefault()
    setError(''); setLoading(true)
    try {
      const r = await api.sendOtp(identifier, role)
      setHint(r.message)
      if (r.demo_otp) setOtp(r.demo_otp)
      setStep('verify')
    } catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  const verify = async (e) => {
    e.preventDefault()
    setError(''); setLoading(true)
    try {
      const r = role === 'student'
        ? await api.studentLogin(identifier, otp)
        : await api.ownerLogin(identifier, otp) // moderator phone resolves to moderator role
      onLoggedIn?.(r.user)
    } catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  return (
    <div className="max-w-sm mx-auto mt-16 p-6 rounded-2xl shadow bg-white">
      <h1 className="text-2xl font-bold mb-4">Log in to CampusNest</h1>

      <div className="flex gap-2 mb-4">
        {['student', 'owner', 'moderator'].map(r => (
          <button key={r} type="button" onClick={() => { setRole(r); setStep('identify'); setError('') }}
            className={`flex-1 py-2 rounded-lg text-sm capitalize ${role === r ? 'bg-indigo-600 text-white' : 'bg-gray-100'}`}>
            {r}
          </button>
        ))}
      </div>

      {step === 'identify' ? (
        <form onSubmit={sendOtp} className="space-y-3">
          <input className="w-full border rounded-lg p-2" required value={identifier}
            onChange={e => setIdentifier(e.target.value)}
            placeholder={role === 'student' ? 'Registration no. (21BCE0001)' : 'Phone number'} />
          <button disabled={loading} className="w-full bg-indigo-600 text-white py-2 rounded-lg">
            {loading ? 'Sending…' : 'Send OTP'}
          </button>
        </form>
      ) : (
        <form onSubmit={verify} className="space-y-3">
          {hint && <p className="text-xs text-gray-500">{hint}</p>}
          <input className="w-full border rounded-lg p-2 tracking-widest" required value={otp}
            onChange={e => setOtp(e.target.value)} placeholder="Enter OTP" maxLength={6} />
          <button disabled={loading} className="w-full bg-indigo-600 text-white py-2 rounded-lg">
            {loading ? 'Verifying…' : 'Verify & Login'}
          </button>
          <button type="button" onClick={() => setStep('identify')} className="w-full text-sm text-gray-500">Change {role === 'student' ? 'reg no' : 'phone'}</button>
        </form>
      )}

      {error && <p className="text-red-600 text-sm mt-3">{error}</p>}
    </div>
  )
}
