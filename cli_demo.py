#!/usr/bin/env python3
"""Interactive CLI demo for testing the URL shortener"""

from talisik import URLShortener, ShortenRequest

def main():
    print("🔗 Talisik URL Shortener - Interactive Demo")
    print("=" * 50)
    print("Commands:")
    print("  shorten <url> [custom_code] [expires_hours] - Shorten a URL")
    print("  expand <code>                               - Expand a short code")
    print("  list                                        - List all URLs")
    print("  quit                                        - Exit")
    print("=" * 50)
    
    shortener = URLShortener()
    
    while True:
        try:
            command = input("\n> ").strip()
            
            if command == "quit":
                print("👋 Goodbye!")
                break
            
            elif command == "list":
                if not shortener._urls:
                    print("📭 No URLs stored yet")
                else:
                    print(f"📊 {len(shortener._urls)} URLs stored:")
                    for code, url_obj in shortener._urls.items():
                        click_info = f"({url_obj.click_count} clicks)" if url_obj.click_count > 0 else ""
                        exp_info = f"expires {url_obj.expires_at}" if url_obj.expires_at else "no expiration"
                        print(f"  {code} → {url_obj.original_url} {click_info} ({exp_info})")
            
            elif command.startswith("shorten "):
                parts = command.split()
                if len(parts) < 2:
                    print("❌ Usage: shorten <url> [custom_code] [expires_hours]")
                    continue
                
                url = parts[1]
                custom_code = parts[2] if len(parts) > 2 else None
                expires_hours = None
                
                if len(parts) > 3:
                    try:
                        expires_hours = int(parts[3])
                    except ValueError:
                        print("❌ expires_hours must be a number")
                        continue
                
                try:
                    request = ShortenRequest(url=url, custom_code=custom_code, expires_hours=expires_hours)
                    result = shortener.shorten(request)
                    print(f"✅ Shortened!")
                    print(f"   Original: {result.original_url}")
                    print(f"   Short:    {result.short_url}")
                    print(f"   Code:     {result.short_code}")
                    if result.expires_at:
                        print(f"   Expires:  {result.expires_at}")
                except ValueError as e:
                    print(f"❌ Error: {e}")
            
            elif command.startswith("expand "):
                parts = command.split()
                if len(parts) != 2:
                    print("❌ Usage: expand <code>")
                    continue
                
                code = parts[1]
                expanded = shortener.expand(code)
                
                if expanded:
                    # Get click count for display
                    url_obj = shortener._urls[code]
                    print(f"✅ Expanded!")
                    print(f"   Code:     {code}")
                    print(f"   URL:      {expanded}")
                    print(f"   Clicks:   {url_obj.click_count}")
                else:
                    print(f"❌ Code '{code}' not found or expired")
            
            elif command == "help" or command == "":
                print("Commands:")
                print("  shorten <url> [custom_code] [expires_hours] - Shorten a URL")
                print("  expand <code>                               - Expand a short code")
                print("  list                                        - List all URLs")
                print("  quit                                        - Exit")
            
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 