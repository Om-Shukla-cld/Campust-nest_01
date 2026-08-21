import { Link } from 'react-router-dom'
import PropertyBrowser from './PropertyBrowser'

export default function GuestDashboard() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <h1 className="text-2xl font-extrabold">Browse housing 👀</h1>
          <p className="text-sm text-slate-500">Guest mode — log in as a student to review, match roommates and join the community.</p>
        </div>
        <Link to="/" className="btn-primary">Login</Link>
      </div>
      <PropertyBrowser canReview={false} />
    </div>
  )
}
