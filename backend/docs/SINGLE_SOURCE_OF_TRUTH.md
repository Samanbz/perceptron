# Single Source of Truth - Implementation Summary

## ✅ Complete

You now have a **single JSON file (`config.json`)** as the source of truth for all teams, sources, and keyword configurations.

## What Was Created

### 1. **config.json** - The Single Source of Truth

- **Location**: `/Users/samanb/dev/perceptron/backend/config.json`
- **Size**: 6.2KB
- **Contains**:
  - 4 teams (regulator, investor, competitor, researcher)
  - 13 RSS feed sources (distributed across teams)
  - Keyword extraction configs per team
  - Sentiment analysis configs per team
  - UI settings (colors, icons)

### 2. **setup_teams.py** - Configuration Manager

- **Purpose**: Reads config.json and populates database
- **Commands**:
  ```bash
  python setup_teams.py validate  # Check config.json is valid
  python setup_teams.py init      # Load config into database
  python setup_teams.py show      # Display all teams
  python setup_teams.py stats     # Show statistics
  python setup_teams.py export    # Backup database to JSON
  ```

### 3. **teams/repository.py** - Data Access Layer

- **Purpose**: Clean API to access team configurations
- **Key Methods**:
  - `get_all_teams()` - List all teams
  - `get_team_by_key(team_key)` - Get specific team
  - `get_team_sources(team_key)` - Get team's RSS feeds
  - `get_keyword_config(team_key)` - Get extraction settings
  - `get_team_list_for_api()` - Frontend-ready team list

### 4. **data/teams.db** - Runtime Database

- **Size**: 24KB
- **Tables**: internal_teams, team_sources
- **Purpose**: Fast query access (populated from config.json)

## How It Works

```
┌─────────────────┐
│  config.json    │  ← Single source of truth (edit this!)
└────────┬────────┘
         │ setup_teams.py init
         ▼
┌─────────────────┐
│  data/teams.db  │  ← Runtime database (generated)
└────────┬────────┘
         │ TeamRepository
         ▼
┌─────────────────┐
│  Application    │  ← Your keyword pipeline
└─────────────────┘
```

## Configuration Structure

### Team Definition

```json
{
  "team_key": "regulator", // Unique ID
  "team_name": "Regulatory Team", // Display name
  "description": "...", // What this team monitors
  "color": "#DC2626", // UI color (red)
  "icon": "balance", // Material icon
  "is_active": true, // Enable/disable

  "keyword_config": {
    "relevance_threshold": 0.45, // Min score (0-1)
    "min_frequency": 2, // Must appear N times
    "max_keywords_per_day": 100, // Daily limit
    "enable_multi_word_phrases": true, // "venture capital"
    "max_phrase_length": 4, // Max words in phrase
    "filter_stopwords": true, // Remove "the", "and"
    "methods": ["tfidf", "spacy", "yake"] // Extraction methods
  },

  "sentiment_config": {
    "enable_sentiment": true, // Enable sentiment
    "sentiment_method": "vader", // VADER or TextBlob
    "importance_weight": 0.1 // Sentiment weight
  },

  "sources": [
    {
      "source_type": "rss",
      "source_name": "Federal Register",
      "source_url": "https://...",
      "fetch_interval_minutes": 60,
      "config": { "max_entries": 50 }
    }
  ]
}
```

## Current Configuration

### 4 Teams Configured:

1. **Regulatory Team** (`regulator`) - Red

   - 3 sources: Federal Register, SEC, Reuters
   - Threshold: 0.45 (more permissive)
   - Focus: Compliance, policy, regulations

2. **Investment Team** (`investor`) - Green

   - 3 sources: TechCrunch, VentureBeat, Crunchbase
   - Threshold: 0.5 (balanced)
   - Focus: Funding, M&A, market trends

3. **Competitive Intelligence** (`competitor`) - Purple

   - 3 sources: The Verge, Product Hunt, TechRadar
   - Threshold: 0.55 (more selective)
   - Focus: Competitors, products, positioning

4. **Research Team** (`researcher`) - Blue
   - 4 sources: Ars Technica, MIT Tech Review, HN, ArXiv
   - Threshold: 0.6 (most selective)
   - Focus: Emerging tech, innovations

**Total**: 13 RSS feed sources

## Making Changes

### Add a New Team

1. Edit `config.json`
2. Add new team object to `teams` array
3. Run: `python setup_teams.py init`

### Add a Source to a Team

1. Edit `config.json`
2. Add source to team's `sources` array
3. Run: `python setup_teams.py init`

### Change Keyword Settings

1. Edit `keyword_config` in `config.json`
2. Run: `python setup_teams.py init`

### Disable a Team

1. Set `"is_active": false` in `config.json`
2. Run: `python setup_teams.py init`

## Using in Your Code

### Get Team Configuration

```python
from teams import TeamRepository, get_team_config

# Method 1: Using repository
repo = TeamRepository()
team = repo.get_team_by_key("regulator")
print(team.keyword_config['relevance_threshold'])  # 0.45

# Method 2: Using helper function
config = get_team_config("investor")
print(config['team_name'])  # "Investment Team"
print(config['sources'])    # List of RSS feeds
```

### Get Team Sources

```python
repo = TeamRepository()
sources = repo.get_team_sources("competitor", enabled_only=True)

for source in sources:
    print(f"{source.source_name}: {source.source_url}")
    print(f"Fetch every {source.fetch_interval_minutes} minutes")
```

### Get Keyword Extraction Settings

```python
repo = TeamRepository()
config = repo.get_keyword_config("researcher")

threshold = config['relevance_threshold']  # 0.6
methods = config['methods']                # ['tfidf', 'spacy', 'yake']
min_freq = config['min_frequency']         # 2
```

### Get All Active Teams (for API)

```python
repo = TeamRepository()
teams = repo.get_team_list_for_api()

# Returns:
# [
#   {
#     "team_key": "regulator",
#     "team_name": "Regulatory Team",
#     "description": "...",
#     "color": "#DC2626",
#     "icon": "balance",
#     "source_count": 3
#   },
#   ...
# ]
```

## Benefits

✅ **Single source of truth** - All config in one place  
✅ **Easy to modify** - Edit JSON, run one command  
✅ **Version controlled** - Track changes in git  
✅ **Team-specific settings** - Different thresholds per team  
✅ **Fast queries** - Database for runtime access  
✅ **Backup/restore** - Export database back to JSON  
✅ **Validated** - Schema validation before loading

## Workflow

```bash
# 1. Modify configuration
vim config.json

# 2. Validate changes
python setup_teams.py validate

# 3. Apply changes
python setup_teams.py init

# 4. Verify
python setup_teams.py show
python test_team_config.py
```

## Files Created

```
backend/
├── config.json                 # Single source of truth ⭐
├── setup_teams.py              # Configuration loader
├── test_team_config.py         # Validation tests
├── CONFIG_GUIDE.md             # Full documentation
├── teams/
│   ├── models.py               # Database models
│   ├── repository.py           # Data access layer
│   └── __init__.py             # Package exports
└── data/
    └── teams.db                # Runtime database (generated)
```

## Next Steps

1. **Integrate with keyword pipeline**:

   ```python
   from teams import TeamRepository

   repo = TeamRepository()
   for team_key in ['regulator', 'investor', 'competitor', 'researcher']:
       config = repo.get_keyword_config(team_key)
       sources = repo.get_team_sources(team_key)

       # Extract keywords using team-specific config
       # Process sources assigned to this team
   ```

2. **Create API endpoints**:

   ```python
   @app.get("/api/teams")
   def get_teams():
       repo = TeamRepository()
       return repo.get_team_list_for_api()
   ```

3. **Use in scheduler**:

   ```python
   repo = TeamRepository()
   sources_to_fetch = repo.get_sources_to_fetch()

   for team, source in sources_to_fetch:
       # Fetch from source
       # Use team.keyword_config for extraction
   ```

## Documentation

- **CONFIG_GUIDE.md** - Complete configuration guide
- **TEAM_SYSTEM_SUMMARY.md** - Architecture overview
- **FRONTEND_GUIDE.md** - API documentation

---

**Your config.json is now the single source of truth!** 🎉
