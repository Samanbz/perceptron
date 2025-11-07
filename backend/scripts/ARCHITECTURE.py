"""
Visual overview of the sourcer pipeline architecture.
"""

ARCHITECTURE = """
┌─────────────────────────────────────────────────────────────────┐
│                     SOURCER PIPELINE                            │
│                   (Data Ingestion Layer)                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
        ┌───────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
        │ RSS Sourcer  │ │Web Scraper │ │ API Sourcer│
        │              │ │  (Future)  │ │  (Future)  │
        └──────┬───────┘ └─────┬──────┘ └─────┬──────┘
               │               │               │
               └───────────────┼───────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  SourcedContent     │
                    │  - title            │
                    │  - content          │
                    │  - url              │
                    │  - published_date   │
                    │  - author           │
                    │  - metadata         │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
        ┌───────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐
        │  Processing  │ │ Filtering│ │  Storage   │
        │   (Future)   │ │ (Future) │ │  (Future)  │
        └──────────────┘ └──────────┘ └────────────┘
"""

CLASS_HIERARCHY = """
┌─────────────────────────────────────────────────────────────────┐
│                     CLASS HIERARCHY                             │
└─────────────────────────────────────────────────────────────────┘

BaseSourcer (Abstract)
├── validate_config()  [abstract]
├── fetch()            [abstract]
└── name

    ├── RSSSourcer
    │   ├── feed_url
    │   ├── max_entries
    │   ├── validate_config()
    │   └── fetch()
    │
    ├── WebScraperSourcer (Future)
    │   ├── url
    │   ├── selector
    │   └── ...
    │
    ├── APISourcer (Future)
    │   ├── api_url
    │   ├── headers
    │   └── ...
    │
    └── TwitterSourcer (Future)
        ├── api_key
        ├── query
        └── ...

SourcedContent (Data Model)
├── title
├── content
├── url
├── published_date
├── author
├── metadata
├── retrieved_at
└── to_dict()
"""

DATA_FLOW = """
┌─────────────────────────────────────────────────────────────────┐
│                      DATA FLOW                                  │
└─────────────────────────────────────────────────────────────────┘

1. CLIENT REQUEST
   │
   ├─► POST /api/sources/rss/fetch
   │   {
   │     "feed_url": "https://example.com/feed",
   │     "max_entries": 20
   │   }
   │
2. SOURCER INITIALIZATION
   │
   ├─► RSSSourcer(feed_url, max_entries)
   │   │
   │   ├─► validate_config()  ✓
   │   └─► Ready to fetch
   │
3. CONTENT FETCHING
   │
   ├─► sourcer.fetch()
   │   │
   │   ├─► Parse RSS feed
   │   ├─► Extract entries
   │   └─► Create SourcedContent objects
   │
4. CONTENT TRANSFORMATION
   │
   ├─► [SourcedContent, SourcedContent, ...]
   │   │
   │   └─► to_dict() for each
   │
5. API RESPONSE
   │
   └─► [
         {
           "title": "...",
           "content": "...",
           "url": "...",
           "published_date": "...",
           "author": "...",
           "metadata": {...},
           "retrieved_at": "..."
         },
         ...
       ]
"""

API_ENDPOINTS = """
┌─────────────────────────────────────────────────────────────────┐
│                     API ENDPOINTS                               │
└─────────────────────────────────────────────────────────────────┘

Core Endpoints:
├─► GET  /                          → Root
├─► GET  /api/health                → Health check
└─► GET  /api/hello                 → Hello world

Sourcer Endpoints:
├─► POST /api/sources/rss/fetch     → Fetch from custom RSS feed
│   Body: {"feed_url": "...", "max_entries": 20}
│
└─► GET  /api/sources/rss/example   → Fetch from example feed
    Returns: Feed info + entries

Interactive Documentation:
├─► GET  /docs                      → Swagger UI
└─► GET  /redoc                     → ReDoc UI
"""

FILE_STRUCTURE = """
┌─────────────────────────────────────────────────────────────────┐
│                   FILE STRUCTURE                                │
└─────────────────────────────────────────────────────────────────┘

backend/
│
├── app.py                          # FastAPI app + RSS endpoints
│
├── sourcers/                       # Sourcer modules
│   ├── __init__.py                # Exports
│   ├── base.py                    # BaseSourcer + SourcedContent
│   ├── rss_sourcer.py             # RSS implementation
│   └── template_sourcer.py        # Template for new sourcers
│
├── example_usage.py                # Usage examples
├── test_sourcers.py                # Test suite
│
├── pyproject.toml                  # Dependencies + config
├── run.sh                          # Quick start script
├── format.sh                       # Code formatting
│
└── Documentation/
    ├── README.md                   # Main documentation
    ├── SOURCERS.md                 # Sourcer pipeline docs
    └── ROADMAP.md                  # Implementation roadmap
"""


def print_diagrams():
    """Print all architecture diagrams."""
    diagrams = [
        ("ARCHITECTURE", ARCHITECTURE),
        ("CLASS HIERARCHY", CLASS_HIERARCHY),
        ("DATA FLOW", DATA_FLOW),
        ("API ENDPOINTS", API_ENDPOINTS),
        ("FILE STRUCTURE", FILE_STRUCTURE),
    ]
    
    for title, diagram in diagrams:
        print(f"\n{diagram}")


if __name__ == "__main__":
    print_diagrams()
