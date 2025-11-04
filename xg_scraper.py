#!/usr/bin/env python3
"""
Football xG/xGA Scraper and Over/Under 2.5 Goals Analysis Tool

This script scrapes expected goals (xG) and expected goals against (xGA) data
for upcoming football matches and predicts over/under 2.5 goals outcomes.

Key Metrics for Over/Under 2.5 Goals Prediction:
1. Team xG Average: Higher xG = more likely to score
2. Team xGA Average: Higher xGA = more likely to concede
3. Combined xG: Both teams' xG + xGA averages
4. Recent Form: Last 5-10 matches performance
5. Head-to-Head xG: Historical matchup data
6. Home/Away Split: Different xG patterns at home vs away
7. Opponent-Adjusted xG: Quality of opposition matters

Rule of Thumb:
- Combined xG > 2.5-3.0: Lean OVER 2.5 goals
- Combined xG < 2.0: Lean UNDER 2.5 goals
- If both teams average 1.5+ xG: Strong OVER signal
- If both teams below 0.9 xG: Strong UNDER signal
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import re

class FootballXGScraper:
    """Scrapes and analyzes xG data from multiple sources"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def scrape_understat_team_data(self, team_name: str, league: str = 'EPL') -> Dict:
        """
        Scrape team xG/xGA data from Understat

        Args:
            team_name: Name of the team
            league: League code (EPL, La_liga, Bundesliga, Serie_A, Ligue_1, RFPL)

        Returns:
            Dictionary with team xG statistics
        """
        try:
            url = f'https://understat.com/team/{team_name}/{datetime.now().year}'
            response = self.session.get(url, timeout=10)

            if response.status_code != 200:
                print(f"Warning: Could not fetch data for {team_name}")
                return {}

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract team data from script tags
            scripts = soup.find_all('script')
            team_data = {}

            for script in scripts:
                if 'teamData' in script.text:
                    # Parse JSON data from JavaScript
                    json_str = re.search(r'JSON\.parse\(\'(.+?)\'\)', script.text)
                    if json_str:
                        data = json.loads(json_str.group(1).encode().decode('unicode_escape'))
                        team_data = self._process_understat_data(data)
                        break

            return team_data

        except Exception as e:
            print(f"Error scraping Understat for {team_name}: {e}")
            return {}

    def _process_understat_data(self, data: List[Dict]) -> Dict:
        """Process raw Understat data to calculate relevant metrics"""
        if not data:
            return {}

        # Get last 10 matches for recent form
        recent_matches = data[-10:] if len(data) >= 10 else data

        total_xg = sum(float(match.get('xG', 0)) for match in recent_matches)
        total_xga = sum(float(match.get('xGA', 0)) for match in recent_matches)
        total_goals = sum(int(match.get('scored', 0)) for match in recent_matches)
        total_conceded = sum(int(match.get('missed', 0)) for match in recent_matches)

        num_matches = len(recent_matches)

        return {
            'avg_xg': round(total_xg / num_matches, 2) if num_matches > 0 else 0,
            'avg_xga': round(total_xga / num_matches, 2) if num_matches > 0 else 0,
            'avg_goals_scored': round(total_goals / num_matches, 2) if num_matches > 0 else 0,
            'avg_goals_conceded': round(total_conceded / num_matches, 2) if num_matches > 0 else 0,
            'total_matches': num_matches,
            'over_25_count': sum(1 for m in recent_matches if int(m.get('scored', 0)) + int(m.get('missed', 0)) > 2.5),
            'recent_form': recent_matches[-5:] if len(recent_matches) >= 5 else recent_matches
        }

    def scrape_fbref_fixtures(self, league_url: str) -> List[Dict]:
        """
        Scrape upcoming fixtures from FBref

        Args:
            league_url: FBref league URL

        Returns:
            List of upcoming fixtures
        """
        try:
            response = self.session.get(league_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            fixtures = []
            fixture_table = soup.find('table', {'id': 'sched_all'})

            if not fixture_table:
                print("Could not find fixture table")
                return fixtures

            rows = fixture_table.find_all('tr')

            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 7:
                    date = cells[0].text.strip()
                    home_team = cells[3].text.strip()
                    away_team = cells[5].text.strip()

                    # Only get upcoming matches (no score yet)
                    score = cells[4].text.strip()
                    if not score or score == '':
                        fixtures.append({
                            'date': date,
                            'home_team': home_team,
                            'away_team': away_team
                        })

            return fixtures

        except Exception as e:
            print(f"Error scraping FBref fixtures: {e}")
            return []

    def get_manual_fixtures(self) -> List[Dict]:
        """
        Get manual input for upcoming fixtures
        Useful when scraping fails or for custom analysis
        """
        print("\n=== Enter Upcoming Fixtures ===")
        fixtures = []

        while True:
            print("\nEnter fixture details (or press Enter to finish):")
            home = input("Home team: ").strip()
            if not home:
                break
            away = input("Away team: ").strip()
            date = input("Date (optional, YYYY-MM-DD): ").strip() or "TBD"

            fixtures.append({
                'home_team': home,
                'away_team': away,
                'date': date
            })

        return fixtures

    def _poisson_probability(self, expected_goals: float, actual_goals: int) -> float:
        """
        Calculate Poisson probability for a given number of goals

        P(X = k) = (λ^k * e^(-λ)) / k!
        where λ is the expected number of goals
        """
        if expected_goals < 0:
            return 0.0

        # Calculate factorial
        factorial = math.factorial(actual_goals)

        # Poisson formula
        probability = (math.pow(expected_goals, actual_goals) * math.exp(-expected_goals)) / factorial
        return probability

    def _calculate_match_probabilities(self, home_lambda: float, away_lambda: float, max_goals: int = 8) -> Dict:
        """
        Calculate probability distribution for match outcomes using Poisson distribution

        Args:
            home_lambda: Expected goals for home team
            away_lambda: Expected goals for away team
            max_goals: Maximum goals to calculate (typically 8 is sufficient)

        Returns:
            Dictionary with probability distributions and key metrics
        """
        # Build probability matrix for all score combinations
        probabilities = {}
        total_over_25 = 0.0
        total_under_25 = 0.0

        for home_goals in range(max_goals + 1):
            for away_goals in range(max_goals + 1):
                # Calculate probability of this exact scoreline
                prob_home = self._poisson_probability(home_lambda, home_goals)
                prob_away = self._poisson_probability(away_lambda, away_goals)
                prob_scoreline = prob_home * prob_away

                probabilities[f"{home_goals}-{away_goals}"] = prob_scoreline

                # Sum probabilities for over/under 2.5
                total_goals = home_goals + away_goals
                if total_goals > 2:  # Over 2.5 (3+ goals)
                    total_over_25 += prob_scoreline
                else:  # Under 2.5 (0, 1, 2 goals)
                    total_under_25 += prob_scoreline

        # Calculate expected total goals
        expected_total = home_lambda + away_lambda

        # Calculate exact probabilities for key totals
        prob_0_goals = probabilities.get("0-0", 0)
        prob_1_goal = probabilities.get("1-0", 0) + probabilities.get("0-1", 0)
        prob_2_goals = (probabilities.get("2-0", 0) + probabilities.get("1-1", 0) +
                       probabilities.get("0-2", 0))
        prob_3_goals = (probabilities.get("3-0", 0) + probabilities.get("2-1", 0) +
                       probabilities.get("1-2", 0) + probabilities.get("0-3", 0))

        return {
            'over_25_probability': total_over_25,
            'under_25_probability': total_under_25,
            'expected_total_goals': expected_total,
            'prob_exactly_0': prob_0_goals,
            'prob_exactly_1': prob_1_goal,
            'prob_exactly_2': prob_2_goals,
            'prob_exactly_3': prob_3_goals,
            'home_lambda': home_lambda,
            'away_lambda': away_lambda,
            'scoreline_probabilities': probabilities
        }

    def analyze_over_under_advanced(self, home_data: Dict, away_data: Dict) -> Dict:
        """
        Advanced analysis using Poisson distribution and proper xG/xGA integration

        This method:
        1. Calculates expected goals using opponent-adjusted metrics
        2. Uses Poisson distribution for probability calculations
        3. Properly integrates both xG (attack) and xGA (defense)
        4. Provides statistical confidence intervals

        Args:
            home_data: Home team xG/xGA statistics
            away_data: Away team xG/xGA statistics

        Returns:
            Detailed analysis with probabilities
        """
        if not home_data or not away_data:
            return {'prediction': 'INSUFFICIENT_DATA', 'confidence': 0, 'reasoning': 'Missing team data'}

        # Extract metrics
        home_attack = home_data.get('avg_xg', 0)  # Home team's attacking strength
        home_defense = home_data.get('avg_xga', 0)  # Home team's defensive weakness
        away_attack = away_data.get('avg_xg', 0)  # Away team's attacking strength
        away_defense = away_data.get('avg_xga', 0)  # Away team's defensive weakness

        # Method 1: Opponent-adjusted expected goals
        # Home team expected goals = (Home attack + Away defensive weakness) / 2
        # This balances the team's attacking ability with opponent's defensive vulnerability
        home_expected_v1 = (home_attack + away_defense) / 2

        # Away team expected goals = (Away attack + Home defensive weakness) / 2
        away_expected_v1 = (away_attack + home_defense) / 2

        # Method 2: Multiplicative adjustment (more sophisticated)
        # Adjust team's attack based on opponent's defense relative to league average
        league_avg_xg = 1.35  # Approximate league average xG per match
        league_avg_xga = 1.35  # Approximate league average xGA per match

        # Attack strength * Opponent defense weakness ratio
        home_attack_strength = home_attack / league_avg_xg if league_avg_xg > 0 else 1.0
        away_defense_ratio = away_defense / league_avg_xga if league_avg_xga > 0 else 1.0
        home_expected_v2 = league_avg_xg * home_attack_strength * away_defense_ratio

        away_attack_strength = away_attack / league_avg_xg if league_avg_xg > 0 else 1.0
        home_defense_ratio = home_defense / league_avg_xga if league_avg_xga > 0 else 1.0
        away_expected_v2 = league_avg_xg * away_attack_strength * home_defense_ratio

        # Weighted combination of both methods (60% method 1, 40% method 2)
        home_lambda = 0.6 * home_expected_v1 + 0.4 * home_expected_v2
        away_lambda = 0.6 * away_expected_v1 + 0.4 * away_expected_v2

        # Add home advantage factor (typically ~0.2-0.3 goals)
        home_advantage = 0.25
        home_lambda += home_advantage

        # Calculate probabilities using Poisson distribution
        prob_results = self._calculate_match_probabilities(home_lambda, away_lambda)

        over_probability = prob_results['over_25_probability'] * 100
        under_probability = prob_results['under_25_probability'] * 100
        expected_total = prob_results['expected_total_goals']

        # Determine prediction based on probabilities
        if over_probability > under_probability:
            prediction = 'OVER 2.5'
            confidence = over_probability
            edge = over_probability - under_probability
        else:
            prediction = 'UNDER 2.5'
            confidence = under_probability
            edge = under_probability - over_probability

        # Adjust confidence based on edge (larger edge = more confident)
        if edge < 10:
            confidence_level = 'LOW'
        elif edge < 20:
            confidence_level = 'MEDIUM'
        else:
            confidence_level = 'HIGH'

        # Historical validation
        home_over_rate = home_data.get('over_25_count', 0) / max(home_data.get('total_matches', 1), 1)
        away_over_rate = away_data.get('over_25_count', 0) / max(away_data.get('total_matches', 1), 1)
        historical_over_rate = (home_over_rate + away_over_rate) / 2

        # Build detailed reasoning
        reasoning = []
        reasoning.append(f"POISSON MODEL PREDICTION:")
        reasoning.append(f"  Expected goals - Home: {home_lambda:.2f}, Away: {away_lambda:.2f}")
        reasoning.append(f"  Total expected goals: {expected_total:.2f}")
        reasoning.append(f"  Over 2.5 probability: {over_probability:.1f}%")
        reasoning.append(f"  Under 2.5 probability: {under_probability:.1f}%")
        reasoning.append(f"  Edge: {edge:.1f}% ({confidence_level} confidence)")
        reasoning.append(f"")
        reasoning.append(f"TEAM METRICS:")
        reasoning.append(f"  Home - Attack: {home_attack:.2f} xG, Defense: {home_defense:.2f} xGA")
        reasoning.append(f"  Away - Attack: {away_attack:.2f} xG, Defense: {away_defense:.2f} xGA")
        reasoning.append(f"")
        reasoning.append(f"VALIDATION:")
        reasoning.append(f"  Historical over 2.5 rate: {historical_over_rate*100:.1f}%")

        # Add contextual warnings
        if home_attack < 1.0 and away_attack < 1.0:
            reasoning.append(f"  ⚠️ Both teams have weak attacks - LOW SCORING GAME likely")
        elif home_attack > 1.8 and away_attack > 1.8:
            reasoning.append(f"  ⚠️ Both teams have strong attacks - HIGH SCORING GAME likely")

        if home_defense > 1.5 and away_defense > 1.5:
            reasoning.append(f"  ⚠️ Both teams have weak defenses - GOALS EXPECTED")
        elif home_defense < 1.0 and away_defense < 1.0:
            reasoning.append(f"  ⚠️ Both teams have strong defenses - TIGHT GAME expected")

        # Most likely scorelines
        sorted_scorelines = sorted(
            prob_results['scoreline_probabilities'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        reasoning.append(f"")
        reasoning.append(f"MOST LIKELY SCORELINES:")
        for scoreline, prob in sorted_scorelines:
            reasoning.append(f"  {scoreline}: {prob*100:.1f}%")

        return {
            'prediction': prediction,
            'confidence': round(confidence, 1),
            'confidence_level': confidence_level,
            'edge': round(edge, 1),
            'over_probability': round(over_probability, 1),
            'under_probability': round(under_probability, 1),
            'expected_goals': round(expected_total, 2),
            'home_expected': round(home_lambda, 2),
            'away_expected': round(away_lambda, 2),
            'reasoning': reasoning,
            'metrics': {
                'home_xg': home_attack,
                'home_xga': home_defense,
                'away_xg': away_attack,
                'away_xga': away_defense,
                'historical_over_rate': round(historical_over_rate * 100, 1)
            },
            'prob_details': {
                'prob_0_goals': round(prob_results['prob_exactly_0'] * 100, 2),
                'prob_1_goal': round(prob_results['prob_exactly_1'] * 100, 2),
                'prob_2_goals': round(prob_results['prob_exactly_2'] * 100, 2),
                'prob_3_goals': round(prob_results['prob_exactly_3'] * 100, 2),
            }
        }

    def analyze_over_under(self, home_data: Dict, away_data: Dict) -> Dict:
        """
        Analyze over/under 2.5 goals prediction

        Args:
            home_data: Home team xG statistics
            away_data: Away team xG statistics

        Returns:
            Analysis results with prediction
        """
        if not home_data or not away_data:
            return {'prediction': 'INSUFFICIENT_DATA', 'confidence': 0, 'reasoning': 'Missing team data'}

        # Key metrics
        home_xg = home_data.get('avg_xg', 0)
        home_xga = home_data.get('avg_xga', 0)
        away_xg = away_data.get('avg_xg', 0)
        away_xga = away_data.get('avg_xga', 0)

        # Combined xG prediction (home attack vs away defense + away attack vs home defense)
        home_expected = (home_xg + away_xga) / 2
        away_expected = (away_xg + home_xga) / 2
        total_expected = home_expected + away_expected

        # Alternative: Simple average method
        simple_total = home_xg + away_xg

        # Weighted prediction (70% combined, 30% simple)
        predicted_goals = 0.7 * total_expected + 0.3 * simple_total

        # Historical over 2.5 rate
        home_over_rate = home_data.get('over_25_count', 0) / max(home_data.get('total_matches', 1), 1)
        away_over_rate = away_data.get('over_25_count', 0) / max(away_data.get('total_matches', 1), 1)
        avg_over_rate = (home_over_rate + away_over_rate) / 2

        # Determine prediction
        if predicted_goals >= 2.8:
            prediction = 'OVER 2.5'
            confidence = min(95, 60 + (predicted_goals - 2.8) * 15)
        elif predicted_goals <= 2.2:
            prediction = 'UNDER 2.5'
            confidence = min(95, 60 + (2.2 - predicted_goals) * 15)
        else:
            prediction = 'MARGINAL (Close to 2.5)'
            confidence = 50

        # Adjust confidence based on historical rate
        if prediction == 'OVER 2.5' and avg_over_rate > 0.6:
            confidence += 5
        elif prediction == 'UNDER 2.5' and avg_over_rate < 0.4:
            confidence += 5

        confidence = min(95, confidence)  # Cap at 95%

        reasoning = []
        reasoning.append(f"Predicted total goals: {predicted_goals:.2f}")
        reasoning.append(f"Home team avg xG: {home_xg:.2f}, avg xGA: {home_xga:.2f}")
        reasoning.append(f"Away team avg xG: {away_xg:.2f}, avg xGA: {away_xga:.2f}")
        reasoning.append(f"Historical over 2.5 rate: {avg_over_rate*100:.1f}%")

        # Additional insights
        if home_xg >= 1.5 and away_xg >= 1.5:
            reasoning.append("⚠️ Both teams strong attackers - HIGH SCORING POTENTIAL")
        if home_xga <= 1.0 and away_xga <= 1.0:
            reasoning.append("⚠️ Both teams strong defenders - LOW SCORING POTENTIAL")

        return {
            'prediction': prediction,
            'confidence': round(confidence, 1),
            'predicted_goals': round(predicted_goals, 2),
            'reasoning': reasoning,
            'metrics': {
                'home_xg': home_xg,
                'home_xga': home_xga,
                'away_xg': away_xg,
                'away_xga': away_xga,
                'over_rate': round(avg_over_rate * 100, 1)
            }
        }

    def generate_report(self, fixtures: List[Dict], analyses: List[Dict]):
        """Generate a formatted report of predictions"""
        print("\n" + "="*80)
        print("FOOTBALL OVER/UNDER 2.5 GOALS PREDICTIONS")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        for fixture, analysis in zip(fixtures, analyses):
            print(f"\n📅 {fixture.get('date', 'TBD')}")
            print(f"🏠 {fixture['home_team']} vs {fixture['away_team']} 🛫")
            print("-" * 80)

            if analysis['prediction'] == 'INSUFFICIENT_DATA':
                print("⚠️  Insufficient data for prediction")
                print(f"Reason: {analysis['reasoning']}")
            else:
                # Check if this is advanced analysis (with probabilities)
                has_probabilities = 'over_probability' in analysis

                print(f"🎯 PREDICTION: {analysis['prediction']}")
                print(f"📊 Confidence: {analysis['confidence']}%")

                if has_probabilities:
                    # Advanced analysis output
                    print(f"🔥 Edge: {analysis.get('edge', 0):.1f}% ({analysis.get('confidence_level', 'MEDIUM')})")
                    print(f"⚽ Expected Goals: {analysis['expected_goals']}")
                    print(f"   Home: {analysis['home_expected']:.2f} | Away: {analysis['away_expected']:.2f}")
                    print(f"\n📈 Probabilities:")
                    print(f"   OVER 2.5: {analysis['over_probability']}%")
                    print(f"   UNDER 2.5: {analysis['under_probability']}%")
                    print(f"\n📊 Key Metrics:")
                    metrics = analysis['metrics']
                    print(f"   Home: xG={metrics['home_xg']:.2f}, xGA={metrics['home_xga']:.2f}")
                    print(f"   Away: xG={metrics['away_xg']:.2f}, xGA={metrics['away_xga']:.2f}")
                    print(f"   Historical Over 2.5 Rate: {metrics['historical_over_rate']}%")
                else:
                    # Simple analysis output (legacy)
                    print(f"⚽ Predicted Goals: {analysis.get('predicted_goals', 0)}")
                    print(f"\n📈 Key Metrics:")
                    metrics = analysis['metrics']
                    print(f"   Home: xG={metrics['home_xg']:.2f}, xGA={metrics['home_xga']:.2f}")
                    print(f"   Away: xG={metrics['away_xg']:.2f}, xGA={metrics['away_xga']:.2f}")
                    print(f"   Historical Over 2.5 Rate: {metrics.get('over_rate', 0)}%")

                print(f"\n💡 Analysis:")
                for reason in analysis['reasoning']:
                    print(f"   {reason}")

            print("-" * 80)

        # Summary statistics
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)

        over_count = sum(1 for a in analyses if 'OVER' in a.get('prediction', ''))
        under_count = sum(1 for a in analyses if 'UNDER' in a.get('prediction', ''))
        marginal_count = sum(1 for a in analyses if 'MARGINAL' in a.get('prediction', ''))

        print(f"Total Fixtures Analyzed: {len(fixtures)}")
        print(f"OVER 2.5 predictions: {over_count}")
        print(f"UNDER 2.5 predictions: {under_count}")
        print(f"Marginal predictions: {marginal_count}")

        # Best bets (high confidence)
        high_conf = [a for a in analyses if a.get('confidence', 0) >= 70]
        if high_conf:
            print(f"\n🔥 High Confidence Bets (≥70%):")
            for i, analysis in enumerate(high_conf):
                fixture = fixtures[analyses.index(analysis)]
                print(f"   {fixture['home_team']} vs {fixture['away_team']}: "
                      f"{analysis['prediction']} ({analysis['confidence']}%)")

        print("="*80)

        # Important notes
        print("\n⚠️  IMPORTANT NOTES:")
        print("• xG data should be combined with team news, injuries, and motivation")
        print("• Consider match context: rivalry games, weather, league position")
        print("• Use this as ONE tool in your analysis, not the only factor")
        print("• Past performance doesn't guarantee future results")
        print("="*80 + "\n")


def main():
    """Main execution function"""
    print("="*80)
    print("FOOTBALL xG SCRAPER & OVER/UNDER 2.5 ANALYSIS TOOL")
    print("ADVANCED POISSON PROBABILITY MODEL")
    print("="*80)
    print("\nKey Metrics for Over/Under 2.5 Prediction:")
    print("1. Average xG (Expected Goals) - Team attacking strength")
    print("2. Average xGA (Expected Goals Against) - Team defensive weakness")
    print("3. Opponent-adjusted expected goals (xG vs xGA)")
    print("4. Poisson probability distribution for goal outcomes")
    print("5. Historical over/under 2.5 rate validation")
    print("\nThis tool uses:")
    print("✓ Poisson distribution for statistical probability")
    print("✓ Both xG AND xGA for accurate predictions")
    print("✓ Opponent-adjusted metrics (attack vs defense)")
    print("✓ Home advantage factor (~0.25 goals)")
    print("✓ Multiple calculation methods for robustness")
    print("="*80)

    scraper = FootballXGScraper()

    # Example: Manual mode for quick analysis
    print("\nChoose mode:")
    print("1. Manual entry (enter team stats directly)")
    print("2. Auto-scrape fixtures (requires league URL)")
    print("3. Demo mode (sample data)")

    mode = input("\nEnter choice (1-3): ").strip() or "1"

    if mode == "3":
        # Demo mode with sample data
        fixtures = [
            {'home_team': 'Manchester City', 'away_team': 'Liverpool', 'date': '2024-11-10'},
            {'home_team': 'Arsenal', 'away_team': 'Chelsea', 'date': '2024-11-10'},
        ]

        # Sample data (replace with real scraping)
        home_data_1 = {'avg_xg': 2.3, 'avg_xga': 0.9, 'total_matches': 10, 'over_25_count': 7}
        away_data_1 = {'avg_xg': 2.1, 'avg_xga': 1.1, 'total_matches': 10, 'over_25_count': 8}

        home_data_2 = {'avg_xg': 1.8, 'avg_xga': 1.0, 'total_matches': 10, 'over_25_count': 5}
        away_data_2 = {'avg_xg': 1.6, 'avg_xga': 1.2, 'total_matches': 10, 'over_25_count': 6}

        # Use advanced Poisson-based analysis
        analyses = [
            scraper.analyze_over_under_advanced(home_data_1, away_data_1),
            scraper.analyze_over_under_advanced(home_data_2, away_data_2)
        ]

        scraper.generate_report(fixtures, analyses)

    elif mode == "1":
        # Manual entry mode
        fixtures = scraper.get_manual_fixtures()

        if not fixtures:
            print("No fixtures entered. Exiting.")
            return

        analyses = []

        for fixture in fixtures:
            print(f"\n--- Analyzing: {fixture['home_team']} vs {fixture['away_team']} ---")
            print("Enter HOME team statistics (last 10 matches average):")
            home_xg = float(input("  Average xG: ") or "1.5")
            home_xga = float(input("  Average xGA: ") or "1.2")
            home_over = int(input("  Number of over 2.5 matches (out of 10): ") or "5")

            print("Enter AWAY team statistics (last 10 matches average):")
            away_xg = float(input("  Average xG: ") or "1.4")
            away_xga = float(input("  Average xGA: ") or "1.3")
            away_over = int(input("  Number of over 2.5 matches (out of 10): ") or "5")

            home_data = {
                'avg_xg': home_xg,
                'avg_xga': home_xga,
                'total_matches': 10,
                'over_25_count': home_over
            }

            away_data = {
                'avg_xg': away_xg,
                'avg_xga': away_xga,
                'total_matches': 10,
                'over_25_count': away_over
            }

            # Use advanced Poisson-based analysis
            analysis = scraper.analyze_over_under_advanced(home_data, away_data)
            analyses.append(analysis)

        scraper.generate_report(fixtures, analyses)

    else:
        print("\nNote: Auto-scraping requires specific league URLs and may need adjustments")
        print("For now, use manual mode or demo mode for testing.")
        print("You can extend this script to scrape from your preferred data source.")

    # Export option
    export = input("\nExport results to JSON? (y/n): ").lower()
    if export == 'y':
        filename = f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump({
                'generated': datetime.now().isoformat(),
                'fixtures': fixtures,
                'analyses': analyses
            }, f, indent=2)
        print(f"✅ Results exported to {filename}")


if __name__ == "__main__":
    main()
