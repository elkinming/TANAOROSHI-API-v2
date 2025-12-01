"""
Test for POST /inventory/record with only required fields

Should successfully create a record with only required fields
"""
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.koujyou_master import KoujyouMaster


def test_create_record_minimal_fields(client: TestClient, test_session: Session):
    """
    Test POST /inventory/record with only required fields

    Should successfully create a record with only required fields
    """
    # Prepare request data with only required fields
    request_data = {
        "company_code": "0002",
        "previous_factory_code": "F002",
        "product_factory_code": "P002",
        "start_operation_date": "2024-01-01",
        "end_operation_date": "2024-12-31"
    }

    # Make request
    response = client.post("/inventory/record", json=request_data)

    # Verify response status
    assert response.status_code == 200

    # Verify response structure
    data = response.json()
    assert data["code"] == 200
    assert data["error"] is None

    # Verify created record data
    created_record = data["data"]
    assert created_record["company_code"] == "0002"
    assert created_record["previous_factory_code"] == "F002"
    assert created_record["product_factory_code"] == "P002"

    # Verify record was actually created in database
    db_record = test_session.get(
        KoujyouMaster,
        ("F002", "0002", "P002", date(2024, 1, 1), date(2024, 12, 31))
    )
    assert db_record is not None

