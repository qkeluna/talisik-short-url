#!/usr/bin/env python3
"""Test script for the FastAPI URL shortener"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api():
    print("🔗 Testing Talisik URL Shortener API")
    print("=" * 50)
    
    # Wait a moment for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(2)
    
    try:
        # Test 1: API root
        print("\n📝 Test 1: API Root")
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test 2: Shorten a URL
        print("\n📝 Test 2: Shorten URL")
        shorten_data = {
            "url": "https://google.com"
        }
        response = requests.post(f"{BASE_URL}/shorten", json=shorten_data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        short_code = result.get("short_code")
        if not short_code:
            print("❌ No short code returned!")
            return
        
        # Test 3: Get URL info
        print(f"\n📝 Test 3: Get URL Info for '{short_code}'")
        response = requests.get(f"{BASE_URL}/info/{short_code}")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test 4: Test redirect (without following)
        print(f"\n📝 Test 4: Test Redirect for '{short_code}' (no follow)")
        response = requests.get(f"{BASE_URL}/{short_code}", allow_redirects=False)
        print(f"Status: {response.status_code}")
        print(f"Location header: {response.headers.get('location', 'Not found')}")
        
        # Test 5: Custom short code
        print("\n📝 Test 5: Custom Short Code")
        custom_data = {
            "url": "https://github.com",
            "custom_code": "github"
        }
        response = requests.post(f"{BASE_URL}/shorten", json=custom_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test 6: URL with expiration
        print("\n📝 Test 6: URL with Expiration")
        expire_data = {
            "url": "https://example.com",
            "expires_hours": 24
        }
        response = requests.post(f"{BASE_URL}/shorten", json=expire_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test 7: Get stats (fixed endpoint)
        print("\n📝 Test 7: Get Statistics")
        response = requests.get(f"{BASE_URL}/api/stats")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test 8: Error handling - invalid URL
        print("\n📝 Test 8: Error Handling - Invalid URL")
        invalid_data = {
            "url": "not-a-valid-url"
        }
        response = requests.post(f"{BASE_URL}/shorten", json=invalid_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test 9: Error handling - nonexistent code
        print("\n📝 Test 9: Error Handling - Nonexistent Code")
        response = requests.get(f"{BASE_URL}/nonexistent", allow_redirects=False)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test 10: Test actual redirect by following it
        print(f"\n📝 Test 10: Follow Redirect for '{short_code}'")
        response = requests.get(f"{BASE_URL}/{short_code}", allow_redirects=True)
        print(f"Status: {response.status_code}")
        print(f"Final URL: {response.url}")
        
        print("\n🎉 API tests completed!")
        print("\n📋 To explore the API interactively:")
        print(f"   • API docs: {BASE_URL}/docs")
        print(f"   • Root: {BASE_URL}/")
        print(f"   • Stats: {BASE_URL}/api/stats")
        print(f"   • Try it: curl -X POST '{BASE_URL}/shorten' -H 'Content-Type: application/json' -d '{{\"url\":\"https://example.com\"}}'")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server.")
        print("   Make sure the server is running: make api")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api() 