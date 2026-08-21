import { useLocation } from 'react-router-dom'

/** VIT Bhopal campus photo behind every page: dark overlay on landing/login, light overlay inside the app. */
export default function Backdrop() {
  const { pathname } = useLocation()
  const hero = pathname === '/' || pathname === '/login'
  return <div className={`backdrop ${hero ? 'backdrop-hero' : 'backdrop-app'}`} aria-hidden="true" />
}
