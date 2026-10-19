
"""Flask REST API for a small retail inventory management system.
 
Inventory is kept in an in-memory list (a mock database). Extra product
details are fetched from the OpenFoodFacts public API.
"""
import copy
 
import requests
from flask import Flask, jsonify, request
 
app = Flask(__name__)
 
OFF_BASE_URL = "https://world.openfoodfacts.org"
# OpenFoodFacts asks API users to identify their app with a User-Agent.
OFF_HEADERS = {"User-Agent": "InventoryManager/1.0 (student-project)"}
OFF_TIMEOUT = 10  # seconds


# Mock database (resembles OpenFoodFacts product data; every item has an id)

INITIAL_INVENTORY = [
    {
        "id": 1,
        "barcode": "0000000000001",
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "ingredients_text": "Filtered water, almonds, cane sugar",
        "price": 3.99,
        "stock": 25,
    },
    {
        "id": 2,
        "barcode": "0000000000002",
        "product_name": "Whole Wheat Bread",
        "brands": "Baker's Best",
        "ingredients_text": "Whole wheat flour, water, yeast, salt",
        "price": 2.49,
        "stock": 40,
    },
    {
        "id": 3,
        "barcode": "0000000000003",
        "product_name": "Peanut Butter",
        "brands": "NutriSpread",
        "ingredients_text": "Roasted peanuts, salt",
        "price": 4.75,
        "stock": 18,
    },
]
inventory = copy.deepcopy(INITIAL_INVENTORY)
 
ALLOWED_FIELDS = {"barcode", "product_name", "brands", "ingredients_text", "price", "stock"}

# Helper functions
# ---------------------------------------------------------------------------
def find_item(item_id):
    """Return the inventory item with this id, or None."""
    return next((item for item in inventory if item["id"] == item_id), None)
 
 
def next_id():
    """Return the next free id (max existing id + 1)."""
    return max((item["id"] for item in inventory), default=0) + 1
 
 
def is_number(value):
    """True for int/float but not bool (bool is a subclass of int)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)
 
 
def validate_fields(data, partial=False):
    """Validate item fields. Returns an error message string, or None if valid."""
    if not partial and not data.get("product_name"):
        return "product_name is required"
    if "product_name" in data and (
        not isinstance(data["product_name"], str) or not data["product_name"].strip()
    ):
        return "product_name must be a non-empty string"
    if "price" in data and (not is_number(data["price"]) or data["price"] < 0):
        return "price must be a number >= 0"
    if "stock" in data and (
        not isinstance(data["stock"], int) or isinstance(data["stock"], bool) or data["stock"] < 0
    ):
        return "stock must be an integer >= 0"
    return None
 
 
def clean_product(product, barcode=None):
    """Keep only the OpenFoodFacts fields we care about."""
    return {
        "barcode": barcode or product.get("code", ""),
        "product_name": product.get("product_name", "Unknown product"),
        "brands": product.get("brands", ""),
        "ingredients_text": product.get("ingredients_text", ""),
    }
 
 
def fetch_product_by_barcode(barcode):
    """Query OpenFoodFacts by barcode. Returns a cleaned dict, or None if not found.
 
    Raises requests.RequestException if the external API is unreachable.
    """
    url = f"{OFF_BASE_URL}/api/v0/product/{barcode}.json"
    response = requests.get(url, headers=OFF_HEADERS, timeout=OFF_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    if data.get("status") != 1:
        return None
    return clean_product(data["product"], barcode)
 
 
def search_products_by_name(name, limit=5):
    """Search OpenFoodFacts by product name. Returns a list of cleaned dicts.
 
    Raises requests.RequestException if the external API is unreachable.
    """
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": limit,
    }
    response = requests.get(
        f"{OFF_BASE_URL}/cgi/search.pl", params=params, headers=OFF_HEADERS, timeout=OFF_TIMEOUT
    )
    response.raise_for_status()
    return [clean_product(p) for p in response.json().get("products", [])]