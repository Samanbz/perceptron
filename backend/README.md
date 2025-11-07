# Perceptron Backend# Signal Radar Backend



Modular NLP pipeline for monitoring RSS feeds, extracting keywords, and tracking trends across different team perspectives.FastAPI-based REST API for the Deutsche Bank Signal Radar intelligence dashboard with a complete **data ingestion and storage pipeline** for NLP/ML processing.



## Quick Start## 🚀 Features



```bash- **Modular Sourcer Pipeline** - Fetch content from RSS feeds, web pages, APIs

# Install dependencies- **Data Lake** - Persistent storage with automatic deduplication

pip install -r requirements.txt- **Perpetual Monitoring** - Scheduler for automatic content fetching

- **NLP-Ready** - Optimized for TF-IDF, sentiment analysis, entity detection

# Download spaCy model- **REST API** - Full API for data lake management

python -m spacy download en_core_web_md

## Quick Start (Hackathon Mode 🏃‍♂️)

# Initialize databases from config.json

python scripts/setup_teams.py init```bash

python scripts/setup_data_lake.py init# Make scripts executable (first time only)

python scripts/setup_keywords.py initchmod +x run.sh format.sh



# Fetch initial data# Start the backend (handles venv, dependencies, and server startup)

python scripts/setup_data_lake.py fetch./run.sh

```

# Run the application

./run.shThe API will be available at:

```

- **API:** `http://localhost:8000`

## Project Structure- **Interactive Docs:** `http://localhost:8000/docs`

- **Alternative Docs:** `http://localhost:8000/redoc`

```

backend/## Manual Setup

├── app.py                      # FastAPI application (main entry point)

├── config.json                 # Single source of truth for teams & sourcesIf you prefer to set up manually:

├── api_models.py               # Pydantic models for API responses

├── scheduler.py                # Perpetual monitoring scheduler```bash

│# Create virtual environment

├── sourcers/                   # Content sourcing modulespython3 -m venv venv

│   ├── base.py                 # Base sourcer interface

│   └── rss_sourcer.py          # RSS feed implementation# Activate it

│source venv/bin/activate  # On macOS/Linux

├── storage/                    # Data lake storage# or

│   ├── models.py               # Content & source config modelsvenv\Scripts\activate     # On Windows

│   └── repository.py           # Database operations

│# Install dependencies (including dev dependencies)

├── keywords/                   # Keyword extraction & analysispip install -e ".[dev]"

│   ├── models.py               # Keyword database models

│   ├── extractor.py            # Multi-method extraction (TF-IDF, spaCy, YAKE)# Run the server

│   ├── processor.py            # Real-time processing pipelineuvicorn app:app --reload --port 8000

│   ├── repository.py           # Keyword database operations```

│   └── importance_models.py    # Importance & sentiment tracking

│## API Endpoints

├── teams/                      # Team-based configuration

│   ├── models.py               # Team & source models### Core Endpoints

│   └── repository.py           # Team data access

│- `GET /` - Root endpoint

├── data/                       # SQLite databases (generated)- `GET /api/health` - Health check

│   ├── sourcer_pipeline.db     # Content & sources- `GET /api/hello` - Hello world example

│   ├── keywords.db             # Extracted keywords

│   └── teams.db                # Team configurations### Sourcer Pipeline Endpoints

│

├── mock_data/                  # Mock JSON for frontend development- `POST /api/sources/rss/fetch` - Fetch entries from any RSS feed

│- `GET /api/sources/rss/example` - Fetch from example RSS feed (TechCrunch)

├── scripts/                    # Setup, test, and demo scripts

│   ├── setup_teams.py          # Initialize teams from config.json### Data Lake Endpoints

│   ├── setup_data_lake.py      # Initialize content database

│   ├── setup_keywords.py       # Initialize keywords database- `POST /api/datalake/sources/add` - Add source to monitor

│   ├── test_*.py               # Test scripts- `GET /api/datalake/sources/list` - List all configured sources

│   └── demo_*.py               # Demo scripts- `POST /api/datalake/fetch-and-store` - Fetch and store with deduplication

│- `GET /api/datalake/stats` - Get database statistics

└── docs/                       # Documentation- `GET /api/datalake/content/unprocessed` - Get content ready for NLP processing

    ├── SINGLE_SOURCE_OF_TRUTH.md  # Config.json guide- `POST /api/datalake/content/{id}/mark-processed` - Mark content as processed

    ├── CONFIG_GUIDE.md            # Complete configuration reference

    ├── FRONTEND_GUIDE.md          # API documentation for frontend📖 **See [DATA_LAKE.md](DATA_LAKE.md) for comprehensive data lake documentation.**  

    ├── FRONTEND_QUICKSTART.md     # Quick frontend integration📖 **See [SOURCERS.md](SOURCERS.md) for detailed sourcer pipeline documentation.**  

    └── TEAM_SYSTEM_SUMMARY.md     # Architecture overview📖 **See [SUMMARY.md](SUMMARY.md) for implementation summary.**

```

## Data Lake & NLP Pipeline

## Key Features

### Initialize Data Lake

### 1. Single Source of Truth (`config.json`)

All teams, RSS sources, and keyword extraction settings are defined in one JSON file:```bash

- 4 teams: Regulatory, Investment, Competitive Intelligence, Research# Create database and add example sources

- 13 RSS feed sourcespython3 setup_data_lake.py init

- Team-specific keyword extraction thresholds

- Team-specific sentiment analysis settings# Fetch from all configured sources

python3 setup_data_lake.py fetch

See: `docs/SINGLE_SOURCE_OF_TRUTH.md`

# View statistics

### 2. Modular Sourcing Pipelinepython3 setup_data_lake.py stats

- RSS feed scraping with `feedparser````

- Automatic deduplication (SHA-256 content hashing)

- Perpetual monitoring with configurable intervals### Perpetual Monitoring

- Metadata tracking (published date, author, tags)

```bash

See: `docs/SOURCERS.md`# Run scheduler for automatic periodic fetching

python3 scheduler.py

### 3. Sophisticated Keyword Extraction```

- Multi-method approach: TF-IDF, spaCy NLP, YAKE

- Multi-word phrase detectionThe scheduler will:

- Stopword filtering

- Team-specific relevance thresholds- Automatically fetch from configured sources on schedule

- Real-time processing as content arrives- Deduplicate content using SHA-256 hashing

- Track statistics and errors

See: `docs/KEYWORD_EXTRACTION.md`- Update next fetch times



### 4. Importance & Sentiment Tracking### Process Content for NLP

- Multi-signal importance scoring:

  - Frequency (30%)```bash

  - Velocity (25%)# Run example NLP processing

  - Source diversity (20%)python3 example_nlp_processing.py process

  - Recency (15%)

  - Sentiment magnitude (10%)# Analyze trends

- Sentiment analysis (VADER/TextBlob)python3 example_nlp_processing.py trends

- Time-series data for trending```



See: `docs/TEAM_SYSTEM_SUMMARY.md`**Ready for:**



### 5. Team-Based Filtering- TF-IDF word frequency analysis

- Each team sees only relevant sources- Sentiment analysis

- Different keyword extraction settings per team- Entity detection

- Proactive threat/trend detection- Topic modeling

- Word cloud visualization support- Any NLP/ML pipeline



See: `docs/CONFIG_GUIDE.md`## Sourcer Pipeline



## ConfigurationThe backend includes a modular data sourcing pipeline that can fetch content from various sources. Currently supports:



### Edit Teams & Sources- **RSS Feeds** - Fetch articles from any RSS/Atom feed



```bash### Quick Example

# 1. Edit the single source of truth

vim config.json```python

from sourcers import RSSSourcer

# 2. Validate changes

python scripts/setup_teams.py validatesourcer = RSSSourcer(

    feed_url="https://techcrunch.com/feed/",

# 3. Apply changes    max_entries=10

python scripts/setup_teams.py init)

```

contents = await sourcer.fetch()

### Add a New Teamfor content in contents:

    print(f"{content.title} - {content.url}")

Add to `config.json`:```

```json

{### Test the Pipeline

  "team_key": "legal",

  "team_name": "Legal Team",```bash

  "description": "Monitors legal developments",# Run the example script

  "color": "#DC2626",python3 example_usage.py

  "icon": "gavel",

  "is_active": true,# Run tests

  "keyword_config": {python3 test_sourcers.py

    "relevance_threshold": 0.55,```

    "min_frequency": 2,

    "max_keywords_per_day": 60,## Code Formatting

    "enable_multi_word_phrases": true,

    "max_phrase_length": 4,This project uses **black** and **isort** for Python code formatting.

    "filter_stopwords": true,

    "methods": ["tfidf", "spacy"]### Format Code

  },

  "sentiment_config": {```bash

    "enable_sentiment": true,./format.sh

    "sentiment_method": "vader",```

    "importance_weight": 0.1

  },Or manually:

  "sources": [...]

}```bash

```isort .

black .

Then run: `python scripts/setup_teams.py init````



## API Endpoints (Planned)### Pre-commit Hooks (Optional)



```To automatically format code before commits:

GET  /api/teams                              # List all teams

GET  /api/keywords/wordcloud?team={key}      # Get word cloud data```bash

GET  /api/keywords/timeseries?keyword={word} # Get time-series datapre-commit install

GET  /api/sources                            # List all sources```

POST /api/content/fetch                      # Trigger manual fetch

```## Development



See: `docs/FRONTEND_GUIDE.md`The server runs with hot-reload enabled by default. Just save your files and the server will restart automatically.



## Development### Key Features



### Run Tests- ⚡ **FastAPI** - Modern, fast, async Python web framework

```bash- 📚 **Auto-generated docs** - Interactive API documentation at `/docs`

python scripts/test_sourcers.py- 🔄 **Hot reload** - Changes reflected immediately

python scripts/test_keyword_extraction.py- 🎨 **Formatted code** - Black & isort configured via pyproject.toml

python scripts/test_team_config.py

```## Project Structure



### View Statistics```

```bashbackend/

python scripts/setup_data_lake.py stats├── app.py                          # Main FastAPI application

python scripts/setup_keywords.py stats├── sourcers/                       # Data sourcing pipeline

python scripts/setup_teams.py stats│   ├── __init__.py                # Package exports

```│   ├── base.py                    # BaseSourcer and SourcedContent

│   ├── rss_sourcer.py             # RSS feed implementation

### Reset Everything│   └── template_sourcer.py        # Template for new sourcers

```bash├── storage/                        # Data lake storage layer

python scripts/reset_databases.py│   ├── __init__.py                # Package exports

```│   ├── models.py                  # Database models

│   └── repository.py              # Data access layer

## Tech Stack├── data/                           # SQLite database

│   └── sourcer_pipeline.db

- **FastAPI** 0.109.0 - REST API framework├── scheduler.py                    # Perpetual fetching service

- **SQLAlchemy** 2.0.44 - ORM for SQLite databases├── setup_data_lake.py              # Data lake setup & management

- **feedparser** 6.0.11 - RSS/Atom feed parsing├── example_usage.py                # Sourcer usage examples

- **scikit-learn** - TF-IDF keyword extraction├── example_nlp_processing.py       # NLP processing examples

- **spaCy** - NLP (named entities, noun phrases)├── test_sourcers.py                # Sourcer tests

- **YAKE** - Keyword extraction algorithm├── pyproject.toml                  # Project config & dependencies

- **Pydantic** - API data validation├── run.sh                          # Quick start script

├── format.sh                       # Code formatting script

## Documentation├── README.md                       # This file

├── DATA_LAKE.md                    # Data lake documentation

- **[Single Source of Truth](docs/SINGLE_SOURCE_OF_TRUTH.md)** - Config.json guide├── SOURCERS.md                     # Sourcer pipeline documentation

- **[Configuration Guide](docs/CONFIG_GUIDE.md)** - Complete reference├── SUMMARY.md                      # Implementation summary

- **[Frontend Integration](docs/FRONTEND_GUIDE.md)** - API documentation├── ROADMAP.md                      # Future features

- **[Frontend Quickstart](docs/FRONTEND_QUICKSTART.md)** - Quick start guide└── QUICKREF.md                     # Quick reference

- **[Team System](docs/TEAM_SYSTEM_SUMMARY.md)** - Architecture overview```

- **[Data Lake](docs/DATA_LAKE.md)** - Storage design

- **[Keyword Extraction](docs/KEYWORD_EXTRACTION.md)** - NLP pipeline## Why FastAPI?



## License- **Fast:** High performance, on par with NodeJS and Go

- **Modern:** Python 3.11+ with type hints

MIT- **Auto docs:** Interactive API documentation out of the box

- **Standards-based:** Based on OpenAPI and JSON Schema
