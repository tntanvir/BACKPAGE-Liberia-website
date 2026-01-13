import os
import django
import json
import sys

# Setup Django environment
sys.path.append('/home/tntanvir/tntanvir/BackPage')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BackPage.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()
client = APIClient()

def run_test():
    email = "test@example.com"
    password = "StrongPassword123!"
    name = "Test User"
    
    print("1. Testing Registration...")
    # Clean up
    User.objects.filter(email=email).delete()
    
    response = client.post('/api/auth/register/', {
        'name': name,
        'email': email,
        'password': password,
        'confirm_password': password
    })
    
    if response.status_code != 201:
        print(f"Registration failed: {response.data}")
        return False
    print("Registration successful.")
    
    # Get OTP from DB
    user = User.objects.get(email=email)
    otp = user.otp
    print(f"OTP retrieved from DB: {otp}")
    
    print("2. Testing OTP Verification...")
    response = client.post('/api/auth/verify-otp/', {
        'email': email,
        'otp': otp
    })
    
    if response.status_code != 200:
        print(f"Verification failed: {response.data}")
        return False
    print("Verification successful.")
    
    print("3. Testing Login...")
    response = client.post('/api/auth/login/', {
        'email': email,
        'password': password
    })
    
    if response.status_code != 200:
        print(f"Login failed: {response.data}")
        return False
    
    access_token = response.data['access']
    print("Login successful.")
    
    print("4. Testing Profile Fetch...")
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    response = client.get('/api/auth/profile/')
    
    if response.status_code != 200:
        print(f"Profile fetch failed: {response.data}")
        return False
    
    if response.data['email'] != email:
        print("Profile email mismatch")
        return False
    print("Profile fetch successful.")
    
    print("5. Testing Change Password...")
    new_password = "newpassword456"
    response = client.post('/api/auth/change-password/', {
        'old_password': password,
        'new_password': new_password
    })
    
    if response.status_code != 200:
        print(f"Change password failed: {response.data}")
        return False
    print("Change password successful.")
    
    print("6. Testing Login with New Password...")
    client.credentials() # clear auth
    response = client.post('/api/auth/login/', {
        'email': email,
        'password': new_password
    })
    
    if response.status_code != 200:
        print(f"Login with new password failed: {response.data}")
        return False
    print("Login with new password successful.")

    return True

if __name__ == "__main__":
    if run_test():
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed.")
