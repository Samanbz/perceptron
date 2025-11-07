# Team-Based Single Source of Truth - Implementation Summary

## What We Built

A complete team-based configuration system where **teams are the single source of truth** for:

1. Which RSS feeds to monitor
2. Keyword extraction parameters
3. Sentiment analysis settings

## Key Files Created

### 1. Team Configuration Models (`teams/models.py`)

- **InternalTeamModel**: Defines teams (regulator, investor, etc.)
- **TeamSourceModel**: Maps RSS sources to teams
- Single database: `data/teams.db`

### 2. Keyword Importance Models (`keywords/importance_models.py`)

- **KeywordImportanceModel**: Tracks keyword importance + sentiment over time
- **KeywordTimeSeriesModel**: Pre-computed time-series for word clouds
- Includes: importance score (0-100), sentiment (-1 to +1), velocity, trend

### 3. Frontend API Models (`api_models.py`)

- Complete Pydantic models for API responses
- Mock data generators for frontend development
- Generated 7 mock JSON files for your colleague

### 4. Frontend Guide (`FRONTEND_GUIDE.md`)

- Complete API documentation
- Data model specifications
- UI component examples
- React/TypeScript code samples

## How It Works

### Team Selection Flow

```
User selects "Regulator" team in dropdown
         ↓
Backend filters to regulator sources only
         ↓
Extracts keywords from regulator content
         ↓
Calculates importance + sentiment
         ↓
Returns top keywords for word cloud
```

### Single Source of Truth Structure

```
data/teams.db
├── internal_teams
│   ├── id, team_key, team_name
│   ├── keyword_config (JSON)
│   └── sentiment_config (JSON)
└── team_sources
    ├── team_id → links to internal_teams
    ├── source_name, source_url
    └── fetch_interval_minutes

data/keywords.db (enhanced)
├── keyword_importance
│   ├── keyword, date, team_id
│   ├── importance_score (0-100)
│   ├── sentiment_score (-1 to +1)
│   ├── velocity, frequency, source_diversity
│   └── content_ids, sample_snippets
└── keyword_timeseries
    ├── keyword, team_id, start_date, end_date
    ├── importance_values[] (array)
    ├── sentiment_values[] (array)
    └── trend (rising/falling/stable/emerging)
```

## Importance Calculation

**Importance Score (0-100)** combines multiple signals:

```python
importance = (
    frequency_score * 0.30 +      # How often mentioned
    velocity_score * 0.25 +       # Rate of change
    source_diversity * 0.20 +     # # of different sources
    recency_score * 0.15 +        # How recent
    sentiment_magnitude * 0.10    # How strong the sentiment
)
```

### Signal Breakdown:

- **Frequency**: Raw mention count, normalized
- **Velocity**: % change vs previous day (positive = trending up)
- **Source Diversity**: # of unique sources (more diverse = more important)
- **Recency**: Exponential decay (recent = higher weight)
- **Sentiment Magnitude**: Strength of sentiment (strong opinions = notable)

## Sentiment Analysis

**Sentiment Score (-1 to +1)**:

- Calculated from sentiment of mentions
- `-1.0`: All negative
- `0.0`: Neutral or balanced
- `+1.0`: All positive

**Sentiment Magnitude (0 to 1)**:

- `0.0-0.3`: Weak (factual)
- `0.3-0.6`: Moderate
- `0.6-1.0`: Strong (opinionated)

## Mock Data Generated

### For Frontend Development:

**Word Cloud Data (by team):**

- `mock_data_regulator_wordcloud.json` - 20 regulatory keywords
- `mock_data_investor_wordcloud.json` - 20 investment keywords
- `mock_data_competitor_wordcloud.json` - 20 competitive keywords
- `mock_data_researcher_wordcloud.json` - 20 research keywords

**Time Series Data:**

- `mock_data_timeseries_federal_regulation.json` - 30 days
- `mock_data_timeseries_venture_capital.json` - 30 days
- `mock_data_timeseries_artificial_intelligence.json` - 30 days

Each file contains realistic data matching the exact API response format.

## API Data Model for Frontend

### Word Cloud Response

```json
{
  "team_key": "regulator",
  "team_name": "Regulatory Team",
  "date_range": {"start": "2025-11-07", "end": "2025-11-07"},
  "keywords": [
    {
      "keyword": "federal regulation",
      "importance": 94.23,
      "sentiment": {
        "score": 0.156,
        "magnitude": 0.624,
        "breakdown": {"positive": 15, "negative": 5, "neutral": 12}
      },
      "metrics": {
        "frequency": 45,
        "document_count": 18,
        "source_diversity": 6,
        "velocity": 23.5
      },
      "documents": [...]
    }
  ]
}
```

### Time Series Response

```json
{
  "team_key": "regulator",
  "period": { "start": "...", "end": "...", "granularity": "day" },
  "keywords": [
    {
      "keyword": "federal regulation",
      "trend": "rising",
      "data_points": [
        {
          "date": "2025-11-01",
          "importance": 45.2,
          "sentiment": 0.12,
          "frequency": 12
        },
        {
          "date": "2025-11-02",
          "importance": 52.3,
          "sentiment": 0.23,
          "frequency": 18
        }
      ],
      "summary": { "avg_importance": 48.5, "max_importance": 87.3 }
    }
  ]
}
```

## Next Steps

### Backend Tasks:

1. **Initialize team database**:

   ```bash
   python setup_teams.py init
   ```

2. **Create team configurations**:

   - Add teams (regulator, investor, etc.)
   - Map RSS sources to teams
   - Configure keyword extraction params per team

3. **Implement importance calculation**:

   - Create `ImportanceCalculator` class
   - Calculate importance from multiple signals
   - Store in `keyword_importance` table

4. **Add sentiment analysis**:

   - Integrate sentiment library (TextBlob, VADER, or transformers)
   - Calculate sentiment per keyword mention
   - Aggregate to overall sentiment score

5. **Build API endpoints**:

   ```python
   @app.get("/api/keywords/wordcloud")
   @app.get("/api/keywords/timeseries")
   @app.get("/api/teams")
   ```

6. **Connect to existing pipeline**:
   - Modify `RealtimeKeywordProcessor` to:
     - Calculate importance scores
     - Run sentiment analysis
     - Store in `keyword_importance` table
     - Update time-series aggregations

### Frontend Tasks (for your colleague):

1. **Use mock data files** to build UI components
2. **Team selector dropdown** component
3. **Word cloud visualization** with:
   - Size = importance
   - Color = sentiment
   - Opacity = sentiment magnitude
4. **Time slider** for "word cloud in time"
5. **Keyword details panel** with document list
6. **Connect to real API** when backend is ready

## Configuration Example

### Team Definition (in database):

```python
{
  "team_key": "regulator",
  "team_name": "Regulatory Team",
  "description": "Government policy and compliance monitoring",
  "keyword_config": {
    "relevance_threshold": 0.6,
    "max_keywords_per_day": 100,
    "tfidf_weight": 0.3,
    "spacy_weight": 0.4,
    "yake_weight": 0.3
  },
  "sentiment_config": {
    "method": "vader",  # or "textblob", "transformers"
    "min_magnitude": 0.2
  },
  "color": "#3B82F6",
  "icon": "shield"
}
```

### Team Sources:

```python
[
  {
    "team_id": 1,  # regulator
    "source_name": "Federal Register",
    "source_url": "https://federalregister.gov/rss",
    "source_type": "rss"
  },
  {
    "team_id": 1,  # regulator
    "source_name": "SEC News",
    "source_url": "https://sec.gov/news/rss",
    "source_type": "rss"
  }
]
```

## Benefits of This Architecture

✅ **Single Source of Truth**: Teams table defines everything  
✅ **Easy to Add Teams**: Just add row in `internal_teams` table  
✅ **Flexible Source Assignment**: Same RSS feed can belong to multiple teams  
✅ **Team-Specific Tuning**: Each team has own keyword extraction params  
✅ **Clean Separation**: Frontend only needs to select team  
✅ **Efficient Queries**: Pre-computed time-series for fast loading

## Files to Give Your Colleague

Hand off these files:

1. ✅ `FRONTEND_GUIDE.md` - Complete documentation
2. ✅ `mock_data_regulator_wordcloud.json` - Regulator sample
3. ✅ `mock_data_investor_wordcloud.json` - Investor sample
4. ✅ `mock_data_competitor_wordcloud.json` - Competitor sample
5. ✅ `mock_data_researcher_wordcloud.json` - Researcher sample
6. ✅ `mock_data_timeseries_federal_regulation.json` - Time series example
7. ✅ `mock_data_timeseries_venture_capital.json` - Time series example
8. ✅ `mock_data_timeseries_artificial_intelligence.json` - Time series example

Your colleague can start building the UI immediately with these mock files!

## Summary

You now have:

- ✅ Complete team-based configuration system
- ✅ Keyword importance + sentiment tracking models
- ✅ Frontend API data models with Pydantic validation
- ✅ 7 mock data files for frontend development
- ✅ Complete frontend integration guide
- ✅ Clear path to implement importance calculation
- ✅ Single source of truth for all team configurations

The frontend can start development now while you implement the importance calculation and sentiment analysis on the backend!
