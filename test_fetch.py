#!/usr/bin/env python3
"""
Simple script to test if a URL can be fetched and what data it returns
"""
import requests
import sys
from datetime import datetime

def test_fetch(url):
    """Try to fetch a URL and show what we get"""
    print(f"Testing URL: {url}")
    print("=" * 80)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    try:
        print(f"⏳ Fetching...")
        response = requests.get(url, headers=headers, timeout=10)

        print(f"✅ Status Code: {response.status_code}")
        print(f"📦 Content Length: {len(response.content)} bytes")
        print(f"📄 Content Type: {response.headers.get('content-type', 'unknown')}")
        print()

        if response.status_code == 200:
            # Show first 2000 characters
            content_preview = response.text[:2000]
            print("📝 Content Preview (first 2000 chars):")
            print("-" * 80)
            print(content_preview)
            print("-" * 80)

            # Save full content to file
            filename = f"fetch_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"\n💾 Full content saved to: {filename}")

        return response

    except requests.exceptions.Timeout:
        print("❌ Request timed out after 10 seconds")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - could not reach the server")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_fetch.py <URL>")
        print("\nExample URLs to test:")
        print("  python test_fetch.py 'https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard'")
        print("  python test_fetch.py 'https://www.thesportsdb.com/api/v1/json/3/eventsnextleague.php?id=4328'")
        sys.exit(1)

    url = sys.argv[1]
    test_fetch(url)
