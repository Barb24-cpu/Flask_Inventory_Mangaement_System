"""Command-line interface for the Flask inventory API.
 
Start the API first (python app.py), then run this in a second terminal (python cli.py).
"""
import requests
 
API_URL = "http://127.0.0.1:5000"
TIMEOUT = 15
 
 # Helpers

def api_request(method, path, **kwargs):
    """Send a request to the Flask API.
 
    Returns (status_code, json_body), or (None, None) if the API cannot be reached.
    """
    try:
        response = requests.request(method, f"{API_URL}{path}", timeout=TIMEOUT, **kwargs)
        return response.status_code, response.json()
    except requests.RequestException:
        print("Error: could not reach the API. Is `python app.py` running?")
    except ValueError:
        print("Error: the API returned an unexpected response.")
    return None, None
 
 
def print_item(item):
    print(
        f"[{item['id']}] {item['product_name']} | brand: {item.get('brands') or 'n/a'} | "
        f"barcode: {item.get('barcode') or 'n/a'} | price: ${float(item.get('price', 0)):.2f} | "
        f"stock: {item.get('stock', 0)}"
    )
 
 
def ask_int(prompt, minimum=0):
    """Keep asking until the user enters an integer >= minimum."""
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
            if value >= minimum:
                return value
        except ValueError:
            pass
        print(f"Please enter a whole number >= {minimum}.")
 
 
def ask_float(prompt, minimum=0.0):
    """Keep asking until the user enters a number >= minimum."""
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
            if value >= minimum:
                return value
        except ValueError:
            pass
        print(f"Please enter a number >= {minimum}.")
 
 
def show_error(body):
    print(f"Error: {body.get('error', 'Something went wrong')}")
 

 # Menu actions

def list_items():
    status, body = api_request("GET", "/inventory")
    if status != 200:
        return
    if not body:
        print("Inventory is empty.")
    for item in body:
        print_item(item)
 
 
def view_item():
    item_id = ask_int("Item ID: ", minimum=1)
    status, body = api_request("GET", f"/inventory/{item_id}")
    if status == 200:
        for key, value in body.items():
            print(f"  {key}: {value}")
    elif status:
        show_error(body)
 
 
def add_item():
    name = input("Product name: ").strip()
    if not name:
        print("Error: product name cannot be empty.")
        return
    payload = {
        "product_name": name,
        "brands": input("Brand (optional): ").strip(),
        "barcode": input("Barcode (optional): ").strip(),
        "price": ask_float("Price: "),
        "stock": ask_int("Stock: "),
    }
    status, body = api_request("POST", "/inventory", json=payload)
    if status == 201:
        print("Item added:")
        print_item(body)
    elif status:
        show_error(body)
 
 
def update_item():
    item_id = ask_int("Item ID to update: ", minimum=1)
    choice = input("Update (p)rice or (s)tock? ").strip().lower()
    if choice == "p":
        payload = {"price": ask_float("New price: ")}
    elif choice == "s":
        payload = {"stock": ask_int("New stock level: ")}
    else:
        print("Error: choose 'p' or 's'.")
        return
    status, body = api_request("PATCH", f"/inventory/{item_id}", json=payload)
    if status == 200:
        print("Item updated:")
        print_item(body)
    elif status:
        show_error(body)
 