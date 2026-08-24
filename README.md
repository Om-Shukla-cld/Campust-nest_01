# Campust-nest_01

//deployment link is coming soon...............


  # 🏠 CampusNest – Student Housing & Community Platform

🚀 **By Team TripleLoop**

CampusNest is a full-stack intelligent housing ecosystem built for students — combining property discovery, roommate matching, community interaction, and smart living tools into one seamless platform.

---

## 🎯 Problem

Students face major challenges while finding accommodation:

* ❌ Unverified and scattered listings
* ❌ No roommate compatibility insights
* ❌ Lack of community & trusted reviews
* ❌ No transparency in pricing or facilities

At the same time, property owners struggle with:

* ❌ Managing listings efficiently
* ❌ Reaching the right tenants
* ❌ Handling approvals and communication

---

## 💡 Solution

CampusNest provides a centralized, smart, and interactive platform that enables:

* 🏠 Verified housing discovery
* 🤝 Roommate compatibility matching
* 💬 Community-driven interaction
* 📊 Data-backed decision tools
* 🛠️ Owner & moderator management systems

---

## 🏗️ Architecture Overview

```
Frontend (React + Vite + Tailwind)
        ↓
API Layer (FastAPI)
        ↓
Database (SQLite / PostgreSQL)
        ↓
Auth Layer (JWT + OTP)
```

---

## 🛠️ Tech Stack

### 🎨 Frontend

* ⚛️ React (Vite)
* 🎨 Tailwind CSS
* 🎬 Framer Motion

### ⚡ Backend

* FastAPI
* JWT Authentication + OTP

### 🗄️ Database

* SQLite (default)
* PostgreSQL (production-ready)

---

## 🚀 Quick Start

### 🔹 Backend Setup

```bash
cd backend
pip install -r requirements.txt

uvicorn backend.main:app --reload --port 8000
```

* ✅ Database auto-created with demo data
* 🌐 API Docs: http://localhost:8000/docs

---

### 🔹 Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

* 🌐 App: http://localhost:5173

---

## 🔧 Environment Variables

### Backend `.env`

```env
USE_SQLITE=true
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/campusnest
SECRET_KEY=your-super-secret-key
DEBUG=true
DEMO_OTP=1234
```

### Frontend `.env`

```env
VITE_API_URL=http://localhost:8000
```

---

## 📁 Project Structure

```
campusnest/
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── auth.py
│   ├── config.py
│   ├── seed.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── utils/api.js
│   │   ├── components/
│   │   │   ├── LandingPage.jsx
│   │   │   ├── StudentDashboard.jsx
│   │   │   ├── OwnerDashboard.jsx
│   │   │   ├── ModeratorDashboard.jsx
│   │   │   ├── GuestDashboard.jsx
│   │   │   ├── CompareProperties.jsx
│   │   │   ├── RentAnalyzer.jsx
│   │   │   ├── SmartTransport.jsx
│   │   │   ├── CommunityHub.jsx
│   │   │   └── GetServices.jsx
│   │   └── index.css
```

---

## 🔑 Demo Credentials

| Role          | Credentials                   |
| ------------- | ----------------------------- |
| 👨‍🎓 Student | Reg No: 21BCE0001 + OTP: 1234 |
| 🏠 Owner      | Any phone + OTP: 1234         |
| 🛡️ Moderator | Phone: +910000000000          |
| 👀 Guest      | No login required             |

---

## 🌐 API Endpoints

| Method | Endpoint                   | Description        |
| ------ | -------------------------- | ------------------ |
| POST   | /auth/send-otp             | Send OTP           |
| POST   | /auth/student/login        | Student login      |
| POST   | /auth/owner/login          | Owner login        |
| GET    | /properties                | Fetch listings     |
| GET    | /properties/{id}           | Property details   |
| POST   | /properties/compare        | Compare properties |
| POST   | /reviews                   | Submit review      |
| GET    | /community/groups          | Community channels |
| GET    | /rent-trends               | Rent analytics     |
| GET    | /services                  | Local services     |
| PATCH  | /moderator/properties/{id} | Approve listings   |

📌 Full Docs: http://localhost:8000/docs

---

## ✨ Key Features

### 👨‍🎓 Student Features

* 🔍 Smart property browsing
* 🤝 Roommate matching
* 📊 Rent trend analysis
* 💬 Community hub (posts, groups)
* 🚌 Smart transport matching

### 🏠 Owner Features

* Add & manage properties
* Track tenants
* Listing approval workflow

### 🛡️ Moderator Features

* Approve/reject owners
* Moderate listings & reviews

---

## 🌍 Platform Highlights

* 🔐 JWT + OTP authentication
* 👥 Role-based access system
* 📈 Data-driven insights
* ⚡ Fast & scalable backend
* 🎨 Modern responsive UI

---

## 🧪 Testing

### Backend

* Open Swagger UI
* Test endpoints
* Verify JSON responses

### Frontend

* Check UI rendering
* Inspect console (F12)
* Verify API calls (Network tab)

---

## 🗄️ Database

### Default

* SQLite (`campusnest.db`) — zero setup

### PostgreSQL

```bash
createdb campusnest
```

Update `.env` to switch.

---

## ⚠️ Common Issues & Fixes

### ❌ CORS Error

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### ❌ White Screen

* Check console errors
* Verify imports
* Ensure components render

---

## 🚀 Future Scope

* 🔐 Google / OAuth login
* 💬 Real-time chat (WebSockets)
* 📍 Map integration
* ⭐ AI recommendations
* 📱 Mobile app

---

## 🏆 Hackathon Edge

* ✅ Solves real student problem
* ✅ Multi-role system (Student / Owner / Moderator / Guest)
* ✅ Combines housing + community + analytics
* ✅ Fully working full-stack app
* ✅ Scalable & clean architecture

---

## 🎤 Demo Flow (For Judges)

1. Login as Student
2. Browse properties
3. Compare listings
4. View rent trends
5. Explore community
6. Switch to Owner → add property
7. Switch to Moderator → approve

---

## 👥 Team – TripleLoop 🚀

* Aradhana Singh – 24BCE10998
* Sanskar Gupta – 24BCE11374
* Om Shukla – 24BSA10205(team lead)

---
---
project link

https://campus-nest.netlify.app/
----

## 📜 License

MIT License

---

## 🌟 Final Note

CampusNest is not just a housing platform —
it’s a complete student living ecosystem designed for **transparency, trust, and smarter decisions**.
