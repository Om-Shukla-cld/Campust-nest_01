"""
Demo data seeder. Runs automatically on startup when the database is empty
(SEED_DEMO_DATA=true). Can also be run manually:

    python -m backend.seed          # seed if empty
    python -m backend.seed --reset  # drop everything and re-seed
"""
import sys
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from . import models
from .config import settings
from .database import Base, SessionLocal, engine
from .models import utcnow

# VIT Bhopal campus (Kothri Kalan) — all demo geo data is around here
CAMPUS_LAT, CAMPUS_LNG = 23.0776, 76.8516


def _users(db: Session) -> dict:
    users = {
        "student1": models.User(
            role="student", reg_no="21BCE0001", name="Aarav Sharma", email="aarav@vitbhopal.ac.in",
            phone="+919876500001", veg="veg", smoker="no", sleep="night-owl", cleanliness="tidy",
            study="quiet", budget=7000, about_me="CSE 3rd year. Love coding late nights, keep my room clean.",
        ),
        "student2": models.User(
            role="student", reg_no="24BCE10998", name="Aradhana Singh", email="aradhana@vitbhopal.ac.in",
            phone="+919876500002", veg="veg", smoker="no", sleep="early-bird", cleanliness="tidy",
            study="quiet", budget=6500, about_me="Early riser, gym at 6am. Looking for a calm roommate.",
        ),
        "student3": models.User(
            role="student", reg_no="24BCE11374", name="Sanskar Gupta", email="sanskar@vitbhopal.ac.in",
            phone="+919876500003", veg="non-veg", smoker="no", sleep="night-owl", cleanliness="average",
            study="music", budget=8000, about_me="Music + hackathons. Chill about most things.",
        ),
        "student4": models.User(
            role="student", reg_no="24BSA10205", name="Om Shukla", email="om@vitbhopal.ac.in",
            phone="+919876500004", veg="eggetarian", smoker="occasionally", sleep="flexible",
            cleanliness="relaxed", study="group", budget=9000, about_me="Team lead @ TripleLoop. Group study fan.",
        ),
        "student5": models.User(
            role="student", reg_no="23BCE10420", name="Priya Verma", email="priya@vitbhopal.ac.in",
            phone="+919876500005", veg="veg", smoker="no", sleep="night-owl", cleanliness="tidy",
            study="quiet", budget=7500, about_me="Night owl, quiet, love plants.",
        ),
        "student6": models.User(
            role="student", reg_no="23BCE10777", name="Rohan Mehta", email="rohan@vitbhopal.ac.in",
            phone="+919876500006", veg="non-veg", smoker="yes", sleep="night-owl", cleanliness="relaxed",
            study="music", budget=6000, about_me="Gamer. Flexible with everything.",
        ),
        "owner1": models.User(role="owner", name="Rajesh Patel", phone="+919800000001", email="rajesh.pg@gmail.com", is_verified=True),
        "owner2": models.User(role="owner", name="Sunita Yadav", phone="+919800000002", email="sunita.homes@gmail.com", is_verified=True),
        "owner3": models.User(role="owner", name="Mohd. Imran", phone="+919800000003", email="imran.stays@gmail.com", is_verified=False),
        "moderator": models.User(role="moderator", name="CampusNest Moderator", phone=settings.MODERATOR_PHONE, email="mod@campusnest.app", is_verified=True),
    }
    for u in users.values():
        db.add(u)
    db.flush()
    return users


PROPERTIES = [
    # name, type, gender, area, rent, deposit, other, dist, safety, slots, amenities, status, featured, owner, lat_off, lng_off, desc
    ("Shree Krishna Boys PG", "PG", "boys", "Kothri Kalan", 6500, 5000, 500, 0.8, 4.5, 12,
     ["wifi", "mess", "laundry", "power-backup", "cctv", "ro-water"], "approved", True, "owner1", 0.004, 0.003,
     "Well maintained boys PG 10 min walk from campus gate. 3 meals included."),
    ("Sunita Girls Hostel", "Hostel", "girls", "Kothri Kalan", 7500, 7500, 300, 1.2, 4.8, 20,
     ["wifi", "mess", "laundry", "cctv", "warden", "ac", "ro-water"], "approved", True, "owner2", -0.006, 0.005,
     "Secure girls hostel with 24x7 warden and biometric entry."),
    ("Green View 2BHK Flat", "2BHK", "any", "Ashta Road", 14000, 20000, 1500, 2.5, 4.2, 4,
     ["wifi", "parking", "balcony", "power-backup", "furnished"], "approved", False, "owner1", 0.015, -0.012,
     "Fully furnished 2BHK ideal for 4 students sharing. Near Ashta road bus stop."),
    ("Campus Corner Shared Room", "Shared Room", "boys", "Kothri Kalan", 4500, 3000, 400, 0.5, 4.0, 8,
     ["wifi", "mess", "ro-water"], "approved", False, "owner1", 0.002, -0.004,
     "Budget-friendly shared rooms right outside the campus."),
    ("Imperial Studio Apartments", "Studio", "any", "Sehore Bypass", 9500, 15000, 1000, 4.0, 4.3, 6,
     ["wifi", "ac", "parking", "gym", "furnished", "power-backup"], "approved", True, "owner2", 0.03, 0.02,
     "Premium studio units with AC and gym access. Shuttle to campus every hour."),
    ("Maa Sharda Girls PG", "PG", "girls", "Ashta Road", 6000, 5000, 300, 2.0, 4.6, 10,
     ["wifi", "mess", "cctv", "warden", "laundry"], "approved", False, "owner2", -0.012, -0.01,
     "Homely girls PG run by a family, home-cooked food."),
    ("Riverside 1BHK", "1BHK", "any", "Sehore Bypass", 8000, 10000, 800, 3.5, 3.8, 2,
     ["parking", "balcony", "semi-furnished"], "approved", False, "owner3", 0.025, -0.02,
     "Quiet 1BHK for two students, close to the river walk."),
    ("Scholars Den Boys Hostel", "Hostel", "boys", "Kothri Kalan", 7000, 6000, 500, 1.0, 4.4, 24,
     ["wifi", "mess", "gym", "study-room", "cctv", "power-backup", "laundry"], "approved", False, "owner3", -0.003, 0.008,
     "Large hostel with dedicated study room and mini gym."),
    ("New Horizon PG (Pending)", "PG", "any", "Ashta Road", 5800, 4000, 300, 2.2, 4.0, 10,
     ["wifi", "mess"], "pending", False, "owner3", 0.01, 0.015,
     "Newly opened PG — awaiting moderator verification."),
    ("Lakeview Flats 3BHK (Pending)", "2BHK", "any", "Sehore Bypass", 18000, 30000, 2000, 4.5, 4.1, 6,
     ["wifi", "parking", "furnished", "ac", "balcony"], "pending", False, "owner2", 0.035, 0.03,
     "Spacious flat for a group of 6. Submitted for approval."),
]

REVIEWS = [
    (0, "student1", 4.5, "Food is genuinely good and the owner is responsive. WiFi drops sometimes.", False),
    (0, "student3", 4.0, "Clean rooms, good location. Power backup works.", False),
    (0, "student6", 3.5, "Decent for the price. Curfew at 11pm is strict.", True),
    (1, "student2", 5.0, "Safest place I've stayed. Warden is kind and food is homely.", False),
    (1, "student5", 4.5, "AC rooms are worth it in summer. Laundry is on time.", False),
    (2, "student4", 4.0, "Great for a group of friends. A bit far from campus.", False),
    (3, "student6", 3.0, "Cheap but cramped. OK if you're on a tight budget.", False),
    (4, "student3", 4.5, "Premium feel. The shuttle is a life saver.", False),
    (5, "student5", 4.5, "Aunty's food is the best. Feels like home.", False),
    (7, "student1", 4.0, "Study room is quiet, gym is basic but fine.", False),
    (7, "student4", 4.5, "Best hostel vibe for group study sessions.", False),
    (6, "student6", 2.5, "Owner was slow to fix the geyser. Location is peaceful though.", True),
]

GROUPS = [
    ("Housing Help", "housing-help", "Ask anything about PGs, flats, brokers and deposits.", "housing", "🏠"),
    ("Roommate Finder", "roommate-finder", "Post what you're looking for in a roommate.", "roommates", "🤝"),
    ("Ride Share", "ride-share", "Share cabs/autos to the station, airport or city.", "transport", "🚕"),
    ("Campus Events", "campus-events", "Fests, hackathons, club meetups.", "events", "🎉"),
    ("Buy & Sell", "buy-sell", "Books, cycles, mattresses, induction stoves…", "general", "🛒"),
    ("Mess & Food Reviews", "food", "Where to eat, what to avoid.", "general", "🍱"),
]

POSTS = [
    (0, "student1", "Is ₹7000 fair for a single room in Kothri Kalan?", "Owner is asking 7k + 500 electricity for a single non-AC. Worth it or should I look further?", ["rent", "kothri-kalan"]),
    (0, "student4", "Deposit refund tips", "Always take a written receipt and photos of the room on day 1. Saved me ₹4000 last year.", ["deposit", "tips"]),
    (1, "student2", "Looking for a tidy early-riser roommate (girls)", "Sunita Girls Hostel, AC room, sharing from August. DM if you're an early bird!", ["girls", "hostel"]),
    (1, "student3", "Need 1 more for Green View 2BHK", "We're 3 guys, need a 4th. ₹3500/head. Night owls welcome.", ["2bhk", "ashta-road"]),
    (2, "student5", "Cab to Bhopal Junction Friday 5pm", "Sharing an Ola, 2 seats left. ₹150/head.", ["station", "friday"]),
    (3, "student4", "TripleLoop hackathon demo day!", "Come see CampusNest live in the AB-1 auditorium at 3pm.", ["hackathon"]),
    (4, "student6", "Selling study table + chair", "Barely used, ₹1200. Pickup from Scholars Den.", ["furniture"]),
    (5, "student1", "Shree Krishna PG mess review", "Dal is great, rotis slightly dry. 4/5 overall.", ["mess"]),
]

RIDES = [
    ("student5", "VIT Bhopal Main Gate", "Bhopal Junction", 1, 17, "cab", 4, 150, "Leaving sharp at 5."),
    ("student3", "VIT Bhopal Main Gate", "Raja Bhoj Airport", 2, 6, "cab", 3, 400, "Early flight, please be on time."),
    ("student1", "Kothri Kalan", "DB Mall, Bhopal", 3, 11, "auto", 3, 80, "Weekend shopping."),
    ("student4", "VIT Bhopal Main Gate", "Sehore Bus Stand", 1, 9, "bus", 6, 40, "Campus bus, will share seat info."),
]

SERVICES = [
    ("Sharma Tiffin Service", "tiffin", "Home-style veg thali delivered to PGs twice a day.", "+919700000001", "Kothri Kalan", 4.6, "₹2500/month", "7am–9pm"),
    ("QuickWash Laundry", "laundry", "Wash + iron, pickup and drop at hostel gates.", "+919700000002", "Kothri Kalan", 4.3, "₹10/piece", "8am–8pm"),
    ("Dr. Meena Clinic", "medical", "General physician, student discount on consultation.", "+919700000003", "Ashta Road", 4.7, "₹200/visit", "10am–2pm, 5pm–9pm"),
    ("Apna Medical Store", "medical", "24x7 pharmacy near campus.", "+919700000004", "Kothri Kalan", 4.4, "—", "24x7"),
    ("Campus Cycle Repair", "repair", "Cycle & bike repair, puncture on call.", "+919700000005", "Kothri Kalan", 4.2, "₹50+", "9am–7pm"),
    ("Bhopal Electric Works", "repair", "Electrician & plumber, same-day service.", "+919700000006", "Ashta Road", 4.1, "₹150/visit", "9am–6pm"),
    ("Annapurna Mess", "mess", "Monthly mess with veg & non-veg options.", "+919700000007", "Kothri Kalan", 4.0, "₹3000/month", "7am–10pm"),
    ("Zoom Stationery & Xerox", "stationery", "Printouts, binding, lab records.", "+919700000008", "Kothri Kalan", 4.5, "₹2/page", "8am–10pm"),
    ("FreshMart Grocery", "grocery", "Daily essentials, free delivery above ₹300.", "+919700000009", "Sehore Bypass", 4.2, "—", "7am–11pm"),
    ("SafeRide Cabs", "transport", "Pre-booked cabs to station/airport, student rates.", "+919700000010", "Kothri Kalan", 4.3, "₹600 to station", "24x7"),
    ("FitZone Gym", "fitness", "Student monthly plan, cardio + weights.", "+919700000011", "Ashta Road", 4.4, "₹800/month", "6am–10pm"),
]

AREAS = {"Kothri Kalan": {"PG": 6200, "Hostel": 7100, "Shared Room": 4300},
         "Ashta Road": {"PG": 5900, "2BHK": 13500, "1BHK": 7800},
         "Sehore Bypass": {"Studio": 9200, "1BHK": 7700, "2BHK": 16500}}


def _months(n: int):
    now = utcnow().replace(day=1)
    out = []
    for i in range(n - 1, -1, -1):
        y, m = now.year, now.month - i
        while m <= 0:
            y, m = y - 1, m + 12
        out.append(f"{y:04d}-{m:02d}")
    return out


def seed(db: Session) -> None:
    users = _users(db)

    props = []
    for (name, ptype, gender, area, rent, dep, other, dist, safety, slots, amen, status, featured,
         owner_key, dlat, dlng, desc) in PROPERTIES:
        p = models.Property(
            owner_id=users[owner_key].id, name=name, type=ptype, gender=gender, area=area,
            city="Bhopal", address=f"{area}, Sehore, Madhya Pradesh", lat=CAMPUS_LAT + dlat,
            lng=CAMPUS_LNG + dlng, rent=rent, deposit=dep, other_price=other, distance_km=dist,
            safety_score=safety, amenities=amen, total_slots=slots, status=status,
            is_featured=featured, description=desc,
            images=[f"https://picsum.photos/seed/campusnest{len(props)+1}/800/500"],
        )
        db.add(p)
        db.flush()
        for i in range(slots):
            db.add(models.Slot(property_id=p.id, label=f"Bed {i+1}", rent_per_slot=rent, is_occupied=(i % 3 == 0)))
        props.append(p)

    for idx, ukey, stars, comment, anon in REVIEWS:
        db.add(models.Review(property_id=props[idx].id, user_id=users[ukey].id, stars=stars, comment=comment, is_anonymous=anon))

    # tenants for owner1 (demo owner dashboard)
    db.add(models.Tenant(property_id=props[0].id, student_id=users["student1"].id, name="Aarav Sharma",
                         reg_no="21BCE0001", phone="+919876500001", rent=6500, rent_status="paid",
                         start_date=utcnow() - timedelta(days=90)))
    db.add(models.Tenant(property_id=props[0].id, student_id=users["student3"].id, name="Sanskar Gupta",
                         reg_no="24BCE11374", phone="+919876500003", rent=6500, rent_status="due",
                         start_date=utcnow() - timedelta(days=40)))
    db.add(models.Tenant(property_id=props[2].id, student_id=users["student4"].id, name="Om Shukla",
                         reg_no="24BSA10205", phone="+919876500004", rent=3500, rent_status="overdue",
                         start_date=utcnow() - timedelta(days=120)))

    groups = []
    for name, slug, desc, cat, icon in GROUPS:
        g = models.CommunityGroup(name=name, slug=slug, description=desc, category=cat, icon=icon)
        db.add(g)
        db.flush()
        groups.append(g)
    for g in groups:
        for ukey in ("student1", "student2", "student3", "student4"):
            db.add(models.GroupMember(group_id=g.id, user_id=users[ukey].id))
    for i, (gi, ukey, title, content, tags) in enumerate(POSTS):
        p = models.CommunityPost(group_id=groups[gi].id, user_id=users[ukey].id, title=title,
                                 content=content, tags=tags, likes=(i * 7) % 23,
                                 created_at=utcnow() - timedelta(hours=i * 5))
        db.add(p)
        db.flush()
        if i % 2 == 0:
            db.add(models.PostComment(post_id=p.id, user_id=users["student5"].id, content="Following this!"))

    for ukey, o, d, days, hour, mode, seats, cost, notes in RIDES:
        dt = (utcnow() + timedelta(days=days)).replace(hour=hour, minute=0, second=0, microsecond=0)
        db.add(models.TransportRide(host_id=users[ukey].id, origin=o, destination=d, depart_at=dt,
                                    mode=mode, seats_total=seats, seats_taken=1, cost_per_head=cost, notes=notes))

    for i, (name, cat, desc, phone, area, rating, price, hours) in enumerate(SERVICES):
        db.add(models.Service(name=name, category=cat, description=desc, phone=phone, area=area,
                              address=f"{area}, Sehore", lat=CAMPUS_LAT + (i % 5) * 0.004,
                              lng=CAMPUS_LNG + (i % 3) * 0.005, rating=rating, price_range=price, open_hours=hours))

    months = _months(12)
    for area, types in AREAS.items():
        for ptype, base in types.items():
            for mi, month in enumerate(months):
                # gentle upward drift + seasonal bump around admission season (Jul/Aug)
                seasonal = 400 if month.endswith(("-07", "-08")) else 0
                rent = int(base * (0.93 + mi * 0.007) + seasonal)
                db.add(models.RentTrend(area=area, property_type=ptype, month=month, avg_rent=rent,
                                        listings=5 + (mi * 3 + len(ptype)) % 9))

    db.commit()


def seed_if_empty() -> bool:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(models.User).first():
            return False
        seed(db)
        return True
    finally:
        db.close()


def reset_and_seed() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()


if __name__ == "__main__":
    if "--reset" in sys.argv:
        reset_and_seed()
        print("Database reset and seeded.")
    else:
        print("Seeded." if seed_if_empty() else "Database already has data — nothing to do.")
