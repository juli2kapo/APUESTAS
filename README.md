# Football xG Scraper & Over/Under 2.5 Goals Analysis Tool

**Automatically scrape upcoming football matches and predict over/under 2.5 goals using advanced xG analysis.**

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the scraper
python xg_scraper.py

# Choose option 1 (AUTO-SCRAPE)
# Sit back and watch it automatically:
#   ✅ Scrape upcoming Premier League fixtures
#   ✅ Get each team's xG/xGA data (with home/away splits)
#   ✅ Analyze using Poisson probability model
#   ✅ Generate predictions report
```

**That's it! No manual input needed.**

## 🎯 Purpose

This tool **automatically**:
- Scrapes upcoming football fixtures (Premier League)
- Scrapes xG (expected goals) and xGA (expected goals against) data
- Uses venue-specific stats (home vs away) for higher accuracy
- Predicts whether matches will go OVER or UNDER 2.5 goals
- Provides statistical probabilities using Poisson distribution
- Works perfectly with AI tools for enhanced analysis

## 📊 Key Metrics for Over/Under 2.5 Prediction

Based on extensive research, the most important metrics are:

### 1. **Average xG (Expected Goals)**
- Measures team's attacking quality
- Higher xG = more likely to score
- **Benchmark**: Teams averaging 1.5+ xG are strong attackers

### 2. **Average xGA (Expected Goals Against)**
- Measures defensive vulnerability
- Higher xGA = more likely to concede
- **Benchmark**: Teams with xGA > 1.3 have weak defenses

### 3. **Combined xG Prediction**
```
Home Expected = (Home xG + Away xGA) / 2
Away Expected = (Away xG + Home xGA) / 2
Total Expected = Home Expected + Away Expected
```

### 4. **Recent Form (Last 10 Matches)**
- More weight on recent performance
- Captures momentum and current team state

### 5. **Historical Over/Under Rate**
- % of matches that went over 2.5 goals
- Strong indicator of team playing style

### 6. **Opponent-Adjusted Metrics**
- Quality of opposition matters
- Strong attack vs weak defense = goal explosion
- Weak attack vs strong defense = low scoring

### 7. **🏠 HOME/AWAY SPLITS (CRITICAL!)** ⭐

**This is the most important factor for accuracy!**

Teams perform **very differently** at home vs away:

**Example - Manchester City (2024/25 season):**
- **At Home**: 2.5 xG, 0.7 xGA (dominant)
- **Away**: 1.9 xG, 1.1 xGA (still good, but much different)
- **Difference**: 0.6 xG and 0.4 xGA swing!

**Why Home/Away Matters:**
- Home advantage is real (crowd, familiarity, travel)
- Some teams have **huge** home/away splits
- Using overall stats + generic adjustment is less accurate
- Venue-specific stats already include home advantage

**This Tool's Approach:**
- ✅ **Option 1 (BEST)**: Enter home team's HOME stats + away team's AWAY stats
- ⚠️ **Option 2 (OK)**: Enter overall stats, tool adds +0.25 goal home advantage
- ❌ **Don't**: Use same overall stats for both teams

**Where to Find Home/Away Splits:**
1. **Understat.com** - Filter by home/away matches
2. **FBref.com** - "Home" and "Away" tables
3. **FootballXG.com** - Venue-specific filters
4. **Manual calculation** - Track last 10 home/away matches separately

## 🔢 Prediction Rules

### Strong OVER 2.5 Signals:
- ✅ Combined xG > 2.8
- ✅ Both teams avg xG > 1.5
- ✅ Historical over rate > 60%
- ✅ Both teams have high xGA (weak defenses)

### Strong UNDER 2.5 Signals:
- ✅ Combined xG < 2.2
- ✅ Both teams avg xG < 0.9
- ✅ Historical over rate < 40%
- ✅ Both teams have low xGA (strong defenses)

### Marginal Zone (2.2 - 2.8):
- Closer analysis needed
- Consider external factors (injuries, motivation, weather)

## 🚀 Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd APUESTAS

# Install dependencies
pip install -r requirements.txt
```

## 💻 Usage

### Run the script:
```bash
python xg_scraper.py
```

### Three Modes Available:

#### 1. **🤖 AUTO-SCRAPE Mode** (PRIMARY FEATURE - What you want!)
```
Choose mode: 1
```
**This is the main feature! It does everything automatically:**

✅ Scrapes upcoming Premier League fixtures from FBref
✅ For each match, scrapes both teams' xG/xGA data from Understat
✅ **Automatically includes home/away splits for accuracy**
✅ Analyzes all matches using Poisson probability model
✅ Generates comprehensive predictions report
✅ Optional JSON export for AI analysis

**What happens:**
```
🔍 Fetching fixtures from FBref...
✅ Found 10 upcoming fixtures

[1/10] Arsenal vs Chelsea
--------------------------------------------------------------
🏠 Scraping Arsenal data...
  ✅ Arsenal at home: 2.1 xG, 0.8 xGA
🛫 Scraping Chelsea data...
  ✅ Chelsea away: 1.6 xG, 1.3 xGA
  🔮 Analyzing...
  📊 Prediction: OVER 2.5 (64.2% confidence)

[2/10] Manchester United vs Liverpool
...
```

**No manual input needed! Just run and get predictions.**

**Data Sources Used:**
- Fixtures: FBref.com (upcoming matches)
- Team Stats: Understat.com (xG/xGA with home/away splits)
- Analysis: Advanced Poisson probability model

**Limitations:**
- Currently supports Premier League only (easy to extend)
- Requires internet connection
- May be rate-limited if run too frequently
- Some team names may need adjustment in normalize_team_name()

#### 2. **Demo Mode** (Recommended for first run)
```
Choose mode: 3
```
- See sample predictions with realistic data
- Understand the output format
- Test without internet connection

#### 3. **Manual Entry Mode**
```
Choose mode: 2
```
- Enter fixtures and team stats manually
- **Use venue-specific stats for best accuracy!**
- Get xG data from sites like:
  - [Understat](https://understat.com/) - Best for home/away splits
  - [FBref](https://fbref.com/) - Comprehensive home/away tables
  - [FootballXG](https://footballxg.com/)
  - [xGscore](https://xgscore.io/)

**Example Manual Entry (Venue-Specific):**
```
Home team: Manchester City
Away team: Liverpool
Date: 2024-11-10

Use venue-specific stats? y

Manchester City stats AT HOME (last 10 HOME matches):
  xG at home: 2.5
  xGA at home: 0.7
  Over 2.5 in home matches: 7

Liverpool stats AWAY (last 10 AWAY matches):
  xG away: 1.8
  xGA away: 1.2
  Over 2.5 in away matches: 6
```

**How to Get Venue-Specific Stats:**

On **Understat.com**:
1. Go to team page (e.g., understat.com/team/Manchester_City/2024)
2. Click "Home" or "Away" filter
3. Look at average xG/xGA for last 10 matches

On **FBref.com**:
1. Go to team page
2. Scroll to "Scores & Fixtures" table
3. Filter by "Home" or "Away"
4. Calculate average from recent matches

**Use This Mode When:**
- Auto-scraping fails for a specific team
- You want to analyze a different league
- You have more recent/accurate data manually
- Testing specific scenarios

## 📈 Output Example

```
================================================================================
FOOTBALL OVER/UNDER 2.5 GOALS PREDICTIONS
================================================================================
Generated: 2024-11-04 18:00:00
================================================================================

📅 2024-11-10
🏠 Manchester City vs Liverpool 🛫
--------------------------------------------------------------------------------
🎯 PREDICTION: OVER 2.5
📊 Confidence: 85.3%
⚽ Predicted Goals: 3.45

📈 Key Metrics:
   Home: xG=2.30, xGA=0.90
   Away: xG=2.10, xGA=1.10
   Historical Over 2.5 Rate: 75.0%

💡 Reasoning:
   • Predicted total goals: 3.45
   • Home team avg xG: 2.30, avg xGA: 0.90
   • Away team avg xG: 2.10, avg xGA: 1.10
   • Historical over 2.5 rate: 75.0%
   • ⚠️ Both teams strong attackers - HIGH SCORING POTENTIAL
--------------------------------------------------------------------------------

================================================================================
SUMMARY
================================================================================
Total Fixtures Analyzed: 2
OVER 2.5 predictions: 1
UNDER 2.5 predictions: 0
Marginal predictions: 1

🔥 High Confidence Bets (≥70%):
   Manchester City vs Liverpool: OVER 2.5 (85.3%)
================================================================================
```

## 🤖 Using with AI

This tool is designed to work alongside AI analysis:

1. **Run the script** to get xG predictions
2. **Export to JSON** for AI processing
3. **Combine with**:
   - Team news and injuries
   - Motivation factors (league position, rivalries)
   - Weather conditions
   - Head-to-head history
   - Betting odds analysis

**AI Prompt Example:**
```
I have xG analysis showing:
- Man City vs Liverpool
- Predicted goals: 3.45
- Both teams xG > 2.0

Consider recent injuries to Liverpool's defense and City's home dominance.
Should I bet OVER 2.5 goals?
```

## 📊 Where to Get xG Data

### Recommended Sources:

1. **[Understat](https://understat.com/)** ⭐ Best
   - Detailed xG for major leagues
   - Free access
   - Historical data

2. **[FBref](https://fbref.com/)** ⭐ Comprehensive
   - Advanced stats
   - Fixtures and results
   - Free

3. **[FootballXG](https://footballxg.com/)**
   - xG stats across 50+ leagues
   - Easy to read

4. **[xGscore](https://xgscore.io/)**
   - Live xG data
   - Multiple leagues

5. **[BetShoot](https://www.betshoot.com/football/xgoals/)**
   - Today's xG stats
   - Betting-focused

## 🔧 Extending the Script

### Add Custom Scraping Source:

```python
def scrape_your_source(self, url: str) -> Dict:
    """Add your custom scraper here"""
    response = self.session.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Your scraping logic
    # ...

    return {
        'avg_xg': extracted_xg,
        'avg_xga': extracted_xga,
        'total_matches': match_count,
        'over_25_count': over_count
    }
```

### Adjust Prediction Algorithm:

Edit the `analyze_over_under()` method to:
- Change confidence thresholds
- Add custom metrics
- Weight factors differently

## ⚠️ Important Notes

### This Tool Should Be Used:
✅ As ONE factor in your analysis
✅ Combined with team news and context
✅ With proper bankroll management
✅ For educational/research purposes

### This Tool Should NOT:
❌ Be your only decision factor
❌ Replace watching matches and understanding teams
❌ Guarantee profits (no tool can)
❌ Ignore match context (injuries, motivation, weather)

## 📚 Research Background

### Why xG Works for Over/Under:

From research (2024):
> "When both teams produce high xG (lots of quality chances), an Over 2.5 goals bet is logical, while low xG output from both sides suggests an Under 2.5 bet is safer."

> "If both teams average 1.5 xG each, statistics strongly lean over, while two sides below 0.9 xG usually spell low-scoring scenarios."

### Advanced Considerations:

1. **Shot Quality Over Quantity**: xG measures chance quality, not just number of shots
2. **Context Matters**: xG doesn't capture match situations (team chasing game, parking the bus)
3. **Regression to Mean**: Teams over/underperforming xG tend to regress
4. **Home/Away Split**: Some teams have vastly different xG at home vs away

## 🎓 Learning Resources

- [xG Explained - Beginner's Guide](https://caanberry.com/guide-to-expected-goals-in-football/)
- [Using xG for Betting](https://first.com/blog/sports/xg-be-used-to-identify-good-bets)
- [Advanced xG Analysis](https://escored.com/how-expected-goals-xg-power-smarter-football-predictions/)

## 📄 License

MIT License - Feel free to modify and extend for your needs.

## 🤝 Contributing

Contributions welcome! Especially:
- Additional scraping sources
- Improved prediction algorithms
- Historical backtesting
- API integrations

## ⚡ Quick Start Checklist

- [ ] Install Python 3.7+
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run demo mode: `python xg_scraper.py` (choose option 3)
- [ ] Try manual entry with real data from Understat
- [ ] Export results to JSON for AI analysis
- [ ] Combine with your football knowledge
- [ ] Start small, track results, refine approach

---

**Remember: Bet responsibly. This is a tool for analysis, not a guarantee of success.**
