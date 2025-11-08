# Signal Radar Backend

FastAPI-based REST API for the Deutsche Bank Signal Radar intelligence dashboard. Monitors RSS feeds, extracts keywords, and tracks trends across different team perspectives.

## 🚀 Features

- **Multi-Team Intelligence**: Track signals for Regulatory, Investment, Research, and Competitive Intelligence teams
- **RSS Monitoring**: Fetch content from 12+ configured sources (Federal Register, ArXiv, TechCrunch, etc.)
- **NLP Processing**: Extract keywords using TF-IDF, spaCy NER, and YAKE algorithms
- **Importance Scoring**: Rank keywords by contextual relevance, frequency, velocity, and sentiment
- **Time-Series Tracking**: Monitor keyword trends over time
- **REST API**: Full CRUD operations for keywords, teams, and content
- **SQLite Storage**: Lightweight persistent storage with 3 specialized databases

## 📁 Project Structure

```
backend/
├── app.py                      # FastAPI application (main entry point)
├── api_models.py               # Pydantic models for API responses
├── config.json                 # Single source of truth for teams & sources
│
├── sourcers/                   # Content sourcing modules
│   ├── base.py                 # Base sourcer interface
│   └── rss_sourcer.py          # RSS feed implementation
│
├── storage/                    # Data storage
│   ├── models.py               # SQLAlchemy models
│   └── repository.py           # Database operations
│
├── services/                   # Business logic
│   ├── data_sourcing_service.py    # Fetch from RSS sources
│   └── nlp_processing_service.py   # Keyword extraction & scoring
│
├── scripts/                    # Management scripts
│   ├── initialize_system.py    # Setup databases
│   ├── fetch_all_sources.py    # Fetch RSS content
│   ├── process_all_content.py  # Run NLP processing
│   └── export_keywords_json.py # Export data as JSON
│
└── data/                       # SQLite databases
    ├── teams.db                # Team configurations
    ├── sourcer_pipeline.db     # Fetched content
    └── keywords.db             # Extracted keywords
```

## 🔧 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt

# Download spaCy model for NLP
python -m spacy download en_core_web_md
```

### 2. Initialize Databases

```bash
# Setup all databases from config.json
python scripts/initialize_system.py
```

### 3. Fetch Data

```bash
# Fetch documents from all RSS sources
PYTHONPATH=$PWD python scripts/fetch_all_sources.py

# Process documents and extract keywords
PYTHONPATH=$PWD python scripts/process_all_content.py
```

### 4. Start API Server

```bash
# Development mode
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Or use the convenience script
./run.sh
```

The API will be available at `http://localhost:8000`

## 📡 API Endpoints

### Health & Info
- `GET /api/health` - Health check
- `GET /api/teams` - List all teams

### Keywords
- `GET /api/keywords?date=YYYY-MM-DD&team=team_key&limit=50&min_score=0` - Get keywords by date/team
- `GET /api/keywords/stats` - Overall keyword statistics
- `GET /api/keywords/search?q=query&team=team_key&limit=20` - Search keywords

### Content Management
- `GET /api/sources` - List all content sources
- `GET /api/content?team_key=X&limit=10` - Get fetched content
- `POST /api/fetch` - Trigger RSS fetch for a source

### Full API Documentation
Visit `http://localhost:8000/docs` for interactive Swagger UI

## 🔄 Data Pipeline Workflow

```
1. Configure (config.json)
   ↓
2. Initialize (initialize_system.py)
   ↓
3. Fetch (fetch_all_sources.py) 
   → RSS Sources → sourcer_pipeline.db
   ↓
4. Process (process_all_content.py)
   → NLP Extraction → keywords.db
   ↓
5. Serve (app.py)
   → FastAPI → JSON responses
   ↓
6. Export (export_keywords_json.py) [Optional]
   → JSON files for external use
```

## 🧪 Testing

```bash
# Test all API endpoints
python scripts/test_keywords_api.py

# Export last 7 days as JSON
python scripts/export_keywords_json.py
```

## 🛠️ Configuration

Edit `config.json` to:
- Add/remove teams
- Configure RSS sources per team
- Set keyword extraction parameters
- Adjust sentiment analysis settings

Example team configuration:
```json
{
  "team_key": "researcher",
  "team_name": "Research Team",
  "description": "Academic and industry research",
  "sources": ["arxiv_cs", "mit_tech_review"],
  "keyword_config": {
    "max_keywords_per_doc": 10,
    "min_keyword_score": 0.3,
    "methods": ["tfidf", "spacy_ner", "yake"]
  },
  "sentiment_config": {
    "enabled": true,
    "track_velocity": true
  }
}
```

## 📊 Database Schema

### teams.db
- `internal_teams` - Team configurations
- `team_sources` - Source-to-team mappings

### sourcer_pipeline.db
- `sourced_content` - Raw fetched content
- `processing_jobs` - NLP processing queue

### keywords.db
- `extracted_keywords` - Keyword occurrences
- `keyword_importance` - Importance scores
- `keyword_timeseries` - Historical tracking

## 🔐 Environment Variables

```bash
# Optional: Configure database paths
export TEAMS_DB_PATH=./data/teams.db
export SOURCER_DB_PATH=./data/sourcer_pipeline.db
export KEYWORDS_DB_PATH=./data/keywords.db

# Optional: API configuration
export API_HOST=0.0.0.0
export API_PORT=8000
```

## 📝 Scripts Reference

See [scripts/README.md](scripts/README.md) for detailed documentation of all management scripts.

## 🐛 Troubleshooting

**API won't start:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Check uvicorn is installed
pip install uvicorn

# Use full path to venv python
./venv/bin/python -m uvicorn app:app
```

**No data in API:**
```bash
# Verify databases exist
ls -la data/*.db

# Re-run data pipeline
python scripts/initialize_system.py
PYTHONPATH=$PWD python scripts/fetch_all_sources.py
PYTHONPATH=$PWD python scripts/process_all_content.py
```

**RSS fetch failures:**
- Check `config.json` for correct URLs
- Some sources may rate-limit or require different formats
- Review Federal Register API vs search page distinction

## 📦 Dependencies

- FastAPI - Web framework
- uvicorn - ASGI server
- SQLAlchemy - ORM
- feedparser - RSS parsing
- spaCy - NLP processing
- sentence-transformers - Semantic similarity
- YAKE - Keyword extraction
- vaderSentiment - Sentiment analysis
- scikit-learn - TF-IDF

## 📄 License

Proprietary - Deutsche Bank Internal Use

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Run tests: `python scripts/test_keywords_api.py`
4. Format code: `./format.sh`
5. Submit pull request
