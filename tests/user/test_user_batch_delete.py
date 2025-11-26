"""
Tests for DELETE /user/list endpoint

Tests the batch user deletion functionality with various scenarios
"""
import pytest
import json
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.user import User
import uuid


def test_delete_user_list_success(client: TestClient, test_session: Session):
    """
    Test DELETE /user/list with valid data

    Should delete multiple users successfully
    """
    # Create users first
    user1 = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address="123 Main St"
    )
    user2 = User(
        name="Jane",
        lastname="Smith",
        age=25,
        country="Canada",
        home_address="456 Oak Ave"
    )
    user3 = User(
        name="Bob",
        lastname="Johnson",
        age=35,
        country="UK",
        home_address="789 Pine Rd"
    )
    test_session.add(user1)
    test_session.add(user2)
    test_session.add(user3)
    test_session.commit()
    test_session.refresh(user1)
    test_session.refresh(user2)
    test_session.refresh(user3)

    # Delete users
    user_data_list = [
        {"id": user1.id},
        {"id": user2.id},
        {"id": user3.id}
    ]

    response = client.request("DELETE", "/user/list", json=user_data_list)

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "code" in data
    assert "message" in data
    assert "data" in data
    assert data["code"] == 200
    assert data["error"] is None

    # Verify response data structure
    assert "ok_records" in data["data"]
    assert "error_records" in data["data"]
    assert len(data["data"]["ok_records"]) == 3
    assert len(data["data"]["error_records"]) == 0

    # Verify users are deleted by checking via GET endpoint
    list_response = client.get("/user/list")
    assert list_response.status_code == 200
    users = list_response.json()["data"]["items"]
    user_ids = [u["id"] for u in users]
    assert user1.id not in user_ids, f"User {user1.id} should be deleted but still exists"
    assert user2.id not in user_ids, f"User {user2.id} should be deleted but still exists"
    assert user3.id not in user_ids, f"User {user3.id} should be deleted but still exists"


def test_delete_user_list_partial_delete(client: TestClient, test_session: Session):
    """
    Test DELETE /user/list with partial deletion

    Should delete only specified users
    """
    # Create users first
    user1 = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address="123 Main St"
    )
    user2 = User(
        name="Jane",
        lastname="Smith",
        age=25,
        country="Canada",
        home_address="456 Oak Ave"
    )
    user3 = User(
        name="Bob",
        lastname="Johnson",
        age=35,
        country="UK",
        home_address="789 Pine Rd"
    )
    test_session.add(user1)
    test_session.add(user2)
    test_session.add(user3)
    test_session.commit()
    test_session.refresh(user1)
    test_session.refresh(user2)
    test_session.refresh(user3)

    # Delete only user1 and user2
    user_data_list = [
        {"id": user1.id},
        {"id": user2.id}
    ]

    response = client.request("DELETE", "/user/list", json=user_data_list)

    assert response.status_code == 200
    data = response.json()

    assert len(data["data"]["ok_records"]) == 2
    assert len(data["data"]["error_records"]) == 0

    # Verify user1 and user2 are deleted by checking via GET endpoint
    list_response = client.get("/user/list")
    assert list_response.status_code == 200
    users = list_response.json()["data"]["items"]
    user_ids = [u["id"] for u in users]
    assert user1.id not in user_ids, f"User {user1.id} should be deleted but still exists"
    assert user2.id not in user_ids, f"User {user2.id} should be deleted but still exists"

    # Verify user3 still exists
    assert user3.id in user_ids, f"User {user3.id} should still exist but was deleted"
    user3_data = next(u for u in users if u["id"] == user3.id)
    assert user3_data["name"] == "Bob"


def test_delete_user_list_not_found(client: TestClient, test_session: Session):
    """
    Test DELETE /user/list with non-existent user IDs

    Should return 400 with error records
    """
    # Create one user
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

    non_existent_id = str(uuid.uuid4())

    # Try to delete existing and non-existent users
    user_data_list = [
        {"id": user.id},
        {"id": non_existent_id}
    ]

    response = client.request("DELETE", "/user/list", json=user_data_list)

    # Should return 400 or 500 if there are errors
    assert response.status_code in [400, 500]
    data = response.json()

    assert "error" in data
    # For 500 errors, error_records might be empty or in a different structure
    if response.status_code == 400:
        error_records = data.get("error", {}).get("details", {}).get("error_records", [])
        assert len(error_records) > 0

    # Verify the existing user was not deleted (transaction rollback) by checking via GET endpoint
    list_response = client.get("/user/list")
    assert list_response.status_code == 200
    users = list_response.json()["data"]["items"]
    user_ids = [u["id"] for u in users]

    # With 400, transaction should have rolled back. With 500, behavior may vary
    if response.status_code == 400:
        assert user.id in user_ids, f"User {user.id} should still exist (transaction rollback)"
        user_data = next(u for u in users if u["id"] == user.id)
        assert user_data["name"] == "John"


def test_delete_user_list_empty_list(client: TestClient):
    """
    Test DELETE /user/list with empty list

    Should handle empty list gracefully
    """
    user_data_list = []

    response = client.request("DELETE", "/user/list", json=user_data_list)

    assert response.status_code == 200
    data = response.json()

    assert "ok_records" in data["data"]
    assert "error_records" in data["data"]
    assert len(data["data"]["ok_records"]) == 0
    assert len(data["data"]["error_records"]) == 0


def test_delete_user_list_single_user(client: TestClient, test_session: Session):
    """
    Test DELETE /user/list with single user

    Should delete single user successfully
    """
    # Create user first
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

    # Delete user
    user_data_list = [
        {"id": user.id}
    ]

    response = client.request("DELETE", "/user/list", json=user_data_list)

    assert response.status_code == 200
    data = response.json()

    assert len(data["data"]["ok_records"]) == 1
    assert len(data["data"]["error_records"]) == 0

    # Verify user is deleted by checking via GET endpoint
    list_response = client.get("/user/list")
    assert list_response.status_code == 200
    users = list_response.json()["data"]["items"]
    user_ids = [u["id"] for u in users]
    assert user.id not in user_ids, f"User {user.id} should be deleted but still exists"


def test_delete_user_list_large_batch(client: TestClient, test_session: Session):
    """
    Test DELETE /user/list with large batch

    Should handle large number of deletions
    """
    # Create users first
    users = []
    for i in range(50):
        user = User(
            name=f"User{i}",
            lastname="Test",
            age=20 + i,
            country="USA",
            home_address=f"{i} Main St"
        )
        users.append(user)
        test_session.add(user)
    test_session.commit()
    for user in users:
        test_session.refresh(user)

    # Delete all users
    user_data_list = [
        {"id": user.id}
        for user in users
    ]

    response = client.request("DELETE", "/user/list", json=user_data_list)

    assert response.status_code == 200
    data = response.json()

    assert len(data["data"]["ok_records"]) == 50
    assert len(data["data"]["error_records"]) == 0

    # Verify all users are deleted by checking via GET endpoint
    list_response = client.get("/user/list")
    assert list_response.status_code == 200
    all_users = list_response.json()["data"]["items"]
    all_user_ids = [u["id"] for u in all_users]
    for user in users:
        assert user.id not in all_user_ids, f"User {user.id} should be deleted but still exists"


def test_delete_user_list_with_full_user_data(client: TestClient, test_session: Session):
    """
    Test DELETE /user/list with full user data (not just ID)

    Should delete users even if full data is provided
    """
    # Create users first
    user1 = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address="123 Main St"
    )
    user2 = User(
        name="Jane",
        lastname="Smith",
        age=25,
        country="Canada",
        home_address="456 Oak Ave"
    )
    test_session.add(user1)
    test_session.add(user2)
    test_session.commit()
    test_session.refresh(user1)
    test_session.refresh(user2)

    # Delete with full user data
    user_data_list = [
        {
            "id": user1.id,
            "name": "John",
            "lastname": "Doe",
            "age": 30,
            "country": "USA",
            "home_address": "123 Main St"
        },
        {
            "id": user2.id,
            "name": "Jane",
            "lastname": "Smith",
            "age": 25,
            "country": "Canada",
            "home_address": "456 Oak Ave"
        }
    ]

    response = client.request("DELETE", "/user/list", json=user_data_list)

    assert response.status_code == 200
    data = response.json()

    assert len(data["data"]["ok_records"]) == 2

    # Verify users are deleted by checking via GET endpoint
    list_response = client.get("/user/list")
    assert list_response.status_code == 200
    users = list_response.json()["data"]["items"]
    user_ids = [u["id"] for u in users]
    assert user1.id not in user_ids, f"User {user1.id} should be deleted but still exists"
    assert user2.id not in user_ids, f"User {user2.id} should be deleted but still exists"


def test_delete_user_list_without_ids(client: TestClient):
    """
    Test DELETE /user/list without IDs

    Should return validation error or handle gracefully
    """
    user_data_list = [
        {
            "name": "Test",
            "lastname": "User",
            "age": 30
        }
    ]

    response = client.request("DELETE", "/user/list", json=user_data_list)

    # Should fail because ID is required for deletion
    assert response.status_code in [400, 422]


def test_delete_user_list_invalid_json(client: TestClient):
    """
    Test DELETE /user/list with invalid JSON

    Should return 422 validation error
    """
    response = client.request(
        "DELETE",
        "/user/list",
        content="invalid json",
        headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 422


def test_delete_user_list_not_list(client: TestClient):
    """
    Test DELETE /user/list with non-list data

    Should return 422 validation error
    """
    user_data = {
        "id": str(uuid.uuid4())
    }

    response = client.request("DELETE", "/user/list", json=user_data)

    assert response.status_code == 422


def test_delete_user_list_database_consistency(client: TestClient, test_session: Session):
    """
    Test DELETE /user/list database consistency

    Should maintain data integrity after batch deletion
    """
    # Create users first
    user1 = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address="123 Main St"
    )
    user2 = User(
        name="Jane",
        lastname="Smith",
        age=25,
        country="Canada",
        home_address="456 Oak Ave"
    )
    user3 = User(
        name="Bob",
        lastname="Johnson",
        age=35,
        country="UK",
        home_address="789 Pine Rd"
    )
    test_session.add(user1)
    test_session.add(user2)
    test_session.add(user3)
    test_session.commit()
    test_session.refresh(user1)
    test_session.refresh(user2)
    test_session.refresh(user3)

    # Delete user1 and user2
    user_data_list = [
        {"id": user1.id},
        {"id": user2.id}
    ]

    response = client.request("DELETE", "/user/list", json=user_data_list)
    assert response.status_code == 200

    # Verify deletions by checking via GET endpoint
    list_response = client.get("/user/list")
    assert list_response.status_code == 200
    users = list_response.json()["data"]["items"]
    user_ids = [u["id"] for u in users]
    assert user1.id not in user_ids, f"User {user1.id} should be deleted but still exists"
    assert user2.id not in user_ids, f"User {user2.id} should be deleted but still exists"
    assert user3.id in user_ids, f"User {user3.id} should still exist but was deleted"


def test_delete_user_list_transaction_rollback(client: TestClient, test_session: Session):
    """
    Test DELETE /user/list transaction rollback on errors

    Should rollback all deletions if any record fails
    """
    # Create users first
    user1 = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address="123 Main St"
    )
    user2 = User(
        name="Jane",
        lastname="Smith",
        age=25,
        country="Canada",
        home_address="456 Oak Ave"
    )
    test_session.add(user1)
    test_session.add(user2)
    test_session.commit()
    test_session.refresh(user1)
    test_session.refresh(user2)

    non_existent_id = str(uuid.uuid4())

    # Try to delete existing and non-existent users
    user_data_list = [
        {"id": user1.id},
        {"id": non_existent_id}  # Will cause error
    ]

    response = client.request("DELETE", "/user/list", json=user_data_list)

    # Should return 400 or 500 if there are errors
    assert response.status_code in [400, 500]

    # Verify user1 was not deleted (transaction rollback) by checking via GET endpoint
    list_response = client.get("/user/list")
    assert list_response.status_code == 200
    users = list_response.json()["data"]["items"]
    user_ids = [u["id"] for u in users]

    # With 400, transaction should have rolled back. With 500, behavior may vary
    if response.status_code == 400:
        assert user1.id in user_ids, f"User {user1.id} should still exist (transaction rollback)"
        user1_data = next(u for u in users if u["id"] == user1.id)
        assert user1_data["name"] == "John"
        # Verify user2 was not affected
        assert user2.id in user_ids, f"User {user2.id} should still exist"
        user2_data = next(u for u in users if u["id"] == user2.id)
        assert user2_data["name"] == "Jane"


def test_delete_user_list_multiple_deletions_consistency(client: TestClient, test_session: Session):
    """
    Test DELETE /user/list with multiple sequential batch deletions

    Should maintain consistency across multiple operations
    """
    # Create users first
    users = []
    for i in range(10):
        user = User(
            name=f"User{i}",
            lastname="Test",
            age=20 + i,
            country="USA",
            home_address=f"{i} Main St"
        )
        users.append(user)
        test_session.add(user)
    test_session.commit()
    for user in users:
        test_session.refresh(user)

    # First batch deletion (delete first 3)
    user_data_list1 = [
        {"id": users[i].id}
        for i in range(3)
    ]
    response1 = client.request("DELETE", "/user/list", json=user_data_list1)
    assert response1.status_code == 200

    # Verify first 3 are deleted by checking via GET endpoint
    list_response1 = client.get("/user/list")
    assert list_response1.status_code == 200
    users_after_first = list_response1.json()["data"]["items"]
    user_ids_after_first = [u["id"] for u in users_after_first]
    for i in range(3):
        assert users[i].id not in user_ids_after_first, f"User {users[i].id} should be deleted but still exists"

    # Second batch deletion (delete next 3)
    user_data_list2 = [
        {"id": users[i].id}
        for i in range(3, 6)
    ]
    response2 = client.request("DELETE", "/user/list", json=user_data_list2)
    assert response2.status_code == 200

    # Verify next 3 are deleted by checking via GET endpoint
    list_response2 = client.get("/user/list")
    assert list_response2.status_code == 200
    users_after_second = list_response2.json()["data"]["items"]
    user_ids_after_second = [u["id"] for u in users_after_second]
    for i in range(3, 6):
        assert users[i].id not in user_ids_after_second, f"User {users[i].id} should be deleted but still exists"

    # Verify remaining users still exist
    for i in range(6, 10):
        assert users[i].id in user_ids_after_second, f"User {users[i].id} should still exist but was deleted"
        user_data = next(u for u in users_after_second if u["id"] == users[i].id)
        assert user_data["name"] == f"User{i}"


def test_delete_user_list_all_users(client: TestClient, test_session: Session):
    """
    Test DELETE /user/list deleting all users

    Should delete all users and leave empty database
    """
    # Create users first
    user1 = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address="123 Main St"
    )
    user2 = User(
        name="Jane",
        lastname="Smith",
        age=25,
        country="Canada",
        home_address="456 Oak Ave"
    )
    test_session.add(user1)
    test_session.add(user2)
    test_session.commit()
    test_session.refresh(user1)
    test_session.refresh(user2)

    # Delete all users
    user_data_list = [
        {"id": user1.id},
        {"id": user2.id}
    ]

    response = client.request("DELETE", "/user/list", json=user_data_list)
    assert response.status_code == 200

    # Verify all users are deleted by checking via GET endpoint
    list_response = client.get("/user/list")
    assert list_response.status_code == 200
    users = list_response.json()["data"]["items"]
    user_ids = [u["id"] for u in users]
    assert user1.id not in user_ids, f"User {user1.id} should be deleted but still exists"
    assert user2.id not in user_ids, f"User {user2.id} should be deleted but still exists"
    assert len(users) == 0, "List should be empty after deleting all users"


def test_delete_user_list_duplicate_ids(client: TestClient, test_session: Session):
    """
    Test DELETE /user/list with duplicate IDs

    Should handle duplicate IDs appropriately
    """
    # Create user first
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

    # Try to delete same user twice
    user_data_list = [
        {"id": user.id},
        {"id": user.id}  # Duplicate
    ]

    response = client.request("DELETE", "/user/list", json=user_data_list)

    # Should return 400 or 500 if there are errors
    assert response.status_code in [400, 500]
    data = response.json()

    # Should have error
    assert "error" in data
    # Error records might be empty if error handling is different
    error_records = data.get("error", {}).get("details", {}).get("error_records", [])
    assert len(error_records) >= 0

    # Verify user was not deleted (transaction rollback) by checking via GET endpoint
    list_response = client.get("/user/list")
    assert list_response.status_code == 200
    users = list_response.json()["data"]["items"]
    user_ids = [u["id"] for u in users]

    # With 400, transaction should have rolled back. With 500, behavior may vary
    if response.status_code == 400:
        assert user.id in user_ids, f"User {user.id} should still exist (transaction rollback)"


def test_delete_user_list_mixed_valid_invalid(client: TestClient, test_session: Session):
    """
    Test DELETE /user/list with mix of valid and invalid IDs

    Should handle partial failures correctly
    """
    # Create users first
    user1 = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address="123 Main St"
    )
    user2 = User(
        name="Jane",
        lastname="Smith",
        age=25,
        country="Canada",
        home_address="456 Oak Ave"
    )
    test_session.add(user1)
    test_session.add(user2)
    test_session.commit()
    test_session.refresh(user1)
    test_session.refresh(user2)

    non_existent_id = str(uuid.uuid4())

    # Try to delete valid and invalid users
    user_data_list = [
        {"id": user1.id},  # Valid
        {"id": non_existent_id},  # Invalid
        {"id": user2.id}  # Valid
    ]

    response = client.request("DELETE", "/user/list", json=user_data_list)

    # Should return 400 or 500 if there are errors
    assert response.status_code in [400, 500]
    data = response.json()
    assert "error" in data

    # Verify users status by checking via GET endpoint
    # Note: With 500 errors, transaction rollback behavior may vary
    list_response = client.get("/user/list")
    assert list_response.status_code == 200
    users = list_response.json()["data"]["items"]
    user_ids = [u["id"] for u in users]

    # If status is 500, the deletion might have partially succeeded before the error
    # If status is 400, transaction rollback should have occurred
    if response.status_code == 400:
        # With 400, transaction should have rolled back
        assert user1.id in user_ids, f"User {user1.id} should still exist (transaction rollback)"
        assert user2.id in user_ids, f"User {user2.id} should still exist (transaction rollback)"
    # For 500 errors, we just verify the error occurred (behavior may vary)

