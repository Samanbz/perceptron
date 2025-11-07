# Configuration Guide - Single Source of Truth

## Overview

**`config.json`** is the **single source of truth** for all team and source configurations in the Perceptron backend.

All teams, their RSS sources, keyword extraction settings, and sentiment analysis parameters are defined in this one file.

## File Location

```
/Users/samanb/dev/perceptron/backend/config.json
```

## Configuration Structure

### Top Level

```json
{
  "teams": [
    // Array of team configurations
  ]
}
```

### Team Configuration

Each team object contains:

```json
{
  "team_key": "regulator", // Unique identifier (used in API calls)
  "team_name": "Regulatory Team", // Display name
  "description": "...", // Team description
  "color": "#DC2626", // UI color (hex)
  "icon": "balance", // Material icon name
  "is_active": true, // Whether team is active

  "keyword_config": {
    // Keyword extraction settings
  },

  "sentiment_config": {
    // Sentiment analysis settings
  },

  "sources": [
    // Array of RSS feed sources
  ]
}
```

### Keyword Configuration

```json
"keyword_config": {
  "relevance_threshold": 0.5,        // Min score to be considered relevant (0-1)
  "min_frequency": 3,                 // Min times keyword must appear
  "max_keywords_per_day": 80,         // Max keywords to extract per day
  "enable_multi_word_phrases": true,  // Extract phrases like "venture capital"
  "max_phrase_length": 3,             // Max words in a phrase
  "filter_stopwords": true,           // Remove common words (the, and, etc.)
  "methods": ["tfidf", "yake"]       // Extraction methods to use
}
```

Available extraction methods:

- `tfidf` - TF-IDF statistical analysis
- `spacy` - spaCy NLP (named entities, noun phrases)
- `yake` - YAKE keyword extraction

### Sentiment Configuration

```json
"sentiment_config": {
  "enable_sentiment": true,           // Enable sentiment analysis
  "sentiment_method": "vader",        // Method: "vader" or "textblob"
  "importance_weight": 0.15          // Weight in importance calculation (0-1)
}
```

### Source Configuration

```json
"sources": [
  {
    "source_type": "rss",                    // Type: "rss", "web", "api"
    "source_name": "TechCrunch",             // Display name
    "source_url": "https://...",             // Feed URL
    "fetch_interval_minutes": 30,            // How often to check (minutes)
    "config": {
      "max_entries": 50                      // Max items to fetch per check
    }
  }
]
```

## Usage

### 1. Initialize Database from Config

```bash
# Validate configuration first
python setup_teams.py validate

# Initialize database from config.json
python setup_teams.py init
```

### 2. View Current Configuration

```bash
# Show all teams and sources
python setup_teams.py show

# Show statistics
python setup_teams.py stats
```

### 3. Export Current Database to JSON

```bash
# Backup current database to config_backup.json
python setup_teams.py export
```

## Modifying Configuration

### Adding a New Team

1. Edit `config.json`
2. Add new team object to `teams` array
3. Define keyword_config, sentiment_config, and sources
4. Re-run: `python setup_teams.py init`

Example:

```json
{
  "team_key": "legal",
  "team_name": "Legal Team",
  "description": "Monitors legal developments and litigation",
  "color": "#DC2626",
  "icon": "gavel",
  "is_active": true,
  "keyword_config": {
    "relevance_threshold": 0.55,
    "min_frequency": 2,
    "max_keywords_per_day": 60,
    "enable_multi_word_phrases": true,
    "max_phrase_length": 4,
    "filter_stopwords": true,
    "methods": ["tfidf", "spacy"]
  },
  "sentiment_config": {
    "enable_sentiment": true,
    "sentiment_method": "vader",
    "importance_weight": 0.1
  },
  "sources": [
    {
      "source_type": "rss",
      "source_name": "Law360",
      "source_url": "https://www.law360.com/rss/feed.xml",
      "fetch_interval_minutes": 60,
      "config": { "max_entries": 30 }
    }
  ]
}
```

### Adding a Source to Existing Team

1. Find the team in `config.json`
2. Add new source object to `sources` array
3. Re-run: `python setup_teams.py init`

### Changing Keyword Thresholds

1. Edit `keyword_config.relevance_threshold` for a team
2. Re-run: `python setup_teams.py init`

### Disabling a Team

1. Set `"is_active": false` for the team
2. Re-run: `python setup_teams.py init`

## Current Teams

### 1. Regulatory Team (`regulator`)

- **Focus**: Regulatory changes, compliance, government policy
- **Color**: Red (#DC2626)
- **Threshold**: 0.45 (more permissive)
- **Sources**: Federal Register, SEC Newsroom, Reuters Regulatory

### 2. Investment Team (`investor`)

- **Focus**: Market trends, funding, M&A, opportunities
- **Color**: Green (#059669)
- **Threshold**: 0.5 (balanced)
- **Sources**: TechCrunch, VentureBeat, Crunchbase News

### 3. Competitive Intelligence Team (`competitor`)

- **Focus**: Competitor activities, product launches, positioning
- **Color**: Purple (#7C3AED)
- **Threshold**: 0.55 (more selective)
- **Sources**: The Verge, Product Hunt, TechRadar

### 4. Research Team (`researcher`)

- **Focus**: Emerging tech, academic research, innovations
- **Color**: Blue (#2563EB)
- **Threshold**: 0.6 (most selective)
- **Sources**: Ars Technica, MIT Tech Review, Hacker News, ArXiv CS

## Database Files

The setup script creates:

- `data/teams.db` - SQLite database with teams and sources
- `config_backup.json` - Export of current database state

## Integration with Pipeline

The keyword extraction pipeline reads team-specific configs from the database:

```python
from teams.repository import TeamRepository

# Get team configuration
team_repo = TeamRepository()
team = team_repo.get_team_by_key("regulator")

# Use team's keyword config
config = team.keyword_config
threshold = config['relevance_threshold']
methods = config['methods']

# Get team's sources
sources = team_repo.get_team_sources("regulator", enabled_only=True)
```

## Best Practices

1. **Always validate** before initializing: `python setup_teams.py validate`
2. **Backup before major changes**: `python setup_teams.py export`
3. **Use consistent team_keys** (lowercase, no spaces)
4. **Test new sources** before adding to production config
5. **Version control** `config.json` in git
6. **Document changes** in commit messages

## Troubleshooting

### "Configuration file not found"

- Ensure `config.json` exists in `/Users/samanb/dev/perceptron/backend/`

### "Configuration is invalid"

- Run `python setup_teams.py validate` to see specific errors
- Check for missing required fields
- Validate JSON syntax (use jsonlint.com)

### "Database already exists"

- Delete `data/teams.db` to start fresh
- Or use `export` to backup current state first

### Sources not fetching

- Check `fetch_interval_minutes` is reasonable (>= 15)
- Verify RSS feed URLs are accessible
- Check `is_enabled: true` for sources

## See Also

- `TEAM_SYSTEM_SUMMARY.md` - Overall architecture
- `FRONTEND_GUIDE.md` - API endpoints for teams
- `setup_teams.py` - Database initialization script
