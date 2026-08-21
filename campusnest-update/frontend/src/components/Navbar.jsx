import { Link, NavLink, useLocation } from 'react-router-dom'
import { useAuth } from '../App'

const links = [
  { to: '/compare', label: 'Compare' },
  { to: '/rent-analyzer', label: 'Rent Analyzer' },
  { to: '/community', label: 'Community' },
  { to: '/transport', label: 'Transport' },
  { to: '/services', label: 'Services' },
]

export default function Navbar() {
  const { user, logout } = useAuth()
  const { pathname } = useLocation()
  if (pathname === '/' || pathname === '/login') return null   // landing & login are full-bleed
  const home = user ? `/${user.role}` : '/'
  const cls = ({ isActive }) => `px-3 py-1.5 rounded-lg text-sm font-medium transition ${isActive ? 'bg-white/15 text-accentGold' : 'text-slate-200 hover:bg-white/10'}`
  return (
    <header className="sticky top-0 z-40 bg-primary/90 backdrop-blur border-b border-white/10 text-white">
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center gap-4">
        <Link to={home} className="font-display font-extrabold text-lg uppercase tracking-tight">
          🏠 Campus<span className="text-accentGold">Nest</span>
        </Link>
        <nav className="hidden md:flex items-center gap-1 ml-4">
          {user ? <NavLink to={home} className={cls}>Dashboard</NavLink> : <NavLink to="/guest" className={cls}>Browse</NavLink>}
          {links.map(l => <NavLink key={l.to} to={l.to} className={cls}>{l.label}</NavLink>)}
        </nav>
        <div className="ml-auto flex items-center gap-3">
          {user ? (
            <>
              <span className="hidden sm:flex items-center gap-2 text-sm">
                <span className="rounded-full bg-accentGold/20 text-accentGold px-2 py-0.5 text-xs font-semibold capitalize">{user.role}</span>
                <span className="font-medium">{user.name}</span>
              </span>
              <button onClick={logout} className="btn bg-white/10 text-white hover:bg-white/20">Logout</button>
            </>
          ) : (
            <Link to="/login" className="btn-primary">Login</Link>
          )}
        </div>
      </div>
    </header>
  )
}
