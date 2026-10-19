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
 