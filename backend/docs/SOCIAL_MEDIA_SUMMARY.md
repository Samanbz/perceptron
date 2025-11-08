# Social Media Data Collection - Implementation Summary

## What We Built

Added three social media sourcers to gather data from Reddit, Twitter/X, and LinkedIn:

### 1. **Reddit Sourcer** (`sourcers/reddit_sourcer.py`)
- ✅ Full official API support
- ✅ Free tier: 100 requests/minute
- ✅ Easy setup (just need app credentials)
- ✅ Reliable and stable
- **Best for**: Monitoring communities, trend detection, sentiment analysis

### 2. **Twitter Sourcer** (`sourcers/twitter_sourcer.py`)
- ✅ No API credentials required
- ✅ Uses public Nitter instances
- ⚠️ May be slower than official API
- ⚠️ Depends on Nitter availability
- **Best for**: Quick prototyping, keyword tracking, hashtag monitoring

### 3. **LinkedIn Sourcer** (`sourcers/linkedin_sourcer.py`)
- ⚠️ Basic scraper is placeholder (LinkedIn blocks scrapers)
- ✅ Proxycurl API implementation included (paid service)
- **Best for**: Company intelligence, B2B monitoring (requires paid API)

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install praw ntscraper
```

### 2. Get Reddit Credentials (5 minutes)

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" → Select "script"
3. Set environment variables:

```powershell
# PowerShell
$env:REDDIT_CLIENT_ID="your_client_id_here"
$env:REDDIT_CLIENT_SECRET="your_client_secret_here"
```

### 3. Test It

```bash
cd backend
python scripts/test_social_media.py
```

## Usage Example

```python
from sourcers import RedditSourcer, TwitterSourcer
import asyncio

async def collect_data():
    # Reddit
    reddit = RedditSourcer(
        subreddit="technology",
        limit=100,
        sort_by="hot"
    )
    posts = await reddit.fetch()
    print(f"Got {len(posts)} Reddit posts")
    
    # Twitter
    twitter = TwitterSourcer(
        search_query="AI regulation",
        max_tweets=50,
        mode="term"
    )
    tweets = await twitter.fetch()
    print(f"Got {len(tweets)} tweets")

asyncio.run(collect_data())
```

## What You Can Monitor

### Reddit
- **r/technology** - Tech trends and news
- **r/worldnews** - Global events
- **r/investing** - Market sentiment
- **r/politics** - Policy discussions
- **Industry-specific subs** - Vertical insights

### Twitter
- **Keywords**: "AI regulation", "venture capital", etc.
- **Users**: @elonmusk, @satyanadella, industry leaders
- **Hashtags**: #AI, #RegTech, #FinTech

### LinkedIn (with Proxycurl)
- **Company posts** - Microsoft, Google, competitors
- **Industry updates** - B2B intelligence
- **Job postings** - Talent trends

## Integration with Your System

### Option A: Manual Collection Script

```python
# backend/scripts/fetch_social_media.py
from sourcers import RedditSourcer
from storage import ArticleRepository

async def fetch_reddit_data():
    sourcer = RedditSourcer(subreddit="technology", limit=50)
    contents = await sourcer.fetch()
    
    repo = ArticleRepository()
    for content in contents:
        await repo.store_article(
            title=content.title,
            content=content.content,
            url=content.url,
            source=f"reddit:r/technology",
            metadata=content.metadata
        )
```

### Option B: Add to Scheduler

```python
# In scheduler.py
from sourcers import RedditSourcer

@scheduler.scheduled_job('interval', hours=2)
async def fetch_social_media():
    """Fetch every 2 hours."""
    sourcer = RedditSourcer(subreddit="technology", limit=100)
    contents = await sourcer.fetch()
    # Store contents...
```

### Option C: API Endpoints

```python
# In app.py
@app.post("/api/sources/reddit/fetch")
async def fetch_reddit(subreddit: str, limit: int = 50):
    sourcer = RedditSourcer(subreddit=subreddit, limit=limit)
    contents = await sourcer.fetch()
    return {"posts": [c.to_dict() for c in contents]}
```

## Cost Comparison

| Platform | Free Tier | Paid API | Setup Time |
|----------|-----------|----------|------------|
| **Reddit** | ✅ 100 req/min | N/A | 5 min |
| **Twitter** | ✅ Via Nitter | $100/month | 0 min |
| **LinkedIn** | ❌ No | $0.01/request | 10 min |

## Recommendations

### For MVP (Starting Now)
1. ✅ **Use Reddit** - Easy setup, free, reliable
2. ✅ **Use Twitter** - No credentials needed
3. ⏳ **Skip LinkedIn** - Add later if needed

### For Production (Next Month)
1. ✅ **Reddit** - Keep using (free & reliable)
2. 🔄 **Twitter** - Upgrade to official API ($100/month)
3. 🔄 **LinkedIn** - Add Proxycurl if B2B focus

### For Enterprise (Long Term)
- Official APIs for all platforms
- Brandwatch/Hootsuite for unified monitoring
- Real-time streaming webhooks
- Custom proxy infrastructure

## Rate Limits & Best Practices

### Reddit
- **Limit**: 100 requests/minute
- **Best practice**: Fetch every 2-4 hours
- **Tip**: Use batch fetching (100 posts per request)

### Twitter (via Nitter)
- **Limit**: Varies by instance
- **Best practice**: Add delays between requests
- **Tip**: Implement retry logic with backoff

### General
```python
# Add rate limiting
import asyncio

async def fetch_with_delay(sourcers):
    for sourcer in sourcers:
        data = await sourcer.fetch()
        await asyncio.sleep(5)  # 5 second delay
        yield data
```

## Troubleshooting

### "Invalid credentials" (Reddit)
→ Check `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` are set
→ Verify app type is "script" at https://www.reddit.com/prefs/apps

### "No instances available" (Twitter)
→ Nitter instances may be down, try again later
→ Consider Twitter official API for reliability

### "Rate limit exceeded"
→ Add delays between requests
→ Reduce fetch frequency
→ Implement exponential backoff

## Files Created

```
backend/
├── sourcers/
│   ├── reddit_sourcer.py      # Reddit API implementation
│   ├── twitter_sourcer.py     # Twitter via Nitter
│   ├── linkedin_sourcer.py    # LinkedIn placeholder + Proxycurl
│   └── __init__.py            # Updated exports
├── scripts/
│   └── test_social_media.py   # Test suite
├── docs/
│   └── SOCIAL_MEDIA_GUIDE.md  # Complete guide
└── requirements.txt           # Updated with praw, ntscraper
```

## Next Steps

1. **Today**: Install dependencies and test Reddit sourcer
   ```bash
   pip install praw ntscraper
   python scripts/test_social_media.py
   ```

2. **This Week**: Add sources to your config and scheduler
   - Edit `config.json` with your target subreddits
   - Add scheduled jobs to `scheduler.py`

3. **This Month**: Monitor and optimize
   - Track data quality and duplicates
   - Adjust fetch frequencies
   - Add error alerting

4. **Future**: Scale up
   - Add more platforms (YouTube, TikTok, etc.)
   - Implement advanced filtering
   - Add real-time streaming for critical keywords

## Support

- **Full Documentation**: `backend/docs/SOCIAL_MEDIA_GUIDE.md`
- **Test Script**: `backend/scripts/test_social_media.py`
- **Reddit API Docs**: https://www.reddit.com/dev/api/
- **PRAW Docs**: https://praw.readthedocs.io/

---

**Ready to start?** Run `python scripts/test_social_media.py` to see it in action!
