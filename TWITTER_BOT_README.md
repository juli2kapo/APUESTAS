# Twitter Bot - Mention Monitor & Auto-Responder

**Automatically detect when your bot is mentioned, read entire threads, and generate intelligent AI responses.**

## 🎯 Features

- ✅ **No Official X API Required** - Uses Playwright web scraping
- 🔍 **Mention Detection** - Monitors Twitter notifications for mentions
- 📖 **Thread Reading** - Reads entire conversation context
- 🤖 **AI Response Generation** - Uses Claude API for intelligent replies
- 💬 **Auto-Reply** - Posts responses directly to Twitter
- 🔄 **Continuous Monitoring** - Runs in loop with configurable intervals
- 💾 **Duplicate Prevention** - Tracks processed tweets to avoid re-responding

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install playwright anthropic
playwright install chromium
```

### 2. Create Configuration

Copy the example config and edit with your credentials:

```bash
cp twitter_config.json.example twitter_config.json
nano twitter_config.json
```

**Required settings:**
```json
{
  "twitter_username": "your_username",
  "twitter_password": "your_password",
  "twitter_email": "your_email@example.com",
  "twitter_handle": "@YourBotHandle",
  "claude_api_key": "sk-ant-api03-..."
}
```

### 3. Run the Bot

```bash
python twitter_bot.py
```

The bot will:
1. Login to Twitter
2. Monitor your mentions
3. Read full thread context when mentioned
4. Generate AI response using Claude
5. Reply automatically

## 📋 Configuration Options

### `twitter_config.json`

| Setting | Description | Default |
|---------|-------------|---------|
| `twitter_username` | Your Twitter username | Required |
| `twitter_password` | Your Twitter password | Required |
| `twitter_email` | Your email (for verification) | Required |
| `twitter_handle` | Your bot's @handle to monitor | Required |
| `claude_api_key` | Anthropic Claude API key | Required |
| `check_interval_seconds` | How often to check mentions | 60 |
| `max_thread_length` | Max tweets to read in thread | 20 |
| `response_temperature` | AI creativity (0-1) | 0.7 |
| `bot_persona` | AI personality/instructions | Custom |
| `headless` | Run browser hidden | true |

## 🔧 How It Works

### 1. **Mention Detection**
The bot periodically checks your Twitter notifications page for new mentions:

```python
# Every 60 seconds (configurable)
mentions = await bot.get_mentions()
```

### 2. **Thread Reading**
When a mention is found, it reads the entire conversation:

```python
thread = await bot.read_thread(mention_url)
# Returns: [Tweet1, Tweet2, Tweet3, ...]
```

### 3. **AI Response Generation**
Sends thread context to Claude API:

```python
response = await bot.generate_response(thread)
# Claude analyzes the conversation and generates reply
```

### 4. **Auto-Reply**
Posts the response back to Twitter:

```python
success = await bot.post_reply(tweet_url, response)
```

## 🎭 Customizing Bot Personality

Edit `bot_persona` in `twitter_config.json`:

**Example: Football Stats Bot**
```json
{
  "bot_persona": "You are a football statistics expert. Provide data-driven insights about xG, team performance, and match predictions. Be concise and cite specific metrics."
}
```

**Example: Friendly Helper**
```json
{
  "bot_persona": "You are a friendly and helpful assistant. Answer questions clearly and enthusiastically. Use casual language and be encouraging."
}
```

**Example: Technical Expert**
```json
{
  "bot_persona": "You are a technical expert in data science and machine learning. Provide detailed, accurate explanations with code examples when relevant."
}
```

## 🔒 Security Best Practices

### Protect Your Credentials

**Never commit `twitter_config.json` to git:**
```bash
echo "twitter_config.json" >> .gitignore
echo "processed_tweets.json" >> .gitignore
```

**Use environment variables (alternative):**
```bash
export TWITTER_USERNAME="your_username"
export TWITTER_PASSWORD="your_password"
export CLAUDE_API_KEY="sk-ant-..."
```

### Rate Limiting

Twitter may temporarily block if too aggressive:
- Keep `check_interval_seconds` ≥ 60
- Don't run multiple instances
- Monitor for "unusual activity" warnings

## 📊 Example Usage

### Scenario: Football Stats Bot

Someone tweets:
```
@YourStatsBot What's your prediction for Arsenal vs Chelsea tomorrow?
```

**Bot Response:**
```
Based on recent xG data:
Arsenal (home): 2.1 xG, 0.8 xGA
Chelsea (away): 1.6 xG, 1.3 xGA

Predicted: OVER 2.5 goals (68% confidence)
Expected score: 2-1 Arsenal
```

### Scenario: Thread Discussion

**Thread:**
```
User1: Is xG a reliable metric for predictions?
User2: @YourStatsBot What do you think?
```

**Bot Response:**
```
xG is highly predictive over time! Research shows teams' actual goals converge toward their xG over ~10-15 matches. It's most reliable when combined with form, venue, and defensive stats.
```

## 🐛 Troubleshooting

### Login Fails

**Issue:** Bot can't login to Twitter

**Solutions:**
- Verify credentials in `twitter_config.json`
- Check if Twitter requires email verification (provide `twitter_email`)
- Twitter may block automated logins - try with `headless: false` first
- Use an app-specific password if 2FA is enabled

### No Mentions Found

**Issue:** Bot doesn't detect mentions

**Solutions:**
- Verify `twitter_handle` is correct (include @)
- Check notifications page manually
- Ensure account has mentions (test by mentioning yourself)

### Response Not Posted

**Issue:** AI generates response but doesn't post

**Solutions:**
- Check Twitter rate limits
- Verify you're not shadowbanned
- Look for error messages in console
- Try with `headless: false` to see what's happening

### Claude API Errors

**Issue:** AI response generation fails

**Solutions:**
- Verify `claude_api_key` is correct
- Check API quota/billing
- Reduce `max_thread_length` if hitting token limits
- Review error messages for specific issues

## 🔍 Monitoring & Logs

### Console Output

```
🤖 Starting Twitter Bot...
👤 Username: my_bot_account
🎯 Monitoring mentions of: @MyStatsBot
✅ Successfully logged in!

👀 Starting mention monitoring...
⏱️  Check interval: 60s

[14:23:45] Found 1 new mention(s)

📨 New mention from @football_fan
💬 Content: @MyStatsBot What do you think about Liverpool's xG?

📖 Reading thread from: https://twitter.com/...
📖 Thread contains 3 tweet(s)
✍️  Generated response: Liverpool's recent xG data shows...
💬 Posting reply...
✅ Successfully replied!
```

### Files Generated

- `processed_tweets.json` - Cache of replied tweets
- Playwright browser cache in `~/.cache/ms-playwright`

## 🚨 Important Notes

### Legal & Ethical

- ⚠️ **Terms of Service**: Using scrapers may violate Twitter's ToS
- 🎓 **Educational Purpose**: This is for learning and experimentation
- 🤖 **Bot Policy**: Clearly label your account as a bot
- 📝 **Transparency**: Don't impersonate humans or spread misinformation

### Technical Limitations

- May break if Twitter changes HTML structure
- Browser automation can be detected
- Rate limits apply (Twitter may temporarily block)
- Requires headless browser (memory intensive)

### Alternatives

If you need production reliability:
- Apply for Twitter API access (v2 Essential is free)
- Use official `tweepy` library
- Consider paid automation services

## 🔄 Alternative: Nitter-Based Scraper (API-Free)

For a lighter alternative without browser automation:

```python
# Scrape via Nitter instances (Twitter mirrors)
# Pros: No browser, faster, less detectable
# Cons: Nitter instances often down, can't post replies

import requests
nitter_url = "https://nitter.net/search?q=@YourBot"
response = requests.get(nitter_url)
# Parse HTML for mentions
```

## 🛠️ Advanced Features (TODO)

Potential enhancements:
- [ ] Multiple account support
- [ ] Scheduled tweets
- [ ] Keyword monitoring (beyond mentions)
- [ ] Image/media response support
- [ ] Analytics dashboard
- [ ] Webhook notifications
- [ ] Docker container deployment

## 📚 Resources

- [Playwright Documentation](https://playwright.dev/python/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Twitter Web Scraping Guide](https://github.com/topics/twitter-scraper)

## 🤝 Contributing

This bot is part of the APUESTAS (xG Football Analysis) project.

**Want to improve it?**
- Add better error handling
- Implement retry logic
- Support for media/images
- More AI providers (OpenAI, local models)

## 📄 License

MIT License - Use at your own risk

---

**Remember:** This tool is for educational purposes. Always respect platform terms of service and practice ethical automation. 🤖✨
