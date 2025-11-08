"""
Simplified API server for keywords endpoint only.
Avoids dependency issues with unused modules.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from keywords.importance_repository import ImportanceRepository
from storage.repository import ContentRepository
from teams.repository import TeamRepository
from datetime import date
import json

app = FastAPI(
    title="Perceptron Keywords API",
    version="1.0.0"
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


@app.get("/")
def home():
    """Home endpoint."""
    return {
        "message": "Perceptron Keywords API is running!",
        "version": "1.0.0",
        "endpoints": [
            "/api/keywords/{team_key}/{date}",
            "/api/teams"
        ]
    }


@app.get("/api/health")
def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Perceptron Keywords API"
    }


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
    content_repo = ContentRepository()
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
            
            # Determine representative published date for this keyword from its documents.
            # Prefer the most common published_date among the documents; fallback to query date.
            keyword_date = date_str
            if documents:
                # Build counts for published_date (YYYY-MM-DD)
                counts = {}
                for d in documents:
                    pd = d.get('published_date')
                    if pd:
                        # If published_date includes time, take date portion
                        pd_date = pd.split('T')[0]
                        counts[pd_date] = counts.get(pd_date, 0) + 1

                if counts:
                    # choose the most common published date
                    keyword_date = max(counts.items(), key=lambda kv: kv[1])[0]

            keywords_data.append({
                "keyword": importance_record.keyword,
                "date": keyword_date,
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
