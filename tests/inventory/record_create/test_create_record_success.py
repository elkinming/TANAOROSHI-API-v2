"""
Test for POST /inventory/record with valid data

Should successfully create a new record and return it
"""
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.koujyou_master import KoujyouMaster


def test_create_record_success(client: TestClient, test_session: Session):
    """
    Test POST /inventory/record with valid data

    Should successfully create a new record and return it
    """
    # Prepare request data
    request_data = {
        "company_code": "0001",
        "previous_factory_code": "F001",
        "product_factory_code": "P001",
        "start_operation_date": "2024-01-01",
        "end_operation_date": "2024-12-31",
        "previous_factory_name": "Factory 1",
        "product_factory_name": "Product Factory 1"
    }

    # Make request
    response = client.post("/inventory/record", json=request_data)

    # Verify response status
    assert response.status_code == 200

    # Verify response structure
    data = response.json()
    assert "code" in data
    assert "message" in data
    assert "data" in data
    assert data["code"] == 200
    assert data["error"] is None

    # Verify created record data
    created_record = data["data"]
    assert created_record["company_code"] == "0001"
    assert created_record["previous_factory_code"] == "F001"
    assert created_record["product_factory_code"] == "P001"
    assert created_record["previous_factory_name"] == "Factory 1"
    assert created_record["product_factory_name"] == "Product Factory 1"
    assert created_record["start_operation_date"] == "2024-01-01"
    assert created_record["end_operation_date"] == "2024-12-31"

    # Verify record was actually created in database
    db_record = test_session.get(
        KoujyouMaster,
        ("F001", "0001", "P001", date(2024, 1, 1), date(2024, 12, 31))
    )
    assert db_record is not None
    assert db_record.previous_factory_name == "Factory 1"

