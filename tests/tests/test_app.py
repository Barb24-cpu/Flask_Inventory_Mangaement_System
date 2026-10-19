"""Tests for the Flask API endpoints and the OpenFoodFacts integration."""
import copy
from unittest.mock import MagicMock, patch
 
import pytest
import requests
 
import app as app_module
from app import INITIAL_INVENTORY, app
 
 
@pytest.fixture
def client():
    """Test client with a fresh copy of the mock database for every test."""
    app_module.inventory[:] = copy.deepcopy(INITIAL_INVENTORY)
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


        def mock_response(json_data, status=200):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    return resp
 
 
# ------------------------------- GET ---------------------------------------
def test_get_all_items(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    assert len(response.get_json()) == len(INITIAL_INVENTORY)
 
 
def test_get_single_item(client):
    response = client.get("/inventory/1")
    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Organic Almond Milk"
 
 
def test_get_missing_item_returns_404(client):
    assert client.get("/inventory/999").status_code == 404
 