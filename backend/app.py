"""Main FastAPI application for Signal Radar backend."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from sourcers import RSSSourcer
from storage import (
    ContentRepository,
    SourceConfigRepository,
    create_database,
    get_database_url,
)
from auth import auth_router, cosmos_client, user_repository

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_database(get_database_url())
    cosmos_client.connect()
    user_repository.initialize()
    yield
    # Shutdown
    pass

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

