# CampusNest — Architecture

> Student Housing & Community Platform · Team TripleLoop

## 1. System overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Frontend (React + Vite)                      │
│  LandingPage · StudentDashboard · OwnerDashboard · ModeratorDashboard │
│  GuestDashboard · CompareProperties · RentAnalyzer · SmartTransport   │
│  CommunityHub · GetServices · RoomMap (Leaflet/OSM) · PaymentButton   │
│                     utils/api.js  (fetch + Bearer JWT)               │
└───────────────────────────────┬──────────────────────────────────────┘
                                │ HTTPS / JSON  (CORS)
┌───────────────────────────────▼──────────────────────────────────────┐
│                         API Layer — FastAPI                          │
│  routers/                                                            │
│   auth ─ profiles ─ properties ─ reviews ─ community ─ roommates     │
│   transport ─ analytics(rent-trends) ─ services ─ owner ─ moderator  │
│   payments (Razorpay, optional)                                      │
│  auth.py  → OTP issue/verify · JWT sign/verify · role guards         │
│  schemas.py (Pydantic v2) · models.py (SQLAlchemy 2) · seed.py       │
└───────────────────────────────┬──────────────────────────────────────┘
                                │ SQLAlchemy ORM
┌───────────────────────────────▼──────────────────────────────────────┐
│   Database:  SQLite (default, zero-setup)  |  PostgreSQL (prod)      │
│   users · otp_codes · properties · slots · tenants · reviews         │
│   community_groups · group_members · community_posts · post_comments │
│   transport_rides · ride_passengers · rent_trends · services · payments│
└──────────────────────────────────────────────────────────────────────┘
```

## 2. Backend layout

```
backend/
├── main.py          FastAPI app, CORS, router mounting, lifespan (create tables + seed)
├── config.py        Settings from .env (DB mode, JWT secret, OTP, CORS, Razorpay)
├── database.py      Engine / SessionLocal / Base / get_db dependency
├── models.py        ORM tables (portable types → same code on SQLite & Postgres)
├── schemas.py       Pydantic request/response models
├── auth.py          OTP + JWT + role dependencies (require_student/owner/moderator)
├── seed.py          Demo data (users, 10 properties, reviews, groups, posts, rides,
│                    services, 12 months of rent trends). `python -m backend.seed --reset`
├── routers/
│   ├── auth.py        /auth/send-otp, /auth/student/login, /auth/owner/login, /auth/me
│   ├── profiles.py    /profile/me (GET/PUT), /profile/{id}
│   ├── properties.py  /properties (search/filter/sort/paginate), /{id}, /compare, /featured, /areas
│   ├── reviews.py     /reviews (POST upsert), /mine, /{id} DELETE, /{id}/flag
│   ├── community.py   /community/groups, /groups/{id}/posts, /posts, /feed, like/comment/flag
│   ├── roommates.py   /roommates/matches (weighted compatibility), /score/{id}, /browse
│   ├── transport.py   /transport/rides (list/create/join/leave/cancel), /rides/mine
│   ├── analytics.py   /rent-trends, /rent-trends/areas, /rent-trends/analyze?rent=…
│   ├── services.py    /services, /services/categories
│   ├── owner.py       /owner/dashboard, /owner/properties CRUD, slots, /owner/tenants CRUD
│   ├── moderator.py   /moderator/dashboard, /properties (approve/reject/feature), /owners, /reviews, /posts
│   └── payments.py    /payments/status, /create-order, /verify (503 if keys not configured)
├── tests/test_api.py  end-to-end smoke tests (pytest, isolated SQLite DB)
├── Dockerfile
├── requirements.txt
└── .env.example
```

## 3. Authentication & roles

```
 client                         API                              DB
   │  POST /auth/send-otp         │                                │
   │  {identifier, role} ────────▶│ issue_otp()  ─────────────────▶│ otp_codes
   │  ◀── {demo_otp (DEBUG)}      │                                │
   │  POST /auth/student/login    │                                │
   │  {reg_no, otp}  ────────────▶│ verify_otp() ─────────────────▶│
   │                              │ get-or-create user             │ users
   │  ◀── {access_token, user}    │ create_access_token() (HS256)  │
   │  Authorization: Bearer …  ──▶│ get_current_user() / require_role()
```

* **Students** log in with registration number, **owners/moderators** with phone.
  Accounts are auto-created on first login (the moderator phone `+910000000000`
  is seeded and resolves to the `moderator` role).
* `DEBUG=true` → `DEMO_OTP` (1234) is always accepted and echoed back; real
  OTPs are logged to the console. `DEBUG=false` → random 4-digit OTP stored in
  `otp_codes` with expiry (plug an SMS provider into `auth.issue_otp`).
* JWT: HS256 signed with `SECRET_KEY`, 24 h default expiry, payload `{sub, role, name}`.
* Role guards: `require_student`, `require_owner`, `require_moderator`;
  public endpoints use `get_current_user_optional`.

## 4. Core domain flows

| Flow | Path |
|------|------|
| **Listing lifecycle** | Owner `POST /owner/properties` → `status=pending` → Moderator `PATCH /moderator/properties/{id} {status: approved/rejected}` → visible in `GET /properties`. Material edits (rent/name/address/type) send an approved listing back to `pending`. |
| **Slots & tenants** | Each property has N `slots` (beds). Owner adds a tenant → first free slot is occupied; ending tenancy frees it. `available_slots` is computed on every listing. |
| **Compare** | `POST /properties/compare {property_ids:[2–4]}` → cheapest / closest / safest / top-rated + weighted *best value* (rent 40 %, rating 25 %, safety 20 %, amenities 15 %). |
| **Roommate matching** | Weighted lifestyle score (sleep 25, cleanliness 20, smoker 20, veg 15, study 10, budget 10). "flexible" matches anything; unknown fields count neutral. |
| **Rent analyzer** | `rent_trends` table (12 months/area/type) for charts; `/rent-trends/analyze` compares a quoted rent with live approved listings → verdict + negotiation tip. |
| **Community** | Groups → posts → comments/likes; users flag, moderators hide. |
| **Transport** | Students host rides with seats; others join/leave; auto `full`. |
| **Payments (optional)** | Razorpay order for a slot → HMAC signature verified server-side → slot marked occupied. Disabled (503) unless keys present. |

## 5. Data model (ER sketch)

```
users 1──∞ properties 1──∞ slots
  │            │ 1──∞ reviews ∞──1 users
  │            └ 1──∞ tenants
  ├ 1──∞ community_posts ∞──1 community_groups ∞──∞ users (group_members)
  │            └ 1──∞ post_comments
  ├ 1──∞ transport_rides ∞──∞ users (ride_passengers)
  └ 1──∞ payments ∞──1 slots
rent_trends (area, type, month, avg_rent)      services (category, area, rating)
otp_codes (identifier, code, expires_at)
```

## 6. Configuration matrix

| Variable | Default | Purpose |
|----------|---------|---------|
| `USE_SQLITE` | `true` | SQLite file DB (`backend/campusnest.db`) vs Postgres |
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/campusnest` | used when `USE_SQLITE=false` |
| `SECRET_KEY` | dev key | JWT signing key — change in production |
| `DEBUG` | `true` | demo OTP + verbose logs + demo creds on `/` |
| `DEMO_OTP` | `1234` | OTP accepted in DEBUG |
| `SEED_DEMO_DATA` | `true` | seed on first start if DB empty |
| `ALLOWED_ORIGINS` | localhost:5173, Netlify URL | CORS |
| `RAZORPAY_KEY_ID/SECRET` | empty | enable payments |

## 7. Deployment

* **Local / demo:** `uvicorn backend.main:app --reload` (SQLite, auto-seed).
* **Docker:** `docker compose up --build` → API on :8000 + Postgres 16.
* **Render / Railway / Fly:** root dir = repo, build `pip install -r backend/requirements.txt`,
  start `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`, set `USE_SQLITE=false`
  + `DATABASE_URL` + `SECRET_KEY` + `ALLOWED_ORIGINS`.
* **Frontend:** Netlify (`npm run build`, publish `dist/`, env `VITE_API_URL=https://<api-host>`).

## 8. Future scope hooks

* Real SMS/email OTP → implement provider call inside `auth.issue_otp`.
* WebSockets chat → new router using the same JWT dependency.
* Map search → `/properties` already supports bounding-box (`min_lat…max_lng`) filters.
* AI recommendations → extend `/properties?sort=recommended` scoring in `routers/properties.py`.
