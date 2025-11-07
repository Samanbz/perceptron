# Sourcer Pipeline - Quick Reference

## 🚀 Quick Start

### 1. Run the Example

```bash
python3 example_usage.py
```

### 2. Run Tests

```bash
python3 test_sourcers.py
```

### 3. Start the API Server

```bash
./run.sh
# Visit http://localhost:8000/docs
```

### 4. Test API Endpoint

```bash
# Example endpoint
curl http://localhost:8000/api/sources/rss/example

# Custom RSS feed
curl -X POST http://localhost:8000/api/sources/rss/fetch \
  -H "Content-Type: application/json" \
  -d '{"feed_url": "https://news.ycombinator.com/rss", "max_entries": 10}'
```

## 📝 Code Examples

### Basic Usage

```python
from sourcers import RSSSourcer

# Create sourcer
sourcer = RSSSourcer(
    feed_url="https://techcrunch.com/feed/",
    max_entries=10
)

# Fetch content
contents = await sourcer.fetch()

# Access data
for content in contents:
    print(content.title)
    print(content.url)
    print(content.to_dict())  # Convert to dict
```

### Multiple Feeds

```python
import asyncio
from sourcers import RSSSourcer

async def fetch_all():
    feeds = [
        RSSSourcer("https://techcrunch.com/feed/", max_entries=5),
        RSSSourcer("https://news.ycombinator.com/rss", max_entries=5),
    ]

    results = await asyncio.gather(*[f.fetch() for f in feeds])
    return [item for sublist in results for item in sublist]

contents = asyncio.run(fetch_all())
```

### Custom Sourcer

```python
from sourcers.base import BaseSourcer, SourcedContent

class MySourcer(BaseSourcer):
    def __init__(self, config):
        super().__init__(name="MySourcer")
        self.config = config

    def validate_config(self, **kwargs):
        # Validate configuration
        return True

    async def fetch(self, **kwargs):
        # Implement fetching logic
        return [
            SourcedContent(
                title="Example",
                content="Content here",
                url="https://example.com"
            )
        ]
```

## 📚 API Reference

### SourcedContent

| Field            | Type      | Description                 |
| ---------------- | --------- | --------------------------- |
| `title`          | str       | Content title               |
| `content`        | str       | Main content text           |
| `url`            | str?      | Source URL (optional)       |
| `published_date` | datetime? | Publication date (optional) |
| `author`         | str?      | Author name (optional)      |
| `metadata`       | dict      | Additional metadata         |
| `retrieved_at`   | datetime  | Fetch timestamp             |

### RSSSourcer

```python
RSSSourcer(
    feed_url: str,           # Required: RSS feed URL
    name: str = None,        # Optional: Sourcer name
    max_entries: int = 50    # Optional: Max entries to fetch
)
```

## 🔧 Common Tasks

### Add New Sourcer

1. Copy `sourcers/template_sourcer.py`
2. Rename and implement `fetch()` and `validate_config()`
3. Add to `sourcers/__init__.py`
4. Test with `test_sourcers.py`

### Add API Endpoint

```python
# In app.py
@app.post("/api/sources/mysource/fetch")
async def fetch_my_source(request: MyRequest):
    sourcer = MySourcer(...)
    contents = await sourcer.fetch()
    return contents
```

### Handle Errors

```python
try:
    sourcer = RSSSourcer(feed_url="https://example.com/feed")
    contents = await sourcer.fetch()
except ValueError as e:
    # Configuration error
    print(f"Config error: {e}")
except Exception as e:
    # Fetch error
    print(f"Fetch error: {e}")
```

## 📖 Documentation Files

| File              | Purpose                                  |
| ----------------- | ---------------------------------------- |
| `README.md`       | Main project documentation               |
| `SOURCERS.md`     | Detailed sourcer pipeline docs           |
| `ROADMAP.md`      | Implementation roadmap & future features |
| `ARCHITECTURE.py` | Visual architecture diagrams             |
| `QUICKREF.md`     | This file - quick reference              |

## 🎯 Popular RSS Feeds

```python
FEEDS = {
    "tech": [
        "https://techcrunch.com/feed/",
        "https://news.ycombinator.com/rss",
        "https://www.theverge.com/rss/index.xml",
    ],
    "news": [
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "https://feeds.bbci.co.uk/news/rss.xml",
    ],
    "finance": [
        "https://www.ft.com/?format=rss",
        "https://seekingalpha.com/feed.xml",
    ]
}
```

## 🐛 Troubleshooting

### Import Errors

```bash
# Make sure you're in the backend directory
cd backend/

# Install dependencies
pip install feedparser
```

### API Not Working

```bash
# Check if server is running
curl http://localhost:8000/api/health

# Restart server
./run.sh
```

### Feed Parsing Fails

- Check feed URL is valid
- Some feeds may be malformed but still work
- Try with a known-good feed first (e.g., TechCrunch)

## 🔗 Useful Links

- FastAPI Docs: https://fastapi.tiangolo.com/
- feedparser Docs: https://feedparser.readthedocs.io/
- API Interactive Docs: http://localhost:8000/docs

## 📞 Support

Issues? Check:

1. `SOURCERS.md` - Detailed documentation
2. `example_usage.py` - Working examples
3. `test_sourcers.py` - Test suite
4. API docs at `/docs` endpoint
