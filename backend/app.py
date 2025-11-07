"""Main FastAPI application for Signal Radar backend."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

from sourcers import RSSSourcer
from storage import (
    ContentRepository,
    SourceConfigRepository,
    create_database,
    get_database_url,
)

# Initialize database on startup
create_database(get_database_url())

app = FastAPI(title="Signal Radar API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    """Home endpoint."""
    return {"message": "Signal Radar API is running!"}


@app.get("/api/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Signal Radar Backend"}


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

