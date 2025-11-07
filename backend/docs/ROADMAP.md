# Sourcer Pipeline - Implementation Plan

## ✅ Completed

### Phase 1: Core Architecture

- [x] Base sourcer abstract class (`BaseSourcer`)
- [x] Content model (`SourcedContent`)
- [x] RSS feed sourcer (`RSSSourcer`)
- [x] API endpoints for RSS feeds
- [x] Example usage scripts
- [x] Test suite
- [x] Documentation

## 🚀 Next Steps

### Phase 2: Additional Sourcers (Priority Order)

#### 1. Web Page Scraper

**Purpose:** Extract content from arbitrary web pages

**Implementation:**

```python
class WebScraperSourcer(BaseSourcer):
    def __init__(self, url: str, selector: str = None):
        # Use BeautifulSoup or Playwright
        # selector: CSS selector for main content
```

**Dependencies:** `beautifulsoup4`, `requests` or `playwright`

**Use Cases:**

- News articles without RSS
- Blog posts
- Documentation pages
- Research papers

#### 2. API Sourcer

**Purpose:** Generic REST API client for structured data

**Implementation:**

```python
class APISourcer(BaseSourcer):
    def __init__(self, api_url: str, headers: dict = None,
                 auth: tuple = None, params: dict = None):
        # Generic REST API client
        # Support for auth, custom headers, query params
```

**Dependencies:** `httpx` (async HTTP client)

**Use Cases:**

- News APIs (NewsAPI, MediaStack, etc.)
- Financial APIs (Alpha Vantage, IEX Cloud)
- Social media APIs
- Custom internal APIs

#### 3. Twitter/X Sourcer

**Purpose:** Fetch tweets based on search queries, hashtags, or user timelines

**Implementation:**

```python
class TwitterSourcer(BaseSourcer):
    def __init__(self, api_key: str, query: str = None,
                 username: str = None):
        # Twitter API v2 client
```

**Dependencies:** `tweepy` or direct API calls

**Use Cases:**

- Trending topics monitoring
- Sentiment analysis
- Breaking news detection
- Influencer tracking

#### 4. Reddit Sourcer

**Purpose:** Fetch posts from subreddits

**Implementation:**

```python
class RedditSourcer(BaseSourcer):
    def __init__(self, subreddit: str, sort_by: str = "hot",
                 time_filter: str = "day"):
        # Reddit API client
```

**Dependencies:** `praw` (Python Reddit API Wrapper)

**Use Cases:**

- Community discussions
- Tech trends (r/technology, r/programming)
- Market sentiment (r/wallstreetbets)
- Customer feedback

#### 5. Database Sourcer

**Purpose:** Query structured data from databases

**Implementation:**

```python
class DatabaseSourcer(BaseSourcer):
    def __init__(self, connection_string: str, query: str):
        # Support PostgreSQL, MySQL, SQLite
```

**Dependencies:** `sqlalchemy`, `asyncpg`

**Use Cases:**

- Internal data sources
- Historical data retrieval
- Analytics pipelines

#### 6. File System Sourcer

**Purpose:** Read and parse local files

**Implementation:**

```python
class FileSystemSourcer(BaseSourcer):
    def __init__(self, directory: str, pattern: str = "*.txt",
                 recursive: bool = False):
        # Read files matching pattern
```

**Dependencies:** Standard library (`pathlib`, `glob`)

**Use Cases:**

- Document processing
- Log file analysis
- Local data import

### Phase 3: Advanced Features

#### Content Processing Pipeline

```python
class SourcerPipeline:
    def __init__(self):
        self.sourcers = []
        self.processors = []  # Text cleaning, extraction, etc.
        self.filters = []      # Content filtering rules

    async def run(self) -> List[SourcedContent]:
        # Fetch from all sourcers
        # Apply processors
        # Apply filters
        # Return aggregated results
```

#### Caching & Rate Limiting

```python
class CachedSourcer(BaseSourcer):
    # Redis or local cache
    # TTL-based invalidation
    # Rate limiting per source
```

#### Scheduled Fetching

```python
class ScheduledSourcer:
    # Periodic fetching with cron-like scheduling
    # Background tasks with Celery or APScheduler
```

#### Content Deduplication

```python
class DeduplicatedPipeline:
    # Hash-based deduplication
    # Fuzzy matching for near-duplicates
```

## 📊 Architecture Enhancements

### 1. Sourcer Registry

```python
# sourcers/registry.py
SOURCER_REGISTRY = {
    "rss": RSSSourcer,
    "web": WebScraperSourcer,
    "api": APISourcer,
    "twitter": TwitterSourcer,
    # ...
}

def create_sourcer(source_type: str, **kwargs):
    sourcer_class = SOURCER_REGISTRY.get(source_type)
    if not sourcer_class:
        raise ValueError(f"Unknown source type: {source_type}")
    return sourcer_class(**kwargs)
```

### 2. Configuration Management

```python
# sourcers/config.py
class SourcerConfig:
    # YAML/JSON configuration
    # Environment variables
    # Secrets management
```

### 3. Error Handling & Retry Logic

```python
class RobustSourcer(BaseSourcer):
    # Automatic retry with exponential backoff
    # Circuit breaker pattern
    # Graceful degradation
```

### 4. Monitoring & Metrics

```python
class MonitoredSourcer(BaseSourcer):
    # Prometheus metrics
    # Logging
    # Performance tracking
```

## 🔧 API Enhancements

### Generic Fetch Endpoint

```python
@app.post("/api/sources/fetch")
async def fetch_from_source(request: GenericSourceRequest):
    # Dynamic sourcer creation
    # Support all sourcer types
    # Unified response format
```

### Batch Processing

```python
@app.post("/api/sources/batch")
async def fetch_multiple_sources(requests: List[SourceRequest]):
    # Concurrent fetching from multiple sources
    # Aggregated results
```

### Webhooks

```python
@app.post("/api/sources/webhook")
async def register_webhook(webhook: WebhookConfig):
    # Push-based updates
    # Event-driven architecture
```

## 📦 Dependencies to Add

```toml
[project]
dependencies = [
    # Current
    "fastapi==0.109.0",
    "uvicorn[standard]==0.27.0",
    "feedparser==6.0.11",

    # Phase 2
    "beautifulsoup4",      # Web scraping
    "httpx",               # Async HTTP client
    "tweepy",              # Twitter API
    "praw",                # Reddit API
    "sqlalchemy",          # Database support

    # Phase 3
    "redis",               # Caching
    "celery",              # Task scheduling
    "pydantic-settings",   # Configuration management
]
```

## 🎯 Immediate Next Actions

1. **Choose next sourcer to implement** (recommend: Web Scraper or API Sourcer)
2. **Add error handling** to existing RSS sourcer
3. **Implement caching** for RSS feeds to reduce API calls
4. **Create sourcer registry** for dynamic sourcer creation
5. **Add more comprehensive tests**

## 💡 Use Case Examples

### Intelligence Dashboard

```python
pipeline = SourcerPipeline([
    RSSSourcer("https://techcrunch.com/feed/"),
    TwitterSourcer(query="#AI"),
    RedditSourcer(subreddit="technology"),
    NewsAPISourcer(query="artificial intelligence"),
])

contents = await pipeline.fetch()
# Process and display on dashboard
```

### Market Intelligence

```python
pipeline = SourcerPipeline([
    RSSSourcer("https://seekingalpha.com/feed.xml"),
    TwitterSourcer(query="$AAPL OR $GOOGL"),
    RedditSourcer(subreddit="wallstreetbets"),
])

# Real-time market sentiment analysis
```

### Competitive Analysis

```python
pipeline = SourcerPipeline([
    WebScraperSourcer(url="competitor.com/blog"),
    TwitterSourcer(username="competitor_official"),
    RedditSourcer(query="competitor_name"),
])

# Track competitor activities and mentions
```
