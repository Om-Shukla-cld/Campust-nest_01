import { Link } from 'react-router-dom'

const PORTALS = [
  { icon: '🎓', title: 'Student Portal', desc: 'Find PGs, Flats & match roommates with AI-powered recommendations.', cta: 'Student Login', to: '/login?role=student', btn: 'btn-primary', popular: true },
  { icon: '👁️', title: 'Guest Explore', desc: 'Browse property listings without registering. No signup needed.', cta: 'Browse Now', to: '/guest', btn: 'btn-blue' },
  { icon: '🏠', title: 'List Property', desc: 'Property owners can register and manage their listings with ease.', cta: 'Register as Owner', to: '/login?role=owner', btn: 'btn-emerald' },
]

export default function LandingPage() {
  return (
    <div className="min-h-[calc(100vh-3rem)] flex flex-col items-center justify-center text-center text-white py-10">
      <div className="rise inline-flex items-center gap-2 rounded-full border border-accentGold/60 bg-accentGold/15 px-4 py-1.5 text-sm font-semibold text-accentGold">
        <span>🛡</span> Verified Housing Platform for Students
      </div>

      <h1 className="rise rise-1 font-display font-extrabold uppercase tracking-tight leading-none mt-6 text-[13vw] sm:text-6xl md:text-7xl lg:text-8xl xl:text-[6.75rem] drop-shadow-[0_4px_24px_rgba(0,0,0,0.45)]">
        CAMPUS<span className="text-accentGold">NEST</span>
      </h1>

      <p className="rise rise-2 mt-5 text-xl sm:text-2xl text-slate-200">
        Find Your Perfect Stay. <span className="text-accentGold font-semibold">Trusted by Students.</span>
      </p>

      <div className="rise rise-2 mt-5 flex flex-wrap justify-center gap-x-8 gap-y-2 text-sm sm:text-base text-slate-200">
        <span>✓ 15+ Verified Properties</span><span>✓ Anonymous Reviews</span><span>✓ Roommate Matching</span>
      </div>

      <div className="mt-12 grid md:grid-cols-3 gap-6 w-full max-w-5xl px-2">
        {PORTALS.map((p, i) => (
          <div key={p.title} className={`glass relative p-7 flex flex-col items-center text-center rise rise-${i + 3}`}>
            {p.popular && <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-accentGold px-3 py-0.5 text-[11px] font-bold text-primary">Most Popular</span>}
            <div className="text-4xl">{p.icon}</div>
            <h3 className="font-display font-bold text-2xl mt-4">{p.title}</h3>
            <p className="text-slate-200 text-sm mt-3 leading-relaxed">{p.desc}</p>
            <Link to={p.to} className={`${p.btn} w-full mt-6 py-2.5`}>{p.cta} <span aria-hidden>→</span></Link>
          </div>
        ))}
      </div>

      <div className="rise rise-5 mt-10 flex flex-wrap justify-center gap-4 text-xs text-slate-300">
        <Link to="/login?role=moderator" className="hover:text-accentGold">🛡️ Moderator Access</Link>
        <span>·</span>
        <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="hover:text-accentGold">API Docs</a>
        <span>·</span>
        <span>Use OTP <b className="text-accentGold">1234</b> for demo access</span>
      </div>
    </div>
  )
}
