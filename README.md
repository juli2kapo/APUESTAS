# Football xG Scraper & Over/Under 2.5 Goals Analysis Tool

A Python tool for scraping expected goals (xG) data and predicting over/under 2.5 goals in football matches.

## 🎯 Purpose

This script helps you:
- Analyze xG (expected goals) and xGA (expected goals against) metrics
- Predict whether matches will go OVER or UNDER 2.5 goals
- Make data-driven betting decisions using advanced metrics
- Work with AI tools to enhance your football analysis

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

#### 1. **Demo Mode** (Recommended for first run)
```
Choose mode: 3
```
- See sample predictions with realistic data
- Understand the output format

#### 2. **Manual Entry Mode**
```
Choose mode: 1
```
- Enter fixtures and team stats manually
- Perfect for quick analysis
- Get xG data from sites like:
  - [Understat](https://understat.com/)
  - [FBref](https://fbref.com/)
  - [FootballXG](https://footballxg.com/)
  - [xGscore](https://xgscore.io/)

**Example Manual Entry:**
```
Home team: Manchester City
Away team: Liverpool
Date: 2024-11-10

HOME team statistics:
  Average xG: 2.3
  Average xGA: 0.9
  Over 2.5 matches: 7

AWAY team statistics:
  Average xG: 2.1
  Average xGA: 1.1
  Over 2.5 matches: 8
```

#### 3. **Auto-Scrape Mode** (Experimental)
```
Choose mode: 2
```
- Automated scraping (may require customization)
- You can extend to scrape from your preferred sources

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
