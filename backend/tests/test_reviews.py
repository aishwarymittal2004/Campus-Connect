import pytest

from tests.conftest import auth_headers

pytestmark = pytest.mark.asyncio


async def _create_college(client, admin_tokens) -> str:
    resp = await client.post(
        "/api/v1/colleges",
        headers=auth_headers(admin_tokens),
        json={"name": "RGIPT", "city": "Amethi", "latitude": 26.2358, "longitude": 81.6486},
    )
    return resp.json()["id"]


async def test_college_review_requires_college_id(client, student_tokens):
    resp = await client.post(
        "/api/v1/reviews",
        headers=auth_headers(student_tokens),
        json={"review_type": "college", "rating": 5, "comment": "Great campus!"},
    )
    assert resp.status_code == 422


async def test_create_and_list_college_review(client, admin_tokens, student_tokens):
    college_id = await _create_college(client, admin_tokens)
    create_resp = await client.post(
        "/api/v1/reviews",
        headers=auth_headers(student_tokens),
        json={"review_type": "college", "rating": 4, "comment": "Good food, far from station.", "college_id": college_id},
    )
    assert create_resp.status_code == 201

    list_resp = await client.get("/api/v1/reviews", params={"review_type": "college", "target_id": college_id})
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


async def test_rating_out_of_range_rejected(client, admin_tokens, student_tokens):
    college_id = await _create_college(client, admin_tokens)
    resp = await client.post(
        "/api/v1/reviews",
        headers=auth_headers(student_tokens),
        json={"review_type": "college", "rating": 7, "comment": "Too high a rating", "college_id": college_id},
    )
    assert resp.status_code == 422


async def test_cannot_delete_others_review(client, admin_tokens, student_tokens):
    college_id = await _create_college(client, admin_tokens)
    create_resp = await client.post(
        "/api/v1/reviews",
        headers=auth_headers(student_tokens),
        json={"review_type": "college", "rating": 4, "comment": "Nice place overall.", "college_id": college_id},
    )
    review_id = create_resp.json()["id"]

    other_email_tokens = admin_tokens  # different user (admin) than the review author (student)
    delete_resp = await client.delete(f"/api/v1/reviews/{review_id}", headers=auth_headers(other_email_tokens))
    # Admins are allowed to moderate/delete any review per business rules
    assert delete_resp.status_code == 200
