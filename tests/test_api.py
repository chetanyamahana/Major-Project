import pytest
from fastapi.testclient import TestClient
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.api.app import app
from app.models.grievance import GrievanceCreate

# Create test client
client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_grievances():
    """Test getting list of grievances."""
    response = client.get("/api/v1/grievances/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)
    assert isinstance(data["total"], int)

def test_get_statistics():
    """Test getting grievance statistics."""
    response = client.get("/api/v1/stats/")
    assert response.status_code == 200
    data = response.json()
    assert "total_grievances" in data
    assert "resolved_grievances" in data
    assert "pending_grievances" in data
    assert "by_category" in data
    assert "by_state" in data
    assert "by_source" in data

# Note: The following test is commented out because it would actually create a grievance in the database
# Uncomment and modify for actual testing with a mock database

"""
def test_create_grievance():
    # Test creating a new grievance.
    grievance_data = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "1234567890",
        "country": "India",
        "state": "Delhi",
        "city": "New Delhi",
        "category": "Roads & Infrastructure",
        "heading": "Test Grievance",
        "description": "This is a test grievance for API testing.",
        "attachment_url": None
    }
    
    response = client.post("/api/v1/grievances/", json=grievance_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == grievance_data["name"]
    assert data["email"] == grievance_data["email"]
    assert data["ticket_id"] is not None
"""
