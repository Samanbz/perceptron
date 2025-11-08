"""Main FastAPI application for Signal Radar backend."""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager
import asyncio
import re
import sys
import logging
import json
from io import BytesIO

# Load environment variables from .env file
from dotenv import load_dotenv
import os
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
import logging

# Configure OpenAI
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

# ReportLab imports for PDF generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch

# Set up logging
logger = logging.getLogger(__name__)

# Fix for Playwright on Windows - must be set before any async operations
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Fix for sourcers import - add current directory to path
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sourcers import RSSSourcer
# from sourcers.web_scraper import BlogScraper, NewsScraper, GenericWebScraper  # Not needed for keywords API
from storage import (
    ContentRepository,
    SourceConfigRepository,
    create_database,
    get_database_url,
)
from payment_routes import router as payment_router
from scout_routes import router as scout_router
from scheduler import get_scheduler
from peers_newsroom_apis import PeersNewsroomAPIs
from reputation_apis import reputation_aggregator, ReputationData

# Initialize peers newsroom APIs
peers_apis = PeersNewsroomAPIs()

# Global scheduler task
scheduler_task = None

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler_task
    # Startup
    create_database(get_database_url())
    
    # Check database connection status
    from auth.repository_v2 import user_repository
    if user_repository.db_available:
        print("✅ Cosmos DB (MongoDB API) connected successfully")
    else:
        print("⚠️  Cosmos DB connection failed - running in offline mode")
    
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


# ============================================================================
# Keywords API Endpoints
# ============================================================================

from keywords.importance_repository import ImportanceRepository
from storage.repository import ContentRepository as KeywordContentRepository
from teams.repository import TeamRepository
from datetime import date
import json


@app.get("/api/keywords/{team_key}/{date_str}")
async def get_keywords_for_team_and_date(team_key: str, date_str: str):
    """
    Get keywords for a specific team and date in API format.
    
    Args:
        team_key: Team key (regulator, investor, competitor, researcher)
        date_str: Date in ISO format (YYYY-MM-DD)
        
    Returns:
        JSON matching api_models.py WordCloudResponse structure
    """
    try:
        # Parse date
        query_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Initialize repositories
    importance_repo = ImportanceRepository()
    content_repo = KeywordContentRepository()
    team_repo = TeamRepository()
    
    try:
        # Get team info
        team = team_repo.get_team_by_key(team_key)
        if not team:
            raise HTTPException(status_code=404, detail=f"Team '{team_key}' not found")
        
        # Get top keywords with importance >= 30
        top_keywords = importance_repo.get_top_keywords(
            team_key=team_key,
            analysis_date=query_date,
            limit=50,
            min_importance=30.0
        )
        
        if not top_keywords:
            return {
                "team_key": team_key,
                "team_name": team.team_name,
                "date_range": {
                    "start": date_str,
                    "end": date_str
                },
                "keywords": [],
                "total_keywords": 0,
                "total_documents": 0
            }
        
        # Build keyword data
        keywords_data = []
        
        for importance_record in top_keywords:
            # Build sentiment data
            sentiment_data = {
                "score": round(float(importance_record.sentiment_score or 0.0), 3),
                "magnitude": round(float(importance_record.sentiment_magnitude or 0.0), 3),
                "breakdown": {
                    "positive": importance_record.positive_mentions or 0,
                    "negative": importance_record.negative_mentions or 0,
                    "neutral": importance_record.neutral_mentions or 0
                }
            }
            
            # Build metrics
            metrics_data = {
                "frequency": importance_record.frequency or 0,
                "document_count": importance_record.document_count or 0,
                "source_diversity": importance_record.source_diversity or 0,
                "velocity": round(float(importance_record.velocity or 0.0), 2)
            }
            
            # Get documents
            documents = []
            if importance_record.content_ids:
                content_ids = json.loads(importance_record.content_ids) if isinstance(importance_record.content_ids, str) else importance_record.content_ids
                
                for content_id in content_ids[:10]:  # Limit to 10 as per API spec
                    content = content_repo.get_content_by_id(content_id)
                    if content:
                        # Extract snippet containing keyword
                        text = content.content or content.title
                        keyword_lower = importance_record.keyword.lower()
                        text_lower = text.lower()
                        pos = text_lower.find(keyword_lower)
                        
                        if pos == -1:
                            snippet = f"{text[:150]}..." if len(text) > 150 else text
                        else:
                            start = max(0, pos - 75)
                            end = min(len(text), pos + len(importance_record.keyword) + 75)
                            snippet = text[start:end]
                            if start > 0:
                                snippet = "..." + snippet
                            if end < len(text):
                                snippet = snippet + "..."
                        
                        documents.append({
                            "content_id": content.id,
                            "title": content.title,
                            "source_name": content.source_name,
                            "published_date": content.published_date.isoformat() if content.published_date else date_str,
                            "url": content.url or content.source_url or f"https://example.com/article-{content.id}",
                            "snippet": snippet
                        })
            
            keywords_data.append({
                "keyword": importance_record.keyword,
                "date": date_str,
                "importance": round(float(importance_record.importance_score or 0.0), 1),
                "sentiment": sentiment_data,
                "metrics": metrics_data,
                "documents": documents
            })
        
        # Return response matching api_models.py WordCloudResponse
        return {
            "team_key": team_key,
            "team_name": team.team_name,
            "date_range": {
                "start": date_str,
                "end": date_str
            },
            "keywords": keywords_data,
            "total_keywords": len(keywords_data),
            "total_documents": sum(kw['metrics']['document_count'] for kw in keywords_data)
        }
    
    finally:
        importance_repo.close()
        content_repo.close()
        team_repo.close()


@app.get("/api/teams")
async def get_teams():
    """
    Get list of all active teams.
    
    Returns:
        List of teams with their keys and names
    """
    team_repo = TeamRepository()
    try:
        teams = [t for t in team_repo.get_all_teams() if t.is_active]
        return {
            "teams": [
                {
                    "key": team.team_key,
                    "name": team.team_name,
                    "description": team.description,
                    "color": team.color,
                    "icon": team.icon
                }
                for team in teams
            ]
        }
    finally:
        team_repo.close()


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


# ============================================================================
# Peers Newsroom API Endpoints
# ============================================================================

@app.get("/api/peers/quarterly-reports")
async def get_quarterly_reports(limit: int = 20):
    """
    Get quarterly reports and earnings data from peer companies.
    
    Returns aggregated quarterly reports with key metrics and highlights.
    """
    try:
        # Use real financial APIs instead of scraped content
        data = peers_apis.get_quarterly_reports()
        
        # Transform to frontend format
        reports = []
        for symbol, report_data in data.get('quarterly_reports', {}).items():
            if 'error' not in report_data:
                # Get earnings data
                earnings = report_data.get('earnings', [])
                income_stmt = report_data.get('income_statement', [])
                
                # Create report entry for each quarter
                for i, earning in enumerate(earnings[:4]):  # Last 4 quarters
                    reports.append({
                        "id": f"{symbol}_Q{i+1}_{earning.get('fiscalDateEnding', '')}",
                        "company": symbol,
                        "quarter": f"Q{((int(earning.get('fiscalDateEnding', '2024-01-01')[:4]) - 2023) % 4) + 1} {earning.get('fiscalDateEnding', '')[:4]}",
                        "title": f"{symbol} Q{((int(earning.get('fiscalDateEnding', '2024-01-01')[:4]) - 2023) % 4) + 1} Earnings Report",
                        "date": earning.get('fiscalDateEnding'),
                        "keyMetrics": {
                            "revenue": earning.get('reportedEPS', 'N/A'),
                            "eps": earning.get('reportedEPS', 'N/A'),
                            "growth": f"{earning.get('reportedEPS', '0')}%"
                        },
                        "highlights": [
                            f"Reported EPS: {earning.get('reportedEPS', 'N/A')}",
                            f"Estimated EPS: {earning.get('estimatedEPS', 'N/A')}",
                            f"Surprise: {earning.get('surprise', 'N/A')}"
                        ],
                        "tone": "positive" if earning.get('surprise', 0) > 0 else "neutral",
                        "authority": 9.5,
                        "url": f"https://finance.yahoo.com/quote/{symbol}"
                    })
        
        return {
            "reports": reports[:limit],
            "count": len(reports),
            "last_updated": data.get('timestamp'),
            "data_source": data.get('data_source')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get quarterly reports: {str(e)}")


@app.get("/api/peers/capital-markets")
async def get_capital_markets_updates(limit: int = 20):
    """
    Get capital markets updates, analyst reports, and economic indicators.
    
    Returns market news and analysis from financial sources.
    """
    try:
        # Use real financial APIs for capital markets updates
        data = peers_apis.get_capital_markets_updates()
        
        # Transform to frontend format
        updates = []
        for symbol, symbol_updates in data.get('capital_markets_updates', {}).items():
            if 'error' not in symbol_updates:
                # Add news articles from Polygon.io
                for news in symbol_updates.get('news', []):
                    updates.append({
                        "id": f"{symbol}_news_{hash(news.get('title', ''))}",
                        "title": news.get('title', f'{symbol} Market News'),
                        "source": news.get('source', 'Polygon.io'),
                        "date": news.get('publishedDate', ''),
                        "summary": news.get('description', '')[:200] + '...' if len(news.get('description', '')) > 200 else news.get('description', ''),
                        "impact": "medium",
                        "sentiment": "neutral",
                        "topics": ["market news", "financial markets"],
                        "url": news.get('url', f"https://polygon.io/")
                    })

                # Add trade data if available
                for trade in symbol_updates.get('recent_trades', []):
                    updates.append({
                        "id": f"{symbol}_trade_{trade.get('timestamp', 0)}",
                        "title": f"{symbol} Recent Trading Activity",
                        "source": "Polygon.io",
                        "date": datetime.fromtimestamp(trade.get('timestamp', 0) / 1000000000).isoformat() if trade.get('timestamp') else '',
                        "summary": f"Last price: ${trade.get('price', 0):.2f}, Size: {trade.get('size', 0)} shares",
                        "impact": "low",
                        "sentiment": "neutral",
                        "topics": ["trading", "price action"],
                        "url": f"https://polygon.io/"
                    })
        
        return {
            "updates": updates[:limit],
            "count": len(updates),
            "last_updated": data.get('timestamp'),
            "data_source": data.get('data_source')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get capital markets updates: {str(e)}")


@app.get("/api/peers/executive-speeches")
async def get_executive_speeches(limit: int = 20):
    """
    Get executive speeches, presentations, and communications.
    
    Returns CEO/CFO speeches and key executive communications.
    """
    try:
        # Use real financial APIs for executive speeches
        data = peers_apis.get_executive_speeches()
        
        # Transform to frontend format
        speeches = []
        for symbol, symbol_speeches in data.get('executive_speeches', {}).items():
            for quarter, speech_data in symbol_speeches.items():
                if speech_data and 'transcript' in speech_data:
                    transcript = speech_data['transcript']
                    
                    speeches.append({
                        "id": f"{symbol}_{quarter}_speech",
                        "speaker": "CEO/CFO",  # Would need to extract from transcript
                        "company": symbol,
                        "title": f"{symbol} {quarter} Earnings Call Transcript",
                        "date": speech_data.get('date', quarter),
                        "topics": ["earnings", "financial results", "outlook"],
                        "keyQuotes": [
                            "Sample quote from earnings call"  # Would extract from transcript
                        ],
                        "tone": "neutral",
                        "authority": 9.8,
                        "url": f"https://finance.yahoo.com/quote/{symbol}"
                    })
        
        return {
            "speeches": speeches[:limit],
            "count": len(speeches),
            "last_updated": data.get('timestamp'),
            "data_source": data.get('data_source')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get executive speeches: {str(e)}")


@app.get("/api/peers/analysis")
async def get_peers_analysis():
    """
    Get comprehensive analysis of peers newsroom content.
    
    Returns topic analysis, tone distribution, authority scores, and content recommendations.
    """
    try:
        # Use real financial APIs for peer analysis
        data = peers_apis.get_peer_analysis()
        
        # Transform to frontend format
        analysis = {
            "topTopics": ["earnings", "financial performance", "market outlook", "executive communications"],
            "toneDistribution": {
                "positive": 45,
                "neutral": 35,
                "negative": 20
            },
            "authorityScores": {
                "high": 60,
                "medium": 30,
                "low": 10
            },
            "recommendedLanes": [
                "Focus on Q4 earnings season analysis",
                "Monitor executive communications for strategic insights",
                "Track capital markets sentiment for investment opportunities"
            ]
        }

        # Add real data insights if available
        if data.get('peer_analysis'):
            companies_analyzed = len([c for c in data['peer_analysis'].values() if 'error' not in c])
            analysis["content_analyzed"] = companies_analyzed
            analysis["data_source"] = data.get('data_source', 'Financial APIs')

            # Add company insights
            company_insights = []
            for symbol, company_data in data['peer_analysis'].items():
                if 'error' not in company_data and company_data.get('company_profile'):
                    profile = company_data['company_profile']
                    company_insights.append({
                        "symbol": symbol,
                        "name": profile.get('name', symbol),
                        "industry": profile.get('finnhubIndustry', 'Unknown'),
                        "market_cap": profile.get('marketCapitalization', 0),
                        "pe_ratio": company_data.get('basic_financials', {}).get('peNormalizedAnnual', 'N/A')
                    })
            analysis["company_insights"] = company_insights[:5]  # Top 5 companies

        return {
            "analysis": analysis,
            "content_analyzed": data.get('peer_analysis', {}),
            "analysis_date": data.get('timestamp', datetime.now().isoformat())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get peers analysis: {str(e)}")


# ChatGPT Analysis Endpoints for Executive Speeches
# ============================================================================

class TranscriptAnalysisRequest(BaseModel):
    """Request model for transcript analysis."""
    speech_id: str
    transcript: str
    company: str
    speaker: Optional[str] = None


class ToneAnalysisRequest(BaseModel):
    """Request model for tone analysis."""
    speech_id: str
    transcript: str
    company: str
    speaker: Optional[str] = None


@app.post("/api/peers/analyze-transcript")
async def analyze_transcript(request: TranscriptAnalysisRequest):
    """
    Analyze executive speech transcript using ChatGPT.

    Returns detailed analysis of the speech content, key points, and insights.
    """
    try:
        if not openai.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")

        # Create ChatGPT prompt for transcript analysis
        prompt = f"""
        Analyze the following executive speech transcript from {request.company}.
        Provide a comprehensive analysis including:

        1. **Key Themes and Topics**: Main subjects discussed
        2. **Strategic Insights**: Important business strategies or directions mentioned
        3. **Financial Highlights**: Any financial performance or outlook information
        4. **Risk Factors**: Potential challenges or concerns raised
        5. **Market Context**: Industry or market observations
        6. **Future Outlook**: Forward-looking statements and projections

        Transcript:
        {request.transcript}

        Please structure your response as a JSON object with the following format:
        {{
            "summary": "Brief 2-3 sentence summary of the speech",
            "keyThemes": ["theme1", "theme2", "theme3"],
            "strategicInsights": ["insight1", "insight2"],
            "financialHighlights": ["highlight1", "highlight2"],
            "riskFactors": ["risk1", "risk2"],
            "marketContext": "Analysis of market/industry observations",
            "futureOutlook": "Key forward-looking statements",
            "sentiment": "positive|neutral|negative",
            "confidence": 0.0-1.0
        }}
        """

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert financial analyst specializing in executive communications analysis. Provide objective, insightful analysis of corporate speeches and presentations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.3
        )

        # Parse the response
        analysis_text = response.choices[0].message.content.strip()

        # Try to parse as JSON, fallback to text if needed
        try:
            analysis = json.loads(analysis_text)
        except json.JSONDecodeError:
            # Fallback: extract key information from text response
            analysis = {
                "summary": analysis_text[:300] + "..." if len(analysis_text) > 300 else analysis_text,
                "keyThemes": ["Analysis completed"],
                "strategicInsights": ["See full analysis"],
                "financialHighlights": [],
                "riskFactors": [],
                "marketContext": "Analysis provided above",
                "futureOutlook": "See summary",
                "sentiment": "neutral",
                "confidence": 0.8,
                "fullAnalysis": analysis_text
            }

        # Add metadata
        analysis.update({
            "speech_id": request.speech_id,
            "company": request.company,
            "speaker": request.speaker,
            "analyzed_at": datetime.now().isoformat(),
            "model": "gpt-3.5-turbo"
        })

        return analysis

    except Exception as e:
        logger.error(f"Error in transcript analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze transcript: {str(e)}")


@app.post("/api/peers/analyze-tone")
async def analyze_tone(request: ToneAnalysisRequest):
    """
    Analyze the tone and sentiment of executive speech using ChatGPT.

    Returns detailed tone analysis including emotional indicators and communication style.
    """
    try:
        if not openai.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")

        # Create ChatGPT prompt for tone analysis
        prompt = f"""
        Analyze the tone, sentiment, and communication style of this executive speech transcript from {request.company}.

        Focus on:
        1. **Overall Sentiment**: Positive, negative, or neutral tone
        2. **Emotional Indicators**: Confidence, optimism, caution, concern
        3. **Communication Style**: Direct, diplomatic, assertive, collaborative
        4. **Key Emotional Triggers**: What aspects seem to evoke strong emotions
        5. **Audience Engagement**: How the speaker connects with the audience
        6. **Confidence Level**: Speaker's apparent confidence in statements

        Transcript:
        {request.transcript}

        Please structure your response as a JSON object with the following format:
        {{
            "overallSentiment": "positive|neutral|negative",
            "sentimentScore": -1.0 to 1.0,
            "emotionalIndicators": {{
                "confidence": 0.0-1.0,
                "optimism": 0.0-1.0,
                "caution": 0.0-1.0,
                "concern": 0.0-1.0
            }},
            "communicationStyle": "direct|diplomatic|assertive|collaborative|other",
            "keyEmotionalTriggers": ["trigger1", "trigger2"],
            "audienceEngagement": "Description of how speaker engages audience",
            "confidenceLevel": 0.0-1.0,
            "toneSummary": "Brief summary of the overall tone and style",
            "confidence": 0.0-1.0
        }}
        """

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in communication analysis and emotional intelligence. Analyze corporate executive communications for tone, sentiment, and psychological indicators."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,
            temperature=0.2
        )

        # Parse the response
        analysis_text = response.choices[0].message.content.strip()

        # Try to parse as JSON, fallback to text if needed
        try:
            analysis = json.loads(analysis_text)
        except json.JSONDecodeError:
            # Fallback: create structured response from text
            analysis = {
                "overallSentiment": "neutral",
                "sentimentScore": 0.0,
                "emotionalIndicators": {
                    "confidence": 0.5,
                    "optimism": 0.5,
                    "caution": 0.5,
                    "concern": 0.5
                },
                "communicationStyle": "professional",
                "keyEmotionalTriggers": ["Analysis completed"],
                "audienceEngagement": "Professional delivery",
                "confidenceLevel": 0.8,
                "toneSummary": analysis_text[:200] + "..." if len(analysis_text) > 200 else analysis_text,
                "confidence": 0.8,
                "fullAnalysis": analysis_text
            }

        # Add metadata
        analysis.update({
            "speech_id": request.speech_id,
            "company": request.company,
            "speaker": request.speaker,
            "analyzed_at": datetime.now().isoformat(),
            "model": "gpt-3.5-turbo"
        })

        return analysis

    except Exception as e:
        logger.error(f"Error in tone analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze tone: {str(e)}")


# Full Company Report Generation Endpoint
# ============================================================================

class FullReportRequest(BaseModel):
    """Request model for full company report generation."""
    company: str
    quarter: str
    report_data: Dict[str, Any]


class KeywordReportRequest(BaseModel):
    """Request model for keyword report generation."""
    keyword: str
    importance: float
    metrics: Dict[str, Any]
    documents: List[Dict[str, Any]]
    timeSeries: List[Dict[str, Any]]
    team: str
    currentDate: str


@app.post("/api/peers/generate-full-report")
async def generate_full_report(request: FullReportRequest):
    """
    Generate a comprehensive AI-powered company report with financial analysis.

    Returns detailed company analysis including financial performance, ratios, risks, and investment recommendations.
    """
    try:
        if not openai.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")

        # Create comprehensive report prompt
        prompt = f"""
        Generate a comprehensive financial analysis report for {request.company} based on their {request.quarter} earnings report.

        Use the following financial data as context:
        - Revenue: {request.report_data.get('keyMetrics', {}).get('revenue', 'N/A')}
        - EPS: {request.report_data.get('keyMetrics', {}).get('eps', 'N/A')}
        - Growth: {request.report_data.get('keyMetrics', {}).get('growth', 'N/A')}
        - Key Highlights: {', '.join(request.report_data.get('highlights', []))}
        - Report Date: {request.report_data.get('date', 'N/A')}

        Please structure your response as a detailed JSON object with the following format:
        {{
            "company": "{request.company}",
            "quarter": "{request.quarter}",
            "executiveSummary": "2-3 paragraph executive summary of the company's performance and outlook",
            "financialAnalysis": {{
                "revenueAnalysis": "Detailed analysis of revenue performance, trends, and drivers",
                "profitabilityAnalysis": "Analysis of profitability metrics, margins, and efficiency",
                "growthAnalysis": "Assessment of growth rates, sustainability, and market position"
            }},
            "balanceSheetAnalysis": "Analysis of balance sheet strength, liquidity, leverage, and asset quality",
            "cashFlowAnalysis": "Assessment of cash flow generation, operating efficiency, and capital allocation",
            "keyRatios": [
                {{
                    "name": "PE Ratio",
                    "value": "25.4x",
                    "interpretation": "Above industry average, suggesting premium valuation"
                }},
                {{
                    "name": "ROE",
                    "value": "18.5%",
                    "interpretation": "Strong return on equity indicating efficient capital utilization"
                }},
                {{
                    "name": "Debt-to-Equity",
                    "value": "0.45",
                    "interpretation": "Conservative leverage providing financial stability"
                }},
                {{
                    "name": "Gross Margin",
                    "value": "38.2%",
                    "interpretation": "Healthy margins showing pricing power and cost control"
                }},
                {{
                    "name": "Current Ratio",
                    "value": "2.1",
                    "interpretation": "Strong liquidity position"
                }}
            ],
            "industryComparison": "Comparison with industry peers and market positioning",
            "riskAssessment": {{
                "financialRisks": ["List 2-3 key financial risks"],
                "operationalRisks": ["List 2-3 key operational risks"],
                "marketRisks": ["List 2-3 key market/external risks"]
            }},
            "investmentRecommendation": {{
                "rating": "BUY|HOLD|SELL",
                "rationale": "Detailed rationale for the recommendation",
                "targetPrice": "$XXX.XX",
                "timeHorizon": "12-18 months"
            }},
            "forwardOutlook": "Assessment of future growth prospects, catalysts, and potential challenges",
            "confidence": 0.85,
            "generated_at": "{datetime.now().isoformat()}"
        }}

        Ensure the analysis is professional, data-driven, and balanced. Include specific numbers and metrics where possible. Make realistic assumptions based on typical industry standards when specific data isn't available.
        """

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a senior financial analyst at a top investment bank. Provide comprehensive, professional financial analysis with specific metrics, ratios, and well-reasoned investment recommendations. Always include specific numbers and be data-driven in your analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,
            temperature=0.3
        )

        # Parse the response
        report_text = response.choices[0].message.content.strip()

        # Try to parse as JSON, fallback to structured text if needed
        try:
            report = json.loads(report_text)
        except json.JSONDecodeError:
            # Fallback: create structured report from text
            report = {
                "company": request.company,
                "quarter": request.quarter,
                "executiveSummary": "Comprehensive financial analysis completed. " + report_text[:500] + "...",
                "financialAnalysis": {
                    "revenueAnalysis": "Revenue analysis indicates solid performance with positive growth trends.",
                    "profitabilityAnalysis": "Profitability metrics show healthy margins and efficient operations.",
                    "growthAnalysis": "Growth trajectory remains strong with sustainable market positioning."
                },
                "balanceSheetAnalysis": "Balance sheet demonstrates financial strength and prudent capital management.",
                "cashFlowAnalysis": "Strong cash flow generation supports operational needs and strategic investments.",
                "keyRatios": [
                    {"name": "PE Ratio", "value": "N/A", "interpretation": "Analysis completed"},
                    {"name": "ROE", "value": "N/A", "interpretation": "Analysis completed"},
                    {"name": "Debt-to-Equity", "value": "N/A", "interpretation": "Analysis completed"}
                ],
                "industryComparison": "Company shows competitive positioning within its industry sector.",
                "riskAssessment": {
                    "financialRisks": ["Analysis completed"],
                    "operationalRisks": ["Analysis completed"],
                    "marketRisks": ["Analysis completed"]
                },
                "investmentRecommendation": {
                    "rating": "HOLD",
                    "rationale": "Balanced risk-reward profile based on current analysis",
                    "targetPrice": "N/A",
                    "timeHorizon": "12 months"
                },
                "forwardOutlook": "Future prospects remain positive with continued focus on core competencies.",
                "confidence": 0.8,
                "generated_at": datetime.now().isoformat(),
                "fullAnalysis": report_text
            }

        # Ensure required fields are present
        report.setdefault("company", request.company)
        report.setdefault("quarter", request.quarter)
        report.setdefault("generated_at", datetime.now().isoformat())
        report.setdefault("confidence", 0.8)

        return report

    except Exception as e:
        logger.error(f"Error generating full report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate full report: {str(e)}")


@app.post("/api/generate-keyword-report")
async def generate_keyword_report(request: KeywordReportRequest):
    """
    Generate a comprehensive PDF report for a keyword using LLM analysis.

    Returns a PDF report analyzing the keyword's importance, trends, and related documents.
    """
    try:
        if not openai.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")

        # Prepare document summaries for the prompt
        document_summaries = []
        for i, doc in enumerate(request.documents[:5]):  # Limit to top 5 documents
            document_summaries.append(f"""
Document {i+1}: {doc.get('title', 'Untitled')}
Source: {doc.get('source_name', 'Unknown')}
Date: {doc.get('published_date', 'Unknown')}
Snippet: {doc.get('snippet', '')[:200]}...
URL: {doc.get('url', '')}
""")

        # Prepare time series data
        time_series_summary = ""
        if request.timeSeries:
            time_series_summary = "\n".join([
                f"{point['date']}: Importance {point['importance']:.2f}"
                for point in request.timeSeries[-10:]  # Last 10 data points
            ])

        # Create comprehensive report prompt
        prompt = f"""
Generate a comprehensive analysis report for the keyword "{request.keyword}" based on the following intelligence data:

KEYWORD METRICS:
- Importance Score: {request.importance:.2f}
- Frequency: {request.metrics.get('frequency', 'N/A')}
- Document Count: {request.metrics.get('document_count', 'N/A')}
- Velocity: {request.metrics.get('velocity', 'N/A')}%
- Source Diversity: {request.metrics.get('source_diversity', 'N/A')}

TEAM CONTEXT: {request.team}
CURRENT DATE: {request.currentDate}

TIME SERIES TREND:
{time_series_summary}

RELATED DOCUMENTS:
{"".join(document_summaries)}

Please generate a detailed PDF report with the following structure:

1. EXECUTIVE SUMMARY
   - Brief overview of the keyword's significance
   - Key findings and trends
   - Risk/opportunity assessment

2. KEYWORD ANALYSIS
   - Importance score interpretation
   - Velocity analysis (rising/falling/stable)
   - Source diversity assessment
   - Comparative context within {request.team}

3. TREND ANALYSIS
   - Historical importance trends
   - Velocity patterns over time
   - Emerging or declining signals

4. DOCUMENT ANALYSIS
   - Summary of key documents
   - Source credibility assessment
   - Thematic clustering of content

5. STRATEGIC IMPLICATIONS
   - Business impact assessment
   - Recommended actions
   - Monitoring priorities

6. RISK ASSESSMENT
   - Potential reputational risks
   - Market sensitivity analysis
   - Early warning indicators

Format the response as a JSON object with the following structure:
{{
    "title": "Keyword Intelligence Report: {request.keyword}",
    "executiveSummary": "2-3 paragraph executive summary",
    "keywordAnalysis": {{
        "importanceInterpretation": "Detailed analysis of importance score",
        "velocityAnalysis": "Analysis of velocity trends",
        "sourceAssessment": "Assessment of source diversity and credibility",
        "teamContext": "Relevance to {request.team} objectives"
    }},
    "trendAnalysis": {{
        "historicalTrends": "Analysis of importance trends over time",
        "velocityPatterns": "Velocity change patterns",
        "signalStrength": "Assessment of signal strength (weak/medium/strong)"
    }},
    "documentAnalysis": {{
        "keyDocuments": ["Summary of top 3-5 most relevant documents"],
        "sourceCredibility": "Assessment of source quality",
        "thematicClusters": ["Main themes identified in documents"]
    }},
    "strategicImplications": {{
        "businessImpact": "Assessment of business impact",
        "recommendedActions": ["3-5 specific recommendations"],
        "monitoringPriorities": ["Key areas to monitor"]
    }},
    "riskAssessment": {{
        "reputationalRisks": ["Potential reputational risks identified"],
        "marketSensitivity": "Assessment of market sensitivity",
        "earlyWarningSignals": ["Key indicators to watch"]
    }},
    "confidence": 0.85,
    "generated_at": "{datetime.now().isoformat()}",
    "data_sources": ["List of data sources used"]
}}

Ensure the analysis is professional, data-driven, and actionable. Include specific numbers and metrics where available. Focus on insights that would be valuable for {request.team} decision-making.
"""

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a senior intelligence analyst specializing in business reputation and risk analysis. Provide comprehensive, professional analysis with specific metrics, actionable insights, and clear risk assessments. Always include specific numbers and be data-driven in your analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.3
        )

        # Parse the response
        report_text = response.choices[0].message.content.strip()

        # Try to parse as JSON, fallback to structured text if needed
        try:
            report = json.loads(report_text)
        except json.JSONDecodeError:
            # Fallback: create structured report from text
            report = {
                "title": f"Keyword Intelligence Report: {request.keyword}",
                "executiveSummary": "Comprehensive keyword analysis completed. " + report_text[:500] + "...",
                "keywordAnalysis": {
                    "importanceInterpretation": f"Importance score of {request.importance:.2f} indicates significant relevance.",
                    "velocityAnalysis": f"Velocity of {request.metrics.get('velocity', 0):.2f}% shows current momentum.",
                    "sourceAssessment": f"Source diversity score of {request.metrics.get('source_diversity', 0)} indicates broad coverage.",
                    "teamContext": f"Analysis prepared for {request.team} team objectives."
                },
                "trendAnalysis": {
                    "historicalTrends": "Trend analysis indicates evolving importance over time.",
                    "velocityPatterns": "Velocity patterns show current market dynamics.",
                    "signalStrength": "medium"
                },
                "documentAnalysis": {
                    "keyDocuments": [f"{len(request.documents)} documents analyzed for keyword context"],
                    "sourceCredibility": "Multiple credible sources identified",
                    "thematicClusters": ["Content analysis completed"]
                },
                "strategicImplications": {
                    "businessImpact": "Analysis indicates potential business implications requiring attention.",
                    "recommendedActions": ["Continue monitoring keyword trends", "Review related documents", "Assess strategic implications"],
                    "monitoringPriorities": ["Keyword importance trends", "Document velocity", "Source sentiment"]
                },
                "riskAssessment": {
                    "reputationalRisks": ["Analysis completed - monitor for emerging risks"],
                    "marketSensitivity": "Medium sensitivity to market conditions",
                    "earlyWarningSignals": ["Sudden velocity changes", "Negative sentiment spikes"]
                },
                "confidence": 0.8,
                "generated_at": datetime.now().isoformat(),
                "fullAnalysis": report_text
            }

        # Ensure required fields are present
        report.setdefault("title", f"Keyword Intelligence Report: {request.keyword}")
        report.setdefault("generated_at", datetime.now().isoformat())
        report.setdefault("confidence", 0.8)

        # Now generate PDF from the report
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        styles = getSampleStyleSheet()

        # Create custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            textColor=colors.blue
        )

        normal_style = styles['Normal']
        normal_style.fontSize = 10
        normal_style.leading = 14

        # Build PDF content
        content = []

        # Title
        content.append(Paragraph(report.get('title', 'Keyword Intelligence Report'), title_style))
        content.append(Spacer(1, 12))

        # Executive Summary
        if 'executiveSummary' in report:
            content.append(Paragraph('EXECUTIVE SUMMARY', heading_style))
            content.append(Paragraph(report['executiveSummary'], normal_style))
            content.append(Spacer(1, 12))

        # Keyword Analysis
        if 'keywordAnalysis' in report:
            content.append(Paragraph('KEYWORD ANALYSIS', heading_style))
            analysis = report['keywordAnalysis']

            # Create a table for metrics
            metrics_data = [
                ['Metric', 'Value'],
                ['Importance Score', f"{request.importance:.2f}"],
                ['Velocity', f"{request.metrics.get('velocity', 0):.2f}%"],
                ['Document Count', str(request.metrics.get('document_count', 'N/A'))],
                ['Source Diversity', str(request.metrics.get('source_diversity', 'N/A'))]
            ]

            metrics_table = Table(metrics_data, colWidths=[2*inch, 2*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            content.append(metrics_table)
            content.append(Spacer(1, 12))

            # Analysis text
            if 'importanceInterpretation' in analysis:
                content.append(Paragraph(f"<b>Importance Analysis:</b> {analysis['importanceInterpretation']}", normal_style))
            if 'velocityAnalysis' in analysis:
                content.append(Paragraph(f"<b>Velocity Analysis:</b> {analysis['velocityAnalysis']}", normal_style))
            content.append(Spacer(1, 12))

        # Trend Analysis
        if 'trendAnalysis' in report:
            content.append(Paragraph('TREND ANALYSIS', heading_style))
            trends = report['trendAnalysis']
            if 'historicalTrends' in trends:
                content.append(Paragraph(f"<b>Historical Trends:</b> {trends['historicalTrends']}", normal_style))
            if 'velocityPatterns' in trends:
                content.append(Paragraph(f"<b>Velocity Patterns:</b> {trends['velocityPatterns']}", normal_style))
            content.append(Spacer(1, 12))

        # Document Analysis
        if 'documentAnalysis' in report:
            content.append(Paragraph('DOCUMENT ANALYSIS', heading_style))
            docs = report['documentAnalysis']
            if 'keyDocuments' in docs and docs['keyDocuments']:
                content.append(Paragraph('<b>Key Documents:</b>', normal_style))
                for doc in docs['keyDocuments'][:3]:  # Limit to 3
                    content.append(Paragraph(f"• {doc}", normal_style))
                content.append(Spacer(1, 6))
            if 'sourceCredibility' in docs:
                content.append(Paragraph(f"<b>Source Credibility:</b> {docs['sourceCredibility']}", normal_style))
            content.append(Spacer(1, 12))

        # Strategic Implications
        if 'strategicImplications' in report:
            content.append(Paragraph('STRATEGIC IMPLICATIONS', heading_style))
            implications = report['strategicImplications']
            if 'businessImpact' in implications:
                content.append(Paragraph(f"<b>Business Impact:</b> {implications['businessImpact']}", normal_style))
            if 'recommendedActions' in implications and implications['recommendedActions']:
                content.append(Paragraph('<b>Recommended Actions:</b>', normal_style))
                for action in implications['recommendedActions']:
                    content.append(Paragraph(f"• {action}", normal_style))
            content.append(Spacer(1, 12))

        # Risk Assessment
        if 'riskAssessment' in report:
            content.append(Paragraph('RISK ASSESSMENT', heading_style))
            risks = report['riskAssessment']
            if 'reputationalRisks' in risks and risks['reputationalRisks']:
                content.append(Paragraph('<b>Reputational Risks:</b>', normal_style))
                for risk in risks['reputationalRisks']:
                    content.append(Paragraph(f"• {risk}", normal_style))
            if 'marketSensitivity' in risks:
                content.append(Paragraph(f"<b>Market Sensitivity:</b> {risks['marketSensitivity']}", normal_style))
            content.append(Spacer(1, 12))

        # Footer with metadata
        content.append(Paragraph(f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ParagraphStyle('Footer', parent=normal_style, fontSize=8, textColor=colors.grey)))
        content.append(Paragraph(f"Confidence: {report.get('confidence', 'N/A')}", ParagraphStyle('Footer', parent=normal_style, fontSize=8, textColor=colors.grey)))

        # Build PDF
        doc.build(content)

        # Return PDF as streaming response
        pdf_buffer.seek(0)
        return StreamingResponse(
            pdf_buffer,
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename={request.keyword.replace(' ', '_')}_report.pdf"}
        )

    except Exception as e:
        logger.error(f"Error generating keyword report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate keyword report: {str(e)}")


# ============================================================================
# Reputation Map API Endpoints
# ============================================================================

@app.get("/api/reputation/map")
async def get_reputation_map_data(
    risk_type: str = "all",
    time_range: str = "30d",
    severity: str = "all",
    region: str = "all"
):
    """
    Get reputation map data with geographic risk/opportunity visualization.

    Returns reputation risks and opportunities by region with severity levels.
    """
    try:
        # Define major companies and countries for reputation monitoring
        companies_countries = [
            ("Apple", "United States"),
            ("Microsoft", "United States"),
            ("Google", "United States"),
            ("Amazon", "United States"),
            ("Meta", "United States"),
            ("Tesla", "United States"),
            ("NVIDIA", "United States"),
            ("Deutsche Bank", "Germany"),
            ("Siemens", "Germany"),
            ("Volkswagen", "Germany"),
            ("BMW", "Germany"),
            ("Alibaba", "China"),
            ("Tencent", "China"),
            ("Baidu", "China"),
            ("Huawei", "China"),
            ("Samsung", "South Korea"),
            ("LG", "South Korea"),
            ("Hyundai", "South Korea"),
            ("Toyota", "Japan"),
            ("Sony", "Japan"),
            ("Honda", "Japan"),
            ("Unilever", "United Kingdom"),
            ("HSBC", "United Kingdom"),
            ("BP", "United Kingdom"),
            ("Santander", "Spain"),
            ("Iberdrola", "Spain"),
            ("Repsol", "Spain"),
            ("Total", "France"),
            ("BNP Paribas", "France"),
            ("AXA", "France"),
            ("ING", "Netherlands"),
            ("ASML", "Netherlands"),
            ("Philips", "Netherlands"),
            ("Ericsson", "Sweden"),
            ("Volvo", "Sweden"),
            ("IKEA", "Sweden"),
            ("Novo Nordisk", "Denmark"),
            ("Maersk", "Denmark"),
            ("Lundbeck", "Denmark"),
            ("Nestle", "Switzerland"),
            ("UBS", "Switzerland"),
            ("Credit Suisse", "Switzerland"),
            ("Enel", "Italy"),
            ("Eni", "Italy"),
            ("Ferrari", "Italy"),
            ("Petrobras", "Brazil"),
            ("Vale", "Brazil"),
            ("Itau", "Brazil"),
            ("Reliance Industries", "India"),
            ("Tata", "India"),
            ("Infosys", "India")
        ]

        # Fetch reputation data from all sources
        all_reputation_data = []
        for company, country in companies_countries[:10]:  # Limit for performance, can be increased
            try:
                company_data = reputation_aggregator.fetch_all_reputation_data(company, country)
                all_reputation_data.extend(company_data)
                logger.info(f"Fetched {len(company_data)} reputation items for {company}")
            except Exception as e:
                logger.error(f"Error fetching reputation data for {company}: {e}")

        # Convert to frontend format
        reputation_issues = []
        for data in all_reputation_data:
            # Apply filters
            if risk_type != "all" and data.risk_type != risk_type:
                continue
            if severity != "all" and data.severity != severity:
                continue
            if region != "all" and data.region != region:
                continue

            reputation_issues.append({
                "id": f"{data.company_name.lower().replace(' ', '_')}_{data.country.lower().replace(' ', '_')}_{len(reputation_issues)}",
                "country": data.country,
                "region": data.region,
                "coordinates": data.coordinates,
                "riskType": data.risk_type,
                "severity": data.severity,
                "title": data.title,
                "description": data.description,
                "impact": data.impact,
                "sources": data.sources,
                "sentiment": data.sentiment,
                "trend": data.trend,
                "lastUpdated": data.last_updated,
                "esgScore": data.esg_score,
                "controversyLevel": data.controversy_level,
                "regulatoryActions": data.regulatory_actions
            })

        return {
            "data": reputation_issues,
            "filters": {
                "risk_type": risk_type,
                "time_range": time_range,
                "severity": severity,
                "region": region
            },
            "count": len(reputation_issues),
            "last_updated": datetime.now().isoformat(),
            "data_sources": ["NewsAPI", "Wikipedia", "OpenCorporates", "SEC EDGAR"]
        }
    except Exception as e:
        logger.error(f"Error in reputation map endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get reputation map data: {str(e)}")


@app.get("/api/reputation/regions")
async def get_reputation_regions():
    """
    Get available regions for reputation map filtering.

    Returns list of regions with reputation summary data.
    """
    try:
        content_repo = ContentRepository()

        # Get recent content for region analysis
        contents = content_repo.get_recent_content(days=90, limit=500)

        # Analyze regions
        regions = analyze_regions(contents)

        content_repo.close()

        return {
            "regions": regions,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get reputation regions: {str(e)}")


@app.get("/api/reputation/analysis")
async def get_reputation_analysis():
    """
    Get comprehensive reputation analysis and trends.

    Returns global reputation trends, risk distribution, and key insights.
    """
    try:
        content_repo = ContentRepository()

        # Get content for comprehensive analysis
        contents = content_repo.get_recent_content(days=180, limit=2000)

        # Perform comprehensive reputation analysis
        analysis = perform_reputation_analysis(contents)

        content_repo.close()

        return {
            "analysis": analysis,
            "content_analyzed": len(contents),
            "analysis_date": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get reputation analysis: {str(e)}")


# ============================================================================
# Helper Functions for Reputation Map Analysis
# ============================================================================

def analyze_reputation_risks(contents, risk_type_filter, severity_filter, region_filter) -> list:
    """Analyze content for reputation risks and opportunities by region."""

    # Define regions with coordinates
    regions_data = {
        "United States": {"coords": [39.8283, -98.5795], "region": "North America"},
        "China": {"coords": [35.8617, 104.1954], "region": "Asia"},
        "European Union": {"coords": [54.5260, 15.2551], "region": "Europe"},
        "Brazil": {"coords": [-14.2350, -51.9253], "region": "South America"},
        "India": {"coords": [20.5937, 78.9629], "region": "Asia"},
        "Japan": {"coords": [36.2048, 138.2529], "region": "Asia"},
        "United Kingdom": {"coords": [55.3781, -3.4360], "region": "Europe"},
        "Canada": {"coords": [56.1304, -106.3468], "region": "North America"},
        "Australia": {"coords": [-25.2744, 133.7751], "region": "Oceania"},
        "South Korea": {"coords": [35.9078, 127.7669], "region": "Asia"}
    }

    reputation_issues = []

    # Analyze each region
    for country, region_info in regions_data.items():
        if region_filter != "all" and region_info["region"] != region_filter:
            continue

        # Filter content relevant to this region
        region_content = [c for c in contents if is_content_relevant_to_region(c, country, region_info["region"])]

        if not region_content:
            continue

        # Analyze reputation risks for this region
        risks = identify_regional_risks(region_content, country)

        for risk in risks:
            # Apply filters
            if risk_type_filter != "all" and risk["riskType"] != risk_type_filter:
                continue
            if severity_filter != "all" and risk["severity"] != severity_filter:
                continue

            reputation_issues.append({
                "id": f"{country.lower().replace(' ', '_')}_{len(reputation_issues)}",
                "country": country,
                "region": region_info["region"],
                "coordinates": region_info["coords"],
                **risk
            })

    return reputation_issues


def is_content_relevant_to_region(content, country, region) -> bool:
    """Check if content is relevant to a specific region/country."""
    text = (content.title + " " + content.content).lower()

    # Country-specific keywords
    country_keywords = {
        "United States": ["us", "usa", "america", "united states", "federal", "sec", "fed"],
        "China": ["china", "chinese", "beijing", "shanghai", "csrc"],
        "European Union": ["eu", "european", "europe", "brussels", "gdpr", "ecb"],
        "Brazil": ["brazil", "brazilian", "brasilia", "sao paulo"],
        "India": ["india", "indian", "mumbai", "delhi", "sebi"],
        "Japan": ["japan", "japanese", "tokyo", "bojs"],
        "United Kingdom": ["uk", "britain", "london", "fca", "bank of england"],
        "Canada": ["canada", "canadian", "toronto", "ottawa"],
        "Australia": ["australia", "australian", "sydney", "asic"],
        "South Korea": ["korea", "korean", "seoul", "fss"]
    }

    # Region-specific keywords
    region_keywords = {
        "North America": ["north america", "nafta"],
        "Asia": ["asia", "asian"],
        "Europe": ["europe", "european"],
        "South America": ["south america", "latin america"],
        "Oceania": ["oceania", "pacific"]
    }

    # Check country keywords
    if country in country_keywords:
        if any(keyword in text for keyword in country_keywords[country]):
            return True

    # Check region keywords
    if region in region_keywords:
        if any(keyword in text for keyword in region_keywords[region]):
            return True

    return False


def identify_regional_risks(contents, country) -> list:
    """Identify reputation risks and opportunities for a specific region."""

    risks = []

    # Analyze content for different risk types
    risk_patterns = {
        "regulatory": {
            "keywords": ["regulation", "regulatory", "compliance", "fine", "penalty", "investigation", "sec", "fca", "gdpr"],
            "severity_weights": {"investigation": "high", "fine": "high", "regulation": "medium", "compliance": "medium"}
        },
        "reputational": {
            "keywords": ["scandal", "controversy", "reputation", "brand", "public", "media", "negative"],
            "severity_weights": {"scandal": "high", "controversy": "medium", "reputation": "medium"}
        },
        "operational": {
            "keywords": ["supply chain", "disruption", "operational", "manufacturing", "production", "crisis"],
            "severity_weights": {"crisis": "high", "disruption": "high", "operational": "medium"}
        },
        "opportunity": {
            "keywords": ["growth", "expansion", "investment", "partnership", "innovation", "opportunity"],
            "severity_weights": {"expansion": "high", "growth": "medium", "opportunity": "low"}
        }
    }

    # Analyze each risk type
    for risk_type, pattern in risk_patterns.items():
        relevant_content = []
        severity_scores = []

        for content in contents:
            text = (content.title + " " + content.content).lower()
            if any(keyword in text for keyword in pattern["keywords"]):
                relevant_content.append(content)

                # Calculate severity based on keywords
                severity = "low"
                for keyword, sev in pattern["severity_weights"].items():
                    if keyword in text:
                        if sev == "high":
                            severity = "high"
                            break
                        elif sev == "medium" and severity != "high":
                            severity = "medium"
                severity_scores.append(severity)

        if relevant_content:
            # Determine overall severity for this risk type
            if "high" in severity_scores:
                overall_severity = "high"
            elif "medium" in severity_scores:
                overall_severity = "medium"
            else:
                overall_severity = "low"

            # Calculate sentiment
            sentiments = [analyze_sentiment_score(c.content) for c in relevant_content]
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0

            # Generate risk details
            risk_details = generate_risk_details(risk_type, relevant_content, country, overall_severity)

            risks.append({
                "riskType": risk_type,
                "severity": overall_severity,
                "title": risk_details["title"],
                "description": risk_details["description"],
                "impact": risk_details["impact"],
                "sources": risk_details["sources"],
                "sentiment": round(avg_sentiment, 2),
                "trend": risk_details["trend"],
                "lastUpdated": max(c.published_date.isoformat() if c.published_date else "2024-11-01" for c in relevant_content)
            })

    return risks


def analyze_sentiment_score(content: str) -> float:
    """Analyze sentiment score (-1 to 1)."""
    positive_words = ["growth", "increase", "strong", "positive", "opportunity", "success", "win", "gain"]
    negative_words = ["decline", "decrease", "weak", "negative", "risk", "crisis", "loss", "penalty", "fine"]

    content_lower = content.lower()
    positive_count = sum(1 for word in positive_words if word in content_lower)
    negative_count = sum(1 for word in negative_words if word in content_lower)

    total_words = len(content.split())
    if total_words == 0:
        return 0

    sentiment = (positive_count - negative_count) / total_words
    return max(-1.0, min(1.0, sentiment * 10))  # Scale and bound


def generate_risk_details(risk_type, contents, country, severity):
    """Generate detailed risk information."""

    # Combine all content
    all_text = " ".join([c.title + " " + c.content for c in contents])
    sources = list(set([c.source_name for c in contents]))[:3]

    # Generate details based on risk type
    if risk_type == "regulatory":
        titles = {
            "high": f"Regulatory Investigation in {country}",
            "medium": f"Regulatory Changes in {country}",
            "low": f"Regulatory Developments in {country}"
        }
        descriptions = {
            "high": f"Ongoing regulatory investigation affecting business operations in {country}",
            "medium": f"New regulatory requirements and compliance changes in {country}",
            "low": f"Minor regulatory updates and monitoring in {country}"
        }
        impacts = {
            "high": f"High regulatory scrutiny impacting operations in {country}",
            "medium": f"Moderate compliance costs and operational changes in {country}",
            "low": f"Low impact regulatory adjustments in {country}"
        }

    elif risk_type == "reputational":
        titles = {
            "high": f"Reputation Crisis in {country}",
            "medium": f"Reputational Concerns in {country}",
            "low": f"Brand Perception Issues in {country}"
        }
        descriptions = {
            "high": f"Significant reputational damage from media coverage in {country}",
            "medium": f"Growing reputational concerns affecting brand perception in {country}",
            "low": f"Minor reputational issues requiring monitoring in {country}"
        }
        impacts = {
            "high": f"Severe brand damage and consumer backlash in {country}",
            "medium": f"Moderate impact on brand perception and trust in {country}",
            "low": f"Low impact on overall reputation in {country}"
        }

    elif risk_type == "operational":
        titles = {
            "high": f"Operational Crisis in {country}",
            "medium": f"Supply Chain Issues in {country}",
            "low": f"Operational Challenges in {country}"
        }
        descriptions = {
            "high": f"Major operational disruptions affecting business continuity in {country}",
            "medium": f"Supply chain and operational challenges in {country}",
            "low": f"Minor operational issues requiring attention in {country}"
        }
        impacts = {
            "high": f"Critical operational disruptions affecting revenue in {country}",
            "medium": f"Moderate operational impacts on efficiency in {country}",
            "low": f"Low impact operational adjustments needed in {country}"
        }

    else:  # opportunity
        titles = {
            "high": f"Major Growth Opportunity in {country}",
            "medium": f"Market Expansion Potential in {country}",
            "low": f"Emerging Opportunities in {country}"
        }
        descriptions = {
            "high": f"Significant market expansion and growth opportunities in {country}",
            "medium": f"Favorable market conditions for expansion in {country}",
            "low": f"Emerging market opportunities requiring monitoring in {country}"
        }
        impacts = {
            "high": f"High potential for revenue growth and market share in {country}",
            "medium": f"Moderate growth potential with strategic investments in {country}",
            "low": f"Low impact opportunities for future consideration in {country}"
        }

    # Determine trend based on content recency and volume
    recent_content = [c for c in contents if c.published_date and (datetime.now() - c.published_date).days <= 7]
    if len(recent_content) > len(contents) * 0.5:
        trend = "increasing"
    elif len(recent_content) < len(contents) * 0.2:
        trend = "decreasing"
    else:
        trend = "stable"

    return {
        "title": titles.get(severity, titles["medium"]),
        "description": descriptions.get(severity, descriptions["medium"]),
        "impact": impacts.get(severity, impacts["medium"]),
        "sources": sources,
        "trend": trend
    }


def analyze_regions(contents) -> list:
    """Analyze available regions with summary data."""

    regions = [
        {"name": "North America", "countries": ["United States", "Canada"]},
        {"name": "Europe", "countries": ["European Union", "United Kingdom"]},
        {"name": "Asia", "countries": ["China", "Japan", "India", "South Korea"]},
        {"name": "South America", "countries": ["Brazil"]},
        {"name": "Oceania", "countries": ["Australia"]}
    ]

    region_summaries = []

    for region in regions:
        region_content = []
        for content in contents:
            if any(is_content_relevant_to_region(content, country, region["name"]) for country in region["countries"]):
                region_content.append(content)

        if region_content:
            # Calculate region metrics
            sentiments = [analyze_sentiment_score(c.content) for c in region_content]
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0

            # Count risk types
            risk_counts = {"regulatory": 0, "reputational": 0, "operational": 0, "opportunity": 0}
            for content in region_content:
                text = (content.title + " " + content.content).lower()
                for risk_type, keywords in [
                    ("regulatory", ["regulation", "compliance", "fine"]),
                    ("reputational", ["reputation", "brand", "scandal"]),
                    ("operational", ["supply chain", "operational", "crisis"]),
                    ("opportunity", ["growth", "expansion", "opportunity"])
                ]:
                    if any(keyword in text for keyword in keywords):
                        risk_counts[risk_type] += 1

            region_summaries.append({
                "name": region["name"],
                "countries": region["countries"],
                "totalIssues": len(region_content),
                "avgSentiment": round(avg_sentiment, 2),
                "riskDistribution": risk_counts,
                "lastUpdated": max(c.published_date.isoformat() if c.published_date else "2024-11-01" for c in region_content)
            })

    return region_summaries


def perform_reputation_analysis(contents) -> dict:
    """Perform comprehensive reputation analysis."""

    # Global risk distribution
    risk_distribution = {"regulatory": 0, "reputational": 0, "operational": 0, "opportunity": 0}

    for content in contents:
        text = (content.title + " " + content.content).lower()
        for risk_type, keywords in [
            ("regulatory", ["regulation", "compliance", "fine", "investigation"]),
            ("reputational", ["reputation", "brand", "scandal", "controversy"]),
            ("operational", ["supply chain", "operational", "crisis", "disruption"]),
            ("opportunity", ["growth", "expansion", "investment", "opportunity"])
        ]:
            if any(keyword in text for keyword in keywords):
                risk_distribution[risk_type] += 1

    # Severity distribution
    severity_distribution = {"high": 0, "medium": 0, "low": 0}
    for content in contents:
        severity = analyze_content_severity(content)
        severity_distribution[severity] += 1

    # Regional hotspots
    regions = analyze_regions(contents)

    # Trend analysis (simplified)
    recent_content = [c for c in contents if c.published_date and (datetime.now() - c.published_date).days <= 30]
    older_content = [c for c in contents if c.published_date and (datetime.now() - c.published_date).days > 30]

    trend = "stable"
    if len(recent_content) > len(older_content) * 1.2:
        trend = "increasing"
    elif len(recent_content) < len(older_content) * 0.8:
        trend = "decreasing"

    # Key insights
    insights = generate_reputation_insights(contents, risk_distribution, regions)

    return {
        "riskDistribution": risk_distribution,
        "severityDistribution": severity_distribution,
        "regionalHotspots": regions[:3],  # Top 3 regions
        "overallTrend": trend,
        "keyInsights": insights
    }


def analyze_content_severity(content) -> str:
    """Analyze severity level of content."""
    text = (content.title + " " + content.content).lower()

    high_severity_keywords = ["crisis", "investigation", "scandal", "major", "severe", "critical"]
    medium_severity_keywords = ["issue", "concern", "challenge", "problem", "risk"]

    if any(keyword in text for keyword in high_severity_keywords):
        return "high"
    elif any(keyword in text for keyword in medium_severity_keywords):
        return "medium"
    else:
        return "low"


def generate_reputation_insights(contents, risk_distribution, regions) -> list:
    """Generate key insights from reputation analysis."""

    insights = []

    # Risk distribution insight
    total_risks = sum(risk_distribution.values())
    if total_risks > 0:
        max_risk_type = max(risk_distribution.items(), key=lambda x: x[1])
        if max_risk_type[1] / total_risks > 0.4:
            insights.append({
                "type": "risk_concentration",
                "title": f"High Concentration of {max_risk_type[0].title()} Risks",
                "description": f"{max_risk_type[1]} {max_risk_type[0]} issues identified, representing {(max_risk_type[1]/total_risks*100):.1f}% of all reputation concerns",
                "priority": "high"
            })

    # Regional insight
    if regions:
        top_region = max(regions, key=lambda x: x["totalIssues"])
        insights.append({
            "type": "regional_focus",
            "title": f"{top_region['name']} Region Requires Attention",
            "description": f"{top_region['totalIssues']} reputation issues identified in {top_region['name']}, highest among all regions",
            "priority": "medium"
        })

    # Opportunity insight
    opportunities = risk_distribution.get("opportunity", 0)
    if opportunities > total_risks * 0.2:
        insights.append({
            "type": "opportunity_focus",
            "title": "Growth Opportunities Identified",
            "description": f"{opportunities} potential opportunities detected, indicating positive market conditions",
            "priority": "medium"
        })

    return insights[:3]  # Max 3 insights

def extract_quarterly_metrics(content: str) -> dict:
    """Extract key financial metrics from quarterly report content."""
    # Simplified extraction - would use regex and NLP in production
    metrics = {
        "revenue": "N/A",
        "eps": "N/A",
        "growth": "N/A"
    }
    
    # Basic regex patterns for demonstration
    import re
    
    revenue_match = re.search(r'revenue[^\d]*\$?([\d,]+\.?\d*[BM]?)', content.lower())
    if revenue_match:
        metrics["revenue"] = revenue_match.group(1).upper()
    
    eps_match = re.search(r'eps[^\d]*\$?([\d,]+\.?\d*)', content.lower())
    if eps_match:
        metrics["eps"] = eps_match.group(1)
    
    growth_match = re.search(r'growth[^\d]*([+-]?[\d,]+\.?\d*%)', content.lower())
    if growth_match:
        metrics["growth"] = growth_match.group(1)
    
    return metrics


def extract_company_name(title: str, content: str) -> str:
    """Extract company name from title/content."""
    # Simplified - would use entity recognition in production
    companies = ["Apple", "Microsoft", "Google", "Amazon", "Meta", "Tesla", "NVIDIA"]
    for company in companies:
        if company.lower() in title.lower() or company.lower() in content.lower():
            return company
    return "Unknown Company"


def extract_quarter(title: str, content: str) -> str:
    """Extract quarter information."""
    quarters = ["Q1", "Q2", "Q3", "Q4", "Q3", "Q4"]
    for quarter in quarters:
        if quarter in title or quarter in content:
            # Add year if available
            year_match = re.search(r'20\d{2}', title + " " + content)
            year = year_match.group(0) if year_match else ""
            return f"{quarter} {year}".strip()
    return "Q3 2024"  # Default


def extract_highlights(content: str) -> list:
    """Extract key highlights from content."""
    # Simplified - take first 150 characters
    sentences = content.split('.')
    highlights = []
    for sentence in sentences[:3]:  # First 3 sentences as highlights
        if len(sentence.strip()) > 20:
            highlights.append(sentence.strip() + '.')
    return highlights if highlights else ["Content analysis in progress"]


def analyze_tone(content: str) -> str:
    """Analyze overall tone of content."""
    # Simplified sentiment analysis
    positive_words = ["growth", "increase", "strong", "positive", "beat", "exceed", "record"]
    negative_words = ["decline", "decrease", "weak", "negative", "miss", "below", "loss"]

    content_lower = content.lower()
    positive_count = sum(1 for word in positive_words if word in content_lower)
    negative_count = sum(1 for word in negative_words if word in content_lower)

    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"


def calculate_authority_score(source_name: str, published_date) -> float:
    """Calculate authority score based on source and recency."""
    # Simplified scoring
    authority_sources = {
        "SEC": 9.5,
        "Federal Reserve": 9.8,
        "CNBC": 8.5,
        "Bloomberg": 8.7,
        "Reuters": 8.9
    }
    
    base_score = 7.0
    for source, score in authority_sources.items():
        if source in source_name:
            base_score = score
            break
    
    # Recency bonus (newer = higher score)
    if published_date:
        days_old = (datetime.now() - published_date).days
        recency_bonus = max(0, 1.0 - (days_old / 365))  # Up to 1 point for very recent
        base_score = min(10.0, base_score + recency_bonus)
    
    return round(base_score, 1)


def generate_summary(content: str) -> str:
    """Generate a summary of the content."""
    # Simplified - take first 150 characters
    return content[:150] + "..." if len(content) > 150 else content


def assess_market_impact(title: str, content: str) -> str:
    """Assess market impact level."""
    high_impact_keywords = ["fed", "federal reserve", "rates", "recession", "crisis", "major"]
    medium_impact_keywords = ["earnings", "quarterly", "economic", "policy"]
    
    text = (title + " " + content).lower()
    
    if any(keyword in text for keyword in high_impact_keywords):
        return "high"
    elif any(keyword in text for keyword in medium_impact_keywords):
        return "medium"
    else:
        return "low"


def analyze_sentiment(content: str) -> str:
    """Analyze sentiment for market content."""
    return analyze_tone(content)  # Reuse tone analysis


def extract_topics(content: str) -> list:
    """Extract key topics from content."""
    # Simplified topic extraction
    topics = []
    topic_keywords = {
        "monetary policy": ["fed", "federal reserve", "interest rates", "monetary"],
        "economic growth": ["growth", "economy", "gdp", "economic"],
        "earnings": ["earnings", "revenue", "profit", "quarterly"],
        "technology": ["tech", "ai", "digital", "innovation"],
        "markets": ["market", "stock", "equity", "trading"]
    }
    
    content_lower = content.lower()
    for topic, keywords in topic_keywords.items():
        if any(keyword in content_lower for keyword in keywords):
            topics.append(topic)
    
    return topics[:3]  # Max 3 topics


def extract_speaker(title: str, content: str) -> str:
    """Extract speaker name from speech content."""
    # Simplified - look for CEO/CFO patterns
    ceo_pattern = r'(?:CEO|Chief Executive Officer)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
    cfo_pattern = r'(?:CFO|Chief Financial Officer)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
    
    for pattern in [ceo_pattern, cfo_pattern]:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1)
    
    # Fallback to common executive names
    executives = ["Satya Nadella", "Tim Cook", "Sundar Pichai", "Andy Jassy", "Mark Zuckerberg"]
    for exec in executives:
        if exec in content:
            return exec
    
    return "Executive Speaker"


def extract_company_from_speech(title: str, content: str) -> str:
    """Extract company from speech content."""
    return extract_company_name(title, content)


def extract_speech_topics(content: str) -> list:
    """Extract topics from speech content."""
    return extract_topics(content)


def extract_key_quotes(content: str) -> list:
    """Extract key quotes from speech content."""
    # Look for quoted text
    quotes = re.findall(r'"([^"]*)"', content)
    return quotes[:3] if quotes else ["Quote extraction in progress"]


def analyze_executive_tone(content: str) -> str:
    """Analyze tone of executive communication."""
    return analyze_tone(content)


def calculate_executive_authority(source_name: str, title: str) -> float:
    """Calculate authority score for executive content."""
    # Executives generally have high authority
    base_score = 9.0
    
    # Bonus for official company sources
    if any(term in source_name.lower() for term in ["newsroom", "investor", "corporate"]):
        base_score += 0.5
    
    return min(10.0, base_score)


def analyze_topics(contents) -> list:
    """Analyze top topics across all content."""
    # Simplified topic analysis
    all_topics = {}
    for content in contents:
        topics = extract_topics(content.content)
        for topic in topics:
            if topic not in all_topics:
                all_topics[topic] = {"count": 0, "sentiment": 0, "trend": "stable"}
            all_topics[topic]["count"] += 1
            all_topics[topic]["sentiment"] += 1 if analyze_tone(content.content) == "positive" else -1 if analyze_tone(content.content) == "negative" else 0
    
    # Convert to percentage and sort
    total = len(contents)
    top_topics = []
    for topic, data in sorted(all_topics.items(), key=lambda x: x[1]["count"], reverse=True)[:5]:
        top_topics.append({
            "topic": topic,
            "frequency": int((data["count"] / total) * 100),
            "trend": data.get("trend", "stable"),
            "sentiment": data["sentiment"] / data["count"] if data["count"] > 0 else 0
        })
    
    return top_topics


def analyze_overall_tone(contents) -> dict:
    """Analyze overall tone distribution."""
    tones = {"positive": 0, "neutral": 0, "negative": 0}
    
    for content in contents:
        tone = analyze_tone(content.content)
        tones[tone] += 1
    
    total = len(contents)
    return {
        "positive": int((tones["positive"] / total) * 100),
        "neutral": int((tones["neutral"] / total) * 100),
        "negative": int((tones["negative"] / total) * 100)
    }


def calculate_authority_distribution(contents) -> dict:
    """Calculate authority score distribution."""
    authorities = [calculate_authority_score(c.source_name, c.published_date) for c in contents]
    
    return {
        "average": round(sum(authorities) / len(authorities), 1) if authorities else 0,
        "highest": max(authorities) if authorities else 0,
        "lowest": min(authorities) if authorities else 0
    }


def generate_content_recommendations(contents) -> list:
    """Generate content lane recommendations based on analysis."""
    # Simplified recommendation engine
    topics = analyze_topics(contents)
    tone_dist = analyze_overall_tone(contents)
    
    recommendations = []
    
    # AI & Tech focus
    ai_topic = next((t for t in topics if "ai" in t["topic"].lower() or "tech" in t["topic"].lower()), None)
    if ai_topic and ai_topic["frequency"] > 10:
        recommendations.append({
            "lane": "AI & Technology Leadership",
            "priority": "high",
            "rationale": f"{ai_topic['frequency']}% of content mentions AI/Tech with strong momentum",
            "contentIdeas": [
                "AI implementation case studies",
                "Technology transformation roadmaps",
                "Executive perspectives on AI adoption"
            ]
        })
    
    # Financial Performance
    if tone_dist["positive"] > 50:
        recommendations.append({
            "lane": "Financial Performance & Growth",
            "priority": "high",
            "rationale": f"{tone_dist['positive']}% positive sentiment indicates strong performance narrative",
            "contentIdeas": [
                "Financial results analysis",
                "Growth strategy insights",
                "Market performance highlights"
            ]
        })
    
    # Economic Policy
    econ_topic = next((t for t in topics if "economic" in t["topic"].lower() or "policy" in t["topic"].lower()), None)
    if econ_topic:
        recommendations.append({
            "lane": "Economic Policy & Market Insights",
            "priority": "medium",
            "rationale": f"Emerging focus on economic policy with {econ_topic['frequency']}% coverage",
            "contentIdeas": [
                "Economic trend analysis",
                "Policy impact assessments",
                "Market outlook reports"
            ]
        })
    
    return recommendations[:3]  # Max 3 recommendations


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

