#!/usr/bin/env python3
"""
Advanced fetch testing with different headers and techniques
"""
import requests
import time

def test_with_different_configs(url):
    """Test URL with various configurations"""

    configs = [
        {
            'name': 'Chrome Desktop',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.google.com/',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'cross-site',
                'Cache-Control': 'max-age=0',
            }
        },
        {
            'name': 'Mobile Chrome',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        },
        {
            'name': 'Firefox Desktop',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
        },
        {
            'name': 'Minimal',
            'headers': {
                'User-Agent': 'curl/7.68.0',
                'Accept': '*/*',
            }
        }
    ]

    print(f"Testing: {url}\n")

    for config in configs:
        try:
            response = requests.get(url, headers=config['headers'], timeout=5)
            print(f"[{config['name']}] Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ SUCCESS! Content-Type: {response.headers.get('content-type')}")
                print(f"  Size: {len(response.content)} bytes")
                return response
        except Exception as e:
            print(f"[{config['name']}] Error: {e}")

        time.sleep(0.5)

    print(f"\n❌ All configs failed")
    return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python test_advanced_fetch.py <URL>")
        sys.exit(1)

    test_with_different_configs(sys.argv[1])
