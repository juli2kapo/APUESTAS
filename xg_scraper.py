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

    # Comprehensive league database
    LEAGUES = {
        # International Tournaments
        'FIFA World Cup': {
            'fbref_id': '1',
            'fbref_name': 'World-Cup',
            'understat': None,
            'season': '2026'
        },
        'FIFA World Cup Qualifying': {
            'fbref_id': 'comps/qualifier',
            'fbref_name': 'World-Cup-Qualifying',
            'understat': None,
        },
        'UEFA Euro': {
            'fbref_id': '676',
            'fbref_name': 'European-Championship',
            'understat': None,
        },
        'UEFA Euro Qualifying': {
            'fbref_id': 'comps/qualifier',
            'fbref_name': 'European-Championship-Qualifying',
            'understat': None,
        },
        'Africa Cup of Nations': {
            'fbref_id': '72',
            'fbref_name': 'Africa-Cup-of-Nations',
            'understat': None,
        },
        'Copa America': {
            'fbref_id': '685',
            'fbref_name': 'Copa-America',
            'understat': None,
        },
        'UEFA Nations League': {
            'fbref_id': '999',
            'fbref_name': 'UEFA-Nations-League',
            'understat': None,
        },

        # European Club Competitions
        'UEFA Champions League': {
            'fbref_id': '8',
            'fbref_name': 'Champions-League',
            'understat': None,
        },
        'UEFA Europa League': {
            'fbref_id': '19',
            'fbref_name': 'Europa-League',
            'understat': None,
        },
        'UEFA Europa Conference League': {
            'fbref_id': '882',
            'fbref_name': 'Europa-Conference-League',
            'understat': None,
        },

        # Top 5 European Leagues (Understat supported)
        'Premier League': {
            'fbref_id': '9',
            'fbref_name': 'Premier-League',
            'understat': 'EPL',
            'country': 'England'
        },
        'La Liga': {
            'fbref_id': '12',
            'fbref_name': 'La-Liga',
            'understat': 'La_liga',
            'country': 'Spain'
        },
        'Bundesliga': {
            'fbref_id': '20',
            'fbref_name': 'Bundesliga',
            'understat': 'Bundesliga',
            'country': 'Germany'
        },
        'Serie A': {
            'fbref_id': '11',
            'fbref_name': 'Serie-A',
            'understat': 'Serie_A',
            'country': 'Italy'
        },
        'Ligue 1': {
            'fbref_id': '13',
            'fbref_name': 'Ligue-1',
            'understat': 'Ligue_1',
            'country': 'France'
        },

        # English Football
        'EFL Championship': {
            'fbref_id': '10',
            'fbref_name': 'Championship',
            'understat': None,
            'country': 'England'
        },
        'EFL League One': {
            'fbref_id': '15',
            'fbref_name': 'League-One',
            'understat': None,
            'country': 'England'
        },
        'EFL League Two': {
            'fbref_id': '16',
            'fbref_name': 'League-Two',
            'understat': None,
            'country': 'England'
        },
        'FA Cup': {
            'fbref_id': '23',
            'fbref_name': 'FA-Cup',
            'understat': None,
            'country': 'England'
        },

        # South American Competitions
        'Copa Libertadores': {
            'fbref_id': '14',
            'fbref_name': 'Copa-Libertadores',
            'understat': None,
        },
        'Copa Sudamericana': {
            'fbref_id': '718',
            'fbref_name': 'Copa-Sudamericana',
            'understat': None,
        },
        'Brasileirao Serie A': {
            'fbref_id': '24',
            'fbref_name': 'Serie-A',
            'understat': None,
            'country': 'Brazil'
        },
        'Brasileirao Serie B': {
            'fbref_id': '38',
            'fbref_name': 'Serie-B',
            'understat': None,
            'country': 'Brazil'
        },
        'Copa do Brasil': {
            'fbref_id': '609',
            'fbref_name': 'Copa-do-Brasil',
            'understat': None,
            'country': 'Brazil'
        },
        'Liga Profesional Argentina': {
            'fbref_id': '21',
            'fbref_name': 'Primera-Division',
            'understat': None,
            'country': 'Argentina'
        },
        'Copa de la Liga Argentina': {
            'fbref_id': '1050',
            'fbref_name': 'Copa-de-la-Liga-Profesional',
            'understat': None,
            'country': 'Argentina'
        },
        'Copa Argentina': {
            'fbref_id': '644',
            'fbref_name': 'Copa-Argentina',
            'understat': None,
            'country': 'Argentina'
        },
        'Primera B Nacional Argentina': {
            'fbref_id': '443',
            'fbref_name': 'Primera-B-Nacional',
            'understat': None,
            'country': 'Argentina'
        },
        'Primera Division Chile': {
            'fbref_id': '37',
            'fbref_name': 'Primera-Division',
            'understat': None,
            'country': 'Chile'
        },
        'Liga Pro Ecuador': {
            'fbref_id': '45',
            'fbref_name': 'Serie-A',
            'understat': None,
            'country': 'Ecuador'
        },
        'Copa Ecuador': {
            'fbref_id': '1026',
            'fbref_name': 'Copa-Ecuador',
            'understat': None,
            'country': 'Ecuador'
        },
        'Categoria Primera A Colombia': {
            'fbref_id': '35',
            'fbref_name': 'Primera-A',
            'understat': None,
            'country': 'Colombia'
        },
        'Liga MX': {
            'fbref_id': '31',
            'fbref_name': 'Liga-MX',
            'understat': None,
            'country': 'Mexico'
        },
    }

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _fetch_with_retry(self, url: str, max_retries: int = 3, timeout: int = 15) -> Optional[requests.Response]:
        """
        Fetch URL with exponential backoff retry logic

        Args:
            url: URL to fetch
            max_retries: Maximum number of retry attempts (default: 3)
            timeout: Request timeout in seconds (default: 15)

        Returns:
            Response object if successful, None otherwise
        """
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=timeout)

                # Success
                if response.status_code == 200:
                    return response

                # Client error (4xx) - don't retry
                if 400 <= response.status_code < 500:
                    return None

                # Server error (5xx) - retry with backoff
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    time.sleep(wait_time)

            except (requests.ConnectionError, requests.Timeout) as e:
                # Network error - retry with backoff
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    time.sleep(wait_time)
                else:
                    # Last attempt failed
                    return None
            except Exception as e:
                # Other errors - don't retry
                return None

        return None

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
            response = self._fetch_with_retry(url, max_retries=3, timeout=10)

            if not response:
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

            # Validate data before returning
            if self._validate_xg_data(team_data, team_name):
                return team_data
            else:
                return {}

        except Exception as e:
            print(f"Error scraping Understat for {team_name}: {e}")
            return {}

    def scrape_fbref_team_data(self, team_name: str, league_name: str) -> Dict:
        """
        Scrape team xG/xGA data from FBref as fallback

        Args:
            team_name: Name of the team
            league_name: League name from LEAGUES dict

        Returns:
            Dictionary with team xG statistics including home/away splits
        """
        try:
            league_info = self.LEAGUES.get(league_name)
            if not league_info:
                return {}

            fbref_id = league_info['fbref_id']
            fbref_name = league_info['fbref_name']

            # Search for team on FBref - construct likely URL
            # FBref team URLs are like: /en/squads/{team_id}/{team_name}-Stats
            # We'll search via the league's team list page instead

            league_url = f"https://fbref.com/en/comps/{fbref_id}/{fbref_name}-Stats"

            response = self._fetch_with_retry(league_url, max_retries=3, timeout=15)
            if not response:
                return {}

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the team's link in the standings/team list
            team_link = None
            for link in soup.find_all('a'):
                if link.text.strip().lower() == team_name.lower():
                    href = link.get('href', '')
                    if '/squads/' in href:
                        team_link = href
                        break

            if not team_link:
                # Try partial match
                for link in soup.find_all('a'):
                    if team_name.lower() in link.text.strip().lower() and '/squads/' in link.get('href', ''):
                        team_link = link.get('href')
                        break

            if not team_link:
                return {}

            # Get team page
            team_url = f"https://fbref.com{team_link}"
            response = self._fetch_with_retry(team_url, max_retries=3, timeout=15)
            if not response:
                return {}

            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for "Scores & Fixtures" table which has xG data
            fixtures_table = None
            for table in soup.find_all('table'):
                if 'scores' in table.get('id', '').lower() or 'fixtures' in table.get('id', '').lower():
                    fixtures_table = table
                    break

            if not fixtures_table:
                return {}

            # Extract xG data from recent matches
            matches = []
            rows = fixtures_table.find_all('tr')

            for row in rows:
                cells = row.find_all('td')
                if len(cells) < 10:
                    continue

                try:
                    # Extract match data
                    match_data = {}

                    for cell in cells:
                        stat_type = cell.get('data-stat', '')

                        if stat_type == 'venue':
                            venue = cell.text.strip()
                            match_data['h_a'] = 'h' if venue == 'Home' else 'a'
                        elif stat_type == 'xg_for':
                            xg_text = cell.text.strip()
                            match_data['xG'] = float(xg_text) if xg_text and xg_text != '' else 0
                        elif stat_type == 'xg_against':
                            xga_text = cell.text.strip()
                            match_data['xGA'] = float(xga_text) if xga_text and xga_text != '' else 0
                        elif stat_type == 'goals_for':
                            goals_text = cell.text.strip()
                            match_data['scored'] = int(goals_text) if goals_text and goals_text != '' else 0
                        elif stat_type == 'goals_against':
                            goals_against_text = cell.text.strip()
                            match_data['missed'] = int(goals_against_text) if goals_against_text and goals_against_text != '' else 0

                    # Only add if we have xG data
                    if 'xG' in match_data and 'xGA' in match_data:
                        matches.append(match_data)

                except Exception as e:
                    continue

            if not matches:
                return {}

            # Process the data using same method as Understat
            processed_data = self._process_understat_data(matches[-10:])  # Last 10 matches

            # Validate data before returning
            if self._validate_xg_data(processed_data, team_name):
                return processed_data
            else:
                return {}

        except Exception as e:
            print(f"  Error scraping FBref for {team_name}: {e}")
            return {}


    def _validate_xg_data(self, data: Dict, team_name: str = "Unknown") -> bool:
        """
        Validate that xG data is realistic and complete

        Args:
            data: Dictionary with team xG data
            team_name: Team name for error reporting

        Returns:
            True if data is valid, False otherwise
        """
        if not data:
            return False

        # Check required fields exist
        has_xg = 'avg_xg' in data or 'avg_xg_home' in data or 'avg_xg_away' in data
        has_xga = 'avg_xga' in data or 'avg_xga_home' in data or 'avg_xga_away' in data

        if not (has_xg and has_xga):
            print(f"  ⚠️  Validation failed for {team_name}: Missing xG or xGA fields")
            return False

        # Validate xG values are realistic (between 0 and 5 goals per match)
        for key, value in data.items():
            if 'avg_xg' in key:  # Covers avg_xg, avg_xg_home, avg_xg_away, avg_xga, etc.
                try:
                    val = float(value)
                    if val < 0 or val > 5.0:
                        print(f"  ⚠️  Validation failed for {team_name}: {key}={val} is unrealistic (must be 0-5)")
                        return False
                    if val == 0:
                        print(f"  ⚠️  Validation warning for {team_name}: {key}=0 (suspicious but allowed)")
                except (TypeError, ValueError):
                    print(f"  ⚠️  Validation failed for {team_name}: {key}={value} is not a number")
                    return False

        return True

    def _process_understat_data(self, data: List[Dict]) -> Dict:
        """Process raw Understat data to calculate overall AND home/away specific metrics"""
        if not data:
            return {}

        # Get last 10 matches for recent form
        recent_matches = data[-10:] if len(data) >= 10 else data

        # Separate home and away matches
        home_matches = [m for m in recent_matches if m.get('h_a') == 'h']
        away_matches = [m for m in recent_matches if m.get('h_a') == 'a']

        # Overall stats
        total_xg = sum(float(match.get('xG', 0)) for match in recent_matches)
        total_xga = sum(float(match.get('xGA', 0)) for match in recent_matches)
        total_goals = sum(int(match.get('scored', 0)) for match in recent_matches)
        total_conceded = sum(int(match.get('missed', 0)) for match in recent_matches)
        num_matches = len(recent_matches)

        result = {
            'avg_xg': round(total_xg / num_matches, 2) if num_matches > 0 else 0,
            'avg_xga': round(total_xga / num_matches, 2) if num_matches > 0 else 0,
            'avg_goals_scored': round(total_goals / num_matches, 2) if num_matches > 0 else 0,
            'avg_goals_conceded': round(total_conceded / num_matches, 2) if num_matches > 0 else 0,
            'total_matches': num_matches,
            'over_25_count': sum(1 for m in recent_matches if int(m.get('scored', 0)) + int(m.get('missed', 0)) > 2.5),
        }

        # Home-specific stats
        if home_matches:
            home_xg = sum(float(m.get('xG', 0)) for m in home_matches)
            home_xga = sum(float(m.get('xGA', 0)) for m in home_matches)
            home_count = len(home_matches)

            result['avg_xg_home'] = round(home_xg / home_count, 2)
            result['avg_xga_home'] = round(home_xga / home_count, 2)
            result['home_matches'] = home_count

        # Away-specific stats
        if away_matches:
            away_xg = sum(float(m.get('xG', 0)) for m in away_matches)
            away_xga = sum(float(m.get('xGA', 0)) for m in away_matches)
            away_count = len(away_matches)

            result['avg_xg_away'] = round(away_xg / away_count, 2)
            result['avg_xga_away'] = round(away_xga / away_count, 2)
            result['away_matches'] = away_count

        return result

    def normalize_team_name(self, team_name: str) -> str:
        """
        Normalize team names for Understat compatibility across Top 5 leagues
        """
        # Comprehensive team name mappings for Understat (Top 5 European leagues)
        team_mapping = {
            # PREMIER LEAGUE (England)
            'Brighton & Hove Albion': 'Brighton',
            'Brighton and Hove Albion': 'Brighton',
            'Manchester Utd': 'Manchester_United',
            'Manchester United': 'Manchester_United',
            'Man United': 'Manchester_United',
            'Man Utd': 'Manchester_United',
            'Manchester City': 'Manchester_City',
            'Man City': 'Manchester_City',
            'Newcastle Utd': 'Newcastle_United',
            'Newcastle United': 'Newcastle_United',
            'Tottenham': 'Tottenham',
            'Spurs': 'Tottenham',
            'West Ham': 'West_Ham',
            'West Ham United': 'West_Ham',
            'Nott\'ham Forest': 'Nottingham_Forest',
            'Nottingham Forest': 'Nottingham_Forest',
            'Wolves': 'Wolverhampton_Wanderers',
            'Wolverhampton': 'Wolverhampton_Wanderers',
            'Leicester City': 'Leicester',

            # LA LIGA (Spain)
            'Athletic Club': 'Athletic_Bilbao',
            'Ath Bilbao': 'Athletic_Bilbao',
            'Atlético Madrid': 'Atletico_Madrid',
            'Atletico Madrid': 'Atletico_Madrid',
            'Atleti': 'Atletico_Madrid',
            'Celta Vigo': 'Celta',
            'Deportivo Alavés': 'Alaves',
            'Deportivo Alaves': 'Alaves',
            'Rayo': 'Rayo_Vallecano',
            'Real Betis': 'Betis',
            'Real Sociedad': 'Real_Sociedad',
            'UD Las Palmas': 'Las_Palmas',

            # SERIE A (Italy)
            'AC Milan': 'Milan',
            'Inter Milan': 'Inter',
            'Inter': 'Inter',
            'Internazionale': 'Inter',
            'AS Roma': 'Roma',
            'Hellas Verona': 'Verona',
            'Verona': 'Verona',

            # BUNDESLIGA (Germany)
            'FC Köln': 'Koln',
            'FC Koln': 'Koln',
            '1. FC Köln': 'Koln',
            'Eintracht Frankfurt': 'Eintracht_Frankfurt',
            'RB Leipzig': 'RasenBallsport_Leipzig',
            'Bayern Munich': 'Bayern_Munich',
            'Bayern München': 'Bayern_Munich',
            'Bayer Leverkusen': 'Bayer_Leverkusen',
            'Bayer 04 Leverkusen': 'Bayer_Leverkusen',
            'Borussia Dortmund': 'Borussia_Dortmund',
            'Dortmund': 'Borussia_Dortmund',
            'BVB': 'Borussia_Dortmund',
            'Borussia M\'gladbach': 'Borussia_Monchengladbach',
            'Borussia Mönchengladbach': 'Borussia_Monchengladbach',
            'M\'gladbach': 'Borussia_Monchengladbach',
            'VfL Wolfsburg': 'Wolfsburg',
            'VfB Stuttgart': 'Stuttgart',

            # LIGUE 1 (France)
            'Paris S-G': 'Paris_Saint_Germain',
            'Paris Saint Germain': 'Paris_Saint_Germain',
            'Paris Saint-Germain': 'Paris_Saint_Germain',
            'PSG': 'Paris_Saint_Germain',
            'Olympique Marseille': 'Marseille',
            'Olympique Lyonnais': 'Lyon',
            'AS Monaco': 'Monaco',
            'AS Saint-Étienne': 'Saint-Etienne',
            'AS Saint-Etienne': 'Saint-Etienne',
        }

        # Check direct mapping
        if team_name in team_mapping:
            return team_mapping[team_name]

        # Default: replace spaces with underscores and remove special characters
        normalized = team_name.replace(' ', '_')
        # Remove common special characters that cause issues
        normalized = normalized.replace('\'', '').replace('.', '').replace('-', '_')
        return normalized

    def _is_within_24_hours(self, date_str: str) -> bool:
        """
        Check if a date string is within the next 24 hours

        Args:
            date_str: Date string from FBref (e.g., "2025-11-05", "2025-11-05 15:00")

        Returns:
            True if match is within next 24 hours
        """
        try:
            now = datetime.now()
            next_24h = now + timedelta(hours=24)

            # Try parsing with time
            try:
                match_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            except:
                # Try parsing without time (assume noon)
                try:
                    match_date = datetime.strptime(date_str, "%Y-%m-%d")
                    match_date = match_date.replace(hour=12)  # Assume noon
                except:
                    return False

            # Check if match is in the future and within 24 hours
            return now <= match_date <= next_24h

        except Exception as e:
            return False

    def scrape_league_fixtures(self, league_name: str, hours_ahead: int = 24) -> List[Dict]:
        """
        Scrape upcoming fixtures for any league from FBref (within specified hours)

        Args:
            league_name: Name of league from LEAGUES dict
            hours_ahead: Only get matches within this many hours (default: 24)

        Returns:
            List of upcoming fixtures with team names
        """
        try:
            league_info = self.LEAGUES.get(league_name)
            if not league_info:
                print(f"❌ League '{league_name}' not found in database")
                return []

            fbref_id = league_info['fbref_id']
            fbref_name = league_info['fbref_name']

            # Construct FBref URL
            url = f"https://fbref.com/en/comps/{fbref_id}/schedule/{fbref_name}-Scores-and-Fixtures"

            print(f"\n🔍 Fetching {league_name} fixtures from FBref...")

            response = self._fetch_with_retry(url, max_retries=3, timeout=15)
            if not response:
                print(f"⚠️  Could not fetch fixtures (network error or bad status)")
                return []

            soup = BeautifulSoup(response.content, 'html.parser')
            fixtures = []
            now = datetime.now()
            cutoff_time = now + timedelta(hours=hours_ahead)

            # Find the fixtures table - try multiple strategies
            table = soup.find('table', class_='stats_table')
            if not table:
                # Try by ID pattern
                tables = soup.find_all('table')
                for t in tables:
                    if 'sched' in t.get('id', ''):
                        table = t
                        break

            if not table:
                print("⚠️  Could not find fixtures table")
                return []

            rows = table.find_all('tr')

            for row in rows:
                # Skip header rows
                if row.find('th', {'scope': 'col'}):
                    continue

                cells = row.find_all('td')
                if len(cells) < 5:
                    continue

                # Extract data
                try:
                    # FBref uses <td> for dates, not <th>
                    date_cell = row.find('td', {'data-stat': 'date'})
                    if not date_cell:
                        continue

                    date_str = date_cell.text.strip()
                    if not date_str:  # Skip rows without dates
                        continue

                    # Get time if available (FBref uses 'start_time' not 'time')
                    time_cell = row.find('td', {'data-stat': 'start_time'})
                    time_str = time_cell.text.strip() if time_cell else ""

                    # Combine date and time
                    full_date_str = f"{date_str} {time_str}".strip() if time_str else date_str

                    # Find home team, score, away team (positions vary by league)
                    home_team = None
                    away_team = None
                    score = ''

                    for cell in cells:
                        stat_type = cell.get('data-stat', '')
                        if stat_type == 'home_team':
                            # Remove country codes (e.g., "eng Arsenal" or "Juventus it")
                            home_team = cell.text.strip()
                            # Remove 2-3 letter lowercase country codes (before or after team name)
                            home_team = re.sub(r'\b[a-z]{2,3}\b\s*', '', home_team).strip()
                        elif stat_type == 'away_team':
                            # Remove country codes (e.g., "de Bayern Munich" or "Monaco fr")
                            away_team = cell.text.strip()
                            # Remove 2-3 letter lowercase country codes (before or after team name)
                            away_team = re.sub(r'\b[a-z]{2,3}\b\s*', '', away_team).strip()
                        elif stat_type == 'score':
                            score = cell.text.strip()

                    # Only get upcoming matches (no score yet)
                    if not home_team or not away_team:
                        continue

                    if score and score != '':
                        # Match already played
                        continue

                    # Check if match is within the time window
                    if not self._is_within_24_hours(full_date_str):
                        continue

                    fixtures.append({
                        'date': full_date_str,
                        'home_team': home_team,
                        'away_team': away_team,
                        'league': league_name
                    })

                except Exception as e:
                    continue

            if fixtures:
                print(f"✅ Found {len(fixtures)} fixtures in next {hours_ahead} hours")
            else:
                print(f"⚠️  No fixtures found in next {hours_ahead} hours")

            return fixtures

        except Exception as e:
            print(f"❌ Error scraping fixtures: {e}")
            return []

    def scrape_fbref_fixtures(self, league_url: str) -> List[Dict]:
        """
        Scrape upcoming fixtures from FBref

        Args:
            league_url: FBref league URL

        Returns:
            List of upcoming fixtures
        """
        try:
            response = self._fetch_with_retry(league_url, max_retries=3, timeout=10)
            if not response:
                print("Could not fetch fixtures")
                return []
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
        4. Uses venue-specific stats (home xG/xGA vs away xG/xGA)
        5. Provides statistical confidence intervals

        Args:
            home_data: Home team's HOME venue statistics (avg_xg_home, avg_xga_home)
            away_data: Away team's AWAY venue statistics (avg_xg_away, avg_xga_away)

        Returns:
            Detailed analysis with probabilities
        """
        if not home_data or not away_data:
            return {'prediction': 'INSUFFICIENT_DATA', 'confidence': 0, 'reasoning': 'Missing team data'}

        # Extract venue-specific metrics (home team at home, away team away)
        # Note: If venue-specific data not available, falls back to overall stats
        home_attack = home_data.get('avg_xg_home', home_data.get('avg_xg', 0))
        home_defense = home_data.get('avg_xga_home', home_data.get('avg_xga', 0))
        away_attack = away_data.get('avg_xg_away', away_data.get('avg_xg', 0))
        away_defense = away_data.get('avg_xga_away', away_data.get('avg_xga', 0))

        # Track if using venue-specific data
        using_venue_specific = ('avg_xg_home' in home_data and 'avg_xg_away' in away_data)

        # Method 1: Opponent-adjusted expected goals
        # Home team expected goals = (Home attack + Away defensive weakness) / 2
        # This balances the team's attacking ability with opponent's defensive vulnerability
        home_expected_v1 = (home_attack + away_defense) / 2

        # Away team expected goals = (Away attack + Home defensive weakness) / 2
        away_expected_v1 = (away_attack + home_defense) / 2

        # Method 2: Multiplicative adjustment (more sophisticated)
        # Adjust team's attack based on opponent's defense relative to league average
        # NOTE: These averages are ONLY used for ratio calculations (attack/defense strength),
        # NOT as fallback data. We skip games if no real team data is available!
        league_avg_xg = 1.35  # Typical league average xG per match (for ratio calculation only)
        league_avg_xga = 1.35  # Typical league average xGA per match (for ratio calculation only)

        # Calculate attack/defense strength ratios relative to average
        # Example: If team has 2.0 xG and average is 1.35, strength = 2.0/1.35 = 1.48 (48% above average)
        home_attack_strength = home_attack / league_avg_xg if league_avg_xg > 0 else 1.0
        away_defense_ratio = away_defense / league_avg_xga if league_avg_xga > 0 else 1.0
        home_expected_v2 = league_avg_xg * home_attack_strength * away_defense_ratio

        away_attack_strength = away_attack / league_avg_xg if league_avg_xg > 0 else 1.0
        home_defense_ratio = home_defense / league_avg_xga if league_avg_xga > 0 else 1.0
        away_expected_v2 = league_avg_xg * away_attack_strength * home_defense_ratio

        # Weighted combination of both methods (60% method 1, 40% method 2)
        home_lambda = 0.6 * home_expected_v1 + 0.4 * home_expected_v2
        away_lambda = 0.6 * away_expected_v1 + 0.4 * away_expected_v2

        # Only add generic home advantage if NOT using venue-specific stats
        # (venue-specific stats already include home advantage)
        if not using_venue_specific:
            home_advantage = 0.25
            home_lambda += home_advantage
        else:
            home_advantage = 0.0  # No adjustment needed

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

        venue_note = " (VENUE-SPECIFIC)" if using_venue_specific else " (overall + home advantage)"
        reasoning.append(f"TEAM METRICS{venue_note}:")
        reasoning.append(f"  Home team AT HOME - Attack: {home_attack:.2f} xG, Defense: {home_defense:.2f} xGA")
        reasoning.append(f"  Away team AWAY - Attack: {away_attack:.2f} xG, Defense: {away_defense:.2f} xGA")
        if not using_venue_specific:
            reasoning.append(f"  ⚠️ Using overall stats + {home_advantage:.2f} home advantage adjustment")
            reasoning.append(f"  💡 TIP: Use venue-specific stats for better accuracy!")
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
            elif analysis['prediction'] == 'SKIPPED':
                print("❌ GAME SKIPPED - No real data available")
                print(f"💡 Reason: {analysis.get('reasoning', 'Could not fetch real xG data from any source')}")
                print(f"   Sources tried: Understat → FBref")
                print(f"   ℹ️  This game was skipped to avoid using fictitious data")
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
        skipped_count = sum(1 for a in analyses if a.get('prediction', '') == 'SKIPPED')

        print(f"Total Fixtures Found: {len(fixtures)}")
        print(f"Successfully Analyzed: {len(fixtures) - skipped_count}")
        print(f"OVER 2.5 predictions: {over_count}")
        print(f"UNDER 2.5 predictions: {under_count}")
        print(f"Marginal predictions: {marginal_count}")
        print(f"Skipped (no real data): {skipped_count}")

        # Best bets (high confidence) - exclude SKIPPED games
        high_conf = [a for a in analyses if a.get('confidence', 0) >= 70 and a.get('prediction', '') != 'SKIPPED']
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

    def auto_scrape_and_analyze(self, league_names: List[str]) -> None:
        """
        Automatically scrape upcoming fixtures and analyze them for multiple leagues

        Args:
            league_names: List of league names to analyze
        """
        print("\n" + "="*80)
        print("🤖 AUTOMATIC MULTI-LEAGUE SCRAPING MODE")
        print("="*80)
        print(f"⏰ Filtering: Only matches in the NEXT 24 HOURS")
        print(f"📋 Analyzing {len(league_names)} league(s):")
        print(f"\n🔍 DATA SOURCE STRATEGY (No Fictitious Data!):")
        print(f"  1️⃣  Try Understat (Top 5 leagues - best quality)")
        print(f"  2️⃣  Try FBref (all leagues - team-specific xG)")
        print(f"  ❌  If both fail → SKIP GAME (no fake data!)")
        print()
        for league in league_names:
            understat_code = self.LEAGUES.get(league, {}).get('understat')
            if understat_code:
                print(f"  ✅ {league} (Understat priority)")
            else:
                print(f"  🔍 {league} (FBref)")
        print("="*80 + "\n")

        all_fixtures = []
        all_analyses = []
        total_successful = 0

        for league_name in league_names:
            print("\n" + "="*80)
            print(f"📊 {league_name.upper()}")
            print("="*80)

            league_info = self.LEAGUES.get(league_name)
            if not league_info:
                print(f"❌ League not found in database")
                continue

            # Step 1: Get upcoming fixtures
            fixtures = self.scrape_league_fixtures(league_name)

            if not fixtures:
                print(f"\n⚠️  No fixtures found for {league_name}")
                continue

            print(f"\n📋 Analyzing {len(fixtures)} upcoming matches...\n")

            # Step 2: For each fixture, scrape team data and analyze
            analyses = []
            successful = 0

            understat_code = league_info.get('understat')

            for i, fixture in enumerate(fixtures, 1):
                home_team = fixture['home_team']
                away_team = fixture['away_team']

                print(f"\n[{i}/{len(fixtures)}] {home_team} vs {away_team}")
                print("-" * 60)

                # 3-TIER APPROACH: Try Understat → FBref → SKIP (NO FICTITIOUS DATA)
                home_data = None
                away_data = None
                home_data_source = None
                away_data_source = None

                # Step 1: Try Understat (if league supported)
                if understat_code:
                    home_normalized = self.normalize_team_name(home_team)
                    away_normalized = self.normalize_team_name(away_team)

                    print(f"🏠 Trying Understat for {home_team}...", end=' ')
                    home_data = self.scrape_understat_team_data(home_normalized, understat_code)
                    if home_data:
                        print(f"✅")
                        home_data_source = 'Understat'
                    else:
                        print(f"❌")
                    time.sleep(1)

                    print(f"🛫 Trying Understat for {away_team}...", end=' ')
                    away_data = self.scrape_understat_team_data(away_normalized, understat_code)
                    if away_data:
                        print(f"✅")
                        away_data_source = 'Understat'
                    else:
                        print(f"❌")
                    time.sleep(1)

                # Step 2: Try FBref (if Understat failed)
                if not home_data:
                    print(f"🏠 Trying FBref for {home_team}...", end=' ')
                    home_data = self.scrape_fbref_team_data(home_team, league_name)
                    if home_data:
                        print(f"✅")
                        home_data_source = 'FBref'
                    else:
                        print(f"❌")
                    time.sleep(1)

                if not away_data:
                    print(f"🛫 Trying FBref for {away_team}...", end=' ')
                    away_data = self.scrape_fbref_team_data(away_team, league_name)
                    if away_data:
                        print(f"✅")
                        away_data_source = 'FBref'
                    else:
                        print(f"❌")
                    time.sleep(1)

                # Step 3: If BOTH sources failed, SKIP this game (no fictitious data!)
                if not home_data or not away_data:
                    print(f"  ❌ SKIPPING GAME - No real data available for both teams")
                    if not home_data:
                        print(f"     Missing: {home_team}")
                    if not away_data:
                        print(f"     Missing: {away_team}")

                    # Add to analyses as skipped
                    analyses.append({
                        'prediction': 'SKIPPED',
                        'confidence': 0,
                        'reasoning': f'No real xG data available (tried Understat, FBref)'
                    })
                    continue

                # Display scraped stats with data source
                if 'avg_xg_home' in home_data:
                    print(f"  📊 {home_team} at home: {home_data['avg_xg_home']} xG, {home_data['avg_xga_home']} xGA ({home_data_source})")
                else:
                    print(f"  📊 {home_team} overall: {home_data['avg_xg']} xG, {home_data['avg_xga']} xGA ({home_data_source})")

                if 'avg_xg_away' in away_data:
                    print(f"  📊 {away_team} away: {away_data['avg_xg_away']} xG, {away_data['avg_xga_away']} xGA ({away_data_source})")
                else:
                    print(f"  📊 {away_team} overall: {away_data['avg_xg']} xG, {away_data['avg_xga']} xGA ({away_data_source})")

                # Analyze the match
                print(f"  🔮 Analyzing...")
                analysis = self.analyze_over_under_advanced(home_data, away_data)
                analyses.append(analysis)
                successful += 1

                print(f"  📊 Prediction: {analysis['prediction']} ({analysis['confidence']}% confidence)")

            # Store results for this league
            all_fixtures.extend(fixtures)
            all_analyses.extend(analyses)
            total_successful += successful

            # Generate league-specific report
            if successful > 0:
                print("\n" + "="*80)
                print(f"✅ {league_name}: Successfully analyzed {successful}/{len(fixtures)} matches")
                print("="*80 + "\n")

        # Step 3: Generate comprehensive report for all leagues
        if total_successful > 0:
            print("\n" + "="*80)
            print(f"📊 OVERALL SUMMARY: {total_successful} matches analyzed across {len(league_names)} league(s)")
            print("="*80 + "\n")

            self.generate_report(all_fixtures, all_analyses)

            # Ask to export
            export = input("\nExport results to JSON? (y/n): ").lower()
            if export == 'y':
                filename = f"predictions_multi_league_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    json.dump({
                        'generated': datetime.now().isoformat(),
                        'leagues': league_names,
                        'fixtures': all_fixtures,
                        'analyses': all_analyses
                    }, f, indent=2)
                print(f"✅ Results exported to {filename}")
        else:
            print("\n❌ No matches were successfully analyzed.")


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

    print("\nChoose mode:")
    print("1. 🤖 AUTO-SCRAPE - Automatically scrape & analyze upcoming matches")
    print("2. ✍️  Manual entry - Enter team stats directly")
    print("3. 📊 Demo mode - See sample predictions")

    mode = input("\nEnter choice (1-3): ").strip() or "1"

    if mode == "1":
        # AUTO-SCRAPE MODE - Main feature!
        print("\n" + "="*80)
        print("SELECT LEAGUES TO ANALYZE")
        print("="*80)

        # Group leagues by category
        print("\n🌍 INTERNATIONAL TOURNAMENTS:")
        print("  1. FIFA World Cup")
        print("  2. UEFA Euro")
        print("  3. Copa America")
        print("  4. Africa Cup of Nations")
        print("  5. UEFA Nations League")

        print("\n🏆 EUROPEAN CLUB COMPETITIONS:")
        print("  6. UEFA Champions League")
        print("  7. UEFA Europa League")
        print("  8. UEFA Europa Conference League")

        print("\n⭐ TOP 5 EUROPEAN LEAGUES (Full xG data):")
        print("  9. Premier League (England)")
        print(" 10. La Liga (Spain)")
        print(" 11. Serie A (Italy)")
        print(" 12. Bundesliga (Germany)")
        print(" 13. Ligue 1 (France)")

        print("\n🏴󠁧󠁢󠁥󠁮󠁧󠁿 ENGLISH FOOTBALL:")
        print(" 14. EFL Championship")
        print(" 15. EFL League One")
        print(" 16. EFL League Two")
        print(" 17. FA Cup")

        print("\n🌎 SOUTH AMERICAN FOOTBALL:")
        print(" 18. Copa Libertadores")
        print(" 19. Copa Sudamericana")
        print(" 20. Brasileirao Serie A")
        print(" 21. Brasileirao Serie B")
        print(" 22. Copa do Brasil")
        print(" 23. Liga Profesional Argentina")
        print(" 24. Copa de la Liga Argentina")
        print(" 25. Copa Argentina")
        print(" 26. Primera Division Chile")
        print(" 27. Liga Pro Ecuador")
        print(" 28. Categoria Primera A Colombia")
        print(" 29. Liga MX (Mexico)")

        print("\n💡 TIP: Enter 'all' for all leagues, or numbers separated by commas (e.g., 9,10,11)")
        print("💡 Or press Enter for recommended leagues (Top 5 European)")

        selection = input("\nYour selection: ").strip().lower()

        # Map numbers to league names
        league_map = {
            1: 'FIFA World Cup',
            2: 'UEFA Euro',
            3: 'Copa America',
            4: 'Africa Cup of Nations',
            5: 'UEFA Nations League',
            6: 'UEFA Champions League',
            7: 'UEFA Europa League',
            8: 'UEFA Europa Conference League',
            9: 'Premier League',
            10: 'La Liga',
            11: 'Serie A',
            12: 'Bundesliga',
            13: 'Ligue 1',
            14: 'EFL Championship',
            15: 'EFL League One',
            16: 'EFL League Two',
            17: 'FA Cup',
            18: 'Copa Libertadores',
            19: 'Copa Sudamericana',
            20: 'Brasileirao Serie A',
            21: 'Brasileirao Serie B',
            22: 'Copa do Brasil',
            23: 'Liga Profesional Argentina',
            24: 'Copa de la Liga Argentina',
            25: 'Copa Argentina',
            26: 'Primera Division Chile',
            27: 'Liga Pro Ecuador',
            28: 'Categoria Primera A Colombia',
            29: 'Liga MX',
        }

        selected_leagues = []

        if selection == 'all':
            selected_leagues = list(league_map.values())
        elif not selection:
            # Default: Top 5 European leagues
            selected_leagues = ['Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1']
        else:
            # Parse comma-separated numbers
            try:
                numbers = [int(n.strip()) for n in selection.split(',')]
                selected_leagues = [league_map[n] for n in numbers if n in league_map]
            except:
                print("❌ Invalid selection. Using Top 5 European leagues as default.")
                selected_leagues = ['Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1']

        if not selected_leagues:
            print("❌ No leagues selected. Exiting.")
            return

        scraper.auto_scrape_and_analyze(league_names=selected_leagues)

    elif mode == "2":
        # Manual entry mode
        fixtures = scraper.get_manual_fixtures()

        if not fixtures:
            print("No fixtures entered. Exiting.")
            return

        analyses = []

        for fixture in fixtures:
            print(f"\n--- Analyzing: {fixture['home_team']} vs {fixture['away_team']} ---")
            print("\n💡 For best accuracy, enter VENUE-SPECIFIC stats:")
            print("   - Home team: stats from HOME matches only")
            print("   - Away team: stats from AWAY matches only")
            print()

            use_venue = input("Use venue-specific stats? (y/n, default=y): ").lower() or "y"

            if use_venue == "y":
                print(f"\nEnter {fixture['home_team']} stats AT HOME (last 10 HOME matches):")
                home_xg = float(input("  xG at home: ") or "1.7")
                home_xga = float(input("  xGA at home: ") or "1.0")
                home_over = int(input("  Over 2.5 in home matches (out of 10): ") or "6")

                print(f"\nEnter {fixture['away_team']} stats AWAY (last 10 AWAY matches):")
                away_xg = float(input("  xG away: ") or "1.3")
                away_xga = float(input("  xGA away: ") or "1.4")
                away_over = int(input("  Over 2.5 in away matches (out of 10): ") or "4")

                home_data = {
                    'avg_xg_home': home_xg,
                    'avg_xga_home': home_xga,
                    'total_matches': 10,
                    'over_25_count': home_over
                }

                away_data = {
                    'avg_xg_away': away_xg,
                    'avg_xga_away': away_xga,
                    'total_matches': 10,
                    'over_25_count': away_over
                }
            else:
                print(f"\nEnter {fixture['home_team']} overall stats (last 10 matches):")
                home_xg = float(input("  Average xG: ") or "1.5")
                home_xga = float(input("  Average xGA: ") or "1.2")
                home_over = int(input("  Number of over 2.5 matches (out of 10): ") or "5")

                print(f"\nEnter {fixture['away_team']} overall stats (last 10 matches):")
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

    elif mode == "3":
        # Demo mode with venue-specific sample data
        print("\n📊 Demo mode: Using realistic venue-specific data")
        print("   (Notice the difference between home/away performance)\n")

        fixtures = [
            {'home_team': 'Manchester City', 'away_team': 'Liverpool', 'date': '2024-11-10'},
            {'home_team': 'Bournemouth', 'away_team': 'Brighton', 'date': '2024-11-10'},
        ]

        # Fixture 1: Man City (home) vs Liverpool (away)
        # Man City at home - dominant attack, strong defense
        home_data_1 = {
            'avg_xg_home': 2.5,   # City creates more chances at home
            'avg_xga_home': 0.7,  # Very strong defense at home
            'total_matches': 10,
            'over_25_count': 7
        }

        # Liverpool away - good attack, but weaker defense away
        away_data_1 = {
            'avg_xg_away': 1.8,   # Still good away, but less than at home (2.3)
            'avg_xga_away': 1.2,  # Concede more away than at home (0.9)
            'total_matches': 10,
            'over_25_count': 6
        }

        # Fixture 2: Bournemouth (home) vs Brighton (away)
        # Bournemouth at home - decent attack, vulnerable defense
        home_data_2 = {
            'avg_xg_home': 1.6,   # Better at home than away (1.2)
            'avg_xga_home': 1.4,  # Weak defense at home
            'total_matches': 10,
            'over_25_count': 6
        }

        # Brighton away - moderate attack, okay defense
        away_data_2 = {
            'avg_xg_away': 1.3,   # Weaker away than at home (1.7)
            'avg_xga_away': 1.3,  # Similar defense away
            'total_matches': 10,
            'over_25_count': 5
        }

        # Use advanced Poisson-based analysis
        analyses = [
            scraper.analyze_over_under_advanced(home_data_1, away_data_1),
            scraper.analyze_over_under_advanced(home_data_2, away_data_2)
        ]

        scraper.generate_report(fixtures, analyses)


if __name__ == "__main__":
    main()
