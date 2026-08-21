"""
SQLAlchemy ORM models. Designed to run unchanged on SQLite (default) and
PostgreSQL — only portable column types are used (JSON instead of JSONB,
Integer PKs instead of UUIDs).
"""
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


def utcnow() -> datetime:
    """Naive UTC timestamp (portable across SQLite/Postgres)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ------------------------------------------------------------------ users ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    role = Column(String(20), nullable=False, default="student")  # student | owner | moderator
    name = Column(String(120))
    email = Column(String(200))
    phone = Column(String(20), index=True)     # owners / moderators log in with phone
    reg_no = Column(String(30), index=True)    # students log in with registration no
    college = Column(String(200), default="VIT Bhopal")
    avatar_url = Column(String(500))
    # owner verification (moderator approves owners before they can list)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    # lifestyle profile used by roommate matching
    veg = Column(String(20))           # veg | non-veg | eggetarian
    smoker = Column(String(20))        # yes | no | occasionally
    sleep = Column(String(20))         # early-bird | night-owl | flexible
    cleanliness = Column(String(20))   # tidy | average | relaxed
    study = Column(String(20))         # quiet | music | group
    budget = Column(Integer)           # monthly rent budget (INR)
    about_me = Column(Text)
    looking_for_roommate = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)

    properties = relationship("Property", back_populates="owner")
    reviews = relationship("Review", back_populates="user")


class OTPCode(Base):
    __tablename__ = "otp_codes"

    id = Column(Integer, primary_key=True)
    identifier = Column(String(100), index=True, nullable=False)  # phone or reg_no
    code = Column(String(10), nullable=False)
    purpose = Column(String(20), default="login")
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)


# ------------------------------------------------------------- properties ---
class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    type = Column(String(40), default="PG")  # PG | Hostel | 1BHK | 2BHK | Shared Room | Studio
    gender = Column(String(10), default="any")  # boys | girls | any
    description = Column(Text)
    address = Column(String(300))
    area = Column(String(100), index=True)   # locality name, used by rent-trends
    city = Column(String(100), default="Bhopal")
    lat = Column(Float)
    lng = Column(Float)
    rent = Column(Integer, nullable=False)          # per month, INR
    deposit = Column(Integer, default=0)
    other_price = Column(Integer, default=0)        # maintenance / electricity etc.
    distance_km = Column(Float, default=0)          # distance from campus
    safety_score = Column(Float, default=4.0)       # 0-5
    amenities = Column(JSON, default=list)          # ["wifi","ac","mess",...]
    images = Column(JSON, default=list)
    total_slots = Column(Integer, default=1)
    status = Column(String(20), default="pending", index=True)  # pending | approved | rejected
    rejection_reason = Column(Text)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    owner = relationship("User", back_populates="properties")
    slots = relationship("Slot", back_populates="property", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="property", cascade="all, delete-orphan")
    tenants = relationship("Tenant", back_populates="property", cascade="all, delete-orphan")

    @property
    def is_approved(self) -> bool:
        return self.status == "approved"


class Slot(Base):
    """One rentable bed/room inside a property."""
    __tablename__ = "slots"

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False, index=True)
    label = Column(String(50))          # "Room 101 - Bed A"
    rent_per_slot = Column(Integer)
    is_occupied = Column(Boolean, default=False)
    occupied_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=utcnow)

    property = relationship("Property", back_populates="slots")


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False, index=True)
    slot_id = Column(Integer, ForeignKey("slots.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(120), nullable=False)
    phone = Column(String(20))
    reg_no = Column(String(30))
    rent = Column(Integer)
    start_date = Column(DateTime, default=utcnow)
    end_date = Column(DateTime)
    rent_status = Column(String(20), default="due")  # paid | due | overdue
    created_at = Column(DateTime, default=utcnow)

    property = relationship("Property", back_populates="tenants")


# ---------------------------------------------------------------- reviews ---
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stars = Column(Float, nullable=False)
    comment = Column(Text)
    is_anonymous = Column(Boolean, default=False)
    is_flagged = Column(Boolean, default=False)
    is_hidden = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)

    property = relationship("Property", back_populates="reviews")
    user = relationship("User", back_populates="reviews")


# -------------------------------------------------------------- community ---
class CommunityGroup(Base):
    __tablename__ = "community_groups"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    slug = Column(String(120), unique=True)
    description = Column(Text)
    category = Column(String(50), default="general")  # housing | roommates | transport | events | general
    icon = Column(String(10), default="💬")
    created_at = Column(DateTime, default=utcnow)

    posts = relationship("CommunityPost", back_populates="group", cascade="all, delete-orphan")
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")


class GroupMember(Base):
    __tablename__ = "group_members"
    __table_args__ = (UniqueConstraint("group_id", "user_id", name="uq_group_member"),)

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("community_groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=utcnow)

    group = relationship("CommunityGroup", back_populates="members")


class CommunityPost(Base):
    __tablename__ = "community_posts"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("community_groups.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(200))
    content = Column(Text, nullable=False)
    tags = Column(JSON, default=list)
    likes = Column(Integer, default=0)
    is_flagged = Column(Boolean, default=False)
    is_hidden = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)

    group = relationship("CommunityGroup", back_populates="posts")
    author = relationship("User")
    comments = relationship("PostComment", back_populates="post", cascade="all, delete-orphan")


class PostComment(Base):
    __tablename__ = "post_comments"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("community_posts.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    post = relationship("CommunityPost", back_populates="comments")
    author = relationship("User")


# -------------------------------------------------------------- transport ---
class TransportRide(Base):
    """A shared ride (cab / auto) posted by a student."""
    __tablename__ = "transport_rides"

    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    origin = Column(String(150), nullable=False)
    destination = Column(String(150), nullable=False)
    depart_at = Column(DateTime, nullable=False)
    mode = Column(String(20), default="cab")   # cab | auto | bike | bus
    seats_total = Column(Integer, default=3)
    seats_taken = Column(Integer, default=0)
    cost_per_head = Column(Integer, default=0)
    notes = Column(Text)
    status = Column(String(20), default="open")  # open | full | completed | cancelled
    created_at = Column(DateTime, default=utcnow)

    host = relationship("User")
    passengers = relationship("RidePassenger", back_populates="ride", cascade="all, delete-orphan")


class RidePassenger(Base):
    __tablename__ = "ride_passengers"
    __table_args__ = (UniqueConstraint("ride_id", "user_id", name="uq_ride_passenger"),)

    id = Column(Integer, primary_key=True)
    ride_id = Column(Integer, ForeignKey("transport_rides.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=utcnow)

    ride = relationship("TransportRide", back_populates="passengers")


# -------------------------------------------------------- analytics & misc ---
class RentTrend(Base):
    """Monthly average rent per area & property type (powers RentAnalyzer)."""
    __tablename__ = "rent_trends"

    id = Column(Integer, primary_key=True)
    area = Column(String(100), index=True, nullable=False)
    property_type = Column(String(40), nullable=False)
    month = Column(String(7), nullable=False)   # "2026-03"
    avg_rent = Column(Integer, nullable=False)
    listings = Column(Integer, default=0)


class Service(Base):
    """Local services near campus: laundry, mess, tiffin, doctor, electrician ..."""
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    category = Column(String(50), index=True, nullable=False)
    description = Column(Text)
    phone = Column(String(20))
    area = Column(String(100))
    address = Column(String(300))
    lat = Column(Float)
    lng = Column(Float)
    rating = Column(Float, default=4.0)
    price_range = Column(String(50))
    is_verified = Column(Boolean, default=True)
    open_hours = Column(String(100))


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    slot_id = Column(Integer, ForeignKey("slots.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    razorpay_order_id = Column(String(100), nullable=False)
    razorpay_payment_id = Column(String(100))
    amount = Column(Integer, nullable=False)   # INR
    status = Column(String(20), default="created")  # created | paid | failed
    created_at = Column(DateTime, default=utcnow)
