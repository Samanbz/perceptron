# 🚀 Quick Command Reference

## Database Management

### Initialize Databases

```bash
# Initialize data lake
python setup_data_lake.py init

# Initialize keywords database
python setup_keywords.py init
```

### Reset All Databases

```bash
# Interactive reset (asks for confirmation)
python reset_databases.py

# Force reset (no confirmation)
python reset_databases.py --force
```

## Content Fetching

### Fetch from RSS Sources

```bash
# Fetch once from all active sources
python setup_data_lake.py fetch

# Continuous monitoring (runs in background)
python scheduler.py
```

### View Data Lake Stats

```bash
python setup_data_lake.py stats
```

## Keyword Extraction

### Run Demo Pipeline

```bash
# Process 5 articles (default)
python demo_keyword_pipeline.py

# Process 10 articles
python demo_keyword_pipeline.py 10

# Process ALL content
python demo_keyword_pipeline.py --full
```

### Test Extraction

```bash
# Test on 5 items
python test_keyword_extraction.py

# Test on 20 items
python test_keyword_extraction.py 20
```

### View Keyword Stats

```bash
python setup_keywords.py stats
```

### Manage Configurations

```bash
# List all configurations
python setup_keywords.py config

# Create demo config (lower threshold)
python setup_keywords.py demo

# Activate a configuration
python setup_keywords.py activate default
python setup_keywords.py activate demo
```

## Configuration Files

### Default Configuration

- **Threshold**: 0.7 (high quality keywords)
- **Max keywords**: 50 per document
- **Use case**: Production

### Demo Configuration

- **Threshold**: 0.5 (more keywords)
- **Max keywords**: 100 per document
- **Use case**: Testing and demonstrations

## Typical Workflows

### First Time Setup

```bash
# 1. Initialize databases
python setup_data_lake.py init
python setup_keywords.py init

# 2. Fetch content
python setup_data_lake.py fetch

# 3. Extract keywords (demo mode)
python setup_keywords.py activate demo
python demo_keyword_pipeline.py 10

# 4. Check results
python setup_keywords.py stats
```

### Daily Operations

```bash
# 1. Check for new content
python setup_data_lake.py fetch

# 2. Extract keywords from new content
python demo_keyword_pipeline.py

# 3. View trending keywords
python setup_keywords.py stats
```

### Reset and Start Fresh

```bash
# Complete reset
python reset_databases.py --force

# Re-initialize
python setup_data_lake.py init
python setup_keywords.py init

# Fetch fresh data
python setup_data_lake.py fetch
```

## File Locations

- **Data Lake**: `data/sourcer_pipeline.db`
- **Keywords**: `data/keywords.db`
- **Logs**: Console output (can be redirected)

## API Endpoints (if running app.py)

```bash
# Start the API server
python app.py

# Or use uvicorn
uvicorn app:app --reload
```

- `POST /api/datalake/fetch-and-store` - Fetch from a source
- `GET /api/datalake/content/unprocessed` - Get unprocessed content
- `GET /api/datalake/stats` - Get database statistics

## Tips

### Extract More Keywords

```bash
# Use demo configuration (threshold 0.5)
python setup_keywords.py activate demo
python demo_keyword_pipeline.py 10
```

### Extract Fewer, Higher Quality Keywords

```bash
# Use default configuration (threshold 0.7)
python setup_keywords.py activate default
python demo_keyword_pipeline.py 10
```

### Monitor Performance

```bash
# The demo shows timing for each article
python demo_keyword_pipeline.py 5
```

### Find Trending Keywords

```bash
# Shows top keywords from last 7 days
python setup_keywords.py stats
```

## Dependencies

### Required Packages

- `fastapi` - Web API framework
- `sqlalchemy` - Database ORM
- `feedparser` - RSS/Atom parsing
- `scikit-learn` - TF-IDF extraction
- `spacy` - NLP and NER
- `yake` - Keyphrase extraction

### Install All

```bash
pip install fastapi sqlalchemy feedparser scikit-learn spacy yake
python -m spacy download en_core_web_md
```

## Troubleshooting

### No Content in Database

```bash
python setup_data_lake.py fetch
```

### No Keywords Extracted

```bash
# Lower the threshold
python setup_keywords.py activate demo
python demo_keyword_pipeline.py 5
```

### TF-IDF Errors

- This is normal for single documents
- TF-IDF works better with multiple documents
- spaCy and YAKE still work fine

### Database Locked

```bash
# Close all Python processes accessing the DB
# Or reset databases
python reset_databases.py
```
