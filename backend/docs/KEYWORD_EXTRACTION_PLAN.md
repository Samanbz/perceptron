# Sophisticated Keyword Extraction - Implementation Plan

## Overview

Extract **highly relevant keywords and multi-word phrases** from accumulated content, aggregated by:

- **Time period** (daily, weekly)
- **Source** (TechCrunch, Hacker News, etc.)
- **Source type** (rss, web, api)

## Requirements

1. ✅ **Relevant keywords only** - No filler words, stop words, or noise
2. ✅ **Multi-word phrases** - "artificial intelligence", "machine learning", "venture capital"
3. ✅ **Sophisticated extraction** - Beyond simple word counting
4. ✅ **Time-based aggregation** - Daily/weekly trends
5. ✅ **Source-based aggregation** - Per source and source type

---

## Proposed Approach: Multi-Level Keyword Extraction

### Level 1: Statistical Methods (TF-IDF)

**What:** Term Frequency-Inverse Document Frequency
**Why:** Identifies words important to specific documents but not common across all
**Library:** `scikit-learn`

### Level 2: NLP-Based Extraction (spaCy)

**What:** Named Entity Recognition + Noun Phrase Extraction
**Why:** Identifies proper nouns, organizations, multi-word concepts
**Library:** `spaCy` with `en_core_web_sm` or `en_core_web_md`

### Level 3: Keyphrase Extraction (RAKE/YAKE)

**What:** Rapid Automatic Keyword Extraction / Yet Another Keyword Extractor
**Why:** Specialized algorithms for multi-word phrase extraction
**Library:** `yake` or `multi-rake`

### Level 4: Contextual Embeddings (Optional - Advanced)

**What:** BERT-based keyword extraction
**Why:** Semantic understanding of keyword importance
**Library:** `keybert` (uses sentence-transformers)

---

## Recommended Architecture

### Phase 1: Foundation (Implement First) ⭐

**Combination of TF-IDF + spaCy + YAKE**

```
Content → [Preprocessing] → [TF-IDF] ┐
                         → [spaCy]   ├→ [Merge & Rank] → Keywords
                         → [YAKE]   ┘
```

**Why this combination?**

- TF-IDF: Fast, good for single words, statistical significance
- spaCy: Excellent for named entities and noun phrases
- YAKE: Language-independent, great for multi-word keyphrases

### Phase 2: Enhancement (Add Later)

- KeyBERT for semantic relevance
- Custom domain-specific filtering
- Trend detection and comparison

---

## Database Schema

### New Table: `extracted_keywords`

```sql
CREATE TABLE extracted_keywords (
    id INTEGER PRIMARY KEY,

    -- What
    keyword TEXT NOT NULL,
    keyword_type VARCHAR(50),  -- 'single', 'phrase', 'entity'
    entity_type VARCHAR(50),   -- 'PERSON', 'ORG', 'GPE', 'PRODUCT', etc.

    -- Scores
    relevance_score FLOAT,     -- Combined score (0-1)
    tfidf_score FLOAT,
    yake_score FLOAT,
    frequency INTEGER,

    -- Time aggregation
    date DATE NOT NULL,
    time_period VARCHAR(20),   -- 'daily', 'weekly'

    -- Source aggregation
    source_type VARCHAR(50),   -- 'rss', 'all'
    source_name VARCHAR(200),  -- 'TechCrunch', 'all'

    -- References
    content_ids JSON,          -- List of content IDs containing this keyword

    -- Metadata
    created_at TIMESTAMP,

    -- Indexes
    INDEX idx_date (date),
    INDEX idx_keyword (keyword),
    INDEX idx_source (source_type, source_name),
    INDEX idx_relevance (relevance_score),
    UNIQUE (keyword, date, source_type, source_name)
)
```

### New Table: `keyword_extraction_jobs`

```sql
CREATE TABLE keyword_extraction_jobs (
    id INTEGER PRIMARY KEY,
    job_name VARCHAR(200),

    -- Scope
    date_from DATE,
    date_to DATE,
    source_filter JSON,

    -- Processing
    total_content INTEGER,
    keywords_extracted INTEGER,
    method VARCHAR(50),        -- 'tfidf+spacy+yake', 'keybert', etc.

    -- Status
    status VARCHAR(50),        -- 'pending', 'running', 'completed', 'failed'
    error_message TEXT,

    -- Timing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds FLOAT,

    created_at TIMESTAMP
)
```

---

## Implementation Strategy

### Step 1: Preprocessing Pipeline

```python
def preprocess_text(text: str) -> str:
    """
    Clean and normalize text for keyword extraction.
    - Remove HTML tags
    - Remove URLs
    - Remove special characters
    - Normalize whitespace
    - Convert to lowercase (for some methods)
    """
```

### Step 2: TF-IDF Extraction

```python
from sklearn.feature_extraction.text import TfidfVectorizer

def extract_tfidf_keywords(documents, top_n=20):
    """
    Extract top keywords using TF-IDF.

    Features:
    - Custom stop words (common tech jargon)
    - N-gram range (1, 3) for phrases
    - Min document frequency to filter rare terms
    """
    vectorizer = TfidfVectorizer(
        max_features=1000,
        ngram_range=(1, 3),
        stop_words='english',
        min_df=2,
        max_df=0.8
    )
```

### Step 3: spaCy NER + Noun Phrases

```python
import spacy

def extract_entities_and_phrases(text):
    """
    Extract named entities and noun phrases.

    Entities:
    - PERSON, ORG, GPE (location), PRODUCT, EVENT, etc.

    Noun Phrases:
    - Multi-word technical terms
    - Product names
    - Concepts
    """
    nlp = spacy.load("en_core_web_md")
    doc = nlp(text)

    entities = [(ent.text, ent.label_) for ent in doc.ents]
    noun_phrases = [chunk.text for chunk in doc.noun_chunks]
```

### Step 4: YAKE Keyphrase Extraction

```python
import yake

def extract_yake_keywords(text, top_n=20):
    """
    Extract keyphrases using YAKE algorithm.

    Advantages:
    - Language-independent
    - No training required
    - Excellent for multi-word phrases
    """
    kw_extractor = yake.KeywordExtractor(
        lan="en",
        n=3,           # Max n-gram size
        dedupLim=0.9,  # Deduplication threshold
        top=top_n
    )

    keywords = kw_extractor.extract_keywords(text)
```

### Step 5: Merge and Rank

```python
def merge_and_rank_keywords(tfidf_kw, spacy_kw, yake_kw):
    """
    Combine keywords from all methods with weighted scoring.

    Scoring:
    - TF-IDF: 30% weight (good for relevance)
    - spaCy: 40% weight (good for entities/phrases)
    - YAKE: 30% weight (good for keyphrases)

    Filtering:
    - Remove duplicates (case-insensitive)
    - Remove substrings of longer phrases
    - Minimum relevance threshold
    """
```

### Step 6: Aggregation

```python
def aggregate_daily_keywords(date, source_type=None, source_name=None):
    """
    Aggregate keywords for a specific day.

    Process:
    1. Get all content for the date
    2. Extract keywords from each piece
    3. Aggregate and rank by combined scores
    4. Store top N keywords in database
    """
```

---

## Processing Pipeline

### Daily Processing Job

```python
# Run daily (e.g., at 1 AM)
def process_daily_keywords():
    """
    Extract keywords for yesterday's content.

    Aggregations:
    1. Global: All sources combined
    2. By source type: All RSS feeds
    3. By source: TechCrunch, HN, The Verge, etc.
    """

    yesterday = date.today() - timedelta(days=1)

    # Global keywords
    extract_and_store_keywords(
        date=yesterday,
        source_type='all',
        source_name='all'
    )

    # Per source type
    extract_and_store_keywords(
        date=yesterday,
        source_type='rss',
        source_name='all'
    )

    # Per source
    for source in ['TechCrunch', 'Hacker News', 'The Verge', 'Ars Technica']:
        extract_and_store_keywords(
            date=yesterday,
            source_type='rss',
            source_name=source
        )
```

---

## Advanced Features

### 1. Phrase Quality Filtering

```python
def is_quality_phrase(phrase: str) -> bool:
    """
    Filter out low-quality phrases.

    Reject if:
    - Too short (<3 chars) or too long (>50 chars)
    - All uppercase (likely acronym spam)
    - Contains only numbers
    - Common patterns like "click here"
    """
```

### 2. Domain-Specific Stop Words

```python
TECH_STOP_WORDS = {
    # Common tech filler
    'tech', 'technology', 'company', 'product', 'service',
    'feature', 'update', 'new', 'launch', 'announce',

    # Add more based on your domain
}
```

### 3. Keyword Deduplication

```python
def deduplicate_similar_keywords(keywords):
    """
    Remove similar/redundant keywords.

    Examples:
    - "AI" vs "artificial intelligence" → Keep longer
    - "Tesla" vs "Tesla Inc" → Keep shorter
    - "machine learning" vs "Machine Learning" → Normalize case
    """
```

### 4. Trend Detection

```python
def detect_trending_keywords():
    """
    Compare today's keywords with previous days.

    Metrics:
    - Velocity: Rate of increase in mentions
    - Novelty: Keywords that didn't appear before
    - Persistence: Keywords appearing consistently
    """
```

---

## API Endpoints

### 1. Extract Keywords (Manual Trigger)

```
POST /api/keywords/extract
{
  "date": "2025-11-07",
  "source_type": "rss",  // optional
  "source_name": "TechCrunch",  // optional
  "top_n": 50
}
```

### 2. Get Daily Keywords

```
GET /api/keywords/daily?date=2025-11-07&source=TechCrunch
Response: {
  "date": "2025-11-07",
  "source": "TechCrunch",
  "keywords": [
    {
      "keyword": "artificial intelligence",
      "type": "phrase",
      "relevance_score": 0.95,
      "frequency": 15,
      "entity_type": null
    },
    ...
  ]
}
```

### 3. Get Trending Keywords

```
GET /api/keywords/trending?days=7
Response: {
  "period": "2025-11-01 to 2025-11-07",
  "trending": [
    {
      "keyword": "GPT-5",
      "velocity": 2.5,  // 2.5x increase
      "appearances": [5, 8, 12, 15, 22, 28, 35]  // Daily counts
    },
    ...
  ]
}
```

---

## Performance Optimization

### 1. Batch Processing

- Process content in batches of 100-500 items
- Use multiprocessing for parallel extraction
- Cache spaCy models

### 2. Incremental Updates

- Only process new/unprocessed content
- Store extraction results to avoid recomputation
- Update aggregations incrementally

### 3. Caching

- Cache daily keyword results
- Cache spaCy model in memory
- Redis for frequent queries

---

## Evaluation & Quality Metrics

### 1. Keyword Quality Score

```python
def compute_quality_score(keyword, metadata):
    """
    Composite score based on:
    - TF-IDF score (30%)
    - Entity confidence (20%)
    - Phrase coherence (20%)
    - Frequency across sources (15%)
    - Length (15% - prefer 2-3 word phrases)
    """
```

### 2. Coverage Metrics

- What % of content is represented by top keywords?
- Are we missing important topics?
- Diversity of keywords across sources

---

## Dependencies Required

```bash
pip install scikit-learn      # TF-IDF
pip install spacy             # NER & noun phrases
python -m spacy download en_core_web_md  # Medium English model
pip install yake              # Keyphrase extraction
pip install keybert           # (Optional) BERT-based extraction
```

---

## Implementation Timeline

### Phase 1 (Recommended Start): TF-IDF + spaCy

**Estimated time:** 4-6 hours

- ✅ Solid foundation
- ✅ Fast processing
- ✅ Good quality keywords

### Phase 2: Add YAKE

**Estimated time:** 2-3 hours

- ✅ Better multi-word phrases
- ✅ Language-independent

### Phase 3: Refinements

**Estimated time:** 3-4 hours

- ✅ Quality filtering
- ✅ Deduplication
- ✅ Trend detection

### Phase 4 (Optional): KeyBERT

**Estimated time:** 2-3 hours

- ✅ Semantic understanding
- ✅ Context-aware extraction

---

## Example Output

### Daily Keywords for 2025-11-07 (All Sources)

```
1. artificial intelligence (0.95) - PHRASE - 34 mentions
2. OpenAI (0.92) - ORG - 28 mentions
3. GPT-5 (0.89) - PRODUCT - 22 mentions
4. venture capital (0.87) - PHRASE - 19 mentions
5. Sam Altman (0.85) - PERSON - 18 mentions
6. machine learning model (0.83) - PHRASE - 16 mentions
7. federal reserve (0.81) - ORG - 15 mentions
8. climate change (0.79) - PHRASE - 14 mentions
9. electric vehicle (0.77) - PHRASE - 13 mentions
10. quantum computing (0.75) - PHRASE - 12 mentions
```

### Keywords by Source (TechCrunch vs Hacker News)

```
TechCrunch:
- startup funding, Series A, venture capital
- product launch, new feature, beta testing

Hacker News:
- open source, programming language, software engineering
- distributed systems, database performance
```

---

## Recommended Approach

**Start with Phase 1 (TF-IDF + spaCy)**

- Proven, reliable methods
- Fast processing
- Good enough for 80% of use cases
- Easy to understand and debug

**Then enhance with:**

- YAKE for better phrase extraction
- Custom filtering for your domain
- Trend detection

**Consider KeyBERT only if:**

- You need semantic understanding
- Simple methods aren't capturing context
- You have GPU resources

---

## Questions for You

1. **Processing frequency:** Daily batch job or real-time as content arrives?
2. **Top N keywords:** How many keywords per day/source? (20? 50? 100?)
3. **UI/API priority:** Do you need API endpoints now or just data storage?
4. **Trend detection:** Important now or later?
5. **Quality threshold:** Would you rather have more keywords (lower quality) or fewer (higher quality)?

---

## Next Steps

Once you approve the plan, I will:

1. Create database models for keyword storage
2. Implement TF-IDF + spaCy extraction pipeline
3. Add YAKE for multi-word phrases
4. Create aggregation and storage logic
5. Build API endpoints
6. Create examples and documentation

**Ready to proceed? Any modifications to the plan?**
