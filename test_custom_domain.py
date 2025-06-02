#!/usr/bin/env python3
"""Test custom domain integration for downlodr.com"""

import requests
import json
import os
import time

# Use custom domain if deployed, localhost for development
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")
CUSTOM_DOMAIN = "https://downlodr.com"

def test_localhost_development():
    """Test with localhost during development"""
    print("🔧 Testing Development Environment (localhost)")
    print("=" * 60)
    
    try:
        # Test 1: API Root
        print("\n📝 Test 1: API Root (localhost)")
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Service: {result['service']}")
            print("✅ Development API working")
        else:
            print("❌ Development API not accessible")
            return False
        
        # Test 2: Shorten URL with localhost
        print("\n📝 Test 2: Shorten URL (localhost)")
        shorten_data = {"url": "https://github.com/frederickluna/talisik-short-url"}
        response = requests.post(f"{BASE_URL}/shorten", json=shorten_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Generated URL: {result['short_url']}")
            
            # Verify URL format
            if result['short_url'].startswith(BASE_URL):
                print("✅ URL generation working correctly")
                return result['short_code']
            else:
                print("❌ URL format incorrect")
                return False
        else:
            print(f"❌ Failed to shorten URL: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing localhost: {e}")
        return False

def test_custom_domain_readiness():
    """Test readiness for custom domain deployment"""
    print("\n🌐 Testing Custom Domain Readiness")
    print("=" * 60)
    
    try:
        # Test environment variables
        print("\n📝 Test 1: Environment Configuration")
        
        # Check if custom domain environment file exists
        if os.path.exists("env.downlodr"):
            print("✅ Custom domain environment file exists")
            
            # Read the file and check configuration
            with open("env.downlodr", "r") as f:
                content = f.read()
                if "BASE_URL=https://downlodr.com" in content:
                    print("✅ BASE_URL configured for downlodr.com")
                if "CORS_ORIGINS=https://downlodr.com" in content:
                    print("✅ CORS configured for custom domain")
                if "ENVIRONMENT=production" in content:
                    print("✅ Production environment configured")
        else:
            print("❌ Custom domain environment file missing")
        
        # Test 2: Check CORS configuration in API
        print("\n📝 Test 2: CORS Configuration")
        
        # Try to make a preflight request
        headers = {
            "Origin": "https://downlodr.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
        
        try:
            response = requests.options(f"{BASE_URL}/shorten", headers=headers)
            cors_headers = response.headers
            
            if "access-control-allow-origin" in cors_headers:
                print("✅ CORS headers present")
            else:
                print("⚠️ CORS headers may need configuration")
                
        except Exception as e:
            print(f"⚠️ CORS test inconclusive: {e}")
        
        # Test 3: URL Generation Logic
        print("\n📝 Test 3: URL Generation Logic")
        
        # Temporarily set environment variable to test custom domain
        original_base_url = os.environ.get("BASE_URL")
        os.environ["BASE_URL"] = "https://downlodr.com"
        
        try:
            # Import and test shortener with custom domain
            from talisik.core.shortener import URLShortener
            from talisik.core.models import ShortenRequest
            
            shortener = URLShortener(base_url="https://downlodr.com")
            request = ShortenRequest(url="https://example.com")
            result = shortener.shorten(request)
            
            if result.success and result.short_url.startswith("https://downlodr.com/"):
                print(f"✅ Custom domain URL generation: {result.short_url}")
                custom_domain_ready = True
            else:
                print("❌ Custom domain URL generation failed")
                custom_domain_ready = False
                
        finally:
            # Restore original environment
            if original_base_url:
                os.environ["BASE_URL"] = original_base_url
            elif "BASE_URL" in os.environ:
                del os.environ["BASE_URL"]
        
        return custom_domain_ready
        
    except Exception as e:
        print(f"❌ Error testing custom domain readiness: {e}")
        return False

def test_production_domain():
    """Test actual production domain (if deployed)"""
    print(f"\n🚀 Testing Production Domain: {CUSTOM_DOMAIN}")
    print("=" * 60)
    
    try:
        # Test 1: Domain accessibility
        print("\n📝 Test 1: Domain Accessibility")
        response = requests.get(CUSTOM_DOMAIN, timeout=10)
        
        if response.status_code == 200:
            print("✅ Domain is accessible")
            result = response.json()
            print(f"Service: {result.get('service', 'Unknown')}")
        else:
            print(f"❌ Domain returned status: {response.status_code}")
            return False
        
        # Test 2: HTTPS and SSL
        print("\n📝 Test 2: HTTPS/SSL")
        if response.url.startswith("https://"):
            print("✅ HTTPS working correctly")
        else:
            print("❌ HTTPS not working")
            return False
        
        # Test 3: API Functionality
        print("\n📝 Test 3: API Functionality")
        shorten_data = {"url": "https://github.com/frederickluna/talisik-short-url"}
        response = requests.post(f"{CUSTOM_DOMAIN}/shorten", json=shorten_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ URL shortening working: {result['short_url']}")
            
            # Test redirect
            short_code = result['short_code']
            redirect_response = requests.get(f"{CUSTOM_DOMAIN}/{short_code}", allow_redirects=False)
            
            if redirect_response.status_code == 301:
                print("✅ Redirects working correctly")
                return True
            else:
                print("❌ Redirects not working")
                return False
        else:
            print(f"❌ API not working: {response.status_code}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot reach production domain: {e}")
        print("ℹ️  This is normal if not yet deployed")
        return False
    except Exception as e:
        print(f"❌ Error testing production domain: {e}")
        return False

def main():
    """Run all custom domain tests"""
    print("🌐 TALISIK CUSTOM DOMAIN TESTING")
    print("=" * 60)
    print(f"Testing environment: {BASE_URL}")
    print(f"Target custom domain: {CUSTOM_DOMAIN}")
    print("=" * 60)
    
    # Test localhost development
    localhost_result = test_localhost_development()
    
    # Test custom domain readiness
    readiness_result = test_custom_domain_readiness()
    
    # Test production domain (if deployed)
    production_result = test_production_domain()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    if localhost_result:
        print("✅ Development Environment: WORKING")
    else:
        print("❌ Development Environment: ISSUES")
    
    if readiness_result:
        print("✅ Custom Domain Readiness: READY")
    else:
        print("❌ Custom Domain Readiness: NOT READY")
    
    if production_result:
        print("✅ Production Domain: WORKING")
    elif production_result is False:
        print("⚠️  Production Domain: NOT DEPLOYED YET")
    else:
        print("❌ Production Domain: ISSUES")
    
    # Overall status
    if localhost_result and readiness_result:
        print("\n🎉 READY FOR CUSTOM DOMAIN DEPLOYMENT!")
        print("\nNext steps:")
        print("1. Deploy to your hosting platform (Railway/Vercel/Heroku)")
        print("2. Add downlodr.com as custom domain")
        print("3. Configure DNS records")
        print("4. Test production endpoints")
        return True
    else:
        print("\n⚠️  ISSUES NEED TO BE RESOLVED FIRST")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 