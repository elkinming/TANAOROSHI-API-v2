"""
Tests for PUT /inventory/record endpoint

Tests the inventory record update functionality
"""
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.koujyou_master import KoujyouMaster


def test_update_record_success(client: TestClient, test_session: Session):
    """
    Test PUT /inventory/record with valid data

    Should successfully update an existing record and return it
    """
    # Create a record first
    existing_record = KoujyouMaster(
        company_code="0001",
        previous_factory_code="F001",
        product_factory_code="P001",
        start_operation_date=date(2024, 1, 1),
        end_operation_date=date(2024, 12, 31),
        previous_factory_name="Factory 1",
        product_factory_name="Product Factory 1"
    )
    test_session.add(existing_record)
    test_session.commit()

    # Prepare update data
    update_data = {
        "company_code": "0001",
        "previous_factory_code": "F001",
        "product_factory_code": "P001",
        "start_operation_date": "2024-01-01",
        "end_operation_date": "2024-12-31",
        "previous_factory_name": "Updated Factory 1",
        "product_factory_name": "Updated Product Factory 1"
    }

    # Make request
    response = client.put("/inventory/record", json=update_data)

    # Verify response status
    assert response.status_code == 200

    # Verify response structure
    data = response.json()
    assert "code" in data
    assert "message" in data
    assert "data" in data
    assert data["code"] == 200
    assert data["error"] is None

    # Verify updated record data
    updated_record = data["data"]
    assert updated_record["company_code"] == "0001"
    assert updated_record["previous_factory_code"] == "F001"
    assert updated_record["product_factory_code"] == "P001"
    assert updated_record["previous_factory_name"] == "Updated Factory 1"
    assert updated_record["product_factory_name"] == "Updated Product Factory 1"

    # Verify record was actually updated in database
    db_record = test_session.get(
        KoujyouMaster,
        ("F001", "0001", "P001", date(2024, 1, 1), date(2024, 12, 31))
    )
    assert db_record is not None
    assert db_record.previous_factory_name == "Updated Factory 1"
    assert db_record.product_factory_name == "Updated Product Factory 1"


def test_update_record_with_all_fields(client: TestClient, test_session: Session):
    """
    Test PUT /inventory/record updating all optional fields

    Should successfully update a record with all fields populated
    """
    # Create a record first
    existing_record = KoujyouMaster(
        company_code="0002",
        previous_factory_code="F002",
        product_factory_code="P002",
        start_operation_date=date(2024, 1, 1),
        end_operation_date=date(2024, 12, 31),
        previous_factory_name="Factory 2"
    )
    test_session.add(existing_record)
    test_session.commit()

    # Prepare update data with all fields
    update_data = {
        "company_code": "0002",
        "previous_factory_code": "F002",
        "product_factory_code": "P002",
        "start_operation_date": "2024-01-01",
        "end_operation_date": "2024-12-31",
        "previous_factory_name": "Updated Factory 2",
        "product_factory_name": "Updated Product Factory 2",
        "material_department_code": "MD02",
        "environmental_information": "ENV002",
        "authentication_flag": "AUTH002",
        "group_corporate_code": "GC002",
        "integration_pattern": "IP002",
        "hulftid": "HULFT002"
    }

    # Make request
    response = client.put("/inventory/record", json=update_data)

    # Verify response status
    assert response.status_code == 200

    # Verify response structure
    data = response.json()
    assert data["code"] == 200
    assert data["error"] is None

    # Verify all fields in updated record
    updated_record = data["data"]
    assert updated_record["company_code"] == "0002"
    assert updated_record["previous_factory_code"] == "F002"
    assert updated_record["product_factory_code"] == "P002"
    assert updated_record["previous_factory_name"] == "Updated Factory 2"
    assert updated_record["product_factory_name"] == "Updated Product Factory 2"
    assert updated_record["material_department_code"] == "MD02"
    assert updated_record["environmental_information"] == "ENV002"
    assert updated_record["authentication_flag"] == "AUTH002"
    assert updated_record["group_corporate_code"] == "GC002"
    assert updated_record["integration_pattern"] == "IP002"
    assert updated_record["hulftid"] == "HULFT002"

    # Verify record was actually updated in database
    db_record = test_session.get(
        KoujyouMaster,
        ("F002", "0002", "P002", date(2024, 1, 1), date(2024, 12, 31))
    )
    assert db_record is not None
    assert db_record.previous_factory_name == "Updated Factory 2"
    assert db_record.material_department_code == "MD02"


def test_update_record_minimal_fields(client: TestClient, test_session: Session):
    """
    Test PUT /inventory/record with only required fields

    Should successfully update a record with only required fields
    """
    # Create a record first with optional fields
    existing_record = KoujyouMaster(
        company_code="0003",
        previous_factory_code="F003",
        product_factory_code="P003",
        start_operation_date=date(2024, 1, 1),
        end_operation_date=date(2024, 12, 31),
        previous_factory_name="Factory 3",
        product_factory_name="Product Factory 3"
    )
    test_session.add(existing_record)
    test_session.commit()

    # Prepare update data with only required fields
    update_data = {
        "company_code": "0003",
        "previous_factory_code": "F003",
        "product_factory_code": "P003",
        "start_operation_date": "2024-01-01",
        "end_operation_date": "2024-12-31"
    }

    # Make request
    response = client.put("/inventory/record", json=update_data)

    # Verify response status
    assert response.status_code == 200

    # Verify response structure
    data = response.json()
    assert data["code"] == 200
    assert data["error"] is None

    # Verify updated record data
    updated_record = data["data"]
    assert updated_record["company_code"] == "0003"
    assert updated_record["previous_factory_code"] == "F003"
    assert updated_record["product_factory_code"] == "P003"

    # Verify record exists in database
    db_record = test_session.get(
        KoujyouMaster,
        ("F003", "0003", "P003", date(2024, 1, 1), date(2024, 12, 31))
    )
    assert db_record is not None

