# Generating API Output Files

This guide shows you how to generate JSON files from your NLP pipeline data for frontend consumption.

## Overview

The `scripts/generate_api_outputs.py` script generates two types of files:

1. **Word Cloud Files** - Top keywords for each team (4 files)

   - `mock_data_regulator_wordcloud.json`
   - `mock_data_investor_wordcloud.json`
   - `mock_data_competitor_wordcloud.json`
   - `mock_data_researcher_wordcloud.json`

2. **Time-Series Files** - Historical trends for specific keywords
   - `mock_data_timeseries_{keyword}.json` (one file per keyword)

## Quick Start

### Generate All Output Files

```bash
cd /Users/samanb/dev/perceptron/backend

# Generate with defaults (today's date, 5 top keywords)
PYTHONPATH=/Users/samanb/dev/perceptron/backend python3 scripts/generate_api_outputs.py

# Or specify custom options
PYTHONPATH=/Users/samanb/dev/perceptron/backend python3 scripts/generate_api_outputs.py \
  --output-dir generated_data \
  --date 2025-11-07 \
  --top-keywords 10
```

### Command Options

```bash
--output-dir DIRECTORY    # Output directory (default: mock_data)
--date YYYY-MM-DD        # Target date (default: today)
--top-keywords N         # Number of keywords for time-series (default: 5)
```

## Output File Structure

### Word Cloud Files

Each team gets a JSON file with this structure:

```json
{
  "team_key": "researcher",
  "team_name": "Research Team",
  "date_range": {
    "start": "2025-11-07",
    "end": "2025-11-07"
  },
  "keywords": [
    {
      "keyword": "machine learning",
      "date": "2025-11-07",
      "importance": 94.99,
      "sentiment": {
        "score": 0.307,
        "magnitude": 0.412,
        "breakdown": {
          "positive": 34,
          "negative": 9,
          "neutral": 6
        }
      },
      "metrics": {
        "frequency": 78,
        "document_count": 10,
        "source_diversity": 2,
        "velocity": 2.78
      },
      "documents": [
        {
          "content_id": 7607,
          "title": "Latest AI Research Findings",
          "source": "arXiv",
          "date": "2025-11-06",
          "snippet": "Machine learning models continue to..."
        }
      ]
    }
  ],
  "total_keywords": 100,
  "total_documents": 500
}
```

### Time-Series Files

Each keyword gets a JSON file with historical data:

```json
{
  "keyword": "artificial intelligence",
  "trend": "rising",
  "data_points": [
    {
      "date": "2025-10-08",
      "importance": 53.78,
      "sentiment": -0.198,
      "frequency": 28
    },
    {
      "date": "2025-10-09",
      "importance": 64.4,
      "sentiment": -0.2,
      "frequency": 40
    }
  ],
  "summary": {
    "avg_importance": 59.09,
    "max_importance": 84.01
  }
}
```

## Workflow Integration

### 1. After Initial Data Processing

After running `reset_and_initialize.py`:

```bash
# Process your content
python3 reset_and_initialize.py

# Generate API outputs
PYTHONPATH=/Users/samanb/dev/perceptron/backend python3 scripts/generate_api_outputs.py
```

### 2. Daily Updates (with Perpetual Services)

```bash
# The services continuously process data
# Generate fresh outputs daily:

PYTHONPATH=/Users/samanb/dev/perceptron/backend python3 scripts/generate_api_outputs.py \
  --output-dir api_outputs \
  --date $(date +%Y-%m-%d)
```

### 3. Custom Date Range

```bash
# Generate outputs for a specific date
PYTHONPATH=/Users/samanb/dev/perceptron/backend python3 scripts/generate_api_outputs.py \
  --date 2025-11-01 \
  --output-dir outputs_nov1
```

## Using the Python API Directly

You can also use the API service in your own scripts:

```python
from keywords.api_service import KeywordAPIService
from datetime import date
import json

# Initialize service
api_service = KeywordAPIService()

# Get word cloud data
word_cloud = api_service.get_word_cloud_data(
    team_key="researcher",
    target_date=date(2025, 11, 7),
    limit=100,
    min_importance=30.0
)

# Save to file
with open('my_wordcloud.json', 'w') as f:
    json.dump(word_cloud.model_dump(mode='json'), f, indent=2)

# Get time-series data
timeseries = api_service.get_keyword_timeseries(
    keyword="artificial intelligence",
    team_key="researcher",
    days=30
)

if timeseries:
    keyword_data = timeseries.keywords[0]
    with open('my_timeseries.json', 'w') as f:
        json.dump(keyword_data.model_dump(mode='json'), f, indent=2)
```

## Data Requirements

For meaningful outputs, ensure you have:

1. **Content processed** - At least 50-100 documents per team
2. **Importance calculated** - Run with `calculate_importance=True`
3. **Time-series generated** - Call `processor.generate_timeseries()`
4. **Recent data** - Data from the target date you're querying

Example complete processing:

```python
from keywords.enhanced_processor import EnhancedKeywordProcessor
from storage.repository import ContentRepository

content_repo = ContentRepository()
processor = EnhancedKeywordProcessor(team_key='researcher')

# Get unprocessed content
content_items = content_repo.get_unprocessed_content(limit=100)

# Process with importance
results = processor.process_batch(
    content_items,
    calculate_importance=True
)

# Generate time-series
processor.generate_timeseries(days=30)
```

## Troubleshooting

### No keywords in output files

**Problem**: Word cloud files have empty keywords array

**Solution**:

```bash
# Check if data exists in database
python3 -c "
from keywords.importance_repository import ImportanceRepository
from datetime import date

repo = ImportanceRepository()
keywords = repo.get_top_keywords('researcher', date.today(), limit=10)
print(f'Found {len(keywords)} keywords')
"

# If empty, process more content first
python3 reset_and_initialize.py
```

### Time-series files have only 1 data point

**Problem**: Historical data not available

**Solution**: Process data over multiple days or generate historical time-series:

```python
from keywords.enhanced_processor import EnhancedKeywordProcessor

processor = EnhancedKeywordProcessor(team_key='researcher')
processor.generate_timeseries(days=30)  # Generate 30 days of history
```

### Module not found error

**Problem**: `ModuleNotFoundError: No module named 'keywords'`

**Solution**: Set PYTHONPATH:

```bash
PYTHONPATH=/Users/samanb/dev/perceptron/backend python3 scripts/generate_api_outputs.py
```

## Advanced Usage

### Generate for Specific Keywords

Customize which keywords get time-series files:

```python
from pathlib import Path
from scripts.generate_api_outputs import generate_timeseries_files

output_dir = Path("custom_outputs")
output_dir.mkdir(exist_ok=True)

# Generate for specific keywords you care about
keywords = [
    "artificial intelligence",
    "machine learning",
    "neural networks",
    "deep learning"
]

generate_timeseries_files(
    output_dir=output_dir,
    keywords=keywords,
    team_key="researcher",
    days=90  # 3 months of data
)
```

### Batch Generation for Multiple Dates

```python
from datetime import date, timedelta
from scripts.generate_api_outputs import generate_all_outputs

# Generate for last 7 days
for i in range(7):
    target_date = date.today() - timedelta(days=i)
    date_str = target_date.isoformat()

    generate_all_outputs(
        output_dir=f"outputs_{date_str}",
        date_str=date_str,
        top_keywords_for_timeseries=5
    )
```

## Performance Optimization

The generation script uses the **batched encoding optimization** (5.1x faster) introduced in the NLP pipeline:

- ✅ All keywords encoded in single batch
- ✅ No progress bar spam
- ✅ Efficient database queries with proper indices
- ✅ Reuses API service models (validated with Pydantic)

Typical performance:

- **Word clouds**: ~2-3 seconds per team (100 keywords)
- **Time-series**: ~1 second per keyword (30 days)
- **Complete run** (4 teams + 5 keywords): ~15-20 seconds

## Integration with Frontend

These files can be:

1. **Directly served** as static JSON files
2. **Used as mock data** during frontend development
3. **Compared with real API** responses for validation
4. **Cached** for faster frontend loading

The format matches exactly what the API endpoints return, so your frontend code works identically with static files or live API.

## Summary

```bash
# Quick reference
cd /Users/samanb/dev/perceptron/backend

# Generate today's data
PYTHONPATH=$PWD python3 scripts/generate_api_outputs.py

# Custom options
PYTHONPATH=$PWD python3 scripts/generate_api_outputs.py \
  --output-dir my_outputs \
  --date 2025-11-07 \
  --top-keywords 10

# Files generated:
# - mock_data_regulator_wordcloud.json
# - mock_data_investor_wordcloud.json
# - mock_data_competitor_wordcloud.json
# - mock_data_researcher_wordcloud.json
# - mock_data_timeseries_{keyword}.json (x5)
```
