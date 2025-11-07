# Sourcer Pipeline

A modular data sourcing pipeline for fetching content from various sources.

## Architecture

The pipeline is built around a simple, extensible architecture:

```
sourcers/
├── __init__.py          # Package exports
├── base.py              # BaseSourcer abstract class and SourcedContent model
└── rss_sourcer.py       # RSS feed implementation
```

### Core Components

#### `SourcedContent`

A data class representing content retrieved from any source:

- `title`: Content title
- `content`: Main content text
- `url`: Source URL (optional)
- `published_date`: Publication date (optional)
- `author`: Author name (optional)
- `metadata`: Additional source-specific data
- `retrieved_at`: Timestamp when content was fetched

#### `BaseSourcer`

Abstract base class for all sourcers. Custom sourcers must implement:

- `fetch(**kwargs)`: Fetch content from the source
- `validate_config(**kwargs)`: Validate sourcer configuration

## Available Sourcers

### RSS Sourcer

Fetches content from RSS/Atom feeds.

**Usage:**

```python
from sourcers import RSSSourcer

# Create an RSS sourcer
sourcer = RSSSourcer(
    feed_url="https://techcrunch.com/feed/",
    name="TechCrunch",
    max_entries=20
)

# Fetch content
contents = await sourcer.fetch()

# Access content
for content in contents:
    print(f"{content.title}")
    print(f"Published: {content.published_date}")
    print(f"URL: {content.url}")
    print(f"Content: {content.content[:200]}...")
```

**Parameters:**

- `feed_url` (required): URL of the RSS/Atom feed
- `name` (optional): Custom name for the sourcer
- `max_entries` (optional): Maximum entries to fetch (default: 50)

## API Endpoints

### POST `/api/sources/rss/fetch`

Fetch entries from any RSS feed.

**Request:**

```json
{
  "feed_url": "https://techcrunch.com/feed/",
  "max_entries": 20
}
```

**Response:**

```json
[
  {
    "title": "Article Title",
    "content": "Article content...",
    "url": "https://example.com/article",
    "published_date": "2025-11-07T10:30:00",
    "author": "John Doe",
    "metadata": {
      "feed_title": "TechCrunch",
      "feed_url": "https://techcrunch.com/feed/",
      "tags": ["technology", "startup"]
    },
    "retrieved_at": "2025-11-07T12:00:00"
  }
]
```

### GET `/api/sources/rss/example`

Fetch entries from an example RSS feed (TechCrunch).

**Response:**

```json
{
  "feed_info": {
    "name": "TechCrunch Example",
    "url": "https://techcrunch.com/feed/",
    "entries_fetched": 10
  },
  "entries": [...]
}
```

## Running Examples

### Command Line Example

```bash
# Make sure dependencies are installed
pip install feedparser

# Run the example script
python example_usage.py
```

### API Example

```bash
# Start the server
./run.sh

# In another terminal, test the example endpoint
curl http://localhost:8000/api/sources/rss/example

# Or fetch a custom feed
curl -X POST http://localhost:8000/api/sources/rss/fetch \
  -H "Content-Type: application/json" \
  -d '{"feed_url": "https://news.ycombinator.com/rss", "max_entries": 10}'
```

## Extending the Pipeline

To add a new sourcer type:

1. Create a new file in `sourcers/` (e.g., `web_scraper.py`)
2. Inherit from `BaseSourcer`
3. Implement `fetch()` and `validate_config()` methods
4. Export in `sourcers/__init__.py`

**Example:**

```python
from .base import BaseSourcer, SourcedContent
from typing import List

class WebScraperSourcer(BaseSourcer):
    def __init__(self, url: str, name: str = None):
        super().__init__(name)
        self.url = url
        self.validate_config(url=url)

    def validate_config(self, **kwargs) -> bool:
        url = kwargs.get("url")
        if not url or not url.startswith("http"):
            raise ValueError("Valid URL required")
        return True

    async def fetch(self, **kwargs) -> List[SourcedContent]:
        # Implement web scraping logic
        # Return list of SourcedContent objects
        pass
```

## Future Sourcers

Planned implementations:

- Web page scraper (BeautifulSoup/Playwright)
- API sourcer (generic REST API client)
- Twitter/X sourcer
- Reddit sourcer
- News API sourcer
- Database sourcer
