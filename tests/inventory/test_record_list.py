"""
Tests for GET /inventory/record-list endpoint

Tests the inventory record list retrieval functionality
"""
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.koujyou_master import KoujyouMaster


def test_get_record_list_empty(client: TestClient):
    """
    Test GET /inventory/record-list with empty database

    Should return an empty list when no records exist
    """
    response = client.get("/inventory/record-list")

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


def test_get_record_list_with_records(client: TestClient, test_session: Session):
    """
    Test GET /inventory/record-list with records in database

    Should return a list of all records
    """
    # Create test records
    record1 = KoujyouMaster(
        company_code="0001",
        previous_factory_code="F001",
        product_factory_code="P001",
        start_operation_date=date(2024, 1, 1),
        end_operation_date=date(2024, 12, 31),
        previous_factory_name="Factory 1",
        product_factory_name="Product Factory 1"
    )
    record2 = KoujyouMaster(
        company_code="0002",
        previous_factory_code="F002",
        product_factory_code="P002",
        start_operation_date=date(2024, 1, 1),
        end_operation_date=date(2024, 12, 31),
        previous_factory_name="Factory 2",
        product_factory_name="Product Factory 2"
    )

    test_session.add(record1)
    test_session.add(record2)
    test_session.commit()
    test_session.refresh(record1)
    test_session.refresh(record2)

    # Make request
    response = client.get("/inventory/record-list")

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert data["code"] == 200
    assert data["error"] is None
    assert "data" in data
    assert "items" in data["data"]

    # Verify records are returned
    items = data["data"]["items"]
    assert len(items) >= 2

    # Verify record data structure
    record_codes = [
        (item["previous_factory_code"], item["company_code"], item["product_factory_code"])
        for item in items
    ]
    assert ("F001", "0001", "P001") in record_codes
    assert ("F002", "0002", "P002") in record_codes

    # Verify record details
    record1_data = next(
        item for item in items
        if item["previous_factory_code"] == "F001"
        and item["company_code"] == "0001"
        and item["product_factory_code"] == "P001"
    )
    assert record1_data["previous_factory_name"] == "Factory 1"
    assert record1_data["product_factory_name"] == "Product Factory 1"

    record2_data = next(
        item for item in items
        if item["previous_factory_code"] == "F002"
        and item["company_code"] == "0002"
        and item["product_factory_code"] == "P002"
    )
    assert record2_data["previous_factory_name"] == "Factory 2"
    assert record2_data["product_factory_name"] == "Product Factory 2"


def test_get_record_list_with_previous_factory_code_filter(client: TestClient, test_session: Session):
    """
    Test GET /inventory/record-list with previous_factory_code filter

    Should return only records matching the previous_factory_code
    """
    # Create test records
    record1 = KoujyouMaster(
        company_code="0001",
        previous_factory_code="F001",
        product_factory_code="P001",
        start_operation_date=date(2024, 1, 1),
        end_operation_date=date(2024, 12, 31),
        previous_factory_name="Factory 1"
    )
    record2 = KoujyouMaster(
        company_code="0002",
        previous_factory_code="F002",
        product_factory_code="P002",
        start_operation_date=date(2024, 1, 1),
        end_operation_date=date(2024, 12, 31),
        previous_factory_name="Factory 2"
    )

    test_session.add(record1)
    test_session.add(record2)
    test_session.commit()

    # Make request with filter
    response = client.get("/inventory/record-list?previous_factory_code=F001")

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert data["code"] == 200
    assert data["error"] is None

    # Verify filtered results
    items = data["data"]["items"]
    assert len(items) >= 1
    assert all(item["previous_factory_code"] == "F001" for item in items)


def test_get_record_list_with_product_factory_code_filter(client: TestClient, test_session: Session):
    """
    Test GET /inventory/record-list with product_factory_code filter

    Should return only records matching the product_factory_code
    """
    # Create test records
    record1 = KoujyouMaster(
        company_code="0001",
        previous_factory_code="F001",
        product_factory_code="P001",
        start_operation_date=date(2024, 1, 1),
        end_operation_date=date(2024, 12, 31)
    )
    record2 = KoujyouMaster(
        company_code="0002",
        previous_factory_code="F002",
        product_factory_code="P002",
        start_operation_date=date(2024, 1, 1),
        end_operation_date=date(2024, 12, 31)
    )

    test_session.add(record1)
    test_session.add(record2)
    test_session.commit()

    # Make request with filter
    response = client.get("/inventory/record-list?product_factory_code=P001")

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert data["code"] == 200
    assert data["error"] is None

    # Verify filtered results
    items = data["data"]["items"]
    assert len(items) >= 1
    assert all(item["product_factory_code"] == "P001" for item in items)


def test_get_record_list_with_search_keyword(client: TestClient, test_session: Session):
    """
    Test GET /inventory/record-list with search_keyword parameter

    Should return records matching the search keyword across all columns
    """
    # Create test records
    record1 = KoujyouMaster(
        company_code="0001",
        previous_factory_code="F001",
        product_factory_code="P001",
        start_operation_date=date(2024, 1, 1),
        end_operation_date=date(2024, 12, 31),
        previous_factory_name="Tokyo Factory"
    )
    record2 = KoujyouMaster(
        company_code="0002",
        previous_factory_code="F002",
        product_factory_code="P002",
        start_operation_date=date(2024, 1, 1),
        end_operation_date=date(2024, 12, 31),
        previous_factory_name="Osaka Factory"
    )

    test_session.add(record1)
    test_session.add(record2)
    test_session.commit()

    # Make request with search keyword
    response = client.get("/inventory/record-list?search_keyword=Tokyo")

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert data["code"] == 200
    assert data["error"] is None

    # Verify search results (at least one record should match)
    items = data["data"]["items"]
    assert len(items) >= 1

