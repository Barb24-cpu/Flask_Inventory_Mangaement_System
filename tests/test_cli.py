"""Tests for the CLI. User input and HTTP calls are both mocked."""
from unittest.mock import MagicMock, patch
 
import requests
 
import cli
 
ITEM = {
    "id": 1, "product_name": "Organic Almond Milk", "brands": "Silk",
    "barcode": "123", "price": 3.99, "stock": 25,
}
 
 
def fake_response(status, body):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = body
    return resp
 
 
@patch("cli.requests.request")
def test_api_request_returns_status_and_body(mock_request):
    mock_request.return_value = fake_response(200, [ITEM])
    assert cli.api_request("GET", "/inventory") == (200, [ITEM])
 
 
@patch("cli.requests.request", side_effect=requests.ConnectionError)
def test_api_request_handles_connection_error(mock_request, capsys):
    assert cli.api_request("GET", "/inventory") == (None, None)
    assert "could not reach the API" in capsys.readouterr().out
 
 
@patch("cli.requests.request")
def test_list_items_prints_items(mock_request, capsys):
    mock_request.return_value = fake_response(200, [ITEM])
    cli.list_items()
    assert "Organic Almond Milk" in capsys.readouterr().out
 
 
@patch("cli.requests.request")
def test_view_item_not_found_shows_error(mock_request, capsys):
    mock_request.return_value = fake_response(404, {"error": "Item not found"})
    with patch("builtins.input", side_effect=["99"]):
        cli.view_item()
    assert "Item not found" in capsys.readouterr().out
 
 
@patch("cli.requests.request")
def test_add_item_sends_payload(mock_request, capsys):
    mock_request.return_value = fake_response(201, {**ITEM, "id": 4, "product_name": "Tea"})
    with patch("builtins.input", side_effect=["Tea", "Leaf", "999", "2.5", "10"]):
        cli.add_item()
    payload = mock_request.call_args.kwargs["json"]
    assert payload["product_name"] == "Tea" and payload["price"] == 2.5 and payload["stock"] == 10
    assert "Item added" in capsys.readouterr().out
 
 
def test_add_item_rejects_empty_name(capsys):
    with patch("builtins.input", side_effect=[""]):
        cli.add_item()
    assert "cannot be empty" in capsys.readouterr().out
 
 
@patch("cli.requests.request")
def test_update_item_price(mock_request):
    mock_request.return_value = fake_response(200, {**ITEM, "price": 5.0})
    with patch("builtins.input", side_effect=["1", "p", "5.0"]):
        cli.update_item()
    assert mock_request.call_args.args[0] == "PATCH"
    assert mock_request.call_args.kwargs["json"] == {"price": 5.0}
 
 
@patch("cli.requests.request")
def test_delete_item(mock_request, capsys):
    mock_request.return_value = fake_response(200, {"message": "Item 1 deleted"})
    with patch("builtins.input", side_effect=["1"]):
        cli.delete_item()
    assert "Item 1 deleted" in capsys.readouterr().out
 
 
def test_ask_int_retries_on_invalid_input(capsys):
    with patch("builtins.input", side_effect=["abc", "-3", "7"]):
        assert cli.ask_int("n: ") == 7
    assert "whole number" in capsys.readouterr().out
 
 
@patch("cli.requests.request")
def test_find_on_api_by_barcode_and_import(mock_request, capsys):
    mock_request.side_effect = [
        fake_response(200, {"product_name": "Nutella", "brands": "Ferrero", "ingredients_text": "Sugar", "barcode": "301"}),
        fake_response(201, {**ITEM, "id": 4, "product_name": "Nutella"}),
    ]
    with patch("builtins.input", side_effect=["b", "301", "y", "4.5", "10"]):
        cli.find_on_api()
    assert "Added to inventory" in capsys.readouterr().out
 
 
@patch("cli.requests.request")
def test_find_on_api_handles_external_failure(mock_request, capsys):
    mock_request.return_value = fake_response(502, {"error": "External API unavailable"})
    with patch("builtins.input", side_effect=["b", "123"]):
        cli.find_on_api()
    assert "External API unavailable" in capsys.readouterr().out
 
 
def test_main_handles_invalid_option_then_quits(capsys):
    with patch("builtins.input", side_effect=["x", "7"]):
        cli.main()
    out = capsys.readouterr().out
    assert "Invalid option" in out and "Goodbye" in out
 