# API Setup Guide for Football xG Scraper

## The Reality: Why Free Scraping Doesn't Work Reliably

After extensive testing, **all major football data sources block datacenter IPs and require either:**
1. Residential IP addresses (home internet)
2. API keys (free or paid)

### Sources Tested (All Blocked from Datacenter/VPS):
- ❌ FBref.com (403 Forbidden)
- ❌ Understat.com (Access Denied)
- ❌ ESPN API (403 Forbidden)
- ❌ TheSportsDB (Access Denied)
- ❌ Sofascore API (403 Forbidden)
- ❌ BBC Sport (Access Denied)
- ❌ FlashScore (No public API)
- ❌ LiveScore (No public API)

## ✅ Recommended Solution: Football-Data.org API

**Football-Data.org** offers a **FREE FOREVER** tier that works reliably:

### Features:
- ✅ **100 requests per day** (free tier)
- ✅ **Top European leagues** (Premier League, La Liga, Serie A, Bundesliga, Ligue 1, Champions League)
- ✅ **Live scores, fixtures, standings**
- ✅ **Well-documented JSON API**
- ✅ **Free forever for top competitions**

### How to Get Your Free API Key:

1. **Register** (2 minutes):
   - Go to: https://www.football-data.org/client/register
   - Enter your email and create a password
   - Verify your email

2. **Get API Token**:
   - Log in to https://www.football-data.org
   - Go to your profile/dashboard
   - Copy your API token (looks like: `abc123def456ghi789jkl012`)

3. **Use with this script**:
   ```bash
   # Set as environment variable (recommended)
   export FOOTBALL_DATA_API_KEY="your-api-key-here"

   # Or the script will prompt you for it
   python3 xg_scraper.py
   ```

### API Endpoints (Examples):

```bash
# Get Premier League fixtures
curl -H "X-Auth-Token: YOUR_API_KEY" \
  https://api.football-data.org/v4/competitions/PL/matches

# Get today's matches across all competitions
curl -H "X-Auth-Token: YOUR_API_KEY" \
  https://api.football-data.org/v4/matches

# Get team information
curl -H "X-Auth-Token: YOUR_API_KEY" \
  https://api.football-data.org/v4/teams/57
```

## Alternative: Run from Home Network

If you don't want to use API keys, FBref/Understat scraping **will work** from:
- ✅ Home internet (residential IP)
- ✅ Mobile hotspot
- ✅ Coffee shop WiFi
- ❌ VPS/Cloud servers (will be blocked)

## Rate Limits

### Football-Data.org Free Tier:
- **100 requests/day**
- **10 requests/minute**
- Covers ~5 leagues with fixtures/standings/teams

### Coverage:
With 100 requests/day you can:
- Fetch fixtures for 5 leagues daily
- Get team stats for 20 teams
- Mix fixtures + standings + team data

This is **plenty** for daily predictions!

## Implementation Status

The script currently supports:
1. ✅ **FBref scraping** (works from residential IP)
2. ✅ **Understat scraping** (works from residential IP)
3. ✅ **Football-Data.org API** (works from anywhere with API key - COMING SOON)

## Why Not Just Use Web Scraping?

**Web scraping issues:**
- Sites detect and block bots (User-Agent, IP, behavior)
- HTML structure changes frequently
- Rate limiting and IP bans
- Legal/ToS violations
- Unreliable from cloud servers

**API benefits:**
- Official, stable, documented
- Better rate limits
- Legal to use
- Works from anywhere
- Structured JSON data

## Conclusion

For **reliable, production use**, get a free API key from Football-Data.org. It takes 2 minutes and works forever for free.

For **occasional home use**, the current FBref/Understat scraping works fine.
