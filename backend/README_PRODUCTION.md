# Perceptron Backend - Production Architecture

Clean, production-ready NLP pipeline for keyword extraction, sentiment analysis, and time-series generation.

## Architecture

### 1. Data Sources

- **Configuration**: `config.json` - Defines teams, sources, NLP settings
- **Teams**: 4 active teams (Regulatory, Investment, Competitive Intelligence, Research)
- **Sources**: 13 RSS feeds across all teams

### 2. Perpetual Services

#### Data Sourcing Service (`services/data_sourcing_service.py`)

- Fetches RSS feeds every hour
- Maintains 7-day rolling window
- Auto-cleans old data
- Concurrent fetching for performance

#### NLP Processing Service (`services/nlp_processing_service.py`)

- Processes unprocessed content every 5 minutes
- Runs full NLP pipeline (keywords, importance, sentiment)
- Generates time-series for keyword trends
- Batch processing for efficiency

### 3. NLP Pipeline

#### Enhanced Keyword Processor (`keywords/enhanced_processor.py`)

- Multi-method extraction (TF-IDF, spaCy NER, YAKE)
- 6-signal importance calculation:
  - Frequency distribution (25%)
  - Contextual relevance (20%)
  - Entity boost (15%)
  - Temporal dynamics (20%)
  - Source diversity (10%)
  - Sentiment magnitude (10%)
- Contextual sentiment analysis (VADER + contextual)
- Time-series generation with trend detection

#### Key Models Used

- **spaCy**: en_core_web_md for NER
- **sentence-transformers**: all-MiniLM-L6-v2 for semantic embeddings
- **YAKE**: Statistical keyword extraction
- **VADER**: Sentiment analysis

### 4. API Layer

- **FastAPI** server (`app.py`)
- **Pydantic** models (`api_models.py`) - Contract with frontend
- **Endpoints**:
  - `/wordcloud/{team_key}` - Keyword data for word clouds
  - `/timeseries/{team_key}` - Time-series data for trends
  - `/trending/{team_key}` - Trending keywords over time

## Setup & Usage

### 1. Reset & Initialize

```bash
python3 reset_and_initialize.py
```

This will:

- Drop all existing tables
- Create fresh schema
- Fetch 7 days of historical data
- Process all content through NLP
- Generate initial time-series

### 2. Start Services

Option A: Manual (separate terminals)

```bash
# Terminal 1: Data sourcing
python3 services/data_sourcing_service.py

# Terminal 2: NLP processing
python3 services/nlp_processing_service.py

# Terminal 3: API server
python3 app.py
```

Option B: Startup script (future enhancement)

```bash
python3 start_services.py  # TODO: Make services run perpetually in background
```

### 3. API Access

Once services are running, API available at: `http://localhost:8000`

## Data Flow

```
RSS Sources → Data Sourcing Service → Storage (sourcer_pipeline.db)
                                           ↓
                                      Unprocessed Content
                                           ↓
                            NLP Processing Service
                                           ↓
                    ┌──────────────────────┴──────────────────────┐
                    ↓                      ↓                       ↓
              Keywords              Importance               Sentiment
           (keywords.db)          + Timeseries            + Context
                                           ↓
                                    API Service
                                           ↓
                                 Frontend (api_models.py)
```

## Configuration

### Team Configuration (`config.json`)

```json
{
  "team_key": "regulator",
  "team_name": "Regulatory Team",
  "keyword_config": {
    "relevance_threshold": 0.45,
    "min_frequency": 2,
    "methods": ["tfidf", "spacy", "yake"]
  },
  "sentiment_config": {
    "enable_sentiment": true,
    "sentiment_method": "vader"
  },
  "sources": [...]
}
```

### Service Configuration

- **Data Sourcing**: Fetch interval = 3600s (1 hour)
- **NLP Processing**: Check interval = 300s (5 minutes)
- **Data Retention**: 7 days

## Databases

- `sourcer_pipeline.db`: Raw content storage
- `keywords.db`: Extracted keywords, importance, sentiment, time-series
- `teams.db`: Team and source configuration (derived from config.json)

## Archived Code

All test, demo, and example scripts moved to `/archive`:

- demo_complete_pipeline.py
- demo_keyword_pipeline.py
- test_keyword_extraction.py
- test_sourcers.py
- test_team_config.py
- example_nlp_processing.py
- example_usage.py
- fetch_historical_data.py

## Key Features

✅ **Perpetual Operation**: Services run continuously, no manual intervention
✅ **7-Day Rolling Window**: Auto-cleanup of old data
✅ **Configurable NLP**: Per-team thresholds and methods
✅ **State-of-the-Art Models**: spaCy, YAKE, sentence-transformers, VADER
✅ **Multi-Signal Importance**: 6 weighted components
✅ **Time-Series Generation**: Tracks keyword trends over time
✅ **API Contract**: api_models.py unchanged (frontend compatibility)

## Next Steps

1. Deploy services to production server
2. Set up process monitoring (systemd/supervisor)
3. Add logging to file for production debugging
4. Consider adding alerting for service failures
5. Optimize RSS feed URLs (some currently failing)
