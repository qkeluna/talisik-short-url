#!/usr/bin/env python3
"""Test script to verify BASE_URL configuration is working correctly"""

import os
import sys
from dotenv import load_dotenv

def test_base_url_configuration():
    """Test that BASE_URL is configured correctly for go.downlodr.com"""
    print("🔧 Testing BASE_URL Configuration Fix")
    print("=" * 60)
    
    # Test 1: Load from env.downlodr file
    print("\n📝 Test 1: Loading from env.downlodr")
    
    # Load the downlodr environment file
    load_dotenv("env.downlodr")
    base_url = os.getenv("BASE_URL")
    
    print(f"BASE_URL from env.downlodr: {base_url}")
    
    if base_url == "https://go.downlodr.com":
        print("✅ BASE_URL correctly set to https://go.downlodr.com")
    else:
        print(f"❌ BASE_URL is wrong. Expected: https://go.downlodr.com, Got: {base_url}")
        return False
    
    # Test 2: Test URLShortener with the configuration
    print("\n📝 Test 2: Testing URLShortener with fixed configuration")
    
    try:
        from talisik.core.shortener import URLShortener
        from talisik.core.models import ShortenRequest
        
        # Create shortener with explicit base URL
        shortener = URLShortener(base_url="https://go.downlodr.com")
        
        # Test URL shortening
        request = ShortenRequest(url="https://github.com/frederickluna/talisik-short-url")
        result = shortener.shorten(request)
        
        if result.success:
            print(f"Generated short URL: {result.short_url}")
            
            if result.short_url.startswith("https://go.downlodr.com/"):
                print("✅ Short URL generation working correctly")
                print(f"Short code: {result.short_code}")
                return True
            else:
                print(f"❌ Short URL has wrong base. Expected prefix: https://go.downlodr.com/")
                return False
        else:
            print(f"❌ URL shortening failed: {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing URLShortener: {e}")
        return False

def test_environment_usage_guide():
    """Show how to use the fixed configuration in other projects"""
    print("\n🔗 How to Use in Other Projects")
    print("=" * 60)
    
    print("""
To use the fixed configuration in other projects:

1. Set environment variable:
   export BASE_URL=https://go.downlodr.com

2. Or create .env file with:
   BASE_URL=https://go.downlodr.com
   STORAGE_BACKEND=supabase
   SUPABASE_DB_URL=your_connection_string

3. In your Python code:
   from talisik.core.shortener import URLShortener
   shortener = URLShortener()  # Will use env BASE_URL
   
   # Or explicitly set:
   shortener = URLShortener(base_url="https://go.downlodr.com")

4. Generated URLs will be:
   https://go.downlodr.com/abc123
   """)

if __name__ == "__main__":
    success = test_base_url_configuration()
    test_environment_usage_guide()
    
    if success:
        print("\n🎉 BASE_URL configuration fix successful!")
        print("Your library now generates URLs with https://go.downlodr.com")
    else:
        print("\n❌ Configuration fix needs attention")
        sys.exit(1) 