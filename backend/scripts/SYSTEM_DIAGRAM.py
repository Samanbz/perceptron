"""
Complete System Architecture Visualization
"""

COMPLETE_SYSTEM = """
╔══════════════════════════════════════════════════════════════════╗
║                   SIGNAL RADAR BACKEND                           ║
║            Complete Data Pipeline Architecture                   ║
╚══════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────┐
│  STEP 1: DATA INGESTION (Sourcers)                              │
└──────────────────────────────────────────────────────────────────┘

    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │ TechCrunch  │  │ Hacker News │  │ The Verge   │  ... more sources
    │  RSS Feed   │  │  RSS Feed   │  │  RSS Feed   │
    └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
           │                │                │
           └────────────────┼────────────────┘
                            │
                   ┌────────▼────────┐
                   │  RSSSourcer     │
                   │  - validate()   │
                   │  - fetch()      │
                   └────────┬────────┘
                            │
                   ┌────────▼────────┐
                   │ SourcedContent  │
                   │ - title         │
                   │ - content       │
                   │ - url           │
                   │ - metadata      │
                   │ - dates         │
                   └────────┬────────┘
                            │
┌──────────────────────────┼────────────────────────────────────────┐
│  STEP 2: DEDUPLICATION & STORAGE (Data Lake)                     │
└──────────────────────────┼────────────────────────────────────────┘
                            │
                   ┌────────▼──────────┐
                   │ Content Hashing   │
                   │ SHA-256(content+  │
                   │         url)      │
                   └────────┬──────────┘
                            │
                   ┌────────▼──────────┐
                   │ Duplicate Check   │
                   │ (Database UNIQUE  │
                   │  constraint)      │
                   └─┬─────────────┬───┘
                     │             │
                     │ New         │ Duplicate
                     │             │
                ┌────▼────┐   ┌───▼────┐
                │  SAVE   │   │  SKIP  │
                └────┬────┘   └────────┘
                     │
         ┌───────────▼────────────┐
         │  SQLite Database       │
         │  (→ PostgreSQL)        │
         ├────────────────────────┤
         │ sourced_content        │
         │ - id                   │
         │ - content_hash (unique)│
         │ - title, content, url  │
         │ - source_type/name     │
         │ - published_date       │
         │ - retrieved_at         │
         │ - processed = FALSE    │
         │ - extra_metadata       │
         └───────────┬────────────┘
                     │
┌──────────────────────────┼────────────────────────────────────────┐
│  STEP 3: PERPETUAL MONITORING (Scheduler)                        │
└──────────────────────────┼────────────────────────────────────────┘
                            │
                   ┌────────▼──────────┐
                   │  Scheduler Loop   │
                   │  (Every 60 sec)   │
                   └────────┬──────────┘
                            │
                   ┌────────▼──────────┐
                   │ Check DB for      │
                   │ sources due for   │
                   │ fetching          │
                   └────────┬──────────┘
                            │
                   ┌────────▼──────────┐
                   │ Fetch → Store     │
                   │ Update statistics │
                   │ Schedule next     │
                   └────────┬──────────┘
                            │
                            │ (Loop back)
                            │
┌──────────────────────────┼────────────────────────────────────────┐
│  STEP 4: NLP/ML PROCESSING                                       │
└──────────────────────────┼────────────────────────────────────────┘
                            │
                   ┌────────▼──────────┐
                   │ Query unprocessed │
                   │ content           │
                   └────────┬──────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
    ┌────▼─────┐   ┌───────▼──────┐   ┌──────▼──────┐
    │ TF-IDF   │   │  Sentiment   │   │  Entities   │
    │ Analysis │   │  Analysis    │   │  Detection  │
    └────┬─────┘   └───────┬──────┘   └──────┬──────┘
         │                 │                  │
         └─────────────────┼──────────────────┘
                           │
                  ┌────────▼──────────┐
                  │ Store Results     │
                  │ Mark as processed │
                  └───────────────────┘


╔══════════════════════════════════════════════════════════════════╗
║                      KEY FEATURES                                ║
╚══════════════════════════════════════════════════════════════════╝

✓ AUTOMATIC DEDUPLICATION
  - SHA-256 content hashing
  - Database-level uniqueness guarantee
  - No duplicate storage

✓ RICH METADATA TRACKING
  - Source type (rss, web, api, ...)
  - Source name (TechCrunch, HN, ...)
  - Published & retrieved dates
  - Author information
  - Flexible JSON metadata

✓ PERPETUAL MONITORING
  - Configurable fetch intervals (30-60 min typical)
  - Automatic retry on failure
  - Statistics tracking
  - Error logging

✓ NLP/ML READY
  - Indexed fields for fast queries
  - Processing flags (processed/unprocessed)
  - Batch processing support
  - Date range filtering

✓ SCALABLE ARCHITECTURE
  - SQLite (dev) → PostgreSQL (production)
  - Repository pattern for clean abstraction
  - Easy to add new source types
  - Ready for distributed processing


╔══════════════════════════════════════════════════════════════════╗
║                      DATA FLOW EXAMPLE                           ║
╚══════════════════════════════════════════════════════════════════╝

1. Scheduler checks: "Is TechCrunch due for fetching?"
   → Yes, last fetch was 31 minutes ago (interval: 30 min)

2. Create RSSSourcer("https://techcrunch.com/feed/", max_entries=50)
   → Validate URL ✓
   → Fetch RSS feed

3. Parse 50 entries from feed
   → Extract title, content, URL, author, date, tags
   → Create 50 SourcedContent objects

4. For each SourcedContent:
   → Compute hash: SHA-256(normalized_content + url)
   → Check if hash exists in database
   
   Entry 1: hash = "abc123..." → New! → Save to DB
   Entry 2: hash = "def456..." → New! → Save to DB
   Entry 3: hash = "abc123..." → Duplicate! → Skip
   ...
   
   Result: 45 new, 5 duplicates

5. Update source statistics:
   → last_fetched_at = now
   → next_fetch_at = now + 30 minutes
   → total_items_fetched += 45

6. NLP Pipeline queries:
   → "Give me 100 unprocessed items"
   → Returns: 45 from TechCrunch + 55 from other sources
   
7. Process each item:
   → Extract keywords (TF-IDF)
   → Analyze sentiment
   → Detect entities (NER)
   → Mark as processed

8. Repeat cycle every 60 seconds...


╔══════════════════════════════════════════════════════════════════╗
║                    TYPICAL USAGE PATTERN                         ║
╚══════════════════════════════════════════════════════════════════╝

Morning (8 AM):
  └─ Developer starts scheduler: `python scheduler.py`
     └─ Runs continuously, fetching every 30-60 min

Throughout Day:
  └─ Scheduler fetches: TechCrunch, HN, The Verge, Ars Technica
     └─ Content accumulates in database
        └─ ~300-500 new articles per day
           └─ All deduplicated automatically

Evening (6 PM):
  └─ Run NLP pipeline: `python example_nlp_processing.py`
     └─ Process unprocessed content
        └─ Extract insights, trends, sentiment
           └─ Mark as processed

Next Day:
  └─ Scheduler continues...
     └─ Data lake grows...
        └─ Ready for analysis at any time
"""


def print_diagram():
    """Print the complete system diagram."""
    print(COMPLETE_SYSTEM)


if __name__ == "__main__":
    print_diagram()
