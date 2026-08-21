// CampusNest API client — JWT + OTP backend (FastAPI).
// Copy to frontend/src/utils/api.js (or src/lib/api.js) and set VITE_API_URL in frontend/.env

const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')
const TOKEN_KEY = 'campusnest_token'
const USER_KEY = 'campusnest_user'

export const auth = {
  token: () => localStorage.getItem(TOKEN_KEY),
  user: () => {
    try { return JSON.parse(localStorage.getItem(USER_KEY) || 'null') } catch { return null }
  },
  save: ({ access_token, user }) => {
    localStorage.setItem(TOKEN_KEY, access_token)
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  },
  clear: () => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  },
  isLoggedIn: () => !!localStorage.getItem(TOKEN_KEY),
}

async function request(path, { method = 'GET', body, params, headers = {} } = {}) {
  const qs = params
    ? '?' + new URLSearchParams(Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== '')).toString()
    : ''
  const token = auth.token()
  const res = await fetch(`${API_URL}${path}${qs}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  if (res.status === 401) auth.clear()
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    const detail = Array.isArray(err.detail) ? err.detail.map(d => d.msg).join(', ') : err.detail
    throw new Error(detail || `Request failed (${res.status})`)
  }
  return res.status === 204 ? null : res.json()
}

const get = (p, params) => request(p, { params })
const post = (p, body) => request(p, { method: 'POST', body })
const put = (p, body) => request(p, { method: 'PUT', body })
const patch = (p, body, params) => request(p, { method: 'PATCH', body, params })
const del = (p) => request(p, { method: 'DELETE' })

export const api = {
  // ---- auth ----
  sendOtp: (identifier, role = 'student') => post('/auth/send-otp', { identifier, role }),
  studentLogin: async (reg_no, otp, name) => { const r = await post('/auth/student/login', { reg_no, otp, name }); auth.save(r); return r },
  ownerLogin: async (phone, otp, name) => { const r = await post('/auth/owner/login', { phone, otp, name }); auth.save(r); return r },
  moderatorLogin: async (phone, otp) => { const r = await post('/auth/moderator/login', { phone, otp }); auth.save(r); return r },
  me: () => get('/auth/me'),
  logout: () => { auth.clear() },

  // ---- profile ----
  getMyProfile: () => get('/profile/me'),
  updateMyProfile: (body) => put('/profile/me', body),
  getPublicProfile: (id) => get(`/profile/${id}`),

  // ---- properties (public) ----
  // filters: { q, type, area, gender, min_rent, max_rent, max_distance, amenities, min_rating, sort, page, page_size }
  searchProperties: (filters) => get('/properties', filters),
  listProperties: async (bounds, filters = {}) => {
    const params = { ...filters, page_size: 100 }
    if (bounds) Object.assign(params, { min_lat: bounds.minLat, max_lat: bounds.maxLat, min_lng: bounds.minLng, max_lng: bounds.maxLng })
    return (await get('/properties', params)).items
  },
  featuredProperties: () => get('/properties/featured'),
  propertyAreas: () => get('/properties/areas'),
  getProperty: (id) => get(`/properties/${id}`),
  getPropertySlots: (id) => get(`/properties/${id}/slots`),
  getPropertyReviews: (id) => get(`/properties/${id}/reviews`),
  compareProperties: (ids) => post('/properties/compare', { property_ids: ids }),

  // ---- reviews ----
  submitReview: (body) => post('/reviews', body), // { property_id, stars, comment, is_anonymous }
  myReviews: () => get('/reviews/mine'),
  deleteReview: (id) => del(`/reviews/${id}`),
  flagReview: (id) => post(`/reviews/${id}/flag`),

  // ---- community ----
  getGroups: (category) => get('/community/groups', { category }),
  getGroup: (id) => get(`/community/groups/${id}`),
  joinGroup: (id) => post(`/community/groups/${id}/join`),
  getGroupPosts: (id) => get(`/community/groups/${id}/posts`),
  getFeed: () => get('/community/feed'),
  createPost: (body) => post('/community/posts', body), // { group_id, title, content, tags }
  getPost: (id) => get(`/community/posts/${id}`),
  likePost: (id) => post(`/community/posts/${id}/like`),
  commentOnPost: (id, content) => post(`/community/posts/${id}/comments`, { content }),
  flagPost: (id) => post(`/community/posts/${id}/flag`),
  deletePost: (id) => del(`/community/posts/${id}`),

  // ---- roommates ----
  roommateMatches: (min_score = 0) => get('/roommates/matches', { min_score }),
  roommateScore: (otherId) => get(`/roommates/score/${otherId}`),
  browseRoommates: (filters) => get('/roommates/browse', filters),

  // ---- transport ----
  getRides: (filters) => get('/transport/rides', filters), // { origin, destination, mode, date }
  myRides: () => get('/transport/rides/mine'),
  createRide: (body) => post('/transport/rides', body),
  joinRide: (id) => post(`/transport/rides/${id}/join`),
  leaveRide: (id) => post(`/transport/rides/${id}/leave`),
  cancelRide: (id) => del(`/transport/rides/${id}`),

  // ---- analytics ----
  rentTrends: (area, type, months = 6) => get('/rent-trends', { area, type, months }),
  areaSummary: () => get('/rent-trends/areas'),
  analyzeRent: (rent, area, type) => get('/rent-trends/analyze', { rent, area, type }),

  // ---- services ----
  getServices: (filters) => get('/services', filters), // { category, area, q, min_rating }
  serviceCategories: () => get('/services/categories'),

  // ---- owner ----
  ownerDashboard: () => get('/owner/dashboard'),
  myProperties: () => get('/owner/properties'),
  createProperty: (body) => post('/owner/properties', body),
  updateProperty: (id, body) => patch(`/owner/properties/${id}`, body),
  deleteProperty: (id) => del(`/owner/properties/${id}`),
  setSlotOccupied: (propertyId, slotId, is_occupied) => patch(`/owner/properties/${propertyId}/slots/${slotId}`, undefined, { is_occupied }),
  getTenants: (property_id) => get('/owner/tenants', { property_id }),
  addTenant: (body) => post('/owner/tenants', body),
  updateTenant: (id, body) => patch(`/owner/tenants/${id}`, body),
  removeTenant: (id) => del(`/owner/tenants/${id}`),

  // ---- moderator ----
  moderatorDashboard: () => get('/moderator/dashboard'),
  moderationQueue: (status = 'pending') => get('/moderator/properties', { status }),
  moderateProperty: (id, status, reason) => patch(`/moderator/properties/${id}`, { status, reason }),
  toggleFeatured: (id) => patch(`/moderator/properties/${id}/feature`),
  listOwners: (verified) => get('/moderator/owners', { verified }),
  verifyOwner: (id, is_verified = true) => patch(`/moderator/owners/${id}`, undefined, { is_verified }),
  flaggedReviews: () => get('/moderator/reviews'),
  moderateReview: (id, body) => patch(`/moderator/reviews/${id}`, body), // { is_hidden, is_flagged }
  flaggedPosts: () => get('/moderator/posts'),
  moderatePost: (id, params) => patch(`/moderator/posts/${id}`, undefined, params), // { is_hidden, is_flagged }

  // ---- payments (optional, Razorpay) ----
  paymentsStatus: () => get('/payments/status'),
  createOrder: (slotId) => post('/payments/create-order', { slot_id: slotId }),
  verifyPayment: (payload) => post('/payments/verify', payload),
}

export default api
