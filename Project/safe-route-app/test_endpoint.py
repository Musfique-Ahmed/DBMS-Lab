#!/usr/bin/env python3
"""
Test script to verify the FastAPI crime endpoint works correctly
"""

import requests
import json

# Test data
test_crime_data = {
    "location": {
        "district_id": 1,
        "area_name": "Dhanmondi",
        "city": "Dhaka",
        "latitude": 23.7465,
        "longitude": 90.3760
    },
    "crime": {
        "crime_type": "theft",
        "description": "Test crime for debugging",
        "date_time": "2025-01-15T14:30:00",
        "status": "reported"
    },
    "victim": {
        "full_name": "Test Victim",
        "dob": "1990-01-01",
        "gender": "M",
        "address": "Test Address",
        "phone_number": "+880123456789",
        "email": "test@example.com",
        "injury_details": "No injuries"
    }
}

def test_endpoint():
    """Test the crime endpoint"""
    url = "http://localhost:8000/api/crimes"
    
    try:
        print("Testing database connection...")
        db_response = requests.get("http://localhost:8000/test-db")
        print(f"Database test response: {db_response.status_code}")
        print(f"Database test result: {db_response.json()}")
        
        print("\nTesting crime endpoint...")
        response = requests.post(
            url,
            json=test_crime_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure FastAPI is running on http://localhost:8000")
        print("Run: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_endpoint()
