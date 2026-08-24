import pytest

from tests.conftest import auth_headers

pytestmark = pytest.mark.asyncio

COLLEGE_PAYLOAD = {
    "name": "Rajiv Gandhi Institute of Petroleum Technology",
    "city": "Amethi",
    "state": "Uttar Pradesh",
    "latitude": 26.2358,
    "longitude": 81.6486,
    "nearby_landmarks": [{"name": "Jais Railway Station", "type": "landmark", "distance_km": 3.5}],
    "emergency_contacts": [{"label": "Campus Security", "phone": "+91-9999999999"}],
    "tags": ["engineering"],
}


async def test_student_cannot_create_college(client, student_tokens):
    resp = await client.post("/api/v1/colleges", headers=auth_headers(student_tokens), json=COLLEGE_PAYLOAD)
    assert resp.status_code == 403


async def test_admin_can_create_college(client, admin_tokens):
    resp = await client.post("/api/v1/colleges", headers=auth_headers(admin_tokens), json=COLLEGE_PAYLOAD)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == COLLEGE_PAYLOAD["name"]
    assert body["nearby_landmarks"][0]["name"] == "Jais Railway Station"


async def test_list_colleges_is_public(client, admin_tokens):
    await client.post("/api/v1/colleges", headers=auth_headers(admin_tokens), json=COLLEGE_PAYLOAD)
    resp = await client.get("/api/v1/colleges")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


async def test_search_colleges_by_city(client, admin_tokens):
    await client.post("/api/v1/colleges", headers=auth_headers(admin_tokens), json=COLLEGE_PAYLOAD)
    resp = await client.get("/api/v1/colleges", params={"q": "Amethi"})
    assert resp.status_code == 200
    assert any(c["city"] == "Amethi" for c in resp.json())


async def test_get_nonexistent_college_404(client):
    resp = await client.get("/api/v1/colleges/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


async def test_college_input_validation_rejects_bad_latitude(client, admin_tokens):
    bad_payload = {**COLLEGE_PAYLOAD, "latitude": 999}
    resp = await client.post("/api/v1/colleges", headers=auth_headers(admin_tokens), json=bad_payload)
    assert resp.status_code == 422
