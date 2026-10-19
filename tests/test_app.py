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
 
 
# ------------------------------- POST --------------------------------------
def test_post_adds_item(client):
    payload = {"product_name": "Green Tea", "brands": "Leaf", "price": 5.5, "stock": 12}
    response = client.post("/inventory", json=payload)
    assert response.status_code == 201
    body = response.get_json()
    assert body["id"] == 4
    assert client.get("/inventory/4").get_json()["product_name"] == "Green Tea"
 
 
def test_post_missing_name_returns_400(client):
    assert client.post("/inventory", json={"price": 1}).status_code == 400
 
 
def test_post_invalid_price_returns_400(client):
    response = client.post("/inventory", json={"product_name": "X", "price": -5})
    assert response.status_code == 400
 
 
def test_post_non_json_returns_400(client):
    assert client.post("/inventory", data="not json").status_code == 400
 
 
# ------------------------------- PATCH -------------------------------------
def test_patch_updates_price_and_stock(client):
    response = client.patch("/inventory/1", json={"price": 9.99, "stock": 3})
    assert response.status_code == 200
    body = response.get_json()
    assert body["price"] == 9.99 and body["stock"] == 3
    assert body["product_name"] == "Organic Almond Milk"  # untouched
 
 
def test_patch_cannot_change_id(client):
    client.patch("/inventory/1", json={"id": 50, "stock": 1})
    assert client.get("/inventory/1").status_code == 200
 
 
def test_patch_missing_item_returns_404(client):
    assert client.patch("/inventory/999", json={"stock": 1}).status_code == 404
 
 
def test_patch_invalid_stock_returns_400(client):
    assert client.patch("/inventory/1", json={"stock": "lots"}).status_code == 400
 
 
# ------------------------------- DELETE ------------------------------------
def test_delete_removes_item(client):
    assert client.delete("/inventory/2").status_code == 200
    assert client.get("/inventory/2").status_code == 404
 
 
def test_delete_missing_item_returns_404(client):
    assert client.delete("/inventory/999").status_code == 404
 
 
# ------------------------- External API (mocked) ---------------------------
FAKE_PRODUCT = {
    "status": 1,
    "product": {
        "product_name": "Nutella",
        "brands": "Ferrero",
        "ingredients_text": "Sugar, palm oil, hazelnuts",
    },
}
 
 
@patch("app.requests.get")
def test_external_barcode_found(mock_get, client):
    mock_get.return_value = mock_response(FAKE_PRODUCT)
    response = client.get("/external/barcode/3017620422003")
    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Nutella"
 
 
@patch("app.requests.get")
def test_external_barcode_not_found(mock_get, client):
    mock_get.return_value = mock_response({"status": 0})
    assert client.get("/external/barcode/000").status_code == 404
 
 
@patch("app.requests.get")
def test_external_api_failure_returns_502(mock_get, client):
    mock_get.side_effect = requests.ConnectionError("network down")
    assert client.get("/external/barcode/123").status_code == 502
 
 
@patch("app.requests.get")
def test_external_search_by_name(mock_get, client):
    mock_get.return_value = mock_response(
        {"products": [{"code": "111", "product_name": "Oat Milk", "brands": "Oatly"}]}
    )
    response = client.get("/external/search?name=oat")
    assert response.status_code == 200
    assert response.get_json()[0]["barcode"] == "111"
 
 
def test_external_search_requires_name(client):
    assert client.get("/external/search").status_code == 400
 
 
@patch("app.requests.get")
def test_import_adds_api_product_to_inventory(mock_get, client):
    mock_get.return_value = mock_response(FAKE_PRODUCT)
    response = client.post("/inventory/import", json={"barcode": "3017620422003", "price": 4.5, "stock": 10})
    assert response.status_code == 201
    body = response.get_json()
    assert body["product_name"] == "Nutella" and body["price"] == 4.5
    assert len(client.get("/inventory").get_json()) == len(INITIAL_INVENTORY) + 1
 
 
@patch("app.requests.get")
def test_import_unknown_barcode_returns_404(mock_get, client):
    mock_get.return_value = mock_response({"status": 0})
    assert client.post("/inventory/import", json={"barcode": "000"}).status_code == 404
 
 
def test_import_requires_barcode(client):
    assert client.post("/inventory/import", json={}).status_code == 400
 