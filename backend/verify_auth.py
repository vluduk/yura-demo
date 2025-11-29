import requests
import json

BASE_URL = 'http://localhost:8000/api/v1/auth'

def test_signup():
    print("Testing Sign Up...")
    payload = {
        "phone": "0991234567",
        "name": "John",
        "surname": "Doe",
        "role": "RETAIL",
        "password": "HardPassword123"
    }
    try:
        response = requests.post(f"{BASE_URL}/sign-up", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 201:
            print("Sign Up SUCCESS")
            return True
        else:
            print("Sign Up FAILED")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_login():
    print("\nTesting Login...")
    payload = {
        "phone": "0991234567",
        "password": "HardPassword123"
    }
    try:
        response = requests.post(f"{BASE_URL}/login", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
            print("Login SUCCESS")
            return True
        else:
            print("Login FAILED")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_admin():
    print("\nTesting Admin Panel...")
    try:
        response = requests.get(f"http://localhost:8000/admin/login/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Admin Panel Reachable")
            return True
        else:
            print("Admin Panel Unreachable")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Ensure server is running before running this script
    if test_signup():
        test_login()
    test_admin()
