import pytest
from httpx import AsyncClient, ASGITransport
from ..main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_login(client):
    response = await client.post("/token", data={"username": "admin", "password": "password"})
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_invalid_login(client):
    response = await client.post("/token", data={"username": "wrong", "password": "incorrect"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_protected_endpoint_no_token(client):
    response = await client.get("/users/1")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_create_user(client):
    token_response = await client.post("/token", data={"username": "admin", "password": "password"})
    token = token_response.json()["access_token"]

    new_user = {
        "_id": 11,
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "registered_objects": 0
    }

    response = await client.post("/users", json=new_user, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == new_user


@pytest.mark.asyncio
async def test_create_existing_user(client):
    token_response = await client.post("/token", data={"username": "admin", "password": "password"})
    token = token_response.json()["access_token"]

    existing_user = {
        "_id": 11,
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "registered_objects": 0
    }

    response = await client.post("/users", json=existing_user, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 409
    assert "detail" in response.json()
    assert response.json()["detail"] == "User already exists"


@pytest.mark.asyncio
async def test_get_user(client):
    token_response = await client.post("/token", data={"username": "admin", "password": "password"})
    token = token_response.json()["access_token"]

    user_id = 11
    user_data = {
        "_id": user_id,
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "registered_objects": 0
    }

    response = await client.get(f"/users/{user_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == user_data


@pytest.mark.asyncio
async def test_create_ticket(client):
    token_response = await client.post("/token", data={"username": "admin", "password": "password"})
    token = token_response.json()["access_token"]

    new_ticket = {
        "_id": "1",
        "flight_number": "CD456",
        "passenger_name": "Jane Doe",
        "destination": "Los Angeles",
        "price": 450.75,
        "user_id": 11,
        "timestamp": None
    }

    response = await client.post("/tickets", json=new_ticket, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == new_ticket


@pytest.mark.asyncio
async def test_get_ticket(client):
    token_response = await client.post("/token", data={"username": "admin", "password": "password"})
    token = token_response.json()["access_token"]

    ticket_id = "1"
    ticket_data = {
        "_id": ticket_id,
        "flight_number": "CD456",
        "passenger_name": "Jane Doe",
        "destination": "Los Angeles",
        "price": 450.75,
        "user_id": 11,
        "timestamp": None
    }

    response = await client.get(f"/tickets/{ticket_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == ticket_data


