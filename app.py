
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


    # CRUD routes

@app.route("/inventory", methods=["GET"])
def get_inventory():
    """Fetch all items."""
    return jsonify(inventory), 200
 
 
@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    """Fetch a single item."""
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200
 
 
@app.route("/inventory", methods=["POST"])
def add_item():
    """Add a new item."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be JSON"}), 400
    error = validate_fields(data)
    if error:
        return jsonify({"error": error}), 400
 
    item = {
        "id": next_id(),
        "barcode": data.get("barcode", ""),
        "product_name": data["product_name"].strip(),
        "brands": data.get("brands", ""),
        "ingredients_text": data.get("ingredients_text", ""),
        "price": data.get("price", 0.0),
        "stock": data.get("stock", 0),
    }
    inventory.append(item)
    return jsonify(item), 201
 
 
@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    """Update fields (e.g. price or stock) of an existing item."""
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return jsonify({"error": "Request body must be non-empty JSON"}), 400
    error = validate_fields(data, partial=True)
    if error:
        return jsonify({"error": error}), 400
 
    for key, value in data.items():
        if key in ALLOWED_FIELDS:  # ignore unknown fields and never allow id changes
            item[key] = value.strip() if isinstance(value, str) else value
    return jsonify(item), 200
 
 
@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    """Remove an item."""
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    inventory.remove(item)
    return jsonify({"message": f"Item {item_id} deleted"}), 200
 
 
 # External API helper routes

@app.route("/external/barcode/<barcode>", methods=["GET"])
def external_by_barcode(barcode):
    """Look up a product on OpenFoodFacts by barcode (does not change inventory)."""
    try:
        product = fetch_product_by_barcode(barcode)
    except requests.RequestException:
        return jsonify({"error": "External API unavailable"}), 502
    if product is None:
        return jsonify({"error": "Product not found on OpenFoodFacts"}), 404
    return jsonify(product), 200
 
 
@app.route("/external/search", methods=["GET"])
def external_search():
    """Search OpenFoodFacts by name: /external/search?name=nutella"""
    name = request.args.get("name", "").strip()
    if not name:
        return jsonify({"error": "name query parameter is required"}), 400
    try:
        products = search_products_by_name(name)
    except requests.RequestException:
        return jsonify({"error": "External API unavailable"}), 502
    return jsonify(products), 200
 
 
@app.route("/inventory/import", methods=["POST"])
def import_item():
    """Fetch a product from OpenFoodFacts by barcode and add it to inventory.
 
    JSON body: {"barcode": "3017620422003", "price": 4.5, "stock": 10}
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data.get("barcode"):
        return jsonify({"error": "barcode is required"}), 400
    error = validate_fields({k: v for k, v in data.items() if k in ("price", "stock")}, partial=True)
    if error:
        return jsonify({"error": error}), 400
 
    try:
        product = fetch_product_by_barcode(str(data["barcode"]))
    except requests.RequestException:
        return jsonify({"error": "External API unavailable"}), 502
    if product is None:
        return jsonify({"error": "Product not found on OpenFoodFacts"}), 404
 
    item = {"id": next_id(), **product, "price": data.get("price", 0.0), "stock": data.get("stock", 0)}
    inventory.append(item)
    return jsonify(item), 201
 
 
if __name__ == "__main__":
    app.run(debug=True)  # Flask debug mode for Task 4
 