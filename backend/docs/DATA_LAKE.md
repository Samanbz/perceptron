# Data Lake Architecture

## Overview

The data lake is designed for **scalable content ingestion, storage, and processing** for downstream NLP/ML tasks like TF-IDF, sentiment analysis, entity detection, etc.

## Key Features

✅ **Automatic Deduplication** - Content hashing prevents storing duplicates  
✅ **Rich Metadata** - Tracks source type, source name, dates, authors, etc.  
✅ **Scheduled Fetching** - Periodic automatic fetching from configured sources  
✅ **Processing Flags** - Track which content has been processed  
✅ **Flexible Storage** - SQLite (dev) → PostgreSQL (production)  
✅ **Fast Queries** - Indexed fields for efficient retrieval

---

## Database Schema

### `sourced_content` Table

Stores all fetched content with full metadata.

| Field               | Type         | Description                      | Indexed    |
| ------------------- | ------------ | -------------------------------- | ---------- |
| `id`                | Integer      | Primary key                      | ✓          |
| `content_hash`      | String(64)   | SHA-256 hash for deduplication   | ✓ (unique) |
| `title`             | String(500)  | Content title                    |            |
| `content`           | Text         | Full content text                |            |
| `url`               | String(2048) | Source URL                       | ✓          |
| `source_type`       | String(50)   | Type: 'rss', 'web', 'api', etc.  | ✓          |
| `source_name`       | String(200)  | Name: 'TechCrunch', 'HN', etc.   | ✓          |
| `source_url`        | String(2048) | Original feed/API URL            |            |
| `author`            | String(200)  | Author name                      |            |
| `published_date`    | DateTime     | When content was published       | ✓          |
| `retrieved_at`      | DateTime     | When we fetched it               | ✓          |
| `extra_metadata`    | JSON         | Additional source-specific data  |            |
| `processed`         | Boolean      | Has this been processed?         | ✓          |
| `processing_status` | String(50)   | 'pending', 'completed', 'failed' | ✓          |
| `created_at`        | DateTime     | Record creation time             |            |
| `updated_at`        | DateTime     | Record update time               |            |

**Composite Indexes:**

- `(source_type, published_date)` - For time-series queries by source
- `(processed, processing_status)` - For batch processing queries
- `retrieved_at` - For recent content queries

### `source_configs` Table

Tracks which sources to monitor and their schedules.

| Field                    | Type         | Description                   |
| ------------------------ | ------------ | ----------------------------- |
| `id`                     | Integer      | Primary key                   |
| `source_type`            | String(50)   | Type of source                |
| `source_name`            | String(200)  | Source name                   |
| `source_url`             | String(2048) | Source URL (unique with type) |
| `config`                 | JSON         | Source-specific config        |
| `enabled`                | Boolean      | Is monitoring enabled?        |
| `fetch_interval_minutes` | Integer      | How often to fetch            |
| `last_fetched_at`        | DateTime     | Last fetch time               |
| `next_fetch_at`          | DateTime     | Next scheduled fetch          |
| `total_items_fetched`    | Integer      | Total items ever fetched      |
| `last_fetch_count`       | Integer      | Items in last fetch           |
| `last_error`             | Text         | Last error message            |
| `created_at`             | DateTime     | Record creation time          |
| `updated_at`             | DateTime     | Record update time            |

### `processing_jobs` Table

Tracks batch processing operations (TF-IDF, sentiment, etc.).

| Field             | Type        | Description                       |
| ----------------- | ----------- | --------------------------------- |
| `id`              | Integer     | Primary key                       |
| `job_type`        | String(50)  | 'tfidf', 'sentiment', 'entities'  |
| `job_name`        | String(200) | Human-readable name               |
| `content_filter`  | JSON        | Filters applied                   |
| `items_processed` | Integer     | How many items processed          |
| `items_total`     | Integer     | Total items to process            |
| `status`          | String(50)  | 'pending', 'running', 'completed' |
| `error_message`   | Text        | Error if failed                   |
| `results`         | JSON        | Processing results                |
| `started_at`      | DateTime    | When job started                  |
| `completed_at`    | DateTime    | When job finished                 |
| `created_at`      | DateTime    | Record creation time              |

---

## Deduplication Strategy

### Content Hashing

Each piece of content is hashed using **SHA-256** based on:

- Normalized content (whitespace removed)
- URL (if available)

```python
def compute_content_hash(content: str, url: str = None) -> str:
    normalized_content = " ".join(content.split())
    hash_input = normalized_content
    if url:
        hash_input += f"|{url}"
    return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
```

### Why This Works

- **Same article, different fetch times** → Same hash, stored once
- **Same article, different sources** → Different URL, stored separately (good for cross-source analysis)
- **Similar but not identical content** → Different hash, stored separately

---

## Perpetual Data Collection

### Scheduler Service

The `scheduler.py` service runs continuously and:

1. Checks database for sources due for fetching
2. Fetches content using appropriate sourcer
3. Stores with automatic deduplication
4. Updates fetch statistics
5. Schedules next fetch

**Running the Scheduler:**

```bash
python scheduler.py
```

**Configuration:**

- Check interval: 60 seconds (configurable)
- Fetch intervals: Per-source (30-60 minutes typical)
- Error handling: Continues on failure, logs errors

### Adding Sources to Monitor

**Via API:**

```bash
curl -X POST http://localhost:8000/api/datalake/sources/add \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "rss",
    "source_name": "Reuters Tech",
    "source_url": "https://www.reutersagency.com/feed/?best-topics=tech",
    "fetch_interval_minutes": 45,
    "config": {"max_entries": 30}
  }'
```

**Via Python:**

```python
from storage import SourceConfigRepository

repo = SourceConfigRepository()
repo.add_source(
    source_type="rss",
    source_name="Reuters Tech",
    source_url="https://www.reutersagency.com/feed/?best-topics=tech",
    fetch_interval_minutes=45,
    config={"max_entries": 30}
)
```

---

## Metadata Tracking

### Core Metadata (Always Captured)

1. **Source Type** - 'rss', 'web', 'api', 'twitter', etc.
2. **Source Name** - Human-readable identifier
3. **Source URL** - Original feed/API endpoint
4. **Published Date** - When content was originally published
5. **Retrieved Date** - When we fetched it
6. **Author** - Content author (if available)
7. **Content Hash** - For deduplication

### Extended Metadata (Source-Specific)

Stored in `extra_metadata` JSON field:

**RSS Sources:**

```json
{
  "feed_title": "TechCrunch",
  "feed_url": "https://techcrunch.com/feed/",
  "entry_id": "https://techcrunch.com/?p=12345",
  "tags": ["ai", "startup", "funding"]
}
```

**Future Web Sources:**

```json
{
  "scraped_selectors": [".article-content", "h1.title"],
  "page_language": "en",
  "word_count": 1500
}
```

**Future API Sources:**

```json
{
  "api_endpoint": "/v1/articles",
  "api_version": "2.0",
  "rate_limit_remaining": 4500
}
```

---

## Query Patterns for NLP/ML

### Get Unprocessed Content

```python
from storage import ContentRepository

repo = ContentRepository()

# Get 1000 items ready for processing
items = repo.get_unprocessed_content(limit=1000)

for item in items:
    # Do TF-IDF, sentiment analysis, etc.
    process_content(item.content)

    # Mark as processed
    repo.mark_as_processed(item.id, status='completed')
```

### Get Content by Date Range

```python
from datetime import datetime, timedelta

# Get last 7 days of content
start_date = datetime.now() - timedelta(days=7)
items = repo.get_content_by_date_range(start_date)

# Time-series sentiment analysis
sentiments = [analyze_sentiment(item.content) for item in items]
```

### Filter by Source Type

```python
# Get only RSS content for TF-IDF
items = repo.get_unprocessed_content(limit=5000, source_type='rss')

# Build TF-IDF corpus
corpus = [item.content for item in items]
tfidf_vectorizer.fit(corpus)
```

### Batch Processing Pattern

```python
BATCH_SIZE = 100

while True:
    batch = repo.get_unprocessed_content(limit=BATCH_SIZE)
    if not batch:
        break

    for item in batch:
        results = run_nlp_pipeline(item.content)
        save_results(item.id, results)
        repo.mark_as_processed(item.id)
```

---

## API Endpoints

### Data Lake Management

| Endpoint                                    | Method | Description                 |
| ------------------------------------------- | ------ | --------------------------- |
| `/api/datalake/sources/add`                 | POST   | Add source to monitor       |
| `/api/datalake/sources/list`                | GET    | List all sources            |
| `/api/datalake/fetch-and-store`             | POST   | Fetch & store from RSS feed |
| `/api/datalake/stats`                       | GET    | Database statistics         |
| `/api/datalake/content/unprocessed`         | GET    | Get unprocessed content     |
| `/api/datalake/content/{id}/mark-processed` | POST   | Mark item as processed      |

### Usage Examples

**Add Source:**

```bash
POST /api/datalake/sources/add
{
  "source_type": "rss",
  "source_name": "BBC News",
  "source_url": "https://feeds.bbci.co.uk/news/rss.xml",
  "fetch_interval_minutes": 30
}
```

**Get Unprocessed Content:**

```bash
GET /api/datalake/content/unprocessed?limit=100&source_type=rss
```

**Get Statistics:**

```bash
GET /api/datalake/stats

Response:
{
  "total_content": 5432,
  "processed": 3210,
  "unprocessed": 2222,
  "by_source_type": {
    "rss": 5432
  }
}
```

---

## Processing Workflow for NLP/ML

### 1. TF-IDF Analysis

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from storage import ContentRepository

repo = ContentRepository()
items = repo.get_unprocessed_content(limit=10000, source_type='rss')

# Build corpus
corpus = [item.content for item in items]

# TF-IDF
vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
tfidf_matrix = vectorizer.fit_transform(corpus)

# Get top keywords for each document
feature_names = vectorizer.get_feature_names_out()
for i, item in enumerate(items):
    top_indices = tfidf_matrix[i].toarray()[0].argsort()[-10:][::-1]
    top_keywords = [feature_names[idx] for idx in top_indices]

    # Store results
    item.extra_metadata['tfidf_keywords'] = top_keywords
    repo.mark_as_processed(item.id)
```

### 2. Sentiment Analysis

```python
from textblob import TextBlob

for item in items:
    blob = TextBlob(item.content)
    sentiment = {
        'polarity': blob.sentiment.polarity,
        'subjectivity': blob.sentiment.subjectivity
    }

    # Store results in extra_metadata
    item.extra_metadata['sentiment'] = sentiment
    repo.mark_as_processed(item.id)
```

### 3. Entity Detection

```python
import spacy

nlp = spacy.load("en_core_web_sm")

for item in items:
    doc = nlp(item.content)
    entities = [
        {'text': ent.text, 'label': ent.label_}
        for ent in doc.ents
    ]

    item.extra_metadata['entities'] = entities
    repo.mark_as_processed(item.id)
```

---

## Scaling Considerations

### Development (Current Setup)

- **Database**: SQLite
- **Storage**: Local filesystem
- **Good for**: <100K articles, single server

### Production (Recommended)

- **Database**: PostgreSQL or TimescaleDB
- **Storage**: S3/GCS for full content, DB for metadata
- **Caching**: Redis for frequent queries
- **Message Queue**: Celery + RabbitMQ for background processing
- **Monitoring**: Prometheus + Grafana

### Migration to PostgreSQL

```python
# In storage/models.py, change:
def get_database_url(db_path: str = None) -> str:
    if db_path:
        return f"sqlite:///{db_path}"
    else:
        # PostgreSQL
        return "postgresql://user:pass@localhost:5432/sourcer_pipeline"
```

---

## Best Practices

### 1. Regular Cleanup

```python
# Delete content older than 90 days
from datetime import timedelta
cutoff_date = datetime.now() - timedelta(days=90)
old_items = repo.get_content_by_date_range(datetime.min, cutoff_date)
for item in old_items:
    if item.processed:
        session.delete(item)
```

### 2. Error Handling

```python
try:
    contents = await sourcer.fetch()
    stats = repo.save_batch(contents, ...)
except Exception as e:
    logger.error(f"Fetch failed: {e}")
    config_repo.update_fetch_status(source_id, 0, error=str(e))
```

### 3. Rate Limiting

```python
# Add to source config
config = {
    "max_entries": 50,
    "rate_limit_delay": 1.0,  # seconds between requests
}
```

### 4. Monitoring

```python
# Track fetch statistics
stats = repo.get_statistics()
if stats['unprocessed'] > 10000:
    alert("Too many unprocessed items!")
```

---

## Command Line Tools

```bash
# Initialize database with example sources
python setup_data_lake.py init

# Fetch from all configured sources
python setup_data_lake.py fetch

# Show statistics
python setup_data_lake.py stats

# Show recent content
python setup_data_lake.py recent 20

# List all sources
python setup_data_lake.py sources

# Run scheduler (continuous fetching)
python scheduler.py
```

---

## Summary

The data lake provides:

1. ✅ **Automatic deduplication** via content hashing
2. ✅ **Rich metadata** for source tracking and filtering
3. ✅ **Perpetual monitoring** via scheduler
4. ✅ **Efficient querying** with indexed fields
5. ✅ **Processing flags** to track NLP/ML pipeline progress
6. ✅ **Flexible storage** ready for scale

**Ready for:** TF-IDF, sentiment analysis, entity detection, topic modeling, and any other NLP/ML tasks!
