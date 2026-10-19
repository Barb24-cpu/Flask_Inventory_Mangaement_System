# Flask_Inventory_Mangaement_System

# A small retail inventory system: a Flask REST API with CRUD operations, an OpenFoodFacts integration for product details, a CLI front end, and a pytest suite. Inventory is stored in an in-memory list (mock database), so data resets on restart.

Installation and setup
bash
git clone <https://github.com/Barb24-cpu/Flask_Inventory_Mangaement_System.git>
cd <Flask_Inventory_Management_system>
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
Running

Terminal 1 (API, Flask debug mode, http://127.0.0.1:5000):

bash
python app.py

Terminal 2 (CLI):

bash
python cli.py
Running tests
bash
pytest -v

Tests use unittest.mock so no real network calls are made.

API endpoints
Method	Endpoint	Description
GET	/inventory	Fetch all items
GET	/inventory/<id>	Fetch a single item (404 if missing)
POST	/inventory	Add an item. JSON: product_name (required), brands, barcode, ingredients_text, price, stock
PATCH	/inventory/<id>	Update any of the item fields, e.g. {"price": 5.0}
DELETE	/inventory/<id>	Remove an item
GET	/external/barcode/<barcode>	Look up a product on OpenFoodFacts by barcode
GET	/external/search?name=<text>	Search OpenFoodFacts by product name
POST	/inventory/import	Fetch by barcode from OpenFoodFacts and add to inventory. JSON: barcode, price, stock

Errors return JSON like {"error": "Item not found"} with status 400, 404 or 502 (external API down).

Example (curl)
bash
curl http://127.0.0.1:5000/inventory
curl -X POST http://127.0.0.1:5000/inventory -H "Content-Type: application/json" \
     -d '{"product_name": "Green Tea", "price": 5.5, "stock": 12}'
curl -X PATCH http://127.0.0.1:5000/inventory/1 -H "Content-Type: application/json" -d '{"stock": 30}'
curl -X DELETE http://127.0.0.1:5000/inventory/1
CLI usage

Run python cli.py and pick an option from the menu:

1. List all items
2. View item details
3. Add new item
4. Update item price/stock
5. Delete item
6. Find item on OpenFoodFacts
7. Quit

Example: option 6 → b (barcode) → 3017620422003 → y to add it to inventory, then enter a price and stock.

Project structure
app.py            Flask API, helper functions, mock database
cli.py            Command-line interface
tests/            pytest suites (test_app.py, test_cli.py)
requirements.txt  Dependencies