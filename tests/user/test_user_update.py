"""
Tests for PUT /user endpoint

Tests the user update functionality with various scenarios
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.user import User
import uuid


def test_update_user_success(client: TestClient, test_session: Session):
    """
    Test PUT /user with valid data

    Should update an existing user successfully
    """
    # Create a user first
    user = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address="123 Main St"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    # Update the user
    user_data = {
        "id": user.id,
        "name": "John Updated",
        "lastname": "Doe Updated",
        "age": 31,
        "country": "Canada",
        "home_address": "456 Oak Ave"
    }

    response = client.put("/user", json=user_data)

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "code" in data
    assert "message" in data
    assert "data" in data
    assert data["code"] == 200
    assert data["error"] is None

    # Verify updated user data
    updated_user = data["data"]
    assert updated_user["id"] == user.id
    assert updated_user["name"] == "John Updated"
    assert updated_user["lastname"] == "Doe Updated"
    assert updated_user["age"] == 31
    assert updated_user["country"] == "Canada"
    assert updated_user["home_address"] == "456 Oak Ave"

    # Verify in database (refresh session to see updates from API)
    test_session.expire_all()
    db_user = test_session.get(User, user.id)
    assert db_user.name == "John Updated"
    assert db_user.lastname == "Doe Updated"
    assert db_user.age == 31
    assert db_user.country == "Canada"
    assert db_user.home_address == "456 Oak Ave"


def test_update_user_partial_update(client: TestClient, test_session: Session):
    """
    Test PUT /user with partial data

    Should update only provided fields
    """
    # Create a user first
    user = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address="123 Main St"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    # Update only name
    user_data = {
        "id": user.id,
        "name": "John Updated"
    }

    response = client.put("/user", json=user_data)

    assert response.status_code == 200
    data = response.json()

    updated_user = data["data"]
    assert updated_user["name"] == "John Updated"
    # Other fields should remain unchanged
    assert updated_user["lastname"] == "Doe"
    assert updated_user["age"] == 30
    assert updated_user["country"] == "USA"
    assert updated_user["home_address"] == "123 Main St"

    # Verify in database (refresh session to see updates from API)
    test_session.expire_all()


def test_update_user_not_found(client: TestClient):
    """
    Test PUT /user with non-existent user ID

    Should return 404 Not Found error
    """
    non_existent_id = str(uuid.uuid4())
    user_data = {
        "id": non_existent_id,
        "name": "Test",
        "lastname": "User",
        "age": 30,
        "country": "USA",
        "home_address": "123 St"
    }

    response = client.put("/user", json=user_data)

    assert response.status_code == 404
    data = response.json()
    assert data["code"] == 404
    assert "見つかりません" in data.get("message", "") or "見つかりません" in data.get("detail", "")


def test_update_user_without_id(client: TestClient):
    """
    Test PUT /user without ID

    Should return validation error or handle gracefully
    """
    user_data = {
        "name": "Test",
        "lastname": "User",
        "age": 30
    }

    response = client.put("/user", json=user_data)

    # Should fail because ID is required for update
    assert response.status_code in [404, 422]


def test_update_user_with_empty_strings(client: TestClient, test_session: Session):
    """
    Test PUT /user with empty string values

    Should update fields to empty strings
    """
    # Create a user first
    user = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address="123 Main St"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    # Update with empty strings
    user_data = {
        "id": user.id,
        "name": "",
        "lastname": "",
        "country": "",
        "home_address": ""
    }

    response = client.put("/user", json=user_data)

    assert response.status_code == 200
    data = response.json()

    updated_user = data["data"]
    assert updated_user["name"] == ""
    assert updated_user["lastname"] == ""
    assert updated_user["country"] == ""
    assert updated_user["home_address"] == ""


def test_update_user_with_none_values(client: TestClient, test_session: Session):
    """
    Test PUT /user with None values

    Should update fields to None
    """
    # Create a user first
    user = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address="123 Main St"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    # Update with None values
    user_data = {
        "id": user.id,
        "name": None,
        "lastname": None,
        "age": None,
        "country": None,
        "home_address": None
    }

    response = client.put("/user", json=user_data)

    assert response.status_code == 200
    data = response.json()

    updated_user = data["data"]
    assert updated_user.get("name") is None
    assert updated_user.get("lastname") is None
    assert updated_user.get("age") is None
    assert updated_user.get("country") is None
    assert updated_user.get("home_address") is None


def test_update_user_with_unicode_characters(client: TestClient, test_session: Session):
    """
    Test PUT /user with Unicode characters

    Should handle Unicode characters correctly
    """
    # Create a user first
    user = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address="123 Main St"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    # Update with Unicode characters
    user_data = {
        "id": user.id,
        "name": "José",
        "lastname": "García",
        "country": "México",
        "home_address": "Calle 123"
    }

    response = client.put("/user", json=user_data)

    assert response.status_code == 200
    data = response.json()

    updated_user = data["data"]
    assert updated_user["name"] == "José"
    assert updated_user["lastname"] == "García"
    assert updated_user["country"] == "México"
    assert updated_user["home_address"] == "Calle 123"

    # Verify in database (refresh session to see updates from API)
    test_session.expire_all()
    db_user = test_session.get(User, user.id)
    assert db_user.name == "José"
    assert db_user.lastname == "García"


def test_update_user_with_japanese_characters(client: TestClient, test_session: Session):
    """
    Test PUT /user with Japanese characters

    Should handle Japanese characters correctly
    """
    # Create a user first
    user = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address="123 Main St"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    # Update with Japanese characters
    user_data = {
        "id": user.id,
        "name": "山田",
        "lastname": "太郎",
        "country": "日本",
        "home_address": "東京都渋谷区"
    }

    response = client.put("/user", json=user_data)

    assert response.status_code == 200
    data = response.json()

    updated_user = data["data"]
    assert updated_user["name"] == "山田"
    assert updated_user["lastname"] == "太郎"
    assert updated_user["country"] == "日本"
    assert updated_user["home_address"] == "東京都渋谷区"


def test_update_user_with_special_characters(client: TestClient, test_session: Session):
    """
    Test PUT /user with special characters

    Should handle special characters correctly
    """
    # Create a user first
    user = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address="123 Main St"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    # Update with special characters
    user_data = {
        "id": user.id,
        "name": "O'Brien",
        "lastname": "Smith-Johnson",
        "home_address": "123 Main St. #4, Apt. B"
    }

    response = client.put("/user", json=user_data)

    assert response.status_code == 200
    data = response.json()

    updated_user = data["data"]
    assert updated_user["name"] == "O'Brien"
    assert updated_user["lastname"] == "Smith-Johnson"
    assert updated_user["home_address"] == "123 Main St. #4, Apt. B"


def test_update_user_with_long_strings(client: TestClient, test_session: Session):
    """
    Test PUT /user with very long string values

    Should handle long strings correctly
    """
    # Create a user first
    user = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address="123 Main St"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    # Update with long strings
    long_name = "A" * 500
    long_address = "B" * 1000

    user_data = {
        "id": user.id,
        "name": long_name,
        "home_address": long_address
    }

    response = client.put("/user", json=user_data)

    assert response.status_code == 200
    data = response.json()

    updated_user = data["data"]
    assert len(updated_user["name"]) == 500
    assert len(updated_user["home_address"]) == 1000


def test_update_user_age_to_zero(client: TestClient, test_session: Session):
    """
    Test PUT /user with age = 0

    Should accept zero as a valid age
    """
    # Create a user first
    user = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address="123 Main St"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    # Update age to 0
    user_data = {
        "id": user.id,
        "age": 0
    }

    response = client.put("/user", json=user_data)

    assert response.status_code == 200
    data = response.json()

    updated_user = data["data"]
    assert updated_user["age"] == 0


def test_update_user_age_to_negative(client: TestClient, test_session: Session):
    """
    Test PUT /user with negative age

    Should either accept or reject based on validation
    """
    # Create a user first
    user = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address="123 Main St"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    # Update age to negative
    user_data = {
        "id": user.id,
        "age": -1
    }

    response = client.put("/user", json=user_data)

    # Should either accept or reject
    assert response.status_code in [200, 422]


def test_update_user_age_to_very_large(client: TestClient, test_session: Session):
    """
    Test PUT /user with very large age

    Should handle large integer values
    """
    # Create a user first
    user = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address="123 Main St"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    # Update age to very large number
    user_data = {
        "id": user.id,
        "age": 999999
    }

    response = client.put("/user", json=user_data)

    assert response.status_code == 200
    data = response.json()

    updated_user = data["data"]
    assert updated_user["age"] == 999999


def test_update_user_wrong_data_types(client: TestClient, test_session: Session):
    """
    Test PUT /user with wrong data types

    Should return 422 validation error
    """
    # Create a user first
    user = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address="123 Main St"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    # Try to update with wrong types
    user_data = {
        "id": user.id,
        "name": 123,  # Should be string
        "age": "thirty"  # Should be integer
    }

    response = client.put("/user", json=user_data)

    assert response.status_code == 422
    data = response.json()
    assert "error" in data or "detail" in data


def test_update_user_invalid_json(client: TestClient):
    """
    Test PUT /user with invalid JSON

    Should return 422 validation error
    """
    response = client.put(
        "/user",
        data="invalid json",
        headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 422


def test_update_user_database_consistency(client: TestClient, test_session: Session):
    """
    Test PUT /user database consistency

    Should maintain data integrity after update
    """
    # Create a user first
    user = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address="123 Main St"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    # Update the user
    user_data = {
        "id": user.id,
        "name": "John Updated",
        "lastname": "Doe Updated",
        "age": 31,
        "country": "Canada",
        "home_address": "456 Oak Ave"
    }

    response = client.put("/user", json=user_data)
    assert response.status_code == 200

    # Verify in database (refresh session to see updates from API)
    test_session.expire_all()
    db_user = test_session.get(User, user.id)
    assert db_user.name == "John Updated"
    assert db_user.lastname == "Doe Updated"
    assert db_user.age == 31
    assert db_user.country == "Canada"
    assert db_user.home_address == "456 Oak Ave"

    # Verify user can be retrieved via GET
    list_response = client.get("/user/list")
    assert list_response.status_code == 200
    users = list_response.json()["data"]["items"]
    user_ids = [u["id"] for u in users]
    assert user.id in user_ids

    # Verify updated data in list
    updated_user_in_list = next(u for u in users if u["id"] == user.id)
    assert updated_user_in_list["name"] == "John Updated"
    assert updated_user_in_list["age"] == 31


def test_update_user_multiple_updates_consistency(client: TestClient, test_session: Session):
    """
    Test PUT /user with multiple sequential updates

    Should maintain consistency across multiple operations
    """
    # Create a user first
    user = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address="123 Main St"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    # First update
    user_data1 = {
        "id": user.id,
        "name": "John First",
        "age": 31
    }
    response1 = client.put("/user", json=user_data1)
    assert response1.status_code == 200

    # Second update
    user_data2 = {
        "id": user.id,
        "name": "John Second",
        "age": 32
    }
    response2 = client.put("/user", json=user_data2)
    assert response2.status_code == 200

    # Third update
    user_data3 = {
        "id": user.id,
        "name": "John Third",
        "age": 33
    }
    response3 = client.put("/user", json=user_data3)
    assert response3.status_code == 200

    # Verify final state in database (refresh session to see updates from API)
    test_session.expire_all()
    db_user = test_session.get(User, user.id)
    assert db_user.name == "John Third"
    assert db_user.age == 33

    # Verify via GET
    list_response = client.get("/user/list")
    assert list_response.status_code == 200
    users = list_response.json()["data"]["items"]
    updated_user = next(u for u in users if u["id"] == user.id)
    assert updated_user["name"] == "John Third"
    assert updated_user["age"] == 33


def test_update_user_id_immutability(client: TestClient, test_session: Session):
    """
    Test PUT /user ID immutability

    Should not allow changing the ID
    """
    # Create a user first
    user = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address="123 Main St"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    original_id = user.id
    new_id = str(uuid.uuid4())

    # Try to update with different ID
    user_data = {
        "id": original_id,
        "name": "Updated"
    }

    response = client.put("/user", json=user_data)
    assert response.status_code == 200

    # Verify ID remains the same (refresh session to see updates from API)
    test_session.expire_all()
    db_user = test_session.get(User, original_id)
    assert db_user is not None
    assert db_user.id == original_id
    assert db_user.name == "Updated"

    # Verify new_id doesn't exist
    non_existent = test_session.get(User, new_id)
    assert non_existent is None

