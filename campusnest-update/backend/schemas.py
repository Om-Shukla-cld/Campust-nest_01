"""Pydantic request / response schemas."""
from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ------------------------------------------------------------------- auth ---
class SendOTPRequest(BaseModel):
    identifier: str = Field(..., description="Phone number (owner/moderator) or registration no (student)")
    role: str = Field("student", pattern="^(student|owner|moderator)$")


class SendOTPResponse(BaseModel):
    message: str
    identifier: str
    expires_in_minutes: int
    demo_otp: Optional[str] = None  # only returned when DEBUG=true


class StudentLoginRequest(BaseModel):
    reg_no: str
    otp: str
    name: Optional[str] = None


class PhoneLoginRequest(BaseModel):
    phone: str
    otp: str
    name: Optional[str] = None


class UserOut(ORM):
    id: int
    role: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    reg_no: Optional[str] = None
    college: Optional[str] = None
    avatar_url: Optional[str] = None
    is_verified: bool = False
    veg: Optional[str] = None
    smoker: Optional[str] = None
    sleep: Optional[str] = None
    cleanliness: Optional[str] = None
    study: Optional[str] = None
    budget: Optional[int] = None
    about_me: Optional[str] = None
    looking_for_roommate: Optional[bool] = True
    created_at: Optional[datetime] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    college: Optional[str] = None
    avatar_url: Optional[str] = None
    veg: Optional[str] = None
    smoker: Optional[str] = None
    sleep: Optional[str] = None
    cleanliness: Optional[str] = None
    study: Optional[str] = None
    budget: Optional[int] = None
    about_me: Optional[str] = None
    looking_for_roommate: Optional[bool] = None


# ------------------------------------------------------------- properties ---
class OwnerBrief(ORM):
    id: int
    name: Optional[str] = None
    phone: Optional[str] = None
    is_verified: bool = False


class SlotOut(ORM):
    id: int
    property_id: int
    label: Optional[str] = None
    rent_per_slot: Optional[int] = None
    is_occupied: bool = False


class PropertyBase(BaseModel):
    name: str
    type: str = "PG"
    gender: str = "any"
    description: Optional[str] = None
    address: Optional[str] = None
    area: Optional[str] = None
    city: Optional[str] = "Bhopal"
    lat: Optional[float] = None
    lng: Optional[float] = None
    rent: int
    deposit: int = 0
    other_price: int = 0
    distance_km: float = 0
    amenities: List[str] = []
    images: List[str] = []
    total_slots: int = 1


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    gender: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    area: Optional[str] = None
    city: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    rent: Optional[int] = None
    deposit: Optional[int] = None
    other_price: Optional[int] = None
    distance_km: Optional[float] = None
    amenities: Optional[List[str]] = None
    images: Optional[List[str]] = None
    total_slots: Optional[int] = None


class PropertyOut(ORM):
    id: int
    owner_id: int
    name: str
    type: Optional[str] = None
    gender: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    area: Optional[str] = None
    city: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    rent: int
    deposit: Optional[int] = 0
    other_price: Optional[int] = 0
    distance_km: Optional[float] = 0
    safety_score: Optional[float] = None
    amenities: List[str] = []
    images: List[str] = []
    total_slots: int = 1
    status: str
    is_approved: bool = False
    rejection_reason: Optional[str] = None
    is_featured: bool = False
    created_at: Optional[datetime] = None
    # computed
    avg_rating: float = 0
    review_count: int = 0
    available_slots: int = 0
    owner: Optional[OwnerBrief] = None


class PropertyDetail(PropertyOut):
    slots: List[SlotOut] = []
    reviews: List["ReviewOut"] = []


class PropertyList(BaseModel):
    total: int
    items: List[PropertyOut]


class CompareRequest(BaseModel):
    property_ids: List[int] = Field(..., min_length=2, max_length=4)


class CompareResponse(BaseModel):
    properties: List[PropertyOut]
    best_value_id: Optional[int] = None
    cheapest_id: Optional[int] = None
    closest_id: Optional[int] = None
    safest_id: Optional[int] = None
    top_rated_id: Optional[int] = None
    summary: dict


class ModerationAction(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected|pending)$")
    reason: Optional[str] = None


# ---------------------------------------------------------------- reviews ---
class ReviewCreate(BaseModel):
    property_id: int
    stars: float = Field(..., ge=0, le=5)
    comment: Optional[str] = None
    is_anonymous: bool = False


class ReviewOut(ORM):
    id: int
    property_id: int
    user_id: Optional[int] = None
    author_name: Optional[str] = None
    stars: float
    comment: Optional[str] = None
    is_anonymous: bool = False
    is_flagged: bool = False
    is_hidden: bool = False
    created_at: Optional[datetime] = None


class ReviewModeration(BaseModel):
    is_hidden: Optional[bool] = None
    is_flagged: Optional[bool] = None


PropertyDetail.model_rebuild()


# ---------------------------------------------------------------- tenants ---
class TenantCreate(BaseModel):
    property_id: int
    slot_id: Optional[int] = None
    name: str
    phone: Optional[str] = None
    reg_no: Optional[str] = None
    rent: Optional[int] = None
    start_date: Optional[datetime] = None


class TenantUpdate(BaseModel):
    rent_status: Optional[str] = Field(None, pattern="^(paid|due|overdue)$")
    end_date: Optional[datetime] = None
    rent: Optional[int] = None


class TenantOut(ORM):
    id: int
    property_id: int
    slot_id: Optional[int] = None
    student_id: Optional[int] = None
    name: str
    phone: Optional[str] = None
    reg_no: Optional[str] = None
    rent: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    rent_status: str = "due"


# -------------------------------------------------------------- community ---
class GroupOut(ORM):
    id: int
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    category: str
    icon: Optional[str] = None
    member_count: int = 0
    post_count: int = 0
    is_member: bool = False


class AuthorBrief(ORM):
    id: int
    name: Optional[str] = None
    role: str
    avatar_url: Optional[str] = None


class CommentOut(ORM):
    id: int
    post_id: int
    content: str
    author: Optional[AuthorBrief] = None
    created_at: Optional[datetime] = None


class PostCreate(BaseModel):
    group_id: int
    title: Optional[str] = None
    content: str
    tags: List[str] = []


class CommentCreate(BaseModel):
    content: str


class PostOut(ORM):
    id: int
    group_id: int
    title: Optional[str] = None
    content: str
    tags: List[str] = []
    likes: int = 0
    is_flagged: bool = False
    author: Optional[AuthorBrief] = None
    comment_count: int = 0
    created_at: Optional[datetime] = None


class PostDetail(PostOut):
    comments: List[CommentOut] = []


# -------------------------------------------------------------- roommates ---
class RoommateMatch(BaseModel):
    user: UserOut
    score: int          # 0-100 compatibility
    matched_on: List[str]
    differs_on: List[str]


# -------------------------------------------------------------- transport ---
class RideCreate(BaseModel):
    origin: str
    destination: str
    depart_at: datetime
    mode: str = "cab"
    seats_total: int = Field(3, ge=1, le=8)
    cost_per_head: int = 0
    notes: Optional[str] = None


class RideOut(ORM):
    id: int
    host: Optional[AuthorBrief] = None
    origin: str
    destination: str
    depart_at: datetime
    mode: str
    seats_total: int
    seats_taken: int
    seats_left: int = 0
    cost_per_head: int = 0
    notes: Optional[str] = None
    status: str
    is_joined: bool = False
    created_at: Optional[datetime] = None


# -------------------------------------------------------------- analytics ---
class RentTrendPoint(BaseModel):
    month: str
    avg_rent: int
    listings: int = 0


class RentTrendSeries(BaseModel):
    area: str
    property_type: str
    points: List[RentTrendPoint]
    change_pct: float = 0


class RentAnalysis(BaseModel):
    rent: int
    area: Optional[str] = None
    property_type: Optional[str] = None
    market_avg: Optional[int] = None
    verdict: str
    diff_pct: Optional[float] = None
    percentile: Optional[int] = None
    suggestion: str


class AreaSummary(BaseModel):
    area: str
    avg_rent: int
    min_rent: int
    max_rent: int
    listings: int
    avg_safety: float


# --------------------------------------------------------------- services ---
class ServiceOut(ORM):
    id: int
    name: str
    category: str
    description: Optional[str] = None
    phone: Optional[str] = None
    area: Optional[str] = None
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    rating: Optional[float] = None
    price_range: Optional[str] = None
    is_verified: bool = True
    open_hours: Optional[str] = None


# --------------------------------------------------------------- payments ---
class CreateOrderRequest(BaseModel):
    slot_id: int


class CreateOrderResponse(BaseModel):
    order_id: str
    amount: int  # in paise
    currency: str
    key_id: str


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


# ---------------------------------------------------------------- generic ---
class Message(BaseModel):
    message: str
    data: Optional[Any] = None
