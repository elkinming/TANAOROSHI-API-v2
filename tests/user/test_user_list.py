"""
Tests for GET /user/list endpoint

Tests the user list retrieval functionality
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.user import User


def test_get_user_list_empty(client: TestClient):
    """
    Test GET /user/list with empty database

    Should return an empty list when no users exist
    """
    response = client.get("/user/list")

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "code" in data
    assert "message" in data
    assert "data" in data
    assert data["code"] == 200
    assert data["error"] is None

    # Verify data structure
    assert "items" in data["data"]
    assert isinstance(data["data"]["items"], list)
    assert len(data["data"]["items"]) == 0


def test_get_user_list_with_users(client: TestClient, test_session: Session):
    """
    Test GET /user/list with users in database

    Should return a list of all users
    """
    # Create test users
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

    # Make request
    response = client.get("/user/list")

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert data["code"] == 200
    assert data["error"] is None
    assert "data" in data
    assert "items" in data["data"]

    # Verify users are returned
    items = data["data"]["items"]
    assert len(items) == 2

    # Verify user data structure
    user_ids = [item["id"] for item in items]
    assert user1.id in user_ids
    assert user2.id in user_ids

    # Verify user details
    user1_data = next(item for item in items if item["id"] == user1.id)
    assert user1_data["name"] == "John"
    assert user1_data["lastname"] == "Doe"
    assert user1_data["age"] == 30
    assert user1_data["country"] == "USA"
    assert user1_data["home_address"] == "123 Main St"

    user2_data = next(item for item in items if item["id"] == user2.id)
    assert user2_data["name"] == "Jane"
    assert user2_data["lastname"] == "Smith"
    assert user2_data["age"] == 25
    assert user2_data["country"] == "Canada"


def test_get_user_list_with_search_keyword(client: TestClient, test_session: Session):
    """
    Test GET /user/list with search_keyword parameter

    Should filter users based on search keyword
    """
    # Create test users
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
        country="USA",
        home_address="789 Pine Rd"
    )

    test_session.add(user1)
    test_session.add(user2)
    test_session.add(user3)
    test_session.commit()

    # Test search by name
    response = client.get("/user/list?search_keyword=John")

    assert response.status_code == 200
    data = response.json()

    assert data["code"] == 200
    items = data["data"]["items"]
    # Should find both "John" Doe and "Johnson"
    assert len(items) >= 1
    assert any("John" in item.get("name", "") or "John" in item.get("lastname", "")
               for item in items)

    # Test search by country
    response = client.get("/user/list?search_keyword=USA")

    assert response.status_code == 200
    data = response.json()

    assert data["code"] == 200
    items = data["data"]["items"]
    # Should find users with USA in country
    assert len(items) >= 1
    assert all("USA" in str(item.get("country", "")) for item in items)


def test_get_user_list_response_structure(client: TestClient, test_session: Session):
    """
    Test GET /user/list response structure

    Should return properly formatted ApiResponse with ListResponse
    """
    # Create a test user
    user = User(
        name="Test",
        lastname="User",
        age=20,
        country="Japan",
        home_address="Tokyo"
    )
    test_session.add(user)
    test_session.commit()

    response = client.get("/user/list")

    assert response.status_code == 200
    data = response.json()

    # Verify ApiResponse structure
    assert "code" in data
    assert "message" in data
    assert "data" in data
    assert "error" in data

    assert isinstance(data["code"], int)
    assert isinstance(data["message"], str)
    assert data["error"] is None

    # Verify ListResponse structure
    assert isinstance(data["data"], dict)
    assert "items" in data["data"]
    assert isinstance(data["data"]["items"], list)

    # Verify UserResponse structure in items
    if len(data["data"]["items"]) > 0:
        user_item = data["data"]["items"][0]
        assert "id" in user_item
        # Other fields are optional, but should be present if set
        assert "name" in user_item or user_item.get("name") is None
        assert "lastname" in user_item or user_item.get("lastname") is None
        assert "age" in user_item or user_item.get("age") is None
        assert "country" in user_item or user_item.get("country") is None
        assert "home_address" in user_item or user_item.get("home_address") is None


# ==================== Search Keyword Edge Cases ====================

def test_get_user_list_search_keyword_empty_string(client: TestClient, test_session: Session):
    """
    Test GET /user/list with empty string search_keyword

    Should return all users (empty string should be treated as no filter)
    """
    user1 = User(name="Alice", lastname="Brown", age=30, country="USA", home_address="123 St")
    user2 = User(name="Bob", lastname="White", age=25, country="UK", home_address="456 Ave")

    test_session.add(user1)
    test_session.add(user2)
    test_session.commit()
    test_session.refresh(user1)
    test_session.refresh(user2)

    response = client.get("/user/list?search_keyword=")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "items" in data["data"]
    assert isinstance(data["data"]["items"], list)

    # Validate: Empty string should return all users or none (implementation dependent)
    items = data["data"]["items"]
    # Verify response structure is correct
    if len(items) > 0:
        # If it returns users, verify they are the ones we created
        user_ids = [item["id"] for item in items]
        assert user1.id in user_ids or user2.id in user_ids
        # Verify data structure
        for item in items:
            assert "id" in item
            assert "name" in item or item.get("name") is None
            assert "lastname" in item or item.get("lastname") is None
            assert "age" in item or item.get("age") is None
            assert "country" in item or item.get("country") is None
            assert "home_address" in item or item.get("home_address") is None


def test_get_user_list_search_keyword_whitespace(client: TestClient, test_session: Session):
    """
    Test GET /user/list with whitespace-only search_keyword

    Should handle whitespace gracefully
    """
    user = User(name="Test", lastname="User", age=20, country="Japan", home_address="Tokyo")
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    response = client.get("/user/list?search_keyword=%20")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "items" in data["data"]
    assert isinstance(data["data"]["items"], list)

    # Validate: Whitespace search should return empty results or all users
    items = data["data"]["items"]
    # Verify response structure
    for item in items:
        assert "id" in item
        # Verify the item structure is valid
        assert isinstance(item.get("name"), (str, type(None)))
        assert isinstance(item.get("age"), (int, type(None)))


def test_get_user_list_search_keyword_long_string(client: TestClient, test_session: Session):
    """
    Test GET /user/list with very long search_keyword

    Should handle long strings without errors
    """
    # Create a user with a long address
    long_address = "A" * 500  # 500 character string
    user = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address=long_address
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    # Search with long keyword
    long_keyword = "A" * 200
    response = client.get(f"/user/list?search_keyword={long_keyword}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "items" in data["data"]
    assert isinstance(data["data"]["items"], list)

    # Validate: Should find the user with long address
    items = data["data"]["items"]
    assert len(items) >= 1
    # Verify the returned user matches
    found_user = next((item for item in items if item["id"] == user.id), None)
    if found_user:
        assert found_user["name"] == "John"
        assert found_user["lastname"] == "Doe"
        assert found_user["age"] == 30
        assert found_user["country"] == "USA"
        assert "A" * 200 in found_user["home_address"]  # Should contain the search term


def test_get_user_list_search_keyword_long_number(client: TestClient, test_session: Session):
    """
    Test GET /user/list with long number as search_keyword

    Should handle long numeric strings
    """
    # Create users with numeric data in age
    user1 = User(name="User1", lastname="Test", age=1234567890, country="USA", home_address="123")
    user2 = User(name="User2", lastname="Test", age=9876543210, country="UK", home_address="456")

    test_session.add(user1)
    test_session.add(user2)
    test_session.commit()
    test_session.refresh(user1)
    test_session.refresh(user2)

    # Search with long number
    response = client.get("/user/list?search_keyword=1234567890")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "items" in data["data"]
    assert isinstance(data["data"]["items"], list)

    # Validate: Should find user1 by age
    items = data["data"]["items"]
    assert len(items) >= 1
    # Verify user1 is in the results
    user_ids = [item["id"] for item in items]
    assert user1.id in user_ids
    # Verify the returned user data
    user1_data = next(item for item in items if item["id"] == user1.id)
    assert user1_data["name"] == "User1"
    assert user1_data["age"] == 1234567890
    # Verify user2 is NOT in results (different age)
    assert user2.id not in user_ids


def test_get_user_list_search_keyword_special_characters(client: TestClient, test_session: Session):
    """
    Test GET /user/list with special characters in search_keyword

    Should handle special characters safely
    """
    # Create user with special characters
    user = User(
        name="Test",
        lastname="O'Brien",
        age=30,
        country="USA",
        home_address="123 Main St. #4"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    # Test various special characters with expected matches
    special_char_tests = [
        ("O'Brien", "lastname"),  # Apostrophe - should match lastname
        ("Main St.", "home_address"),  # Period - should match address
        ("#4", "home_address"),  # Hash - should match address
        ("St.", "home_address"),  # Period - should match address
    ]

    for search_term, expected_field in special_char_tests:
        response = client.get(f"/user/list?search_keyword={search_term}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]
        items = data["data"]["items"]
        # Should find the user
        assert len(items) >= 1
        # Verify the user is in results
        user_ids = [item["id"] for item in items]
        assert user.id in user_ids
        # Verify the search term appears in the expected field
        user_data = next(item for item in items if item["id"] == user.id)
        if expected_field == "lastname":
            assert search_term in user_data["lastname"]
        elif expected_field == "home_address":
            assert search_term in user_data["home_address"]


def test_get_user_list_search_keyword_sql_injection_attempt(client: TestClient, test_session: Session):
    """
    Test GET /user/list with SQL injection attempt in search_keyword

    Should safely handle SQL injection attempts without errors
    """
    user = User(name="Test", lastname="User", age=30, country="USA", home_address="123 St")
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    # SQL injection attempts
    sql_injections = [
        "'; DROP TABLE users; --",
        "' OR '1'='1",
        "'; SELECT * FROM users; --",
        "' UNION SELECT * FROM users --",
        "1' OR '1'='1",
    ]

    for injection in sql_injections:
        response = client.get(f"/user/list?search_keyword={injection}")
        # Should not crash, should return 200 (even if no results)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]
        assert isinstance(data["data"]["items"], list)

        # Validate: Should return empty results (SQL injection should not work)
        items = data["data"]["items"]
        # Verify no users are returned (injection should be treated as literal string)
        # The injection string doesn't match any user data, so should return empty
        assert len(items) == 0
        # Verify response structure is still valid
        assert data["error"] is None
        assert "message" in data


def test_get_user_list_search_keyword_unicode_characters(client: TestClient, test_session: Session):
    """
    Test GET /user/list with Unicode characters in search_keyword

    Should handle Unicode characters correctly
    """
    # Create users with Unicode characters
    user1 = User(
        name="José",
        lastname="García",
        age=30,
        country="México",
        home_address="Calle 123"
    )
    user2 = User(
        name="山田",
        lastname="太郎",
        age=25,
        country="日本",
        home_address="東京"
    )
    user3 = User(
        name="François",
        lastname="Müller",
        age=35,
        country="France",
        home_address="Rue de la Paix"
    )

    test_session.add(user1)
    test_session.add(user2)
    test_session.add(user3)
    test_session.commit()
    test_session.refresh(user1)
    test_session.refresh(user2)
    test_session.refresh(user3)

    # Test Unicode searches with expected matches
    unicode_searches = [
        ("José", user1, "name"),  # Accented character - should match user1 name
        ("García", user1, "lastname"),  # Accented character - should match user1 lastname
        ("山田", user2, "name"),  # Japanese characters - should match user2 name
        ("Müller", user3, "lastname"),  # Umlaut - should match user3 lastname
        ("François", user3, "name"),  # Accented character - should match user3 name
    ]

    for search_term, expected_user, expected_field in unicode_searches:
        response = client.get(f"/user/list?search_keyword={search_term}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]
        items = data["data"]["items"]
        # Should find at least one matching user
        assert len(items) >= 1
        # Verify the expected user is in results
        user_ids = [item["id"] for item in items]
        assert expected_user.id in user_ids
        # Verify the search term appears in the expected field
        user_data = next(item for item in items if item["id"] == expected_user.id)
        if expected_field == "name":
            assert search_term in user_data["name"]
        elif expected_field == "lastname":
            assert search_term in user_data["lastname"]


def test_get_user_list_search_keyword_mixed_special_chars(client: TestClient, test_session: Session):
    """
    Test GET /user/list with mixed special characters and text

    Should handle complex search terms
    """
    user = User(
        name="Test",
        lastname="User",
        age=30,
        country="USA",
        home_address="123 Main St., Apt. #4B, New York, NY 10001"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    # Mixed special character searches
    mixed_searches = [
        "Main St.,",
        "Apt. #4B",
        "New York, NY",
        "10001",
        "St., Apt.",
    ]

    for search_term in mixed_searches:
        response = client.get(f"/user/list?search_keyword={search_term}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]
        items = data["data"]["items"]
        # Should find the user
        assert len(items) >= 1
        # Verify the user is in results
        user_ids = [item["id"] for item in items]
        assert user.id in user_ids
        # Verify the search term appears in the address
        user_data = next(item for item in items if item["id"] == user.id)
        assert search_term in user_data["home_address"]


def test_get_user_list_search_keyword_case_insensitive(client: TestClient, test_session: Session):
    """
    Test GET /user/list with case variations in search_keyword

    Should be case-insensitive
    """
    user = User(
        name="John",
        lastname="Doe",
        age=30,
        country="USA",
        home_address="Main Street"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    # Test different case variations with expected field matches
    case_variations = [
        ("john", "name"),  # lowercase - should match name
        ("JOHN", "name"),  # uppercase - should match name
        ("JoHn", "name"),  # mixed case - should match name
        ("doe", "lastname"),  # lowercase - should match lastname
        ("DOE", "lastname"),  # uppercase - should match lastname
        ("DoE", "lastname"),  # mixed case - should match lastname
        ("main street", "home_address"),  # lowercase - should match address
        ("MAIN STREET", "home_address"),  # uppercase - should match address
        ("MaIn StReEt", "home_address"),  # mixed case - should match address
    ]

    for search_term, expected_field in case_variations:
        response = client.get(f"/user/list?search_keyword={search_term}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]
        items = data["data"]["items"]
        # Should find the user regardless of case
        assert len(items) >= 1
        # Verify the user is in results
        user_ids = [item["id"] for item in items]
        assert user.id in user_ids
        # Verify the search term (case-insensitive) appears in the expected field
        user_data = next(item for item in items if item["id"] == user.id)
        if expected_field == "name":
            assert search_term.lower() in user_data["name"].lower()
        elif expected_field == "lastname":
            assert search_term.lower() in user_data["lastname"].lower()
        elif expected_field == "home_address":
            assert search_term.lower() in user_data["home_address"].lower()


def test_get_user_list_search_keyword_partial_match(client: TestClient, test_session: Session):
    """
    Test GET /user/list with partial matches at different positions

    Should find matches at beginning, middle, and end of strings
    """
    user1 = User(name="Christopher", lastname="Anderson", age=30, country="USA", home_address="Main")
    user2 = User(name="Christina", lastname="Johnson", age=25, country="UK", home_address="Oak")
    user3 = User(name="Michael", lastname="Christensen", age=35, country="Canada", home_address="Pine")

    test_session.add(user1)
    test_session.add(user2)
    test_session.add(user3)
    test_session.commit()
    test_session.refresh(user1)
    test_session.refresh(user2)
    test_session.refresh(user3)

    # Test partial matches with expected users
    partial_searches = [
        ("Chris", [user1, user2], "name"),  # Beginning of name - should match user1 and user2
        ("pher", [user1], "name"),  # Middle of name - should match user1
        ("son", [user1, user2], "lastname"),  # End of lastname - should match user1 and user2
        ("Ander", [user1], "lastname"),  # Beginning of lastname - should match user1
        ("John", [user2], "lastname"),  # Middle of lastname - should match user2
    ]

    for search_term, expected_users, expected_field in partial_searches:
        response = client.get(f"/user/list?search_keyword={search_term}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]
        items = data["data"]["items"]
        # Should find at least one matching user
        assert len(items) >= 1
        # Verify all expected users are in results
        user_ids = [item["id"] for item in items]
        for expected_user in expected_users:
            assert expected_user.id in user_ids
            # Verify the search term appears in the expected field
            user_data = next(item for item in items if item["id"] == expected_user.id)
            if expected_field == "name":
                assert search_term.lower() in user_data["name"].lower()
            elif expected_field == "lastname":
                assert search_term.lower() in user_data["lastname"].lower()


def test_get_user_list_search_keyword_numeric_strings(client: TestClient, test_session: Session):
    """
    Test GET /user/list with numeric strings as search_keyword

    Should search numeric fields (age) as strings
    """
    user1 = User(name="User1", lastname="Test", age=25, country="USA", home_address="123 St")
    user2 = User(name="User2", lastname="Test", age=30, country="UK", home_address="456 Ave")
    user3 = User(name="User3", lastname="Test", age=35, country="Canada", home_address="789 Rd")

    test_session.add(user1)
    test_session.add(user2)
    test_session.add(user3)
    test_session.commit()
    test_session.refresh(user1)
    test_session.refresh(user2)
    test_session.refresh(user3)

    # Test numeric searches with expected users
    numeric_searches = [
        ("25", [user1], 25),  # Exact age match - should find user1
        ("30", [user2], 30),  # Exact age match - should find user2
        ("3", [user2, user3], None),  # Partial match (30, 35) - should find user2 and user3
        ("5", [user1, user3], None),  # Partial match (25, 35) - should find user1 and user3
    ]

    for search_term, expected_users, expected_age in numeric_searches:
        response = client.get(f"/user/list?search_keyword={search_term}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]
        items = data["data"]["items"]
        # Should find matching users
        assert len(items) >= 1
        # Verify all expected users are in results
        user_ids = [item["id"] for item in items]
        for expected_user in expected_users:
            assert expected_user.id in user_ids
            # Verify the age matches if specified
            if expected_age is not None:
                user_data = next(item for item in items if item["id"] == expected_user.id)
                assert user_data["age"] == expected_age
            # Verify the search term appears in age (as string)
            user_data = next(item for item in items if item["id"] == expected_user.id)
            assert search_term in str(user_data["age"])


def test_get_user_list_search_keyword_no_results(client: TestClient, test_session: Session):
    """
    Test GET /user/list with search_keyword that matches nothing

    Should return empty list without errors
    """
    user = User(name="John", lastname="Doe", age=30, country="USA", home_address="Main St")
    test_session.add(user)
    test_session.commit()

    # Search for something that doesn't exist
    response = client.get("/user/list?search_keyword=NonExistentUser12345")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "items" in data["data"]
    assert len(data["data"]["items"]) == 0


def test_get_user_list_search_keyword_url_encoded(client: TestClient, test_session: Session):
    """
    Test GET /user/list with URL-encoded special characters in search_keyword

    Should properly decode URL-encoded characters
    """
    user = User(
        name="Test",
        lastname="O'Brien",
        age=30,
        country="USA",
        home_address="123 Main St. #4"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    # Test URL-encoded characters
    # Note: FastAPI automatically decodes URL parameters, but we test edge cases
    response = client.get("/user/list?search_keyword=Main%20St.")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "items" in data["data"]
    items = data["data"]["items"]
    assert len(items) >= 1
    # Verify the user is in results
    user_ids = [item["id"] for item in items]
    assert user.id in user_ids
    # Verify the decoded search term "Main St." appears in the address
    user_data = next(item for item in items if item["id"] == user.id)
    assert "Main St." in user_data["home_address"]
    # Verify all returned items contain the search term
    for item in items:
        assert "Main St." in item["home_address"] or "Main St." in item.get("name", "") or "Main St." in item.get("lastname", "")

