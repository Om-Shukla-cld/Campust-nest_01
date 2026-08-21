import { useEffect, useState, createContext, useContext } from 'react'
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { api, auth } from './utils/api'
import Navbar from './components/Navbar'
import Backdrop from './components/Backdrop'
import LandingPage from './components/LandingPage'
import Login from './components/Login'
import StudentDashboard from './components/StudentDashboard'
import OwnerDashboard from './components/OwnerDashboard'
import ModeratorDashboard from './components/ModeratorDashboard'
import GuestDashboard from './components/GuestDashboard'
import CompareProperties from './components/CompareProperties'
import RentAnalyzer from './components/RentAnalyzer'
import SmartTransport from './components/SmartTransport'
import CommunityHub from './components/CommunityHub'
import GetServices from './components/GetServices'
import { Toaster, ToastContext } from './components/Toast'

export const AuthContext = createContext(null)
export const useAuth = () => useContext(AuthContext)

const HOME = { student: '/student', owner: '/owner', moderator: '/moderator' }

export default function App() {
  const [user, setUser] = useState(auth.user())
  const [toasts, setToasts] = useState([])
  const navigate = useNavigate()

  const toast = (message, type = 'info') => {
    const id = Date.now() + Math.random()
    setToasts(t => [...t, { id, message, type }])
    setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 3500)
  }

  // re-validate the stored token against the backend on load
  useEffect(() => {
    if (auth.token()) api.me().then(setUser).catch(() => { auth.clear(); setUser(null) })
  }, [])

  const login = (u) => { setUser(u); navigate(HOME[u.role] || '/guest') }
  const logout = () => { api.logout(); setUser(null); navigate('/') }

  const Protected = ({ role, children }) => {
    if (!user) return <Navigate to="/" replace />
    if (role && user.role !== role) return <Navigate to={HOME[user.role] || '/guest'} replace />
    return children
  }

  return (
    <AuthContext.Provider value={{ user, setUser, login, logout }}>
      <ToastContext.Provider value={toast}>
        <div className="min-h-screen flex flex-col overflow-x-hidden">
          <Backdrop />
          <Navbar />
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6">
            <Routes>
              <Route path="/" element={user ? <Navigate to={HOME[user.role] || '/guest'} replace /> : <LandingPage />} />
              <Route path="/login" element={user ? <Navigate to={HOME[user.role] || '/guest'} replace /> : <Login />} />
              <Route path="/guest" element={<GuestDashboard />} />
              <Route path="/student" element={<Protected role="student"><StudentDashboard /></Protected>} />
              <Route path="/owner" element={<Protected role="owner"><OwnerDashboard /></Protected>} />
              <Route path="/moderator" element={<Protected role="moderator"><ModeratorDashboard /></Protected>} />
              <Route path="/compare" element={<CompareProperties />} />
              <Route path="/rent-analyzer" element={<RentAnalyzer />} />
              <Route path="/transport" element={<SmartTransport />} />
              <Route path="/community" element={<CommunityHub />} />
              <Route path="/services" element={<GetServices />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          <footer className="text-center text-xs text-slate-400 py-6">CampusNest · Team TripleLoop · MIT License</footer>
          <Toaster toasts={toasts} />
        </div>
      </ToastContext.Provider>
    </AuthContext.Provider>
  )
}
