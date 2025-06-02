#!/usr/bin/env python3
"""
Production Testing Suite for Talisik Short URL Service

This script tests the deployed production API to ensure all functionality
works correctly in the live environment.

Usage:
    python test_production.py https://your-production-url.com
"""

import sys
import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional
from datetime import datetime
import time


class ProductionTester:
    """Comprehensive production testing suite"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results = []
        self.created_urls = []  # Track created URLs for cleanup
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        # Color coding for console output
        color = "\033[92m" if status == "PASS" else "\033[91m" if status == "FAIL" else "\033[93m"
        reset = "\033[0m"
        
        print(f"{color}[{status}]{reset} {test_name}")
        if details:
            print(f"      {details}")
    
    async def test_health_check(self):
        """Test basic API health and availability"""
        try:
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("Health Check", "PASS", f"API accessible, response: {data}")
                    return True
                else:
                    self.log_test("Health Check", "FAIL", f"Status: {response.status}")
                    return False
        except Exception as e:
            self.log_test("Health Check", "FAIL", f"Connection error: {str(e)}")
            return False
    
    async def test_shorten_url(self, test_url: str = "https://github.com/frederickluna/talisik-short-url", custom_code: str = None):
        """Test URL shortening functionality"""
        payload = {"url": test_url}
        if custom_code:
            payload["custom_code"] = custom_code
            
        try:
            async with self.session.post(
                f"{self.base_url}/shorten",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    short_code = data.get("short_code")
                    short_url = data.get("short_url")
                    
                    if short_code and short_url:
                        self.created_urls.append(short_code)
                        test_name = f"Shorten URL {'(Custom)' if custom_code else '(Auto)'}"
                        self.log_test(test_name, "PASS", f"Created: {short_url}")
                        return short_code
                    else:
                        self.log_test("Shorten URL", "FAIL", "Missing short_code or short_url in response")
                        return None
                else:
                    error_text = await response.text()
                    self.log_test("Shorten URL", "FAIL", f"Status: {response.status}, Error: {error_text}")
                    return None
                    
        except Exception as e:
            self.log_test("Shorten URL", "FAIL", f"Request error: {str(e)}")
            return None
    
    async def test_redirect(self, short_code: str, expected_url: str):
        """Test URL redirection"""
        try:
            # Use allow_redirects=False to check the redirect response
            async with self.session.get(
                f"{self.base_url}/{short_code}",
                allow_redirects=False
            ) as response:
                
                if response.status in [301, 302, 307, 308]:
                    location = response.headers.get("Location")
                    if location == expected_url:
                        self.log_test("URL Redirect", "PASS", f"Redirects to: {location}")
                        return True
                    else:
                        self.log_test("URL Redirect", "FAIL", f"Wrong redirect: {location} != {expected_url}")
                        return False
                else:
                    self.log_test("URL Redirect", "FAIL", f"Status: {response.status}")
                    return False
                    
        except Exception as e:
            self.log_test("URL Redirect", "FAIL", f"Request error: {str(e)}")
            return False
    
    async def test_get_info(self, short_code: str):
        """Test URL info retrieval"""
        try:
            async with self.session.get(f"{self.base_url}/info/{short_code}") as response:
                
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["short_code", "original_url", "created_at", "click_count"]
                    
                    if all(field in data for field in required_fields):
                        self.log_test("Get URL Info", "PASS", f"Clicks: {data['click_count']}")
                        return data
                    else:
                        missing = [f for f in required_fields if f not in data]
                        self.log_test("Get URL Info", "FAIL", f"Missing fields: {missing}")
                        return None
                else:
                    error_text = await response.text()
                    self.log_test("Get URL Info", "FAIL", f"Status: {response.status}, Error: {error_text}")
                    return None
                    
        except Exception as e:
            self.log_test("Get URL Info", "FAIL", f"Request error: {str(e)}")
            return None
    
    async def test_stats(self):
        """Test API statistics"""
        try:
            async with self.session.get(f"{self.base_url}/api/stats") as response:
                
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["total_urls", "total_clicks"]
                    
                    if all(field in data for field in required_fields):
                        self.log_test("API Stats", "PASS", f"URLs: {data['total_urls']}, Clicks: {data['total_clicks']}")
                        return data
                    else:
                        missing = [f for f in required_fields if f not in data]
                        self.log_test("API Stats", "FAIL", f"Missing fields: {missing}")
                        return None
                else:
                    error_text = await response.text()
                    self.log_test("API Stats", "FAIL", f"Status: {response.status}, Error: {error_text}")
                    return None
                    
        except Exception as e:
            self.log_test("API Stats", "FAIL", f"Request error: {str(e)}")
            return None
    
    async def test_click_tracking(self, short_code: str):
        """Test click tracking by making multiple requests"""
        try:
            # Get initial click count
            info_before = await self.test_get_info(short_code)
            if not info_before:
                return False
                
            initial_clicks = info_before.get("click_count", 0)
            
            # Make a redirect request (should increment clicks)
            async with self.session.get(
                f"{self.base_url}/{short_code}",
                allow_redirects=True
            ) as response:
                pass  # We just want to trigger the click
            
            # Wait a moment for the click to be recorded
            await asyncio.sleep(1)
            
            # Get updated click count
            info_after = await self.test_get_info(short_code)
            if not info_after:
                return False
                
            final_clicks = info_after.get("click_count", 0)
            
            if final_clicks > initial_clicks:
                self.log_test("Click Tracking", "PASS", f"Clicks: {initial_clicks} → {final_clicks}")
                return True
            else:
                self.log_test("Click Tracking", "FAIL", f"Clicks not incremented: {initial_clicks} → {final_clicks}")
                return False
                
        except Exception as e:
            self.log_test("Click Tracking", "FAIL", f"Request error: {str(e)}")
            return False
    
    async def test_error_handling(self):
        """Test API error handling"""
        # Test invalid URL
        try:
            async with self.session.post(
                f"{self.base_url}/shorten",
                json={"url": "not-a-valid-url"},
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 422:  # Validation error
                    self.log_test("Error Handling (Invalid URL)", "PASS", "Properly rejects invalid URLs")
                else:
                    self.log_test("Error Handling (Invalid URL)", "FAIL", f"Status: {response.status}")
        except Exception as e:
            self.log_test("Error Handling (Invalid URL)", "FAIL", f"Request error: {str(e)}")
        
        # Test non-existent short code
        try:
            async with self.session.get(f"{self.base_url}/nonexistent123") as response:
                if response.status == 404:
                    self.log_test("Error Handling (Not Found)", "PASS", "Properly returns 404 for missing URLs")
                else:
                    self.log_test("Error Handling (Not Found)", "FAIL", f"Status: {response.status}")
        except Exception as e:
            self.log_test("Error Handling (Not Found)", "FAIL", f"Request error: {str(e)}")
    
    async def run_comprehensive_test(self):
        """Run all production tests"""
        print(f"\n🚀 Starting Production Test Suite for: {self.base_url}")
        print("=" * 60)
        
        # Test 1: Health Check
        if not await self.test_health_check():
            print("\n❌ API is not accessible. Stopping tests.")
            return
        
        print()
        
        # Test 2: URL Shortening (Auto-generated code)
        test_url = "https://github.com/frederickluna/talisik-short-url"
        short_code = await self.test_shorten_url(test_url)
        
        if short_code:
            # Test 3: URL Redirection
            await self.test_redirect(short_code, test_url)
            
            # Test 4: URL Info
            await self.test_get_info(short_code)
            
            # Test 5: Click Tracking
            await self.test_click_tracking(short_code)
        
        print()
        
        # Test 6: Custom Code Shortening
        custom_code = f"test-{int(time.time())}"
        custom_short_code = await self.test_shorten_url(
            "https://www.example.com/test-page", 
            custom_code
        )
        
        print()
        
        # Test 7: API Statistics
        await self.test_stats()
        
        print()
        
        # Test 8: Error Handling
        await self.test_error_handling()
        
        print()
        
        # Print Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        
        print("=" * 60)
        print(f"📊 TEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"   • {result['test']}: {result['details']}")
        
        if passed_tests == total_tests:
            print(f"\n🎉 All tests passed! Your production API is working perfectly.")
        else:
            print(f"\n⚠️  Some tests failed. Please review the issues above.")


async def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python test_production.py <production-url>")
        print("Example: python test_production.py https://your-app.leapcell.io")
        sys.exit(1)
    
    production_url = sys.argv[1]
    
    async with ProductionTester(production_url) as tester:
        await tester.run_comprehensive_test()


if __name__ == "__main__":
    # Check if asyncio is available
    try:
        asyncio.run(main())
    except ImportError:
        print("❌ This script requires Python 3.7+ with asyncio support")
        sys.exit(1) 