# Multi-Source Integration Guide

## Overview

The platform now supports multiple data source types beyond RSS feeds. Sources are configured in `config.json` and seamlessly integrated into the data pipeline.

## Supported Source Types

### 1. **RSS** (✅ No setup required)

Standard RSS/Atom feed sourcer.

```json
{
  "source_type": "rss",
  "source_name": "TechCrunch",
  "source_url": "https://techcrunch.com/feed/",
  "config": {
    "max_entries": 50
  }
}
```

### 2. **Reddit** (Requires credentials)

Scrapes Reddit posts from specific subreddits.

**Setup:**

1. Create Reddit account at https://www.reddit.com
2. Go to https://www.reddit.com/prefs/apps
3. Click "Create App" → Choose "script" type
4. Set environment variables:
   ```bash
   export REDDIT_CLIENT_ID="your_client_id"
   export REDDIT_CLIENT_SECRET="your_client_secret"
   ```

**Config:**

```json
{
  "source_type": "reddit",
  "source_name": "r/technology",
  "source_url": "https://reddit.com/r/technology",
  "config": {
    "subreddit": "technology",
    "limit": 50,
    "time_filter": "day",
    "sort_by": "hot"
  }
}
```

**Options:**

- `time_filter`: `hour`, `day`, `week`, `month`, `year`, `all`
- `sort_by`: `hot`, `new`, `rising`, `top`, `controversial`

### 3. **NewsAPI** (Requires API key)

Access 80,000+ news sources via NewsAPI.org.

**Setup:**

1. Sign up at https://newsapi.org/register
2. Get your API key
3. Set environment variable:
   ```bash
   export NEWSAPI_KEY="your_api_key"
   ```

**Free tier:** 100 requests/day

**Config:**

```json
{
  "source_type": "newsapi",
  "source_name": "NewsAPI - Funding & Investment",
  "source_url": "https://newsapi.org",
  "config": {
    "query": "funding OR investment OR venture capital",
    "language": "en",
    "max_articles": 50,
    "sort_by": "publishedAt"
  }
}
```

**Options:**

- `query`: Keywords to search for
- `sources`: Comma-separated source IDs (e.g., "bbc-news,cnn")
- `domains`: Comma-separated domains (e.g., "bbc.co.uk")
- `category`: `business`, `entertainment`, `general`, `health`, `science`, `sports`, `technology`
- `country`: 2-letter country code (e.g., "us")
- `sort_by`: `relevancy`, `popularity`, `publishedAt`

### 4. **YouTube** (Requires API key)

Fetch YouTube videos via official YouTube Data API v3.

**Setup:**

1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable "YouTube Data API v3"
4. Create credentials → API Key
5. Set environment variable:
   ```bash
   export YOUTUBE_API_KEY="your_api_key"
   ```

**Free tier:** ~100 searches/day (10,000 units/day, 100 units per search)

**Config:**

```json
{
  "source_type": "youtube",
  "source_name": "YouTube AI Research",
  "source_url": "https://youtube.com",
  "config": {
    "search_query": "machine learning research",
    "max_results": 25,
    "order": "relevance"
  }
}
```

**Options:**

- `search_query`: Search keywords
- `channel_id`: Specific channel ID to search within
- `max_results`: Maximum videos (default: 25, max: 50)
- `order`: `date`, `rating`, `relevance`, `title`, `viewCount`

### 5. **Twitter/X** (No credentials needed)

Scrapes Twitter via Nitter instances (no API key required).

**Setup:**

```bash
pip install ntscraper
```

**Config:**

```json
{
  "source_type": "twitter",
  "source_name": "AI Regulation Tweets",
  "source_url": "https://twitter.com",
  "config": {
    "search_query": "AI regulation",
    "max_tweets": 50,
    "mode": "term"
  }
}
```

**Options:**

- `mode`: `term` (search), `hashtag`, or `user`
- `search_query`: For `mode="term"`
- `username`: For `mode="user"` (without @)
- `hashtag`: For `mode="hashtag"` (without #)

**Note:** Depends on Nitter instance availability; may be slower than official API.

## Architecture

### Data Flow

```
config.json
    ↓
TeamRepository (loads config)
    ↓
DataSourcingService (fetches from all sources)
    ↓
ContentRepository (stores in data lake)
    ↓
NLPProcessingService (processes content)
    ↓
EnhancedKeywordProcessor (extracts keywords & importance)
    ↓
Keywords Database
```

### Key Design Principles

1. **Source Type Transparency**: The NLP pipeline doesn't care about source types - all content is normalized to `SourcedContent` format

2. **Dynamic Sourcer Creation**: `DataSourcingService._create_sourcer()` instantiates the correct sourcer based on `source_type`

3. **Graceful Degradation**: Missing credentials or dependencies result in warnings, not crashes

4. **Extensibility**: Add new sourcers by:
   - Implementing `BaseSourcer` interface
   - Adding case in `_create_sourcer()`
   - Updating config.json

## Testing

### Quick Test (Individual Sourcers)

```bash
cd backend
python test_multi_source_integration.py
```

This tests:

1. ✅ Individual sourcer functionality
2. ✅ Config.json integration
3. ✅ Database storage
4. ✅ NLP processing
5. ✅ Keyword extraction

### Full Production Test

```bash
# 1. Fetch data from all sources
cd backend
python services/data_sourcing_service.py

# 2. Process with NLP
python services/nlp_processing_service.py
```

## Adding a New Source Type

### Example: Adding LinkedIn Sourcer

1. **Implement the sourcer** (already exists in `sourcers/linkedin_sourcer.py`)

2. **Import in data_sourcing_service.py**:

```python
from sourcers import LinkedInSourcer
```

3. **Add case in `_create_sourcer()`**:

```python
elif source_type == 'linkedin':
    return LinkedInSourcer(
        search_query=config.get('search_query'),
        name=source['name'],
        max_posts=config.get('max_posts', 50),
    )
```

4. **Add to config.json**:

```json
{
  "source_type": "linkedin",
  "source_name": "LinkedIn Tech Posts",
  "source_url": "https://linkedin.com",
  "config": {
    "search_query": "artificial intelligence",
    "max_posts": 50
  }
}
```

5. **Test**:

```bash
python test_multi_source_integration.py
```

## Configuration Reference

### Team Configuration Structure

Each team in `config.json` has:

```json
{
  "team_key": "researcher",
  "team_name": "Research Team",
  "is_active": true,
  "keyword_config": {
    /* extraction settings */
  },
  "sentiment_config": {
    /* sentiment settings */
  },
  "sources": [
    {
      "source_type": "rss|reddit|newsapi|youtube|twitter",
      "source_name": "Display Name",
      "source_url": "URL",
      "fetch_interval_minutes": 60,
      "is_enabled": true, // optional, defaults to true
      "config": {
        // Source-specific configuration
      },
      "notes": "Optional description"
    }
  ]
}
```

### Common Fields

- `source_type`: Type of sourcer to use
- `source_name`: Display name (must be unique)
- `source_url`: Source URL (for reference)
- `fetch_interval_minutes`: How often to fetch (used by scheduler)
- `is_enabled`: Enable/disable without deleting (optional, default: true)
- `config`: Source-specific parameters
- `notes`: Human-readable notes (optional)

## Environment Variables

Set these in your shell or `.env` file:

```bash
# Reddit
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"

# NewsAPI
export NEWSAPI_KEY="your_api_key"

# YouTube
export YOUTUBE_API_KEY="your_api_key"

# Twitter (uses Nitter, no credentials needed)
# No setup required

# LinkedIn (Proxycurl API)
export PROXYCURL_API_KEY="your_api_key"
```

## Troubleshooting

### "Missing dependency" errors

Install required packages:

```bash
pip install praw                    # Reddit
pip install newsapi-python          # NewsAPI
pip install google-api-python-client  # YouTube
pip install ntscraper               # Twitter
```

### "Missing credentials" errors

Set the appropriate environment variables (see above).

### Sources not fetching

1. Check `is_enabled: true` in config.json
2. Verify credentials are set
3. Check logs for specific errors
4. Test individual sourcer:
   ```bash
   python test_multi_source_integration.py
   ```

### Rate limits

- **NewsAPI**: 100 requests/day (free tier)
- **YouTube**: ~100 searches/day (free tier)
- **Reddit**: 100 requests/minute (free tier)
- **Twitter**: Depends on Nitter instance availability

Adjust `fetch_interval_minutes` in config to stay within limits.

## Best Practices

1. **Start with RSS feeds** (no setup required) to validate your pipeline

2. **Add API-based sources gradually** once RSS is working

3. **Set appropriate fetch intervals** based on:

   - API rate limits
   - Content update frequency
   - Your data needs

4. **Monitor source health**:

   ```bash
   # Check last fetch times and errors
   sqlite3 data/teams.db "SELECT source_name, last_fetched_at, last_error FROM team_sources;"
   ```

5. **Use `is_enabled: false`** to temporarily disable sources without deleting configuration

6. **Test new sources individually** before adding to production config

## Performance Notes

- RSS feeds are fastest (no rate limits, no credentials)
- Reddit is very reliable (generous free tier)
- NewsAPI free tier is limited but reliable
- YouTube free tier is limited but sufficient for moderate use
- Twitter scraping via Nitter is slowest and least reliable

For production use at scale, consider paid API tiers or focus on RSS/Reddit sources.
