#!/usr/bin/env python3
"""
Comprehensive Fixture Source Tester
Tests multiple football data sources and logs which ones work
"""
import requests
import json
import time
from datetime import datetime

class FixtureTester:
    def __init__(self):
        self.results = []
        self.successful_sources = []

    def test_source(self, name, url, check_func=None, headers=None):
        """Test a single source"""
        print(f"\n{'='*60}")
        print(f"Testing: {name}")
        print(f"URL: {url[:80]}...")

        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }

        if headers:
            default_headers.update(headers)

        try:
            response = requests.get(url, headers=default_headers, timeout=10)

            result = {
                'name': name,
                'url': url,
                'status': response.status_code,
                'success': False,
                'content_type': response.headers.get('content-type', 'unknown'),
                'size': len(response.content),
                'timestamp': datetime.now().isoformat()
            }

            if response.status_code == 200:
                print(f"✅ SUCCESS! Status: {response.status_code}")
                print(f"   Content-Type: {result['content_type']}")
                print(f"   Size: {result['size']} bytes")

                # Try to extract fixture data
                if check_func:
                    fixtures = check_func(response)
                    if fixtures:
                        result['success'] = True
                        result['fixtures_found'] = len(fixtures)
                        result['sample_data'] = fixtures[:2]  # First 2 fixtures
                        print(f"   🎯 Found {len(fixtures)} fixtures!")
                        self.successful_sources.append(result)
                else:
                    result['success'] = True
                    result['sample_preview'] = response.text[:500]
                    print(f"   Preview: {response.text[:200]}")
                    self.successful_sources.append(result)
            else:
                print(f"❌ FAILED: Status {response.status_code}")

            self.results.append(result)
            return result

        except Exception as e:
            print(f"❌ ERROR: {e}")
            result = {
                'name': name,
                'url': url,
                'status': 'error',
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.results.append(result)
            return result

        finally:
            time.sleep(0.5)  # Be nice to servers

    def check_json_fixtures(self, response):
        """Check if response contains JSON fixture data"""
        try:
            data = response.json()

            # Try different JSON structures
            fixtures = []

            # Structure 1: {matches: [...]}
            if 'matches' in data:
                fixtures = data['matches']
            # Structure 2: {events: [...]}
            elif 'events' in data:
                fixtures = data['events']
            # Structure 3: {response: [...]}
            elif 'response' in data:
                fixtures = data['response']
            # Structure 4: Direct array
            elif isinstance(data, list):
                fixtures = data

            return fixtures if fixtures else None
        except:
            return None

    def check_csv_fixtures(self, response):
        """Check if response contains CSV fixture data"""
        try:
            lines = response.text.split('\n')
            if len(lines) > 1:  # Has header + data
                return [{'csv_row': line} for line in lines[1:6]]  # First 5 rows
        except:
            return None

    def run_all_tests(self):
        """Run comprehensive tests on all sources"""

        print("="*60)
        print("COMPREHENSIVE FIXTURE SOURCE TEST")
        print("="*60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # GitHub Sources (Known to work)
        print("\n" + "="*60)
        print("CATEGORY: GitHub Raw Files")
        print("="*60)

        self.test_source(
            "OpenFootball - Premier League",
            "https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/en.1.json",
            self.check_json_fixtures
        )

        self.test_source(
            "OpenFootball - La Liga",
            "https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/es.1.json",
            self.check_json_fixtures
        )

        # API Sources
        print("\n" + "="*60)
        print("CATEGORY: Public APIs")
        print("="*60)

        self.test_source(
            "ESPN API - Premier League",
            "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard",
            self.check_json_fixtures
        )

        self.test_source(
            "TheSportsDB - Premier League",
            "https://www.thesportsdb.com/api/v1/json/3/eventsnextleague.php?id=4328",
            self.check_json_fixtures
        )

        self.test_source(
            "Football-Data.org",
            "https://api.football-data.org/v4/competitions/PL/matches",
            self.check_json_fixtures,
            headers={'X-Auth-Token': '9373f6cc6ce54a348eb1e5cfd2a4de65'}
        )

        self.test_source(
            "ScoreBat Video API",
            "https://www.scorebat.com/video-api/v3/feed/",
            self.check_json_fixtures
        )

        # CSV Sources
        print("\n" + "="*60)
        print("CATEGORY: CSV Data Sources")
        print("="*60)

        self.test_source(
            "FiveThirtyEight Soccer Data",
            "https://projects.fivethirtyeight.com/soccer-api/club/spi_matches.csv",
            self.check_csv_fixtures
        )

        # Website Scraping
        print("\n" + "="*60)
        print("CATEGORY: Website Scraping")
        print("="*60)

        self.test_source(
            "BBC Sport Football",
            "https://www.bbc.com/sport/football/scores-fixtures"
        )

        self.test_source(
            "LiveScore",
            "https://www.livescore.com/en/football/"
        )

        self.test_source(
            "FBref",
            "https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures"
        )

        self.test_source(
            "Flashscore",
            "https://www.flashscore.com/football/"
        )

        self.test_source(
            "Soccerway",
            "https://www.soccerway.com/"
        )

        self.test_source(
            "Transfermarkt",
            "https://www.transfermarkt.com/"
        )

        self.test_source(
            "OneFootball",
            "https://onefootball.com/en/competition/premier-league-9/fixtures"
        )

        self.test_source(
            "Goal.com",
            "https://www.goal.com/en/premier-league/fixtures"
        )

        self.test_source(
            "365Scores",
            "https://www.365scores.com/en/football"
        )

        self.test_source(
            "Forebet",
            "https://www.forebet.com/en/football-predictions"
        )

        self.test_source(
            "FootyStats",
            "https://footystats.org/england/premier-league/fixtures"
        )

        # Official League Sites
        print("\n" + "="*60)
        print("CATEGORY: Official League Websites")
        print("="*60)

        self.test_source(
            "Premier League Official",
            "https://www.premierleague.com/fixtures"
        )

        self.test_source(
            "UEFA Champions League",
            "https://www.uefa.com/uefachampionsleague/fixtures-results/"
        )

        self.test_source(
            "La Liga Official",
            "https://www.laliga.com/en-GB/laliga-santander/fixtures"
        )

    def save_results(self):
        """Save test results to files"""

        # Save full results as JSON
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        results_file = f"fixture_source_test_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump({
                'test_time': datetime.now().isoformat(),
                'total_tested': len(self.results),
                'successful': len(self.successful_sources),
                'results': self.results,
                'successful_sources': self.successful_sources
            }, f, indent=2)

        print(f"\n💾 Full results saved to: {results_file}")

        # Save summary report
        summary_file = f"fixture_source_summary_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write("="*60 + "\n")
            f.write("FIXTURE SOURCE TEST SUMMARY\n")
            f.write("="*60 + "\n")
            f.write(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Sources Tested: {len(self.results)}\n")
            f.write(f"Successful: {len(self.successful_sources)}\n")
            f.write(f"Failed: {len(self.results) - len(self.successful_sources)}\n")
            f.write("\n" + "="*60 + "\n")
            f.write("SUCCESSFUL SOURCES:\n")
            f.write("="*60 + "\n")

            if self.successful_sources:
                for source in self.successful_sources:
                    f.write(f"\n✅ {source['name']}\n")
                    f.write(f"   URL: {source['url']}\n")
                    f.write(f"   Status: {source['status']}\n")
                    f.write(f"   Content-Type: {source['content_type']}\n")
                    if 'fixtures_found' in source:
                        f.write(f"   Fixtures Found: {source['fixtures_found']}\n")
            else:
                f.write("\nNO SUCCESSFUL SOURCES FOUND\n")

            f.write("\n" + "="*60 + "\n")
            f.write("FAILED SOURCES:\n")
            f.write("="*60 + "\n")

            failed = [r for r in self.results if not r['success']]
            for result in failed:
                f.write(f"\n❌ {result['name']}\n")
                f.write(f"   URL: {result['url']}\n")
                if 'error' in result:
                    f.write(f"   Error: {result['error']}\n")
                else:
                    f.write(f"   Status: {result.get('status', 'unknown')}\n")

        print(f"📄 Summary saved to: {summary_file}")

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Sources Tested: {len(self.results)}")
        print(f"✅ Successful: {len(self.successful_sources)}")
        print(f"❌ Failed: {len(self.results) - len(self.successful_sources)}")

        if self.successful_sources:
            print("\n🎉 WORKING SOURCES:")
            for source in self.successful_sources:
                print(f"  • {source['name']}")
                if 'fixtures_found' in source:
                    print(f"    ({source['fixtures_found']} fixtures found)")
        else:
            print("\n⚠️  NO WORKING SOURCES FOUND")
            print("All sources returned errors or were blocked (403)")

        print("\n" + "="*60)

if __name__ == "__main__":
    tester = FixtureTester()
    tester.run_all_tests()
    tester.print_summary()
    tester.save_results()

    print("\n✅ Testing complete!")
    print("Check the generated files for detailed results.")
