import pytest

from tests.conftest import auth_headers

pytestmark = pytest.mark.asyncio

COLLEGE_PAYLOAD = {
    "name": "RGIPT",
    "city": "Amethi",
    "latitude": 26.2358,
    "longitude": 81.6486,
}


async def _create_college(client, admin_tokens) -> str:
    resp = await client.post("/api/v1/colleges", headers=auth_headers(admin_tokens), json=COLLEGE_PAYLOAD)
    return resp.json()["id"]


async def test_route_search_returns_multiple_transport_modes(client, admin_tokens, student_tokens):
    college_id = await _create_college(client, admin_tokens)
    resp = await client.post(
        "/api/v1/routes/search",
        headers=auth_headers(student_tokens),
        json={
            "source_location": "Lucknow Charbagh Railway Station",
            "source_type": "railway_station",
            "college_id": college_id,
            "source_latitude": 26.8305,
            "source_longitude": 80.9210,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    modes = {opt["transport_type"] for opt in body["options"]}
    assert {"metro", "bus", "cab", "auto"}.issubset(modes)
    for opt in body["options"]:
        assert opt["distance_km"] > 0
        assert opt["duration_minutes"] > 0
        assert opt["estimated_cost_inr"] >= 0
        assert len(opt["steps"]) >= 1


async def test_route_search_unknown_college_404(client, student_tokens):
    resp = await client.post(
        "/api/v1/routes/search",
        headers=auth_headers(student_tokens),
        json={
            "source_location": "Somewhere",
            "source_type": "airport",
            "college_id": "00000000-0000-0000-0000-000000000000",
        },
    )
    assert resp.status_code == 404


async def test_bookmark_and_history(client, admin_tokens, student_tokens):
    college_id = await _create_college(client, admin_tokens)
    search_resp = await client.post(
        "/api/v1/routes/search",
        headers=auth_headers(student_tokens),
        json={
            "source_location": "Amethi Bus Stand",
            "source_type": "bus_stand",
            "college_id": college_id,
            "source_latitude": 26.15,
            "source_longitude": 81.80,
        },
    )
    route_id = search_resp.json()["options"][0]["id"]

    bookmark_resp = await client.patch(
        f"/api/v1/routes/{route_id}/bookmark", headers=auth_headers(student_tokens), json={"is_bookmarked": True}
    )
    assert bookmark_resp.status_code == 200
    assert bookmark_resp.json()["is_bookmarked"] is True

    history_resp = await client.get(
        "/api/v1/routes/history", params={"bookmarked_only": True}, headers=auth_headers(student_tokens)
    )
    assert history_resp.status_code == 200
    assert any(r["id"] == route_id for r in history_resp.json())


async def test_cannot_bookmark_another_users_route(client, admin_tokens, student_tokens):
    college_id = await _create_college(client, admin_tokens)
    search_resp = await client.post(
        "/api/v1/routes/search",
        headers=auth_headers(student_tokens),
        json={
            "source_location": "Somewhere",
            "source_type": "airport",
            "college_id": college_id,
            "source_latitude": 26.5,
            "source_longitude": 81.0,
        },
    )
    route_id = search_resp.json()["options"][0]["id"]

    other_resp = await client.patch(
        f"/api/v1/routes/{route_id}/bookmark", headers=auth_headers(admin_tokens), json={"is_bookmarked": True}
    )
    assert other_resp.status_code == 403
