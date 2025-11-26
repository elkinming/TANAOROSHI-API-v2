"""
Tests for POST /user endpoint

Tests the user creation functionality with various scenarios
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.user import User
import uuid


def test_create_user_success(client: TestClient, test_session: Session):
    """
    Test POST /user with valid data

    Should create a new user successfully
    """
    user_data = {
        "name": "John",
        "lastname": "Doe",
        "age": 30,
        "country": "USA",
        "home_address": "123 Main St"
    }

    response = client.post("/user", json=user_data)

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "code" in data
    assert "message" in data
    assert "data" in data
    assert data["code"] == 200
    assert data["error"] is None

    # Verify user data
    user = data["data"]
    assert "id" in user
    assert user["name"] == "John"
    assert user["lastname"] == "Doe"
    assert user["age"] == 30
    assert user["country"] == "USA"
    assert user["home_address"] == "123 Main St"

    # Verify user exists in database
    db_user = test_session.get(User, user["id"])
    assert db_user is not None
    assert db_user.name == "John"
    assert db_user.lastname == "Doe"
    assert db_user.age == 30


def test_create_user_with_id(client: TestClient, test_session: Session):
    """
    Test POST /user with explicit ID

    Should create a user with the provided ID
    """
    user_id = str(uuid.uuid4())
    user_data = {
        "id": user_id,
        "name": "Jane",
        "lastname": "Smith",
        "age": 25,
        "country": "Canada",
        "home_address": "456 Oak Ave"
    }

    response = client.post("/user", json=user_data)

    assert response.status_code == 200
    data = response.json()

    # Verify user was created with the specified ID
    user = data["data"]
    assert user["id"] == user_id

    # Verify in database
    db_user = test_session.get(User, user_id)
    assert db_user is not None
    assert db_user.id == user_id


def test_create_user_with_minimal_data(client: TestClient, test_session: Session):
    """
    Test POST /user with minimal required data

    Should create a user with only some fields
    """
    user_data = {
        "name": "Minimal"
    }

    response = client.post("/user", json=user_data)

    assert response.status_code == 200
    data = response.json()

    user = data["data"]
    assert user["name"] == "Minimal"
    assert user.get("lastname") is None
    assert user.get("age") is None
    assert user.get("country") is None
    assert user.get("home_address") is None

    # Verify in database
    db_user = test_session.get(User, user["id"])
    assert db_user is not None
    assert db_user.name == "Minimal"


def test_create_user_with_all_optional_fields(client: TestClient, test_session: Session):
    """
    Test POST /user with all optional fields

    Should create a user with all fields populated
    """
    user_data = {
        "name": "Complete",
        "lastname": "User",
        "age": 35,
        "country": "Japan",
        "home_address": "Tokyo, Shibuya"
    }

    response = client.post("/user", json=user_data)

    assert response.status_code == 200
    data = response.json()

    user = data["data"]
    assert user["name"] == "Complete"
    assert user["lastname"] == "User"
    assert user["age"] == 35
    assert user["country"] == "Japan"
    assert user["home_address"] == "Tokyo, Shibuya"


def test_create_user_duplicate_id(client: TestClient, test_session: Session):
    """
    Test POST /user with duplicate ID

    Should return 409 Conflict error
    """
    user_id = str(uuid.uuid4())
    
    # Create first user
    user1 = User(
        id=user_id,
        name="First",
        lastname="User",
        age=30,
        country="USA",
        home_address="123 St"
    )
    test_session.add(user1)
    test_session.commit()

    # Try to create another user with same ID
    user_data = {
        "id": user_id,
        "name": "Second",
        "lastname": "User",
        "age": 25,
        "country": "UK",
        "home_address": "456 Ave"
    }

    response = client.post("/user", json=user_data)

    assert response.status_code == 409
    data = response.json()
    assert data["code"] == 409
    assert "既にユーザーが存在します" in data.get("message", "") or "既にユーザーが存在します" in data.get("detail", "")


def test_create_user_with_empty_strings(client: TestClient, test_session: Session):
    """
    Test POST /user with empty string values

    Should handle empty strings appropriately
    """
    user_data = {
        "name": "",
        "lastname": "",
        "age": None,
        "country": "",
        "home_address": ""
    }

    response = client.post("/user", json=user_data)

    assert response.status_code == 200
    data = response.json()

    user = data["data"]
    assert user["name"] == ""
    assert user["lastname"] == ""
    assert user["country"] == ""
    assert user["home_address"] == ""


def test_create_user_with_unicode_characters(client: TestClient, test_session: Session):
    """
    Test POST /user with Unicode characters

    Should handle Unicode characters correctly
    """
    user_data = {
        "name": "José",
        "lastname": "García",
        "age": 30,
        "country": "México",
        "home_address": "Calle 123"
    }

    response = client.post("/user", json=user_data)

    assert response.status_code == 200
    data = response.json()

    user = data["data"]
    assert user["name"] == "José"
    assert user["lastname"] == "García"
    assert user["country"] == "México"
    assert user["home_address"] == "Calle 123"

    # Verify in database
    db_user = test_session.get(User, user["id"])
    assert db_user.name == "José"
    assert db_user.lastname == "García"


def test_create_user_with_japanese_characters(client: TestClient, test_session: Session):
    """
    Test POST /user with Japanese characters

    Should handle Japanese characters correctly
    """
    user_data = {
        "name": "山田",
        "lastname": "太郎",
        "age": 25,
        "country": "日本",
        "home_address": "東京都渋谷区"
    }

    response = client.post("/user", json=user_data)

    assert response.status_code == 200
    data = response.json()

    user = data["data"]
    assert user["name"] == "山田"
    assert user["lastname"] == "太郎"
    assert user["country"] == "日本"
    assert user["home_address"] == "東京都渋谷区"


def test_create_user_with_special_characters(client: TestClient, test_session: Session):
    """
    Test POST /user with special characters

    Should handle special characters correctly
    """
    user_data = {
        "name": "O'Brien",
        "lastname": "Smith-Johnson",
        "age": 30,
        "country": "USA",
        "home_address": "123 Main St. #4, Apt. B"
    }

    response = client.post("/user", json=user_data)

    assert response.status_code == 200
    data = response.json()

    user = data["data"]
    assert user["name"] == "O'Brien"
    assert user["lastname"] == "Smith-Johnson"
    assert user["home_address"] == "123 Main St. #4, Apt. B"


def test_create_user_with_long_strings(client: TestClient, test_session: Session):
    """
    Test POST /user with very long string values

    Should handle long strings correctly
    """
    long_name = "A" * 500
    long_address = "B" * 1000

    user_data = {
        "name": long_name,
        "lastname": "Test",
        "age": 30,
        "country": "USA",
        "home_address": long_address
    }

    response = client.post("/user", json=user_data)

    assert response.status_code == 200
    data = response.json()

    user = data["data"]
    assert len(user["name"]) == 500
    assert len(user["home_address"]) == 1000


def test_create_user_with_zero_age(client: TestClient, test_session: Session):
    """
    Test POST /user with age = 0

    Should accept zero as a valid age
    """
    user_data = {
        "name": "Baby",
        "lastname": "User",
        "age": 0,
        "country": "USA",
        "home_address": "123 St"
    }

    response = client.post("/user", json=user_data)

    assert response.status_code == 200
    data = response.json()

    user = data["data"]
    assert user["age"] == 0


def test_create_user_with_negative_age(client: TestClient, test_session: Session):
    """
    Test POST /user with negative age

    Should accept negative age (validation may vary)
    """
    user_data = {
        "name": "Test",
        "lastname": "User",
        "age": -1,
        "country": "USA",
        "home_address": "123 St"
    }

    response = client.post("/user", json=user_data)

    # Should either accept or reject based on validation
    # For now, we'll check it doesn't crash
    assert response.status_code in [200, 422]


def test_create_user_with_very_large_age(client: TestClient, test_session: Session):
    """
    Test POST /user with very large age

    Should handle large integer values
    """
    user_data = {
        "name": "Old",
        "lastname": "User",
        "age": 999999,
        "country": "USA",
        "home_address": "123 St"
    }

    response = client.post("/user", json=user_data)

    assert response.status_code == 200
    data = response.json()

    user = data["data"]
    assert user["age"] == 999999


def test_create_user_missing_required_fields(client: TestClient):
    """
    Test POST /user with empty body

    Should create user with all None values (all fields are optional)
    """
    user_data = {}

    response = client.post("/user", json=user_data)

    # All fields are optional, so this should succeed
    assert response.status_code == 200
    data = response.json()

    user = data["data"]
    assert "id" in user


def test_create_user_invalid_json(client: TestClient):
    """
    Test POST /user with invalid JSON

    Should return 422 validation error
    """
    response = client.post(
        "/user",
        data="invalid json",
        headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 422


def test_create_user_wrong_data_types(client: TestClient):
    """
    Test POST /user with wrong data types

    Should return 422 validation error
    """
    user_data = {
        "name": 123,  # Should be string
        "lastname": "Doe",
        "age": "thirty",  # Should be integer
        "country": "USA",
        "home_address": "123 St"
    }

    response = client.post("/user", json=user_data)

    assert response.status_code == 422
    data = response.json()
    assert "error" in data or "detail" in data


def test_create_user_with_none_values(client: TestClient, test_session: Session):
    """
    Test POST /user with explicit None values

    Should handle None values correctly
    """
    user_data = {
        "name": None,
        "lastname": None,
        "age": None,
        "country": None,
        "home_address": None
    }

    response = client.post("/user", json=user_data)

    assert response.status_code == 200
    data = response.json()

    user = data["data"]
    assert user.get("name") is None
    assert user.get("lastname") is None
    assert user.get("age") is None
    assert user.get("country") is None
    assert user.get("home_address") is None


def test_create_user_database_consistency(client: TestClient, test_session: Session):
    """
    Test POST /user database consistency

    Should maintain data integrity after creation
    """
    user_data = {
        "name": "Consistency",
        "lastname": "Test",
        "age": 30,
        "country": "USA",
        "home_address": "123 Main St"
    }

    response = client.post("/user", json=user_data)
    assert response.status_code == 200

    user_id = response.json()["data"]["id"]

    # Verify user exists in database
    db_user = test_session.get(User, user_id)
    assert db_user is not None

    # Verify all fields match
    assert db_user.name == user_data["name"]
    assert db_user.lastname == user_data["lastname"]
    assert db_user.age == user_data["age"]
    assert db_user.country == user_data["country"]
    assert db_user.home_address == user_data["home_address"]

    # Verify user can be retrieved via GET
    list_response = client.get("/user/list")
    assert list_response.status_code == 200
    users = list_response.json()["data"]["items"]
    user_ids = [u["id"] for u in users]
    assert user_id in user_ids


def test_create_user_multiple_users_consistency(client: TestClient, test_session: Session):
    """
    Test POST /user with multiple sequential creates

    Should maintain consistency across multiple operations
    """
    users_data = [
        {"name": "User1", "lastname": "Test", "age": 20, "country": "USA"},
        {"name": "User2", "lastname": "Test", "age": 25, "country": "UK"},
        {"name": "User3", "lastname": "Test", "age": 30, "country": "Canada"},
    ]

    created_ids = []
    for user_data in users_data:
        response = client.post("/user", json=user_data)
        assert response.status_code == 200
        created_ids.append(response.json()["data"]["id"])

    # Verify all users exist in database
    for user_id in created_ids:
        db_user = test_session.get(User, user_id)
        assert db_user is not None

    # Verify all users appear in list
    list_response = client.get("/user/list")
    assert list_response.status_code == 200
    users = list_response.json()["data"]["items"]
    user_ids = [u["id"] for u in users]
    for user_id in created_ids:
        assert user_id in user_ids

    # Verify count matches
    assert len(users) >= len(created_ids)

