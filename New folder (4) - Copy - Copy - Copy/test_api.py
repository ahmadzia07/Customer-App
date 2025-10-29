#!/usr/bin/env python3
"""
Simple test script for the Employee Management API
Run this script to test all API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_create_employee():
    """Test creating a new employee"""
    print("\nTesting employee creation...")
    unique_email = f"john.doe+{int(time.time())}@company.com"
    employee_data = {
        "name": "John Doe",
        "email": unique_email,
        "department": "Engineering",
        "salary": 75000.00
    }
    
    try:
        response = requests.post(f"{BASE_URL}/employees", json=employee_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            return response.json()['data']['id']
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_get_employees():
    """Test getting all employees"""
    print("\nTesting get all employees...")
    try:
        response = requests.get(f"{BASE_URL}/employees")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_employee(employee_id):
    """Test getting a single employee"""
    print(f"\nTesting get employee {employee_id}...")
    try:
        response = requests.get(f"{BASE_URL}/employees/{employee_id}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_update_employee(employee_id):
    """Test updating an employee"""
    print(f"\nTesting update employee {employee_id}...")
    update_data = {
        "salary": 80000.00,
        "department": "Senior Engineering"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/employees/{employee_id}", json=update_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_validation():
    """Test input validation"""
    print("\nTesting input validation...")
    
    # Test invalid salary
    invalid_data = {
        "name": "Test User",
        "email": "test@company.com",
        "department": "Test",
        "salary": -1000  # Invalid salary
    }
    
    try:
        response = requests.post(f"{BASE_URL}/employees", json=invalid_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 400
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_delete_employee(employee_id):
    """Test deleting an employee"""
    print(f"\nTesting delete employee {employee_id}...")
    try:
        response = requests.delete(f"{BASE_URL}/employees/{employee_id}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_duplicate_email():
    """Test duplicate email validation"""
    print("\nTesting duplicate email validation...")
    
    employee_data = {
        "name": "Jane Smith",
        "email": "john.doe@company.com",  # Same email as first employee
        "department": "Marketing",
        "salary": 65000.00
    }
    
    try:
        response = requests.post(f"{BASE_URL}/employees", json=employee_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 409  # Conflict
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Employee Management API Test Suite")
    print("=" * 50)
    
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    # Test health check
    if not test_health_check():
        print("Health check failed. Make sure the server is running.")
        return
    
    # Test employee creation
    employee_id = test_create_employee()
    if not employee_id:
        print("Employee creation failed. Stopping tests.")
        return
    
    # Test getting all employees
    test_get_employees()
    
    # Test getting single employee
    test_get_employee(employee_id)
    
    # Test updating employee
    test_update_employee(employee_id)
    
    # Test input validation
    test_validation()
    
    # Create another employee for duplicate email test
    test_create_employee()
    
    # Test duplicate email validation
    test_duplicate_email()
    
    # Test deleting employee
    test_delete_employee(employee_id)
    
    print("\n" + "=" * 50)
    print("Test suite completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()
