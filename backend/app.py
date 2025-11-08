"""Main FastAPI application for Signal Radar backend."""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime
from contextlib import asynccontextmanager
import asyncio
import sys

# Fix for Playwright on Windows - must be set before any async operations
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from sourcers import RSSSourcer
from sourcers.web_scraper import BlogScraper, NewsScraper, GenericWebScraper
from storage import (
    ContentRepository,
    SourceConfigRepository,
    create_database,
    get_database_url,
)
from auth.routes_v2 import router as auth_router
from auth.repository_v2 import user_repository
from payment_routes import router as payment_router
from scout_routes import router as scout_router
from scheduler import get_scheduler

# Global scheduler task
scheduler_task = None

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler_task
    # Startup
    create_database(get_database_url())
    print(f"✅ Connected to Cosmos DB (MongoDB API): futurydb")
    
    # Start scheduler in background
    scheduler = get_scheduler()
    scheduler_task = asyncio.create_task(scheduler.run())
    print(f"✅ Background scheduler started")
    
    yield
    
    # Shutdown
    if scheduler_task:
        scheduler.stop()
        scheduler_task.cancel()
        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass
    print(f"✅ Scheduler stopped")

app = FastAPI(
    title="Perceptron API",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth_router)

# Include payment routes
app.include_router(payment_router)

# Include scouting routes
app.include_router(scout_router)


@app.get("/")
def home():
    """Home endpoint."""
    return {
        "message": "Perceptron API is running!",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Perceptron Backend",
        "auth": "enabled"
    }


@app.get("/api/hello")
def hello():
    """Hello world endpoint for testing."""
    return {
        "message": "Hello from Signal Radar!",
        "description": "Deutsche Bank Intelligence Dashboard",
    }


# Pydantic models for RSS endpoints
class RSSFetchRequest(BaseModel):
    """Request model for fetching RSS feed."""
    feed_url: HttpUrl
    max_entries: Optional[int] = 20


class SourcedContentResponse(BaseModel):
    """Response model for sourced content."""
    title: str
    content: str
    url: Optional[str] = None
    published_date: Optional[str] = None
    author: Optional[str] = None
    metadata: dict
    retrieved_at: str


@app.post("/api/sources/rss/fetch", response_model=List[SourcedContentResponse])
async def fetch_rss_feed(request: RSSFetchRequest):
    """
    Fetch entries from an RSS feed.
    
    Args:
        request: RSS feed URL and optional max entries
        
    Returns:
        List of sourced content items
    """
    try:
        sourcer = RSSSourcer(
            feed_url=str(request.feed_url),
            name="API RSS Feed",
            max_entries=request.max_entries
        )
        
        contents = await sourcer.fetch()
        
        return [
            SourcedContentResponse(
                title=content.title,
                content=content.content,
                url=content.url,
                published_date=content.published_date.isoformat() if content.published_date else None,
                author=content.author,
                metadata=content.metadata,
                retrieved_at=content.retrieved_at.isoformat(),
            )
            for content in contents
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch RSS feed: {str(e)}")


@app.get("/api/sources/rss/example")
async def fetch_example_rss():
    """
    Fetch entries from an example RSS feed (TechCrunch).
    
    Returns:
        List of sourced content items from the example feed
    """
    try:
        sourcer = RSSSourcer(
            feed_url="https://techcrunch.com/feed/",
            name="TechCrunch Example",
            max_entries=10
        )
        
        contents = await sourcer.fetch()
        
        return {
            "feed_info": {
                "name": sourcer.name,
                "url": sourcer.feed_url,
                "entries_fetched": len(contents),
            },
            "entries": [content.to_dict() for content in contents]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch example RSS feed: {str(e)}")


# ============================================================================
# Web Scraping API Endpoints
# ============================================================================

class BlogScrapeRequest(BaseModel):
    """Request model for scraping a blog"""
    base_url: HttpUrl
    source_name: str
    max_pages: Optional[int] = 5
    article_selector: Optional[str] = "article"
    title_selector: Optional[str] = "h1, h2.entry-title, .post-title"
    content_selector: Optional[str] = ".entry-content, .post-content, article p"
    add_to_monitoring: Optional[bool] = False


class GenericScrapeRequest(BaseModel):
    """Request model for generic web scraping"""
    base_url: HttpUrl
    source_name: str
    max_pages: Optional[int] = 10
    selectors: dict
    add_to_monitoring: Optional[bool] = False


@app.post("/api/sources/scrape/blog")
async def scrape_blog(request: BlogScrapeRequest):
    """
    Scrape content from a blog website
    
    Works with most WordPress, Medium, and standard blog platforms
    """
    try:
        scraper = BlogScraper(
            base_url=str(request.base_url),
            name=request.source_name,
            article_selector=request.article_selector,
            title_selector=request.title_selector,
            content_selector=request.content_selector,
            max_pages=request.max_pages
        )
        
        contents = await scraper.scrape()
        
        # Store in data lake
        if contents:
            content_repo = ContentRepository()
            stats = content_repo.save_batch(
                contents,
                source_type="blog_scrape",
                source_name=request.source_name,
                source_url=str(request.base_url)
            )
            content_repo.close()
        else:
            stats = {"saved": 0, "duplicates": 0, "errors": 0}
        
        # Optionally add to monitoring
        source_id = None
        if request.add_to_monitoring and contents:
            config_repo = SourceConfigRepository()
            source = config_repo.add_source(
                source_type="blog_scrape",
                source_name=request.source_name,
                source_url=str(request.base_url),
                config={
                    "article_selector": request.article_selector,
                    "title_selector": request.title_selector,
                    "content_selector": request.content_selector,
                    "max_pages": request.max_pages
                },
                fetch_interval_minutes=240  # 4 hours default for scraping
            )
            source_id = source.id
            config_repo.close()
        
        return {
            "message": "Blog scraped successfully",
            "items_found": len(contents),
            "stats": stats,
            "monitoring": {
                "added": request.add_to_monitoring,
                "source_id": source_id
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to scrape blog: {str(e)}")


@app.post("/api/sources/scrape/generic")
async def scrape_generic(request: GenericScrapeRequest):
    """
    Scrape content using custom selectors
    
    Provide CSS selectors for:
    - item: selector for article/item containers
    - link: selector for article links
    - title: selector for titles
    - content: selector for content paragraphs
    - date: selector for publication dates (optional)
    """
    try:
        config = {
            'base_url': str(request.base_url),
            'name': request.source_name,
            'max_pages': request.max_pages,
            'selectors': request.selectors
        }
        
        scraper = GenericWebScraper(config)
        contents = await scraper.scrape()
        
        # Store in data lake
        if contents:
            content_repo = ContentRepository()
            stats = content_repo.save_batch(
                contents,
                source_type="web_scrape",
                source_name=request.source_name,
                source_url=str(request.base_url)
            )
            content_repo.close()
        else:
            stats = {"saved": 0, "duplicates": 0, "errors": 0}
        
        # Optionally add to monitoring
        source_id = None
        if request.add_to_monitoring and contents:
            config_repo = SourceConfigRepository()
            source = config_repo.add_source(
                source_type="web_scrape",
                source_name=request.source_name,
                source_url=str(request.base_url),
                config={
                    "selectors": request.selectors,
                    "max_pages": request.max_pages
                },
                fetch_interval_minutes=360  # 6 hours default
            )
            source_id = source.id
            config_repo.close()
        
        return {
            "message": "Website scraped successfully",
            "items_found": len(contents),
            "stats": stats,
            "monitoring": {
                "added": request.add_to_monitoring,
                "source_id": source_id
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to scrape website: {str(e)}")


@app.post("/api/sources/scrape/setup-blogs")
async def setup_blog_sources():
    """
    Bulk add all configured blog sources from scraping_sources.json
    
    This will add all blogs organized by team to the monitoring system
    """
    try:
        import json
        from pathlib import Path
        
        # Load scraping sources
        config_file = Path(__file__).parent / "scraping_sources.json"
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        repo = SourceConfigRepository()
        added = []
        skipped = []
        errors = []
        
        for team_key, team_data in config['scraping_sources'].items():
            for blog in team_data['blogs']:
                # Check if already exists
                existing = repo.list_sources()
                if any(s.source_url == blog['url'] for s in existing):
                    skipped.append(blog['name'])
                    continue
                
                try:
                    source = repo.add_source(
                        source_type="blog_scrape",
                        source_name=f"{team_key.upper()}: {blog['name']}",
                        source_url=blog['url'],
                        config={
                            'selectors': blog['selectors'],
                            'max_pages': 5,
                            'team_key': team_key
                        },
                        fetch_interval_minutes=blog['fetch_interval_hours'] * 60
                    )
                    added.append({
                        "name": blog['name'],
                        "url": blog['url'],
                        "team": team_key,
                        "source_id": source.id
                    })
                except Exception as e:
                    errors.append({
                        "name": blog['name'],
                        "error": str(e)
                    })
        
        repo.close()
        
        return {
            "message": "Blog sources setup complete",
            "added": len(added),
            "skipped": len(skipped),
            "errors": len(errors),
            "details": {
                "added_sources": added,
                "skipped_sources": skipped,
                "errors": errors
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to setup blog sources: {str(e)}")


@app.get("/api/sources/scrape/stats")
async def get_scraping_stats():
    """Get statistics about configured scraping sources"""
    try:
        repo = SourceConfigRepository()
        all_sources = repo.list_sources()
        repo.close()
        
        # Filter blog/web scraping sources
        scraping_sources = [s for s in all_sources if s.source_type in ["blog_scrape", "web_scrape"]]
        
        # Group by team
        by_team = {}
        for source in scraping_sources:
            team_key = source.config.get('team_key', 'unknown')
            if team_key not in by_team:
                by_team[team_key] = {
                    "sources": [],
                    "total_items": 0,
                    "enabled_count": 0
                }
            
            by_team[team_key]["sources"].append({
                "id": source.id,
                "name": source.source_name,
                "url": source.source_url,
                "enabled": source.enabled,
                "items_fetched": source.total_items_fetched,
                "last_fetched": source.last_fetched_at.isoformat() if source.last_fetched_at else None
            })
            by_team[team_key]["total_items"] += source.total_items_fetched
            if source.enabled:
                by_team[team_key]["enabled_count"] += 1
        
        return {
            "total_sources": len(scraping_sources),
            "enabled": sum(1 for s in scraping_sources if s.enabled),
            "disabled": sum(1 for s in scraping_sources if not s.enabled),
            "total_items_fetched": sum(s.total_items_fetched for s in scraping_sources),
            "by_team": by_team
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get scraping stats: {str(e)}")


# ========== SCHEDULER ENDPOINTS ==========

@app.get("/api/scheduler/status")
async def get_scheduler_status():
    """Get scheduler status"""
    scheduler = get_scheduler()
    return {
        "running": scheduler.is_running(),
        "stats": scheduler.get_stats()
    }


@app.post("/api/scheduler/start")
async def start_scheduler(background_tasks: BackgroundTasks):
    """Manually start the scheduler"""
    global scheduler_task
    scheduler = get_scheduler()
    
    if scheduler.is_running():
        return {"message": "Scheduler is already running", "status": "running"}
    
    if scheduler_task and not scheduler_task.done():
        return {"message": "Scheduler task is already active", "status": "running"}
    
    # Start scheduler in background
    scheduler_task = asyncio.create_task(scheduler.run())
    return {"message": "Scheduler started", "status": "running"}


@app.post("/api/scheduler/stop")
async def stop_scheduler():
    """Manually stop the scheduler"""
    global scheduler_task
    scheduler = get_scheduler()
    
    if not scheduler.is_running():
        return {"message": "Scheduler is not running", "status": "stopped"}
    
    scheduler.stop()
    if scheduler_task:
        scheduler_task.cancel()
        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass
        scheduler_task = None
    
    return {"message": "Scheduler stopped", "status": "stopped"}


# ============================================================================
# Data Lake / Storage API Endpoints
# ============================================================================

class AddSourceRequest(BaseModel):
    """Request model for adding a source to monitor."""
    source_type: str
    source_name: str
    source_url: str
    fetch_interval_minutes: Optional[int] = 60
    config: Optional[dict] = {}


class FetchAndStoreRequest(BaseModel):
    """Request model for fetching and storing RSS feed."""
    feed_url: HttpUrl
    source_name: str
    max_entries: Optional[int] = 50
    add_to_monitoring: Optional[bool] = False
    fetch_interval_minutes: Optional[int] = 60


@app.post("/api/datalake/sources/add")
async def add_source_to_monitor(request: AddSourceRequest):
    """
    Add a new source to the monitoring list.
    
    The scheduler will automatically fetch from this source at the specified interval.
    """
    try:
        config_repo = SourceConfigRepository()
        
        source = config_repo.add_source(
            source_type=request.source_type,
            source_name=request.source_name,
            source_url=request.source_url,
            config=request.config,
            fetch_interval_minutes=request.fetch_interval_minutes,
        )
        
        config_repo.close()
        
        return {
            "message": "Source added successfully",
            "source": {
                "id": source.id,
                "name": source.source_name,
                "type": source.source_type,
                "url": source.source_url,
                "fetch_interval_minutes": source.fetch_interval_minutes,
                "next_fetch_at": source.next_fetch_at.isoformat() if source.next_fetch_at else None,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add source: {str(e)}")


@app.get("/api/datalake/sources/list")
async def list_monitored_sources(enabled_only: bool = False):
    """
    List all configured sources.
    
    Args:
        enabled_only: If true, only return enabled sources
    """
    try:
        config_repo = SourceConfigRepository()
        sources = config_repo.list_sources(enabled_only=enabled_only)
        config_repo.close()
        
        return {
            "total": len(sources),
            "sources": [
                {
                    "id": s.id,
                    "name": s.source_name,
                    "type": s.source_type,
                    "url": s.source_url,
                    "enabled": s.enabled,
                    "fetch_interval_minutes": s.fetch_interval_minutes,
                    "total_items_fetched": s.total_items_fetched,
                    "last_fetched_at": s.last_fetched_at.isoformat() if s.last_fetched_at else None,
                    "next_fetch_at": s.next_fetch_at.isoformat() if s.next_fetch_at else None,
                    "last_error": s.last_error,
                }
                for s in sources
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sources: {str(e)}")


@app.post("/api/datalake/fetch-and-store")
async def fetch_and_store_rss(request: FetchAndStoreRequest):
    """
    Fetch from RSS feed and store in data lake with deduplication.
    
    Optionally add the source to monitoring for automatic periodic fetching.
    """
    try:
        # Fetch content
        sourcer = RSSSourcer(
            feed_url=str(request.feed_url),
            name=request.source_name,
            max_entries=request.max_entries
        )
        
        contents = await sourcer.fetch()
        
        # Store with deduplication
        content_repo = ContentRepository()
        stats = content_repo.save_batch(
            contents,
            source_type="rss",
            source_name=request.source_name,
            source_url=str(request.feed_url),
        )
        content_repo.close()
        
        # Optionally add to monitoring
        source_id = None
        if request.add_to_monitoring:
            config_repo = SourceConfigRepository()
            source = config_repo.add_source(
                source_type="rss",
                source_name=request.source_name,
                source_url=str(request.feed_url),
                config={"max_entries": request.max_entries},
                fetch_interval_minutes=request.fetch_interval_minutes,
            )
            source_id = source.id
            config_repo.close()
        
        return {
            "message": "Content fetched and stored successfully",
            "stats": stats,
            "monitoring": {
                "added": request.add_to_monitoring,
                "source_id": source_id,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch and store: {str(e)}")


@app.get("/api/datalake/stats")
async def get_datalake_stats():
    """Get statistics about stored content in the data lake."""
    try:
        content_repo = ContentRepository()
        stats = content_repo.get_statistics()
        content_repo.close()
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@app.get("/api/datalake/content/unprocessed")
async def get_unprocessed_content(limit: int = 100, source_type: Optional[str] = None):
    """
    Get unprocessed content ready for NLP/ML processing.
    
    Args:
        limit: Maximum number of items to return
        source_type: Filter by source type (optional)
    """
    try:
        content_repo = ContentRepository()
        contents = content_repo.get_unprocessed_content(limit=limit, source_type=source_type)
        content_repo.close()
        
        return {
            "total": len(contents),
            "contents": [
                {
                    "id": c.id,
                    "title": c.title,
                    "content": c.content,
                    "url": c.url,
                    "source_type": c.source_type,
                    "source_name": c.source_name,
                    "author": c.author,
                    "published_date": c.published_date.isoformat() if c.published_date else None,
                    "retrieved_at": c.retrieved_at.isoformat(),
                    "metadata": c.extra_metadata,
                }
                for c in contents
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get unprocessed content: {str(e)}")


@app.post("/api/datalake/content/{content_id}/mark-processed")
async def mark_content_processed(content_id: int, status: str = "completed"):
    """
    Mark content as processed.
    
    Args:
        content_id: ID of the content item
        status: Processing status ('completed', 'failed', etc.)
    """
    try:
        content_repo = ContentRepository()
        content_repo.mark_as_processed(content_id, status)
        content_repo.close()
        
        return {"message": "Content marked as processed", "content_id": content_id, "status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark content: {str(e)}")


# ============================================================================
# Keywords API Endpoints
# ============================================================================

import sqlite3
import json
from pathlib import Path

# Database paths for keywords
KEYWORDS_DB = Path(__file__).parent / "data" / "keywords.db"
TEAMS_DB = Path(__file__).parent / "data" / "teams.db"


def get_keywords_db():
    """Get keywords database connection."""
    conn = sqlite3.connect(KEYWORDS_DB)
    conn.row_factory = sqlite3.Row
    return conn


def get_teams_db():
    """Get teams database connection."""
    conn = sqlite3.connect(TEAMS_DB)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/api/teams")
async def get_teams():
    """Get all active teams."""
    try:
        conn = get_teams_db()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT team_key, team_name, description, color, icon, is_active
            FROM internal_teams
            WHERE is_active = 1
            ORDER BY team_name
        """)
        
        teams = []
        for row in cur.fetchall():
            teams.append({
                "team_key": row['team_key'],
                "team_name": row['team_name'],
                "description": row['description'],
                "color": row['color'],
                "icon": row['icon'],
                "is_active": bool(row['is_active'])
            })
        
        conn.close()
        return {"teams": teams, "count": len(teams)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get teams: {str(e)}")


@app.get("/api/keywords")
async def get_keywords(
    date: str,
    team: Optional[str] = None,
    limit: int = 50,
    min_score: float = 0
):
    """
    Get keywords for a specific date and optional team.
    
    Query parameters:
    - date: YYYY-MM-DD (required)
    - team: team_key (optional, default: all teams)
    - limit: max results (optional, default: 50)
    - min_score: minimum importance score (optional, default: 0)
    """
    try:
        # Validate date format
        from datetime import datetime
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Query database
        conn = get_keywords_db()
        cur = conn.cursor()
        
        # Build query
        sql = """
            SELECT 
                keyword,
                team_key,
                importance_score,
                sentiment_score,
                sentiment_magnitude,
                frequency,
                document_count,
                source_diversity,
                velocity,
                positive_mentions,
                negative_mentions,
                neutral_mentions,
                content_ids,
                sample_snippets
            FROM keyword_importance
            WHERE date = ?
              AND importance_score >= ?
        """
        params = [date, min_score]
        
        if team:
            sql += " AND team_key = ?"
            params.append(team)
        
        sql += " ORDER BY importance_score DESC LIMIT ?"
        params.append(limit)
        
        cur.execute(sql, params)
        
        keywords = []
        for row in cur.fetchall():
            # Parse JSON fields
            content_ids = json.loads(row['content_ids']) if row['content_ids'] else []
            snippets_raw = json.loads(row['sample_snippets']) if row['sample_snippets'] else []
            
            keywords.append({
                "keyword": row['keyword'],
                "team_key": row['team_key'],
                "importance_score": round(row['importance_score'], 2),
                "sentiment": {
                    "score": round(row['sentiment_score'], 3),
                    "magnitude": round(row['sentiment_magnitude'], 3),
                    "positive": row['positive_mentions'],
                    "negative": row['negative_mentions'],
                    "neutral": row['neutral_mentions']
                },
                "metrics": {
                    "frequency": row['frequency'],
                    "document_count": row['document_count'],
                    "source_diversity": row['source_diversity'],
                    "velocity": round(row['velocity'], 2) if row['velocity'] else 0.0
                },
                "content_ids": content_ids,
                "sample_snippets": snippets_raw[:3]  # Max 3 snippets
            })
        
        conn.close()
        
        return {
            "date": date,
            "team": team or "all",
            "keywords": keywords,
            "count": len(keywords)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get keywords: {str(e)}")


@app.get("/api/keywords/stats")
async def get_keyword_stats():
    """Get overall keyword statistics."""
    try:
        conn = get_keywords_db()
        cur = conn.cursor()
        
        # Total keywords
        cur.execute("SELECT COUNT(*) as total FROM keyword_importance")
        total = cur.fetchone()['total']
        
        # By team
        cur.execute("""
            SELECT team_key, COUNT(*) as count
            FROM keyword_importance
            GROUP BY team_key
            ORDER BY count DESC
        """)
        by_team = [{"team": row['team_key'], "count": row['count']} for row in cur.fetchall()]
        
        # By date
        cur.execute("""
            SELECT date, COUNT(DISTINCT keyword) as count
            FROM keyword_importance
            GROUP BY date
            ORDER BY date DESC
            LIMIT 10
        """)
        by_date = [{"date": row['date'], "count": row['count']} for row in cur.fetchall()]
        
        # Date range
        cur.execute("""
            SELECT MIN(date) as min_date, MAX(date) as max_date
            FROM keyword_importance
        """)
        date_range_row = cur.fetchone()
        
        conn.close()
        
        return {
            "total_keywords": total,
            "by_team": by_team,
            "by_date": by_date,
            "date_range": {
                "start": date_range_row['min_date'],
                "end": date_range_row['max_date']
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@app.get("/api/keywords/search")
async def search_keywords(
    q: str,
    team: Optional[str] = None,
    limit: int = 20
):
    """
    Search for keywords by text.
    
    Query parameters:
    - q: search query (required)
    - team: team_key (optional)
    - limit: max results (optional, default: 20)
    """
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required and cannot be empty")
    
    try:
        conn = get_keywords_db()
        cur = conn.cursor()
        
        sql = """
            SELECT DISTINCT
                keyword,
                team_key,
                MAX(importance_score) as max_score,
                SUM(frequency) as total_freq,
                COUNT(*) as occurrences
            FROM keyword_importance
            WHERE keyword LIKE ?
        """
        params = [f"%{q.strip()}%"]
        
        if team:
            sql += " AND team_key = ?"
            params.append(team)
        
        sql += """
            GROUP BY keyword, team_key
            ORDER BY max_score DESC
            LIMIT ?
        """
        params.append(limit)
        
        cur.execute(sql, params)
        
        results = []
        for row in cur.fetchall():
            results.append({
                "keyword": row['keyword'],
                "team_key": row['team_key'],
                "max_score": round(row['max_score'], 2),
                "total_frequency": row['total_freq'],
                "occurrences": row['occurrences']
            })
        
        conn.close()
        
        return {
            "query": q.strip(),
            "results": results,
            "count": len(results)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search keywords: {str(e)}")

