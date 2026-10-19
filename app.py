
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