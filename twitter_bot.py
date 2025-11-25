#!/usr/bin/env python3
"""
Twitter Bot - Detects mentions, reads threads, and generates AI responses
Uses Playwright for web scraping (no official X API required)
"""

import os
import json
import time
import asyncio
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path

try:
    from playwright.async_api import async_playwright, Page, Browser
    import anthropic
except ImportError:
    print("❌ Missing dependencies. Install with: pip install playwright anthropic")
    print("   Then run: playwright install chromium")
    exit(1)


@dataclass
class Tweet:
    """Represents a single tweet"""
    tweet_id: str
    author: str
    content: str
    timestamp: str
    is_reply: bool = False
    reply_to: Optional[str] = None


@dataclass
class Thread:
    """Represents a Twitter thread"""
    tweets: List[Tweet]
    root_tweet: Tweet

    def to_context(self) -> str:
        """Convert thread to readable context for AI"""
        context = "=== Twitter Thread Context ===\n\n"
        for i, tweet in enumerate(self.tweets):
            context += f"[{i+1}] @{tweet.author}: {tweet.content}\n\n"
        return context


class TwitterBot:
    """
    Twitter bot that monitors mentions and responds to threads
    Uses Playwright for scraping (no official API needed)
    """

    def __init__(self, config_path: str = "twitter_config.json"):
        """Initialize bot with configuration"""
        self.config = self.load_config(config_path)
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.claude_client = None

        # Track processed tweets to avoid duplicates
        self.processed_tweets = self.load_processed_tweets()

        # Initialize Claude API if key exists
        if self.config.get('claude_api_key'):
            self.claude_client = anthropic.Anthropic(
                api_key=self.config['claude_api_key']
            )

    def load_config(self, config_path: str) -> Dict:
        """Load bot configuration from JSON file"""
        if not Path(config_path).exists():
            print(f"⚠️  Config file not found: {config_path}")
            print("Creating template config file...")

            template = {
                "twitter_username": "your_twitter_username",
                "twitter_password": "your_twitter_password",
                "twitter_email": "your_email@example.com",
                "twitter_handle": "@your_handle",
                "claude_api_key": "sk-ant-...",
                "check_interval_seconds": 60,
                "max_thread_length": 20,
                "response_temperature": 0.7,
                "bot_persona": "You are a helpful AI assistant that provides insightful analysis about football statistics and predictions. Be concise, friendly, and data-driven.",
                "headless": True
            }

            with open(config_path, 'w') as f:
                json.dump(template, f, indent=2)

            print(f"✅ Created template config: {config_path}")
            print("Please edit the config file with your credentials and run again.")
            exit(0)

        with open(config_path, 'r') as f:
            return json.load(f)

    def load_processed_tweets(self) -> set:
        """Load set of already processed tweet IDs"""
        cache_file = Path("processed_tweets.json")
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
                return set(data.get('tweet_ids', []))
        return set()

    def save_processed_tweets(self):
        """Save processed tweet IDs to cache"""
        cache_file = Path("processed_tweets.json")
        with open(cache_file, 'w') as f:
            json.dump({
                'tweet_ids': list(self.processed_tweets),
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)

    async def start(self):
        """Start the bot - initialize browser and login"""
        print("🤖 Starting Twitter Bot...")
        print(f"👤 Username: {self.config['twitter_username']}")
        print(f"🎯 Monitoring mentions of: {self.config['twitter_handle']}")

        async with async_playwright() as p:
            # Launch browser
            self.browser = await p.chromium.launch(
                headless=self.config.get('headless', True)
            )

            # Create context with user agent
            context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            self.page = await context.new_page()

            # Login to Twitter
            if not await self.login():
                print("❌ Failed to login to Twitter")
                return

            print("✅ Successfully logged in!")

            # Start monitoring loop
            await self.monitor_mentions()

    async def login(self) -> bool:
        """Login to Twitter"""
        try:
            print("🔐 Logging in to Twitter...")

            await self.page.goto('https://twitter.com/login', wait_until='networkidle')
            await asyncio.sleep(2)

            # Enter username
            username_input = await self.page.wait_for_selector('input[autocomplete="username"]', timeout=10000)
            await username_input.fill(self.config['twitter_username'])
            await asyncio.sleep(1)

            # Click next
            await self.page.click('text="Next"')
            await asyncio.sleep(2)

            # Check if email verification is needed
            try:
                email_input = await self.page.wait_for_selector('input[data-testid="ocfEnterTextTextInput"]', timeout=3000)
                if email_input:
                    print("📧 Email verification required...")
                    await email_input.fill(self.config['twitter_email'])
                    await self.page.click('text="Next"')
                    await asyncio.sleep(2)
            except:
                pass  # Email not required

            # Enter password
            password_input = await self.page.wait_for_selector('input[name="password"]', timeout=10000)
            await password_input.fill(self.config['twitter_password'])
            await asyncio.sleep(1)

            # Click login
            await self.page.click('text="Log in"')
            await asyncio.sleep(5)

            # Check if login successful by looking for home timeline
            try:
                await self.page.wait_for_selector('[data-testid="primaryColumn"]', timeout=10000)
                return True
            except:
                return False

        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    async def monitor_mentions(self):
        """Main loop - monitor mentions and respond"""
        print("\n👀 Starting mention monitoring...")
        print(f"⏱️  Check interval: {self.config['check_interval_seconds']}s\n")

        while True:
            try:
                mentions = await self.get_mentions()

                print(f"[{datetime.now().strftime('%H:%M:%S')}] Found {len(mentions)} new mention(s)")

                for mention in mentions:
                    if mention['tweet_id'] not in self.processed_tweets:
                        print(f"\n📨 New mention from @{mention['author']}")
                        print(f"💬 Content: {mention['content'][:100]}...")

                        # Read the full thread
                        thread = await self.read_thread(mention['tweet_url'])

                        if thread:
                            print(f"📖 Thread contains {len(thread.tweets)} tweet(s)")

                            # Generate response
                            response = await self.generate_response(thread, mention)

                            if response:
                                print(f"✍️  Generated response: {response[:100]}...")

                                # Post the response
                                success = await self.post_reply(mention['tweet_url'], response)

                                if success:
                                    print(f"✅ Successfully replied!")
                                    self.processed_tweets.add(mention['tweet_id'])
                                    self.save_processed_tweets()
                                else:
                                    print(f"❌ Failed to post reply")
                            else:
                                print(f"⚠️  Could not generate response")
                        else:
                            print(f"⚠️  Could not read thread")

                # Wait before next check
                await asyncio.sleep(self.config['check_interval_seconds'])

            except KeyboardInterrupt:
                print("\n\n👋 Stopping bot...")
                break
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(30)  # Wait before retry

    async def get_mentions(self) -> List[Dict]:
        """Get recent mentions of the bot's handle"""
        try:
            # Navigate to notifications
            await self.page.goto('https://twitter.com/notifications/mentions', wait_until='networkidle')
            await asyncio.sleep(3)

            mentions = []

            # Get all tweet articles
            tweets = await self.page.query_selector_all('article[data-testid="tweet"]')

            for tweet in tweets[:10]:  # Check last 10 mentions
                try:
                    # Extract tweet data
                    author_elem = await tweet.query_selector('div[data-testid="User-Name"] a')
                    author = await author_elem.get_attribute('href')
                    author = author.strip('/') if author else "unknown"

                    content_elem = await tweet.query_selector('div[data-testid="tweetText"]')
                    content = await content_elem.inner_text() if content_elem else ""

                    # Get tweet URL and ID
                    time_elem = await tweet.query_selector('time')
                    parent_link = await time_elem.evaluate('el => el.closest("a")')
                    tweet_url = await self.page.evaluate('el => el ? el.href : null', parent_link)

                    if tweet_url:
                        tweet_id = tweet_url.split('/')[-1]

                        mentions.append({
                            'tweet_id': tweet_id,
                            'author': author,
                            'content': content,
                            'tweet_url': tweet_url
                        })
                except Exception as e:
                    continue

            return mentions

        except Exception as e:
            print(f"❌ Error getting mentions: {e}")
            return []

    async def read_thread(self, tweet_url: str) -> Optional[Thread]:
        """Read entire thread starting from a tweet"""
        try:
            print(f"📖 Reading thread from: {tweet_url}")

            await self.page.goto(tweet_url, wait_until='networkidle')
            await asyncio.sleep(3)

            # Scroll to load more tweets in thread
            for _ in range(3):
                await self.page.evaluate('window.scrollBy(0, 1000)')
                await asyncio.sleep(1)

            tweets_data = []

            # Get all tweets in the thread
            tweet_articles = await self.page.query_selector_all('article[data-testid="tweet"]')

            for article in tweet_articles[:self.config.get('max_thread_length', 20)]:
                try:
                    # Author
                    author_elem = await article.query_selector('div[data-testid="User-Name"] a')
                    author_href = await author_elem.get_attribute('href') if author_elem else "/unknown"
                    author = author_href.strip('/')

                    # Content
                    content_elem = await article.query_selector('div[data-testid="tweetText"]')
                    content = await content_elem.inner_text() if content_elem else ""

                    # Time
                    time_elem = await article.query_selector('time')
                    timestamp = await time_elem.get_attribute('datetime') if time_elem else ""

                    # Tweet ID
                    time_parent = await time_elem.evaluate('el => el.closest("a")') if time_elem else None
                    tweet_link = await self.page.evaluate('el => el ? el.href : null', time_parent) if time_parent else None
                    tweet_id = tweet_link.split('/')[-1] if tweet_link else f"unknown_{len(tweets_data)}"

                    tweet = Tweet(
                        tweet_id=tweet_id,
                        author=author,
                        content=content,
                        timestamp=timestamp,
                        is_reply=True
                    )

                    tweets_data.append(tweet)

                except Exception as e:
                    continue

            if tweets_data:
                return Thread(
                    tweets=tweets_data,
                    root_tweet=tweets_data[0]
                )

            return None

        except Exception as e:
            print(f"❌ Error reading thread: {e}")
            return None

    async def generate_response(self, thread: Thread, mention: Dict) -> Optional[str]:
        """Generate AI response based on thread context"""
        try:
            if not self.claude_client:
                print("⚠️  Claude API key not configured")
                return None

            # Build context from thread
            context = thread.to_context()

            # Create prompt
            prompt = f"""You are responding to a Twitter thread. Here's the conversation:

{context}

Your role: {self.config.get('bot_persona', 'You are a helpful AI assistant.')}

Generate a thoughtful, concise response (max 280 characters for Twitter). Be helpful and engaging.
Do not include hashtags unless necessary. Be conversational and natural.

Response:"""

            # Call Claude API
            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                temperature=self.config.get('response_temperature', 0.7),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response = message.content[0].text.strip()

            # Ensure it fits Twitter's limit
            if len(response) > 280:
                response = response[:277] + "..."

            return response

        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return None

    async def post_reply(self, tweet_url: str, response: str) -> bool:
        """Post a reply to a tweet"""
        try:
            print(f"💬 Posting reply...")

            # Navigate to tweet
            await self.page.goto(tweet_url, wait_until='networkidle')
            await asyncio.sleep(2)

            # Click reply button
            reply_button = await self.page.wait_for_selector('div[data-testid="reply"]', timeout=5000)
            await reply_button.click()
            await asyncio.sleep(2)

            # Type response
            tweet_box = await self.page.wait_for_selector('div[data-testid="tweetTextarea_0"]', timeout=5000)
            await tweet_box.fill(response)
            await asyncio.sleep(1)

            # Click tweet button
            tweet_button = await self.page.wait_for_selector('div[data-testid="tweetButton"]', timeout=5000)
            await tweet_button.click()
            await asyncio.sleep(3)

            return True

        except Exception as e:
            print(f"❌ Error posting reply: {e}")
            return False


async def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════╗
║         Twitter Bot - Mention Monitor & Responder        ║
║          Uses Playwright (No Official API Needed)        ║
╚══════════════════════════════════════════════════════════╝
    """)

    bot = TwitterBot()
    await bot.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
