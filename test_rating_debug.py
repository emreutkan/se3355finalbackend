#!/usr/bin/env python3
"""
Rating Debug Test Script
========================

This script helps test the rating functionality and debug issues.
Run this after deploying the updated code to see what's happening.
"""

import requests
import json
import sys

# Configuration
BASE_URL = "https://be984984-aphkd5f2e7ake9ey.westeurope-01.azurewebsites.net"
API_BASE = f"{BASE_URL}/api"

def test_debug_endpoints():
    """Test the debug endpoints to check logging and configuration"""
    
    print("🔧 Testing Debug Endpoints...")
    print("=" * 50)
    
    # Test logging configuration
    try:
        response = requests.get(f"{API_BASE}/dev/debug/logs")
        print(f"📊 Logging Debug: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Environment: {data.get('logging_config', {}).get('environment')}")
            print(f"   Log Level: {data.get('logging_config', {}).get('config_log_level')}")
            print(f"   Handlers: {len(data.get('logging_config', {}).get('handlers', []))}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Connection Error: {e}")
    
    print()
    
    # Test rating validation
    try:
        test_cases = [
            {"rating": 5},
            {"rating": "5"},
            {"rating": 0},
            {"rating": 11},
            {"rating": "invalid"}
        ]
        
        for test_case in test_cases:
            response = requests.post(
                f"{API_BASE}/dev/debug/validate-rating",
                json=test_case
            )
            print(f"🧪 Rating Validation Test: {test_case['rating']} -> ", end="")
            if response.status_code == 200:
                data = response.json()
                print(f"Valid: {data.get('is_valid')}")
            else:
                print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"   Validation Test Error: {e}")

def test_authentication():
    """Test authentication to get a token"""
    
    print("\n🔐 Testing Authentication...")
    print("=" * 50)
    
    # You'll need to update these with real test credentials
    test_user = {
        "email": "test@example.com",
        "password": "testpassword123!"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=test_user)
        print(f"Login Test: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"✅ Got token: {token[:50] if token else 'None'}...")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication Error: {e}")
        return None

def test_rating_functionality(token, movie_id=None):
    """Test rating functionality with a valid token"""
    
    if not token:
        print("❌ No token available for rating test")
        return
    
    print(f"\n🎬 Testing Rating Functionality...")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get first movie if no movie_id provided
    if not movie_id:
        try:
            response = requests.get(f"{API_BASE}/movies?size=1")
            if response.status_code == 200:
                movies = response.json().get('movies', [])
                if movies:
                    movie_id = movies[0]['id']
                    print(f"Using movie: {movies[0]['title']} ({movie_id})")
                else:
                    print("❌ No movies found")
                    return
            else:
                print(f"❌ Failed to get movies: {response.status_code}")
                return
        except Exception as e:
            print(f"❌ Error getting movies: {e}")
            return
    
    # Test debug endpoint for this movie
    try:
        response = requests.get(
            f"{API_BASE}/dev/debug/rating/{movie_id}",
            headers=headers
        )
        print(f"Debug Rating Check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Can Rate: {data.get('can_rate')}")
            issues = data.get('issues', [])
            if issues:
                print(f"   Issues: {', '.join(issues)}")
            else:
                print("   ✅ No issues found")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Debug Error: {e}")
    
    # Try to submit a rating
    rating_data = {
        "rating": 8,
        "comment": "Test rating from debug script"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/movies/{movie_id}/ratings",
            json=rating_data,
            headers=headers
        )
        print(f"Submit Rating: {response.status_code}")
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"   ✅ Success: {data.get('msg')}")
            print(f"   Rating ID: {data.get('rating', {}).get('id')}")
        else:
            print(f"   ❌ Failed: {response.text}")
    except Exception as e:
        print(f"   Rating Submit Error: {e}")

def main():
    """Main test function"""
    
    print("🚀 Rating Debug Test Script")
    print("=" * 50)
    print(f"Testing API at: {API_BASE}")
    print()
    
    # Test debug endpoints (no auth required)
    test_debug_endpoints()
    
    # Test authentication
    token = test_authentication()
    
    # Test rating functionality
    test_rating_functionality(token)
    
    print("\n" + "=" * 50)
    print("✅ Test complete!")
    print("\nNEXT STEPS:")
    print("1. Check your application logs for detailed debug information")
    print("2. Look for messages with 🎬 emoji for movie rating operations")
    print("3. If rating fails, check the 'details' field in error responses")
    print("4. Use /api/dev/debug/rating/<movie_id> endpoint to diagnose specific issues")

if __name__ == "__main__":
    main() 