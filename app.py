
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