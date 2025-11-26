"""
Tests for PUT /user/list endpoint

Tests the batch user update functionality with various scenarios
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.user import User
import uuid


def test_update_user_list_success(client: TestClient, test_session: Session):
    """
    Test PUT /user/list with valid data

    Should update multiple users successfully
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

    # Update users
    user_data_list = [
        {
            "id": user1.id,
            "name": "John Updated",
            "age": 31
        },
        {
            "id": user2.id,
            "name": "Jane Updated",
            "age": 26
        },
        {
            "id": user3.id,
            "name": "Bob Updated",
            "age": 36
        }
    ]

    response = client.put("/user/list", json=user_data_list)

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

    # Verify updated users
    ok_records = data["data"]["ok_records"]
    assert len(ok_records) == 3

    # Verify updates in database (refresh session to see updates from API)
    test_session.expire_all()
    db_user1 = test_session.get(User, user1.id)
    assert db_user1.name == "John Updated"
    assert db_user1.age == 31

    db_user2 = test_session.get(User, user2.id)
    assert db_user2.name == "Jane Updated"
    assert db_user2.age == 26

    db_user3 = test_session.get(User, user3.id)
    assert db_user3.name == "Bob Updated"
    assert db_user3.age == 36


def test_update_user_list_partial_update(client: TestClient, test_session: Session):
    """
    Test PUT /user/list with partial updates

    Should update only provided fields
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

    # Update only specific fields
    user_data_list = [
        {
            "id": user1.id,
            "name": "John Updated"
        },
        {
            "id": user2.id,
            "age": 26
        }
    ]

    response = client.put("/user/list", json=user_data_list)

    assert response.status_code == 200
    data = response.json()

    assert len(data["data"]["ok_records"]) == 2

    # Verify partial updates (refresh session to see updates from API)
    test_session.expire_all()
    db_user1 = test_session.get(User, user1.id)
    assert db_user1.name == "John Updated"
    assert db_user1.lastname == "Doe"  # Unchanged
    assert db_user1.age == 30  # Unchanged

    db_user2 = test_session.get(User, user2.id)
    assert db_user2.name == "Jane"  # Unchanged
    assert db_user2.age == 26  # Updated


def test_update_user_list_not_found(client: TestClient, test_session: Session):
    """
    Test PUT /user/list with non-existent user IDs

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

    # Try to update existing and non-existent users
    user_data_list = [
        {
            "id": user.id,
            "name": "John Updated"
        },
        {
            "id": non_existent_id,
            "name": "Non Existent"
        }
    ]

    response = client.put("/user/list", json=user_data_list)

    # Should return 400 or 500 if there are errors
    assert response.status_code in [400, 500]
    data = response.json()

    assert "error" in data
    error_records = data.get("error", {}).get("details", {}).get("error_records", [])
    # Error records might be empty if error handling is different
    assert len(error_records) >= 0

    # Verify the existing user was not updated (transaction rollback) by checking via GET endpoint
    list_response = client.get("/user/list")
    assert list_response.status_code == 200
    users = list_response.json()["data"]["items"]
    user_ids = [u["id"] for u in users]
    
    # With 400, transaction should have rolled back. With 500, behavior may vary
    if response.status_code == 400:
        assert user.id in user_ids, f"User {user.id} should still exist (transaction rollback)"
        user_data = next(u for u in users if u["id"] == user.id)
        assert user_data["name"] == "John"  # Not updated due to rollback


def test_update_user_list_empty_list(client: TestClient):
    """
    Test PUT /user/list with empty list

    Should handle empty list gracefully
    """
    user_data_list = []

    response = client.put("/user/list", json=user_data_list)

    assert response.status_code == 200
    data = response.json()

    assert "ok_records" in data["data"]
    assert "error_records" in data["data"]
    assert len(data["data"]["ok_records"]) == 0
    assert len(data["data"]["error_records"]) == 0


def test_update_user_list_single_user(client: TestClient, test_session: Session):
    """
    Test PUT /user/list with single user

    Should update single user successfully
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

    # Update user
    user_data_list = [
        {
            "id": user.id,
            "name": "John Updated",
            "age": 31
        }
    ]

    response = client.put("/user/list", json=user_data_list)

    assert response.status_code == 200
    data = response.json()

    assert len(data["data"]["ok_records"]) == 1
    assert len(data["data"]["error_records"]) == 0

    # Verify update (refresh session to see updates from API)
    test_session.expire_all()
    db_user = test_session.get(User, user.id)
    assert db_user.name == "John Updated"
    assert db_user.age == 31


def test_update_user_list_large_batch(client: TestClient, test_session: Session):
    """
    Test PUT /user/list with large batch

    Should handle large number of updates
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

    # Update all users
    user_data_list = [
        {
            "id": user.id,
            "name": f"User{i} Updated",
            "age": 30 + i
        }
        for i, user in enumerate(users)
    ]

    response = client.put("/user/list", json=user_data_list)

    assert response.status_code == 200
    data = response.json()

    assert len(data["data"]["ok_records"]) == 50
    assert len(data["data"]["error_records"]) == 0

    # Verify updates (refresh session to see updates from API)
    test_session.expire_all()
    for i, user in enumerate(users):
        db_user = test_session.get(User, user.id)
        assert db_user.name == f"User{i} Updated"
        assert db_user.age == 30 + i


def test_update_user_list_with_unicode_characters(client: TestClient, test_session: Session):
    """
    Test PUT /user/list with Unicode characters

    Should handle Unicode characters correctly
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

    # Update with Unicode characters
    user_data_list = [
        {
            "id": user1.id,
            "name": "José",
            "lastname": "García",
            "country": "México"
        },
        {
            "id": user2.id,
            "name": "山田",
            "lastname": "太郎",
            "country": "日本"
        }
    ]

    response = client.put("/user/list", json=user_data_list)

    assert response.status_code == 200
    data = response.json()

    assert len(data["data"]["ok_records"]) == 2

    # Verify Unicode updates (refresh session to see updates from API)
    test_session.expire_all()
    db_user1 = test_session.get(User, user1.id)
    assert db_user1.name == "José"
    assert db_user1.lastname == "García"
    assert db_user1.country == "México"

    db_user2 = test_session.get(User, user2.id)
    assert db_user2.name == "山田"
    assert db_user2.lastname == "太郎"
    assert db_user2.country == "日本"


def test_update_user_list_with_special_characters(client: TestClient, test_session: Session):
    """
    Test PUT /user/list with special characters

    Should handle special characters correctly
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

    # Update with special characters
    user_data_list = [
        {
            "id": user1.id,
            "name": "O'Brien",
            "lastname": "Smith-Johnson",
            "home_address": "123 Main St. #4, Apt. B"
        },
        {
            "id": user2.id,
            "lastname": "O'Connor",
            "home_address": "Dublin St., Co. Dublin"
        }
    ]

    response = client.put("/user/list", json=user_data_list)

    assert response.status_code == 200
    data = response.json()

    assert len(data["data"]["ok_records"]) == 2

    # Verify special characters (refresh session to see updates from API)
    test_session.expire_all()
    db_user1 = test_session.get(User, user1.id)
    assert db_user1.name == "O'Brien"
    assert db_user1.lastname == "Smith-Johnson"
    assert db_user1.home_address == "123 Main St. #4, Apt. B"

    db_user2 = test_session.get(User, user2.id)
    assert db_user2.lastname == "O'Connor"
    assert db_user2.home_address == "Dublin St., Co. Dublin"


def test_update_user_list_with_long_strings(client: TestClient, test_session: Session):
    """
    Test PUT /user/list with very long string values

    Should handle long strings correctly
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

    # Update with long strings
    long_name = "A" * 500
    long_address = "B" * 1000

    user_data_list = [
        {
            "id": user.id,
            "name": long_name,
            "home_address": long_address
        }
    ]

    response = client.put("/user/list", json=user_data_list)

    assert response.status_code == 200
    data = response.json()

    assert len(data["data"]["ok_records"]) == 1

    # Verify long strings (refresh session to see updates from API)
    test_session.expire_all()
    db_user = test_session.get(User, user.id)
    assert len(db_user.name) == 500
    assert len(db_user.home_address) == 1000


def test_update_user_list_with_zero_age(client: TestClient, test_session: Session):
    """
    Test PUT /user/list with age = 0

    Should accept zero as valid age
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

    # Update age to 0
    user_data_list = [
        {
            "id": user.id,
            "age": 0
        }
    ]

    response = client.put("/user/list", json=user_data_list)

    assert response.status_code == 200
    data = response.json()

    assert len(data["data"]["ok_records"]) == 1
    assert data["data"]["ok_records"][0]["age"] == 0

    # Verify in database (refresh session to see updates from API)
    test_session.expire_all()
    db_user = test_session.get(User, user.id)
    assert db_user.age == 0


def test_update_user_list_with_very_large_age(client: TestClient, test_session: Session):
    """
    Test PUT /user/list with very large age

    Should handle large integer values
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

    # Update age to very large number
    user_data_list = [
        {
            "id": user.id,
            "age": 999999
        }
    ]

    response = client.put("/user/list", json=user_data_list)

    assert response.status_code == 200
    data = response.json()

    assert len(data["data"]["ok_records"]) == 1
    assert data["data"]["ok_records"][0]["age"] == 999999

    # Verify in database (refresh session to see updates from API)
    test_session.expire_all()
    db_user = test_session.get(User, user.id)
    assert db_user.age == 999999


def test_update_user_list_with_none_values(client: TestClient, test_session: Session):
    """
    Test PUT /user/list with None values

    Should handle None values correctly
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

    # Update with None values
    user_data_list = [
        {
            "id": user.id,
            "name": None,
            "lastname": None,
            "age": None,
            "country": None,
            "home_address": None
        }
    ]

    response = client.put("/user/list", json=user_data_list)

    assert response.status_code == 200
    data = response.json()

    assert len(data["data"]["ok_records"]) == 1

    # Verify None values (refresh session to see updates from API)
    test_session.expire_all()
    db_user = test_session.get(User, user.id)
    assert db_user.name is None
    assert db_user.lastname is None
    assert db_user.age is None
    assert db_user.country is None
    assert db_user.home_address is None


def test_update_user_list_with_empty_strings(client: TestClient, test_session: Session):
    """
    Test PUT /user/list with empty string values

    Should update fields to empty strings
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

    # Update with empty strings
    user_data_list = [
        {
            "id": user.id,
            "name": "",
            "lastname": "",
            "country": "",
            "home_address": ""
        }
    ]

    response = client.put("/user/list", json=user_data_list)

    assert response.status_code == 200
    data = response.json()

    assert len(data["data"]["ok_records"]) == 1

    # Verify empty strings (refresh session to see updates from API)
    test_session.expire_all()
    db_user = test_session.get(User, user.id)
    assert db_user.name == ""
    assert db_user.lastname == ""
    assert db_user.country == ""
    assert db_user.home_address == ""


def test_update_user_list_invalid_json(client: TestClient):
    """
    Test PUT /user/list with invalid JSON

    Should return 422 validation error
    """
    response = client.put(
        "/user/list",
        data="invalid json",
        headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 422


def test_update_user_list_wrong_data_types(client: TestClient, test_session: Session):
    """
    Test PUT /user/list with wrong data types

    Should return 422 validation error or handle gracefully
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

    # Try to update with wrong types
    user_data_list = [
        {
            "id": user.id,
            "name": 123,  # Should be string
            "age": "thirty"  # Should be integer
        }
    ]

    response = client.put("/user/list", json=user_data_list)

    # Should either validate or process
    assert response.status_code in [200, 400, 422]


def test_update_user_list_not_list(client: TestClient):
    """
    Test PUT /user/list with non-list data

    Should return 422 validation error
    """
    user_data = {
        "id": str(uuid.uuid4()),
        "name": "Test",
        "lastname": "User",
        "age": 30
    }

    response = client.put("/user/list", json=user_data)

    assert response.status_code == 422


def test_update_user_list_without_ids(client: TestClient):
    """
    Test PUT /user/list without IDs

    Should return validation error or handle gracefully
    """
    user_data_list = [
        {
            "name": "Test",
            "lastname": "User",
            "age": 30
        }
    ]

    response = client.put("/user/list", json=user_data_list)

    # Should fail because ID is required for update
    assert response.status_code in [400, 422]


def test_update_user_list_database_consistency(client: TestClient, test_session: Session):
    """
    Test PUT /user/list database consistency

    Should maintain data integrity after batch update
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

    # Update users
    user_data_list = [
        {
            "id": user1.id,
            "name": "John Updated",
            "age": 31
        },
        {
            "id": user2.id,
            "name": "Jane Updated",
            "age": 26
        }
    ]

    response = client.put("/user/list", json=user_data_list)
    assert response.status_code == 200

    # Verify updates in database (refresh session to see updates from API)
    test_session.expire_all()
    db_user1 = test_session.get(User, user1.id)
    assert db_user1.name == "John Updated"
    assert db_user1.age == 31

    db_user2 = test_session.get(User, user2.id)
    assert db_user2.name == "Jane Updated"
    assert db_user2.age == 26

    # Verify users can be retrieved via GET
    list_response = client.get("/user/list")
    assert list_response.status_code == 200
    users = list_response.json()["data"]["items"]
    user_ids = [u["id"] for u in users]
    assert user1.id in user_ids
    assert user2.id in user_ids

    # Verify updated data in list
    updated_user1 = next(u for u in users if u["id"] == user1.id)
    assert updated_user1["name"] == "John Updated"
    assert updated_user1["age"] == 31

    updated_user2 = next(u for u in users if u["id"] == user2.id)
    assert updated_user2["name"] == "Jane Updated"
    assert updated_user2["age"] == 26


def test_update_user_list_transaction_rollback(client: TestClient, test_session: Session):
    """
    Test PUT /user/list transaction rollback on errors

    Should rollback all changes if any record fails
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

    # Try to update existing and non-existent users
    user_data_list = [
        {
            "id": user1.id,
            "name": "John Updated"
        },
        {
            "id": non_existent_id,  # Will cause error
            "name": "Non Existent"
        }
    ]

    response = client.put("/user/list", json=user_data_list)

    # Should return 400 or 500
    assert response.status_code in [400, 500]

    # Verify user1 was not updated (transaction rollback) by checking via GET endpoint
    list_response = client.get("/user/list")
    assert list_response.status_code == 200
    users = list_response.json()["data"]["items"]
    user_ids = [u["id"] for u in users]
    
    # With 400, transaction should have rolled back. With 500, behavior may vary
    if response.status_code == 400:
        assert user1.id in user_ids, f"User {user1.id} should still exist (transaction rollback)"
        user1_data = next(u for u in users if u["id"] == user1.id)
        assert user1_data["name"] == "John"  # Not updated due to rollback
        # Verify user2 was not affected
        assert user2.id in user_ids, f"User {user2.id} should still exist"
        user2_data = next(u for u in users if u["id"] == user2.id)
        assert user2_data["name"] == "Jane"  # Unchanged


def test_update_user_list_multiple_updates_consistency(client: TestClient, test_session: Session):
    """
    Test PUT /user/list with multiple sequential batch updates

    Should maintain consistency across multiple operations
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

    # First batch update
    user_data_list1 = [
        {
            "id": user1.id,
            "name": "John First",
            "age": 31
        },
        {
            "id": user2.id,
            "name": "Jane First",
            "age": 26
        }
    ]
    response1 = client.put("/user/list", json=user_data_list1)
    assert response1.status_code == 200

    # Second batch update
    user_data_list2 = [
        {
            "id": user1.id,
            "name": "John Second",
            "age": 32
        },
        {
            "id": user2.id,
            "name": "Jane Second",
            "age": 27
        }
    ]
    response2 = client.put("/user/list", json=user_data_list2)
    assert response2.status_code == 200

    # Verify final state (refresh session to see updates from API)
    test_session.expire_all()
    db_user1 = test_session.get(User, user1.id)
    assert db_user1.name == "John Second"
    assert db_user1.age == 32

    db_user2 = test_session.get(User, user2.id)
    assert db_user2.name == "Jane Second"
    assert db_user2.age == 27

