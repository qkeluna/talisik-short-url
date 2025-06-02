#!/usr/bin/env python3
"""Demo script to test the URL shortener functionality"""

from talisik import URLShortener, ShortenRequest

def main():
    print("🔗 Talisik URL Shortener Demo")
    print("=" * 40)
    
    # Create shortener instance
    shortener = URLShortener()
    
    # Test 1: Basic URL shortening
    print("\n📝 Test 1: Basic URL Shortening")
    result1 = shortener.shorten(ShortenRequest('https://google.com'))
    print(f"Original URL: https://google.com")
    print(f"Short URL:    {result1.short_url}")
    print(f"Short Code:   {result1.short_code}")
    
    # Test 2: Expanding the short code
    print("\n🔍 Test 2: Expanding Short Code")
    expanded = shortener.expand(result1.short_code)
    print(f"Short Code:   {result1.short_code}")
    print(f"Expands to:   {expanded}")
    print(f"✅ Match:     {expanded == 'https://google.com'}")
    
    # Test 3: Custom short code
    print("\n⚙️ Test 3: Custom Short Code")
    result2 = shortener.shorten(ShortenRequest('https://github.com', custom_code='github'))
    print(f"Original URL: https://github.com")
    print(f"Custom Code:  {result2.short_code}")
    print(f"Short URL:    {result2.short_url}")
    
    # Test 4: Multiple URLs
    print("\n📚 Test 4: Multiple URLs")
    urls = ['https://stackoverflow.com', 'https://python.org', 'https://fastapi.tiangolo.com']
    shortened_urls = []
    
    for url in urls:
        result = shortener.shorten(ShortenRequest(url))
        shortened_urls.append((url, result.short_code, result.short_url))
        print(f"{url} → {result.short_code}")
    
    # Test 5: Expanding all
    print("\n🔄 Test 5: Expanding All Short Codes")
    for original, code, short_url in shortened_urls:
        expanded = shortener.expand(code)
        status = "✅" if expanded == original else "❌"
        print(f"{code} → {expanded} {status}")
    
    # Test 6: URL with expiration
    print("\n⏰ Test 6: URL with Expiration")
    result3 = shortener.shorten(ShortenRequest('https://example.com', expires_hours=24))
    print(f"Original URL: https://example.com")
    print(f"Short Code:   {result3.short_code}")
    print(f"Expires at:   {result3.expires_at}")
    print(f"Expandable:   {shortener.expand(result3.short_code) is not None}")
    
    print("\n🎉 All tests completed successfully!")
    print(f"📊 Total URLs shortened: {len(shortener._urls)}")

if __name__ == "__main__":
    main() 