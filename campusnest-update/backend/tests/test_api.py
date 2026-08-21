"""
End-to-end smoke tests against an isolated SQLite database.
Run from the project root:  pytest backend/tests -q
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

TEST_DB = Path(__file__).resolve().parent / "_test.db"
os.environ["USE_SQLITE"] = "true"
os.environ["SQLITE_PATH"] = str(TEST_DB)
os.environ["DEBUG"] = "true"
os.environ["DEMO_OTP"] = "1234"
os.environ["SEED_DEMO_DATA"] = "true"
os.environ["RAZORPAY_KEY_ID"] = ""
os.environ["RAZORPAY_KEY_SECRET"] = ""

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from backend.main import app  # noqa: E402
from backend.seed import reset_and_seed  # noqa: E402


@pytest.fixture(scope="session")
def client():
    reset_and_seed()
    with TestClient(app) as c:
        yield c
    try:
        TEST_DB.unlink()
    except FileNotFoundError:
        pass


def _login(client, path, payload):
    r = client.post(path, json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    return {"Authorization": f"Bearer {data['access_token']}"}, data["user"]


@pytest.fixture(scope="session")
def student(client):
    return _login(client, "/auth/student/login", {"reg_no": "21BCE0001", "otp": "1234"})


@pytest.fixture(scope="session")
def owner(client):
    return _login(client, "/auth/owner/login", {"phone": "+919800000001", "otp": "1234"})


@pytest.fixture(scope="session")
def moderator(client):
    return _login(client, "/auth/owner/login", {"phone": "+910000000000", "otp": "1234"})


# ------------------------------------------------------------------ meta ---
def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


# ------------------------------------------------------------------ auth ---
def test_send_otp_and_login_roles(client, student, owner, moderator):
    r = client.post("/auth/send-otp", json={"identifier": "21BCE0001", "role": "student"})
    assert r.status_code == 200 and r.json()["demo_otp"] == "1234"
    assert student[1]["role"] == "student"
    assert owner[1]["role"] == "owner"
    assert moderator[1]["role"] == "moderator"
    assert client.post("/auth/student/login", json={"reg_no": "21BCE0001", "otp": "0000"}).status_code == 401
    r = client.get("/auth/me", headers=student[0])
    assert r.status_code == 200 and r.json()["reg_no"] == "21BCE0001"


def test_new_student_autocreated(client):
    headers, user = _login(client, "/auth/student/login", {"reg_no": "25bce99999", "otp": "1234", "name": "New Kid"})
    assert user["reg_no"] == "25BCE99999" and user["name"] == "New Kid"


# ------------------------------------------------------------ properties ---
def test_list_and_filter_properties(client):
    r = client.get("/properties")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 8
    assert all(p["status"] == "approved" for p in body["items"])
    r = client.get("/properties", params={"type": "PG", "max_rent": 7000, "amenities": "wifi,mess"})
    assert r.status_code == 200 and all(p["type"] == "PG" and p["rent"] <= 7000 for p in r.json()["items"])
    r = client.get("/properties", params={"sort": "rent_asc"})
    rents = [p["rent"] for p in r.json()["items"]]
    assert rents == sorted(rents)
    assert client.get("/properties/areas").status_code == 200
    assert len(client.get("/properties/featured").json()) >= 1


def test_property_detail_and_compare(client):
    first = client.get("/properties").json()["items"][0]
    r = client.get(f"/properties/{first['id']}")
    assert r.status_code == 200
    d = r.json()
    assert "slots" in d and "reviews" in d and d["available_slots"] <= d["total_slots"]
    ids = [p["id"] for p in client.get("/properties").json()["items"][:3]]
    r = client.post("/properties/compare", json={"property_ids": ids})
    assert r.status_code == 200
    cmp_ = r.json()
    assert len(cmp_["properties"]) == 3 and cmp_["best_value_id"] in ids
    assert client.get("/properties/999999").status_code == 404


# --------------------------------------------------------------- reviews ---
def test_review_flow(client, student):
    prop = client.get("/properties").json()["items"][0]
    r = client.post("/reviews", json={"property_id": prop["id"], "stars": 4, "comment": "Nice"}, headers=student[0])
    assert r.status_code == 201
    rid = r.json()["id"]
    # second submission updates rather than duplicates
    r2 = client.post("/reviews", json={"property_id": prop["id"], "stars": 5, "comment": "Great"}, headers=student[0])
    assert r2.status_code == 201 and r2.json()["id"] == rid
    assert client.post("/reviews", json={"property_id": prop["id"], "stars": 5}).status_code == 401
    assert client.post(f"/reviews/{rid}/flag", headers=student[0]).status_code == 200


# ---------------------------------------------------- owner + moderator ---
def test_owner_creates_listing_and_moderator_approves(client, owner, moderator, student):
    payload = {"name": "Test PG", "type": "PG", "area": "Kothri Kalan", "rent": 5000, "total_slots": 3,
               "amenities": ["wifi"], "lat": 23.08, "lng": 76.85}
    r = client.post("/owner/properties", json=payload, headers=owner[0])
    assert r.status_code == 201, r.text
    pid = r.json()["id"]
    assert r.json()["status"] == "pending" and len(r.json()["slots"]) == 3

    # not visible publicly yet
    assert client.get(f"/properties/{pid}").status_code == 404
    # student cannot use owner routes
    assert client.post("/owner/properties", json=payload, headers=student[0]).status_code == 403

    pending = client.get("/moderator/properties", params={"status": "pending"}, headers=moderator[0]).json()
    assert any(p["id"] == pid for p in pending)
    r = client.patch(f"/moderator/properties/{pid}", json={"status": "approved"}, headers=moderator[0])
    assert r.status_code == 200 and r.json()["status"] == "approved"
    assert client.get(f"/properties/{pid}").status_code == 200
    # owner cannot moderate
    assert client.patch(f"/moderator/properties/{pid}", json={"status": "rejected"}, headers=owner[0]).status_code == 403

    # owner dashboard & tenants
    assert client.get("/owner/dashboard", headers=owner[0]).json()["stats"]["total_properties"] >= 1
    r = client.post("/owner/tenants", json={"property_id": pid, "name": "Tenant A", "reg_no": "21BCE0001"}, headers=owner[0])
    assert r.status_code == 201 and r.json()["slot_id"] is not None
    tid = r.json()["id"]
    r = client.patch(f"/owner/tenants/{tid}", json={"rent_status": "paid"}, headers=owner[0])
    assert r.json()["rent_status"] == "paid"
    assert client.get("/moderator/dashboard", headers=moderator[0]).status_code == 200
    owners = client.get("/moderator/owners", headers=moderator[0]).json()
    assert len(owners) >= 3


# -------------------------------------------------------------- community ---
def test_community(client, student):
    groups = client.get("/community/groups").json()
    assert len(groups) >= 5
    gid = groups[0]["id"]
    assert client.post(f"/community/groups/{gid}/join", headers=student[0]).status_code == 200
    r = client.post("/community/posts", json={"group_id": gid, "title": "Hi", "content": "Hello"}, headers=student[0])
    assert r.status_code == 201
    pid = r.json()["id"]
    assert client.post(f"/community/posts/{pid}/like", headers=student[0]).json()["data"]["likes"] == 1
    assert client.post(f"/community/posts/{pid}/comments", json={"content": "yo"}, headers=student[0]).status_code == 201
    assert client.get(f"/community/posts/{pid}").json()["comment_count"] == 1
    assert len(client.get("/community/feed").json()) >= 1


# -------------------------------------------------------------- roommates ---
def test_roommates(client, student):
    r = client.get("/roommates/matches", headers=student[0])
    assert r.status_code == 200
    matches = r.json()
    assert len(matches) >= 3 and all(0 <= m["score"] <= 100 for m in matches)
    assert matches == sorted(matches, key=lambda m: -m["score"])
    r = client.put("/profile/me", json={"sleep": "early-bird", "budget": 6500}, headers=student[0])
    assert r.json()["sleep"] == "early-bird"


# -------------------------------------------------------------- transport ---
def test_transport(client, student):
    rides = client.get("/transport/rides").json()
    assert len(rides) >= 3
    other = next(r for r in rides if r["host"]["id"] != student[1]["id"])
    r = client.post(f"/transport/rides/{other['id']}/join", headers=student[0])
    assert r.status_code == 200 and r.json()["is_joined"] is True
    assert client.post(f"/transport/rides/{other['id']}/join", headers=student[0]).status_code == 400
    r = client.post("/transport/rides", json={"origin": "Gate", "destination": "Station", "depart_at": "2030-01-01T10:00:00", "seats_total": 2}, headers=student[0])
    assert r.status_code == 201


# ---------------------------------------------- analytics & services & pay ---
def test_analytics_services_payments(client):
    trends = client.get("/rent-trends", params={"area": "Kothri Kalan"}).json()
    assert trends and all(len(t["points"]) == 6 for t in trends)
    assert client.get("/rent-trends/areas").json()
    a = client.get("/rent-trends/analyze", params={"rent": 6000, "area": "Kothri Kalan", "type": "PG"}).json()
    assert a["verdict"] in {"great deal", "fair", "slightly high", "overpriced"}
    svcs = client.get("/services", params={"category": "medical"}).json()
    assert len(svcs) == 2
    assert client.get("/services/categories").json()
    assert client.get("/payments/status").json()["enabled"] is False
