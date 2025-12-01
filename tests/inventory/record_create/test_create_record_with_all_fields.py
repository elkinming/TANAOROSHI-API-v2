"""
Test for POST /inventory/record with all optional fields

Should successfully create a record with all fields populated
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session


def test_create_record_with_all_fields(client: TestClient, test_session: Session):
    """
    Test POST /inventory/record with all optional fields

    Should successfully create a record with all fields populated
    """
    # Prepare request data with all fields
    request_data = {
        "company_code": "0003",
        "previous_factory_code": "F003",
        "product_factory_code": "P003",
        "start_operation_date": "2024-01-01",
        "end_operation_date": "2024-12-31",
        "previous_factory_name": "Factory 3",
        "product_factory_name": "Product Factory 3",
        "material_department_code": "MD01",
        "environmental_information": "ENV001",
        "authentication_flag": "AUTH001",
        "group_corporate_code": "GC001",
        "integration_pattern": "IP001",
        "hulftid": "HULFT001"
    }

    # Make request
    response = client.post("/inventory/record", json=request_data)

    # Verify response status
    assert response.status_code == 200

    # Verify response structure
    data = response.json()
    assert data["code"] == 200
    assert data["error"] is None

    # Verify all fields in created record
    created_record = data["data"]
    assert created_record["company_code"] == "0003"
    assert created_record["previous_factory_code"] == "F003"
    assert created_record["product_factory_code"] == "P003"
    assert created_record["previous_factory_name"] == "Factory 3"
    assert created_record["product_factory_name"] == "Product Factory 3"
    assert created_record["material_department_code"] == "MD01"
    assert created_record["environmental_information"] == "ENV001"
    assert created_record["authentication_flag"] == "AUTH001"
    assert created_record["group_corporate_code"] == "GC001"
    assert created_record["integration_pattern"] == "IP001"
    assert created_record["hulftid"] == "HULFT001"

