# 🏠 CampusNest – Student Housing & Community Platform

🚀 **By Team TripleLoop** · Live frontend: https://campus-nest.netlify.app/

CampusNest is a full-stack intelligent housing ecosystem built for students — combining property discovery, roommate matching, community interaction, and smart living tools into one seamless platform.

---

## 🎯 Problem

Students face major challenges while finding accommodation:

- ❌ Unverified and scattered listings
- ❌ No roommate compatibility insights
- ❌ Lack of community & trusted reviews
- ❌ No transparency in pricing or facilities

At the same time, property owners struggle with:

- ❌ Managing listings efficiently
- ❌ Reaching the right tenants
- ❌ Handling approvals and communication

## 💡 Solution

CampusNest provides a centralized, smart, and interactive platform that enables:

- 🏠 Verified housing discovery (moderator-approved listings)
- 🤝 Roommate compatibility matching (weighted lifestyle score)
- 💬 Community-driven interaction (groups, posts, comments, likes)
- 📊 Data-backed decision tools (compare, rent trends, "is this rent fair?")
- 🚌 Smart transport (shared rides)
- 🛠️ Owner & moderator management systems

---

## 🏗️ Architecture Overview

```
Frontend (React + Vite + Tailwind + Framer Motion)
        ↓  fetch + Bearer JWT
API Layer (FastAPI · Pydantic v2 · SQLAlchemy 2)
        ↓
Database (SQLite by default · PostgreSQL for production)
        ↓
Auth Layer (OTP → JWT, role-based: student / owner / moderator / guest)
```

📐 Full design (modules, auth flow, data model, domain flows): **[ARCHITECTURE.md](ARCHITECTURE.md)**

## 🛠️ Tech Stack

| Layer | Tech |
|-------|------|
| 🎨 Frontend | React (Vite), Tailwind CSS, Framer Motion, Leaflet/OpenStreetMap (map) · Syne + Inter fonts, slate/gold theme matching https://campus-nest.netlify.app, VIT Bhopal campus photo (`frontend/public/vit-bg.jpg`) as backdrop |
| ⚡ Backend | FastAPI, Pydantic v2, SQLAlchemy 2, PyJWT, Uvicorn |
| 🗄️ Database | SQLite (default, zero setup) · PostgreSQL (production) |
| 🔐 Auth | OTP (demo `1234`) + JWT (HS256) |
| 💳 Payments (optional) | Razorpay |

---

## 🚀 Quick Start — run the project

### Prerequisites

- Python **3.10+** (tested on 3.12 / 3.13)
- Node.js **18+** (for the frontend)
- (optional) Docker, PostgreSQL

### 🔹 Step 1 — Backend

```bash
# 1. go to the project root (the folder that contains backend/)
cd campusnest-update

# 2. create & activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. install dependencies
pip install -r backend/requirements.txt

# 4. create your env file (defaults are fine for local/demo)
cp backend/.env.example backend/.env

# 5. start the API  (run from the project root, NOT from inside backend/)
uvicorn backend.main:app --reload --port 8000
```

✅ On first start the database is **auto-created and seeded with demo data**
(`backend/campusnest.db`).

- 🌐 API root (shows demo credentials): http://localhost:8000/
- 📘 Swagger docs: http://localhost:8000/docs
- ❤️ Health: http://localhost:8000/health

> Shortcut: `make setup && make run` does steps 2–5.

### 🔹 Step 2 — Frontend

```bash
# in a second terminal, from the project root
cd frontend
npm install
npm run dev          # .env already points at http://localhost:8000 (edit VITE_API_URL for a remote API)
```

🌐 App: http://localhost:5173 — log in with the demo credentials below (OTP `1234`).

The React app (`frontend/src/components/`) covers every screen: `LandingPage` + `Login` (OTP login, `/login`),
`StudentDashboard` (browse · roommates · **ProfileBuilder**), `OwnerDashboard`, `ModeratorDashboard`, `GuestDashboard`,
`CompareProperties`, `RentAnalyzer`, `SmartTransport`, `CommunityHub`, `GetServices`, plus **`RoomMap`** (OpenStreetMap /
Leaflet map of listings — toggle *Grid / Map* on the browse screen or open `/guest?view=map`) and **`PaymentButton`**
(Razorpay slot booking inside the property detail — shown when `RAZORPAY_KEY_ID/SECRET` are set on the backend).
All calls go through `src/utils/api.js` (JWT in localStorage, `Authorization: Bearer …`).

**Look & feel** mirrors the deployed site: full-bleed VIT Bhopal campus photo (`public/vit-bg.jpg`, from Wikimedia Commons)
with a dark overlay + glass cards on the landing/login pages, and the same photo softly behind the app pages;
Syne display font + Inter body; slate-900 primary with gold (`#f59e0b`) accent. Replace `public/vit-bg.jpg` to use your own campus photo.

`frontend-additions/` keeps the original standalone versions of `api.js`, `Login.jsx`, `ProfileBuilder.jsx`,
`RoomMap.jsx`, `PaymentButton.jsx` — handy if you want to drop them into another React app.

### 🔹 Step 3 — Verify it works

```bash
# run the backend smoke tests (auth, listings, compare, reviews, owner→moderator flow,
# community, roommates, transport, analytics, services)
pytest backend/tests -q
```

Or by hand:

```bash
curl -X POST localhost:8000/auth/send-otp -H 'content-type: application/json' \
     -d '{"identifier":"21BCE0001","role":"student"}'
curl -X POST localhost:8000/auth/student/login -H 'content-type: application/json' \
     -d '{"reg_no":"21BCE0001","otp":"1234"}'          # → access_token
curl "localhost:8000/properties?max_rent=7000&sort=rent_asc"
```

### 🔹 Alternative — Docker (API + PostgreSQL)

```bash
docker compose up --build
# API on http://localhost:8000, Postgres on :5432, demo data seeded automatically
```

### 🔹 Useful commands

| Command | What it does |
|---------|--------------|
| `make run` | start API with auto-reload |
| `cd frontend && npm run dev` | start the React app on :5173 |
| `make test` | run tests |
| `python -m backend.seed` | seed demo data if DB is empty |
| `python -m backend.seed --reset` | **drop** and re-seed the database |
| `docker compose up --build` | API + Postgres |

---

## 🔧 Environment Variables

### Backend `backend/.env` (see `.env.example`)

```env
USE_SQLITE=true                  # false → use DATABASE_URL (PostgreSQL)
SQLITE_PATH=campusnest.db
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/campusnest
SECRET_KEY=your-super-secret-key  # change in production
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DEBUG=true                       # demo OTP accepted + logged; demo creds shown on /
DEMO_OTP=1234
OTP_EXPIRE_MINUTES=10
SEED_DEMO_DATA=true
ALLOWED_ORIGINS=http://localhost:5173,https://campus-nest.netlify.app
RAZORPAY_KEY_ID=                 # optional
RAZORPAY_KEY_SECRET=             # optional
```

### Frontend `frontend/.env`

```env
VITE_API_URL=http://localhost:8000
```

---

## 📁 Project Structure

```
campusnest-update/
├── README.md
├── ARCHITECTURE.md
├── Makefile
├── docker-compose.yml
├── backend/
│   ├── main.py            # FastAPI app, CORS, routers, startup seed
│   ├── config.py          # settings from .env
│   ├── database.py        # engine / session
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   ├── auth.py            # OTP + JWT + role guards
│   ├── seed.py            # demo data
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   ├── routers/
│   │   ├── auth.py  profiles.py  properties.py  reviews.py
│   │   ├── community.py  roommates.py  transport.py  analytics.py
│   │   ├── services.py  owner.py  moderator.py  payments.py
│   └── tests/test_api.py
│
├── frontend-additions/     # standalone copies of the reusable React pieces (see Step 2)
│   ├── lib/api.js
│   ├── pages/Login.jsx · ProfileBuilder.jsx
│   └── components/RoomMap.jsx · PaymentButton.jsx
│
└── frontend/               # React + Vite + Tailwind + Framer Motion
    ├── package.json · vite.config.js · tailwind.config.js · .env (VITE_API_URL)
    └── src/
        ├── main.jsx · App.jsx (routes, auth context) · index.css
        ├── utils/api.js           # API client (JWT)
        └── components/
            ├── LandingPage.jsx        StudentDashboard.jsx
            ├── OwnerDashboard.jsx     ModeratorDashboard.jsx
            ├── GuestDashboard.jsx     CompareProperties.jsx
            ├── RentAnalyzer.jsx       SmartTransport.jsx
            ├── CommunityHub.jsx       GetServices.jsx
            ├── RoomMap.jsx            PaymentButton.jsx
            ├── ProfileBuilder.jsx     Login.jsx
            └── Navbar.jsx · PropertyBrowser.jsx · shared.jsx · Toast.jsx
```

---

## 🔑 Demo Credentials (DEBUG mode, OTP = `1234`)

| Role | Credentials |
|------|-------------|
| 👨‍🎓 Student | Reg No: `21BCE0001` + OTP `1234` (any new reg no auto-creates a student) |
| 🏠 Owner | Phone: `+919800000001` (verified, has listings & tenants) · or any phone + OTP `1234` |
| 🛡️ Moderator | Phone: `+910000000000` + OTP `1234` |
| 👀 Guest | No login required — all `GET /properties`, `/community/*`, `/rent-trends`, `/services` are public |

---

## 🌐 API Endpoints

📌 Full interactive docs: http://localhost:8000/docs

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/send-otp` | – | Send OTP (`identifier`, `role`) |
| POST | `/auth/student/login` | – | Student login (`reg_no`, `otp`) → JWT |
| POST | `/auth/owner/login` | – | Owner / moderator login (`phone`, `otp`) → JWT |
| GET | `/auth/me` | 🔒 | Current user |
| GET/PUT | `/profile/me` | 🔒 | View / update lifestyle profile |
| GET | `/properties` | – | Search, filter (`q,type,area,gender,min_rent,max_rent,max_distance,amenities,min_rating`), sort, paginate |
| GET | `/properties/{id}` | – | Property details (slots, reviews, rating) |
| GET | `/properties/featured` · `/properties/areas` | – | Featured listings · area list |
| POST | `/properties/compare` | – | Compare 2–4 properties → best value / cheapest / closest / safest |
| POST | `/reviews` | 🔒 | Submit (or update) a review |
| POST | `/reviews/{id}/flag` | 🔒 | Report a review |
| GET | `/community/groups` | – | Community channels |
| GET | `/community/groups/{id}/posts` · `/community/feed` | – | Posts in a group · global feed |
| POST | `/community/posts` · `/posts/{id}/like` · `/posts/{id}/comments` | 🔒 | Post, like, comment |
| GET | `/roommates/matches` | 🔒 student | Compatibility-ranked roommates |
| GET | `/roommates/browse` | – | Browse students looking for roommates |
| GET/POST | `/transport/rides` | –/🔒 | List / create shared rides |
| POST | `/transport/rides/{id}/join` · `/leave` | 🔒 | Join / leave a ride |
| GET | `/rent-trends` | – | Monthly rent trends (`area`, `type`, `months`) |
| GET | `/rent-trends/areas` | – | Live per-area summary |
| GET | `/rent-trends/analyze?rent=&area=&type=` | – | Is this rent fair? verdict + tip |
| GET | `/services` · `/services/categories` | – | Local services |
| GET | `/owner/dashboard` | 🔒 owner | Stats |
| GET/POST | `/owner/properties` | 🔒 owner | My listings / add listing (→ pending) |
| PATCH/DELETE | `/owner/properties/{id}` | 🔒 owner | Edit / remove |
| GET/POST/PATCH/DELETE | `/owner/tenants` | 🔒 owner | Tenant tracking |
| GET | `/moderator/dashboard` | 🔒 mod | Queue counts |
| GET | `/moderator/properties?status=pending` | 🔒 mod | Moderation queue |
| PATCH | `/moderator/properties/{id}` | 🔒 mod | `{status: approved\|rejected, reason}` |
| GET/PATCH | `/moderator/owners` | 🔒 mod | Approve / deactivate owners |
| GET/PATCH | `/moderator/reviews` · `/moderator/posts` | 🔒 mod | Moderate flagged content |
| GET | `/payments/status` · POST `/create-order` · `/verify` | 🔒 | Razorpay (503 unless configured) |

---

## ✨ Key Features

**👨‍🎓 Student** — smart property browsing & filters · compare listings · roommate matching · rent trend analysis · community hub · shared transport · local services

**🏠 Owner** — add & manage properties (slots/beds) · track tenants & rent status · listing approval workflow · dashboard stats

**🛡️ Moderator** — approve/reject listings · verify owners · moderate reviews & posts · feature listings

**🌍 Platform** — 🔐 OTP + JWT auth · 👥 role-based access · 📈 data-driven insights · ⚡ fast FastAPI backend · 🎨 modern responsive UI

---

## 🧪 Testing

**Backend**
```bash
pytest backend/tests -q        # 11 end-to-end tests against an isolated SQLite DB
```
Or open Swagger UI → *Authorize* with a token from `/auth/student/login` → try endpoints.

**Frontend** — check UI rendering, inspect console (F12), verify API calls in the Network tab.

## 🗄️ Database

- **Default:** SQLite `backend/campusnest.db` — zero setup, auto-created.
- **PostgreSQL:** `createdb campusnest`, then in `backend/.env` set `USE_SQLITE=false` and `DATABASE_URL=postgresql://user:pass@host:5432/campusnest`. Tables are created automatically on startup; the same models run on both.
- Reset anytime: `python -m backend.seed --reset`.

## 🚀 Deployment

- **API (Render / Railway / Fly):** build `pip install -r backend/requirements.txt`, start `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`, env: `USE_SQLITE=false`, `DATABASE_URL`, `SECRET_KEY`, `ALLOWED_ORIGINS=https://campus-nest.netlify.app`.
- **Frontend (Netlify):** build `npm run build`, publish `dist/`, env `VITE_API_URL=https://<your-api-host>`.

## ⚠️ Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: backend` | Run uvicorn from the **project root**: `uvicorn backend.main:app` (not from inside `backend/`). |
| CORS error in browser | Add your frontend origin to `ALLOWED_ORIGINS` in `backend/.env` (or `*` for demo). |
| `psycopg2` build error | Upgrade pip (`pip install -U pip`) — wheels exist for Python 3.8–3.13. |
| OTP rejected | In DEBUG mode use `1234`; with `DEBUG=false` the OTP is printed in the server console. |
| Want fresh demo data | `python -m backend.seed --reset` |
| White screen (frontend) | Check console errors, verify imports, ensure `VITE_API_URL` points to a running API. |

## 🚀 Future Scope

🔐 Google / OAuth login · 💬 Real-time chat (WebSockets) · 📍 Richer map integration · ⭐ AI recommendations · 📱 Mobile app · 📲 Real SMS OTP provider

## 🏆 Hackathon Edge

✅ Solves a real student problem · ✅ Multi-role system (Student / Owner / Moderator / Guest) · ✅ Housing + community + analytics in one · ✅ Fully working full-stack app with seeded demo · ✅ Scalable & clean architecture

## 🎤 Demo Flow (For Judges)

1. Login as **Student** (`21BCE0001` / `1234`) → browse & filter properties
2. **Compare** 2–3 listings → see best value / cheapest / safest
3. **Rent Analyzer** → trends + "is ₹8000 fair for a PG in Kothri Kalan?"
4. **Roommate matches** → compatibility scores
5. Explore **Community** & **Transport**
6. Switch to **Owner** (`+919800000001`) → add a property (goes to *pending*)
7. Switch to **Moderator** (`+910000000000`) → approve it → it appears publicly

## 👥 Team – TripleLoop 🚀

- Aradhana Singh – 24BCE10998
- Sanskar Gupta – 24BCE11374
- Om Shukla – 24BSA10205 (team lead)

## 📜 License

MIT License

---

🌟 *CampusNest is not just a housing platform — it's a complete student living ecosystem designed for transparency, trust, and smarter decisions.*
