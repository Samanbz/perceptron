# Social Media Data Collection Guide

This guide explains how to gather social media data for the Perceptron intelligence platform.

## Overview

We've implemented multiple social media sourcers following the same architecture as the RSS sourcer:

- **Reddit**: Full API access (free, requires app credentials)
- **Twitter/X**: Web scraping via Nitter (no API key needed)
- **LinkedIn**: Placeholder + Proxycurl API option (commercial)

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install praw ntscraper
```

### 2. Set Up Credentials

#### Reddit (Recommended - Easy & Free)

1. Create Reddit account at https://www.reddit.com
2. Go to https://www.reddit.com/prefs/apps
3. Click "Create App" → Choose "script" type
4. Get your `client_id` and `client_secret`
5. Set environment variables:

```bash
# Windows PowerShell
$env:REDDIT_CLIENT_ID="your_client_id"
$env:REDDIT_CLIENT_SECRET="your_client_secret"

# Or create .env file in backend/
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=Perceptron Intelligence Aggregator v1.0
```

#### Twitter/X (No Credentials Needed)

Uses public Nitter instances - no setup required!

## Usage Examples

### Reddit Sourcer

```python
from sourcers import RedditSourcer

# Monitor a subreddit for emerging trends
sourcer = RedditSourcer(
    subreddit="technology",
    name="Tech Trends",
    limit=100,
    sort_by="hot",
    time_filter="day"
)

# Fetch posts
contents = await sourcer.fetch()

for content in contents:
    print(f"{content.title}")
    print(f"Score: {content.metadata['score']}")
    print(f"Comments: {content.metadata['num_comments']}")
    print(f"URL: {content.url}")
    print("---")
```

**Available Parameters:**
- `sort_by`: "hot", "new", "rising", "top", "controversial"
- `time_filter`: "hour", "day", "week", "month", "year", "all"
- `limit`: Max posts to fetch (default: 100)

**Use Cases:**
- Monitor r/technology for tech trends
- Track r/investing for market sentiment
- Watch r/politics for policy discussions
- Monitor industry-specific subreddits

### Twitter Sourcer

```python
from sourcers import TwitterSourcer

# Search by keyword
sourcer = TwitterSourcer(
    search_query="artificial intelligence regulation",
    name="AI Policy Tracker",
    max_tweets=50,
    mode="term"
)

# Or track a specific user
sourcer = TwitterSourcer(
    username="elonmusk",
    mode="user",
    max_tweets=20
)

# Or follow a hashtag
sourcer = TwitterSourcer(
    hashtag="AI",
    mode="hashtag",
    max_tweets=30
)

# Fetch tweets
contents = await sourcer.fetch()

for content in contents:
    print(f"@{content.author}: {content.title}")
    print(f"Likes: {content.metadata['likes']}")
    print(f"Retweets: {content.metadata['retweets']}")
    print("---")
```

**Modes:**
- `term`: Search by keywords/phrases
- `user`: Get tweets from specific user
- `hashtag`: Follow hashtag trends

**Limitations:**
- Depends on Nitter instance availability
- May be slower than official API
- Limited historical data

### LinkedIn Sourcer (Placeholder)

LinkedIn actively blocks scrapers. For production use:

```python
from sourcers import ProxycurlLinkedInSourcer

# Using Proxycurl API (paid service)
sourcer = ProxycurlLinkedInSourcer(
    company_url="https://www.linkedin.com/company/microsoft/",
    api_key="your_proxycurl_api_key",  # Or set PROXYCURL_API_KEY env var
    max_posts=20
)

contents = await sourcer.fetch()
```

**LinkedIn Options:**
1. **Proxycurl** (https://nubela.co/proxycurl/) - $0.01 per request
2. **Official API** - Requires partnership approval
3. **RapidAPI** - Various LinkedIn data endpoints
4. **Browser Automation** - Playwright/Selenium (complex)

## Integration with Perceptron

### Add Social Media Sources to Your Config

Edit `backend/config.json`:

```json
{
  "sources": [
    {
      "type": "reddit",
      "name": "Tech News",
      "subreddit": "technology",
      "limit": 50,
      "sort_by": "hot"
    },
    {
      "type": "reddit",
      "name": "AI Research",
      "subreddit": "MachineLearning",
      "limit": 30,
      "sort_by": "top",
      "time_filter": "week"
    },
    {
      "type": "twitter",
      "name": "AI Regulation Tracker",
      "search_query": "AI regulation OR artificial intelligence policy",
      "mode": "term",
      "max_tweets": 100
    },
    {
      "type": "twitter",
      "name": "Industry Leaders",
      "username": "satyanadella",
      "mode": "user",
      "max_tweets": 20
    }
  ]
}
```

### Create a Social Media Fetcher Script

```python
# backend/scripts/fetch_social_media.py
import asyncio
from sourcers import RedditSourcer, TwitterSourcer
from storage import ArticleRepository

async def fetch_all_social():
    """Fetch from all social media sources."""
    
    repo = ArticleRepository()
    
    # Reddit sources
    reddit_sources = [
        ("technology", "Tech News"),
        ("worldnews", "World News"),
        ("business", "Business Trends"),
    ]
    
    for subreddit, name in reddit_sources:
        try:
            sourcer = RedditSourcer(subreddit=subreddit, name=name, limit=50)
            contents = await sourcer.fetch()
            
            # Store in database
            for content in contents:
                await repo.store_article(
                    title=content.title,
                    content=content.content,
                    url=content.url,
                    source=f"reddit:r/{subreddit}",
                    author=content.author,
                    published_date=content.published_date,
                    metadata=content.metadata
                )
            
            print(f"✓ Fetched {len(contents)} posts from r/{subreddit}")
        except Exception as e:
            print(f"✗ Failed to fetch r/{subreddit}: {e}")
    
    # Twitter sources
    twitter_queries = [
        ("artificial intelligence regulation", "AI Policy"),
        ("venture capital", "VC News"),
        ("cybersecurity", "Security Trends"),
    ]
    
    for query, name in twitter_queries:
        try:
            sourcer = TwitterSourcer(
                search_query=query,
                name=name,
                max_tweets=30,
                mode="term"
            )
            contents = await sourcer.fetch()
            
            # Store in database
            for content in contents:
                await repo.store_article(
                    title=content.title,
                    content=content.content,
                    url=content.url,
                    source=f"twitter:search",
                    author=content.author,
                    published_date=content.published_date,
                    metadata=content.metadata
                )
            
            print(f"✓ Fetched {len(contents)} tweets for '{query}'")
        except Exception as e:
            print(f"✗ Failed to fetch Twitter '{query}': {e}")

if __name__ == "__main__":
    asyncio.run(fetch_all_social())
```

Run it:
```bash
python scripts/fetch_social_media.py
```

### Add to Scheduler

Edit `backend/scheduler.py` to include social media fetching:

```python
# Add to your scheduler
@scheduler.scheduled_job('interval', hours=2)  # Every 2 hours
async def fetch_social_media():
    """Fetch social media data periodically."""
    from scripts.fetch_social_media import fetch_all_social
    await fetch_all_social()
```

## API Endpoints

### Reddit Endpoint

```python
# Add to app.py
from sourcers import RedditSourcer

@app.post("/api/sources/reddit/fetch")
async def fetch_reddit(
    subreddit: str,
    limit: int = 50,
    sort_by: str = "hot",
    time_filter: str = "day"
):
    """Fetch posts from a subreddit."""
    try:
        sourcer = RedditSourcer(
            subreddit=subreddit,
            limit=limit,
            sort_by=sort_by,
            time_filter=time_filter
        )
        contents = await sourcer.fetch()
        return {
            "source": f"r/{subreddit}",
            "count": len(contents),
            "posts": [content.to_dict() for content in contents]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

Test it:
```bash
curl -X POST http://localhost:8000/api/sources/reddit/fetch \
  -H "Content-Type: application/json" \
  -d '{"subreddit": "technology", "limit": 10}'
```

### Twitter Endpoint

```python
@app.post("/api/sources/twitter/fetch")
async def fetch_twitter(
    search_query: str = None,
    username: str = None,
    hashtag: str = None,
    mode: str = "term",
    max_tweets: int = 50
):
    """Fetch tweets."""
    try:
        sourcer = TwitterSourcer(
            search_query=search_query,
            username=username,
            hashtag=hashtag,
            mode=mode,
            max_tweets=max_tweets
        )
        contents = await sourcer.fetch()
        return {
            "source": "twitter",
            "count": len(contents),
            "tweets": [content.to_dict() for content in contents]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Best Practices

### 1. Rate Limiting

```python
import asyncio
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, calls_per_minute=30):
        self.calls_per_minute = calls_per_minute
        self.calls = []
    
    async def wait_if_needed(self):
        now = datetime.now()
        self.calls = [c for c in self.calls if now - c < timedelta(minutes=1)]
        
        if len(self.calls) >= self.calls_per_minute:
            sleep_time = 60 - (now - self.calls[0]).total_seconds()
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        self.calls.append(now)
```

### 2. Error Handling

```python
async def fetch_with_retry(sourcer, max_retries=3):
    """Fetch with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return await sourcer.fetch()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s")
            await asyncio.sleep(wait_time)
```

### 3. Data Deduplication

```python
def deduplicate_content(contents):
    """Remove duplicate posts by URL or content hash."""
    seen = set()
    unique = []
    
    for content in contents:
        # Use URL as unique identifier
        identifier = content.url or hash(content.content)
        if identifier not in seen:
            seen.add(identifier)
            unique.append(content)
    
    return unique
```

## Platform Comparison

| Platform | API Access | Rate Limits | Cost | Setup Difficulty |
|----------|-----------|-------------|------|------------------|
| **Reddit** | ✅ Official | 100 req/min | Free | Easy |
| **Twitter/X** | ⚠️ Via Nitter | Variable | Free | None |
| **LinkedIn** | ❌ Limited | N/A | $$$ | Hard |
| **Facebook** | ❌ Restricted | N/A | Free (limited) | Medium |
| **Instagram** | ❌ Restricted | N/A | Free (limited) | Medium |

## Recommendations

### For Minimum Viable Product (MVP)
1. **Reddit** - Easy setup, reliable, free
2. **Twitter** - No credentials needed, good for trends

### For Production
1. **Reddit** - Keep using official API
2. **Twitter** - Consider upgrading to official API ($100/month basic)
3. **LinkedIn** - Use Proxycurl for company intelligence
4. **Add**: NewsAPI, Google Trends, Mentions trackers

### For Enterprise
- Official APIs for all platforms
- Brandwatch or Hootsuite for unified social listening
- Custom webhooks and real-time streaming
- Dedicated proxy infrastructure

## Troubleshooting

### Reddit: "Invalid credentials"
- Check environment variables are set
- Verify client_id and client_secret from https://www.reddit.com/prefs/apps
- Ensure using "script" type app

### Twitter: "No instances available"
- Nitter instances may be down
- Try again later or implement instance rotation
- Consider Twitter API for reliability

### General: Rate limiting
- Add delays between requests
- Implement exponential backoff
- Monitor API response headers
- Use caching where possible

## Next Steps

1. **Install dependencies**: `pip install praw ntscraper`
2. **Set up Reddit credentials**: Get from https://www.reddit.com/prefs/apps
3. **Test sourcers**: Run example scripts
4. **Add to scheduler**: Integrate into your scheduler.py
5. **Monitor data quality**: Check for duplicates and errors
6. **Scale up**: Add more sources as needed

For questions or issues, refer to:
- Reddit API docs: https://www.reddit.com/dev/api/
- PRAW docs: https://praw.readthedocs.io/
- ntscraper: https://github.com/bocchilorenzo/ntscraper
