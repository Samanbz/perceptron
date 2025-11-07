# Signal Radar Backend

FastAPI-based REST API for the Deutsche Bank Signal Radar intelligence dashboard with a complete **data ingestion and storage pipeline** for NLP/ML processing.

## 🚀 Features

- **Modular Sourcer Pipeline** - Fetch content from RSS feeds, web pages, APIs
- **Data Lake** - Persistent storage with automatic deduplication
- **Perpetual Monitoring** - Scheduler for automatic content fetching
- **NLP-Ready** - Optimized for TF-IDF, sentiment analysis, entity detection
- **REST API** - Full API for data lake management

## Quick Start (Hackathon Mode 🏃‍♂️)

```bash
# Make scripts executable (first time only)
chmod +x run.sh format.sh

# Start the backend (handles venv, dependencies, and server startup)
./run.sh
```

The API will be available at:

- **API:** `http://localhost:8000`
- **Interactive Docs:** `http://localhost:8000/docs`
- **Alternative Docs:** `http://localhost:8000/redoc`

## Manual Setup

If you prefer to set up manually:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies (including dev dependencies)
pip install -e ".[dev]"

# Run the server
uvicorn app:app --reload --port 8000
```

## API Endpoints

### Core Endpoints

- `GET /` - Root endpoint
- `GET /api/health` - Health check
- `GET /api/hello` - Hello world example

### Sourcer Pipeline Endpoints

- `POST /api/sources/rss/fetch` - Fetch entries from any RSS feed
- `GET /api/sources/rss/example` - Fetch from example RSS feed (TechCrunch)

### Data Lake Endpoints

- `POST /api/datalake/sources/add` - Add source to monitor
- `GET /api/datalake/sources/list` - List all configured sources
- `POST /api/datalake/fetch-and-store` - Fetch and store with deduplication
- `GET /api/datalake/stats` - Get database statistics
- `GET /api/datalake/content/unprocessed` - Get content ready for NLP processing
- `POST /api/datalake/content/{id}/mark-processed` - Mark content as processed

📖 **See [DATA_LAKE.md](DATA_LAKE.md) for comprehensive data lake documentation.**  
📖 **See [SOURCERS.md](SOURCERS.md) for detailed sourcer pipeline documentation.**  
📖 **See [SUMMARY.md](SUMMARY.md) for implementation summary.**

## Data Lake & NLP Pipeline

### Initialize Data Lake

```bash
# Create database and add example sources
python3 setup_data_lake.py init

# Fetch from all configured sources
python3 setup_data_lake.py fetch

# View statistics
python3 setup_data_lake.py stats
```

### Perpetual Monitoring

```bash
# Run scheduler for automatic periodic fetching
python3 scheduler.py
```

The scheduler will:

- Automatically fetch from configured sources on schedule
- Deduplicate content using SHA-256 hashing
- Track statistics and errors
- Update next fetch times

### Process Content for NLP

```bash
# Run example NLP processing
python3 example_nlp_processing.py process

# Analyze trends
python3 example_nlp_processing.py trends
```

**Ready for:**

- TF-IDF word frequency analysis
- Sentiment analysis
- Entity detection
- Topic modeling
- Any NLP/ML pipeline

## Sourcer Pipeline

The backend includes a modular data sourcing pipeline that can fetch content from various sources. Currently supports:

- **RSS Feeds** - Fetch articles from any RSS/Atom feed

### Quick Example

```python
from sourcers import RSSSourcer

sourcer = RSSSourcer(
    feed_url="https://techcrunch.com/feed/",
    max_entries=10
)

contents = await sourcer.fetch()
for content in contents:
    print(f"{content.title} - {content.url}")
```

### Test the Pipeline

```bash
# Run the example script
python3 example_usage.py

# Run tests
python3 test_sourcers.py
```

## Code Formatting

This project uses **black** and **isort** for Python code formatting.

### Format Code

```bash
./format.sh
```

Or manually:

```bash
isort .
black .
```

### Pre-commit Hooks (Optional)

To automatically format code before commits:

```bash
pre-commit install
```

## Development

The server runs with hot-reload enabled by default. Just save your files and the server will restart automatically.

### Key Features

- ⚡ **FastAPI** - Modern, fast, async Python web framework
- 📚 **Auto-generated docs** - Interactive API documentation at `/docs`
- 🔄 **Hot reload** - Changes reflected immediately
- 🎨 **Formatted code** - Black & isort configured via pyproject.toml

## Project Structure

```
backend/
├── app.py                          # Main FastAPI application
├── sourcers/                       # Data sourcing pipeline
│   ├── __init__.py                # Package exports
│   ├── base.py                    # BaseSourcer and SourcedContent
│   ├── rss_sourcer.py             # RSS feed implementation
│   └── template_sourcer.py        # Template for new sourcers
├── storage/                        # Data lake storage layer
│   ├── __init__.py                # Package exports
│   ├── models.py                  # Database models
│   └── repository.py              # Data access layer
├── data/                           # SQLite database
│   └── sourcer_pipeline.db
├── scheduler.py                    # Perpetual fetching service
├── setup_data_lake.py              # Data lake setup & management
├── example_usage.py                # Sourcer usage examples
├── example_nlp_processing.py       # NLP processing examples
├── test_sourcers.py                # Sourcer tests
├── pyproject.toml                  # Project config & dependencies
├── run.sh                          # Quick start script
├── format.sh                       # Code formatting script
├── README.md                       # This file
├── DATA_LAKE.md                    # Data lake documentation
├── SOURCERS.md                     # Sourcer pipeline documentation
├── SUMMARY.md                      # Implementation summary
├── ROADMAP.md                      # Future features
└── QUICKREF.md                     # Quick reference
```

## Why FastAPI?

- **Fast:** High performance, on par with NodeJS and Go
- **Modern:** Python 3.11+ with type hints
- **Auto docs:** Interactive API documentation out of the box
- **Standards-based:** Based on OpenAPI and JSON Schema
