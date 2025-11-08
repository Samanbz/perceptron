
"""
Scouting API Routes
Handles content analysis from browser extension
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from teams.repository import TeamRepository
import json
import re
from collections import Counter
import spacy

# Load spaCy model once at startup
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    nlp = None
    print("spaCy model 'en_core_web_md' not found. Please run: python -m spacy download en_core_web_md")

router = APIRouter(prefix="/api/scout", tags=["scouting"])

# --- Scouting enabled state ---
scouting_enabled_state = {"enabled": False}

@router.get("/enabled")
async def get_scouting_enabled():
    """Get current scouting enabled state."""
    return {"enabled": scouting_enabled_state["enabled"]}

@router.post("/enabled")
async def set_scouting_enabled(payload: dict):
    """Set scouting enabled state."""
    enabled = payload.get("enabled")
    if not isinstance(enabled, bool):
        raise HTTPException(status_code=400, detail="'enabled' must be a boolean.")
    scouting_enabled_state["enabled"] = enabled
    return {"enabled": enabled}

# Simple keyword extraction without heavy dependencies
def simple_keyword_extraction(text: str, top_n: int = 10) -> List[Dict]:
    """Extract keywords using simple frequency analysis"""
    # Convert to lowercase and split into words
    words = re.findall(r'\b[a-z]{4,}\b', text.lower())
    
    # Common stop words to filter out
    stop_words = {'that', 'this', 'with', 'from', 'have', 'been', 'their', 'which', 
                  'will', 'would', 'there', 'about', 'them', 'into', 'than', 'more',
                  'could', 'some', 'other', 'then', 'only', 'also', 'these', 'when'}
    
    # Filter words
    filtered_words = [w for w in words if w not in stop_words]
    
    # Count frequencies
    word_counts = Counter(filtered_words)
    
    # Get top keywords with normalized scores
    max_count = max(word_counts.values()) if word_counts else 1
    top_keywords = [
        {"keyword": word, "score": count / max_count}
        for word, count in word_counts.most_common(top_n)
    ]
    
    return top_keywords

class ScoutedContent(BaseModel):
    url: str
    title: str
    description: Optional[str] = ""
    content: str
    headings: List[str] = []
    keywords: Optional[str] = ""
    timestamp: str
    domain: str

class AnalysisResult(BaseModel):
    url: str
    title: str
    team: Optional[str] = None
    relevance_score: float = 0.0
    top_keywords: List[Dict[str, float]] = []
    sentiment: Optional[Dict[str, float]] = None
    company_names: List[str] = []
    analyzed_at: str
def extract_company_names(text: str) -> List[str]:
    """Extract company/organization names using spaCy NER."""
    if not nlp:
        return []
    doc = nlp(text)
    orgs = set(ent.text.strip() for ent in doc.ents if ent.label_ == "ORG")
    return list(orgs)


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_content(content: ScoutedContent):
    """
    Analyze scouted content and determine relevance to teams
    Uses existing keyword extraction and team assignment logic
    Now also extracts company names (ORG entities).
    """
    try:
        # Combine all text for analysis
        full_text = f"{content.title} {content.description} {' '.join(content.headings)} {content.content}"

        # Extract keywords using simple frequency analysis
        extracted_keywords = simple_keyword_extraction(full_text, top_n=20)

        # Extract company names (ORG entities)
        company_names = extract_company_names(full_text)

        if not extracted_keywords:
            return AnalysisResult(
                url=content.url,
                title=content.title,
                team=None,
                relevance_score=0.0,
                top_keywords=[],
                company_names=company_names,
                analyzed_at=datetime.utcnow().isoformat()
            )

        # Get all teams
        team_repo = TeamRepository()
        teams = []
        try:
            teams = team_repo.get_all_teams()
        finally:
            team_repo.close()

        # Calculate relevance for each team
        team_scores = {}
        for team in teams:
            if not team.get("is_active", True):
                continue

            team_key = team["team_key"]
            team_sources = team.get("sources", [])

            # Calculate score based on keyword match
            score = calculate_team_relevance(extracted_keywords, team, full_text)
            team_scores[team_key] = score

        # Find best matching team
        best_team = None
        best_score = 0.0

        if team_scores:
            best_team = max(team_scores, key=team_scores.get)
            best_score = team_scores[best_team]

        # Format top keywords
        top_keywords = [
            {"keyword": kw["keyword"], "score": kw["score"]}
            for kw in extracted_keywords[:10]
        ]

        return AnalysisResult(
            url=content.url,
            title=content.title,
            team=best_team if best_score > 0.3 else None,
            relevance_score=best_score,
            top_keywords=top_keywords,
            company_names=company_names,
            analyzed_at=datetime.utcnow().isoformat()
        )

    except Exception as e:
        print(f"Error analyzing content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

def calculate_team_relevance(keywords: List[Dict], team: Dict, full_text: str) -> float:
    """
    Calculate how relevant content is to a specific team
    Based on keyword matches and team configuration
    """
    team_key = team["team_key"]
    team_name = team["team_name"].lower()
    team_desc = team.get("description", "").lower()
    
    # Keywords that indicate team relevance
    team_indicators = {
        "regulator": ["regulation", "compliance", "policy", "government", "law", "legal", "sec", "federal", "mandate"],
        "investor": ["investment", "funding", "venture", "capital", "revenue", "valuation", "ipo", "acquisition", "m&a"],
        "competitor": ["competitor", "market share", "product", "launch", "feature", "pricing", "strategy"],
        "researcher": ["research", "study", "technology", "innovation", "ai", "machine learning", "algorithm", "patent"]
    }
    
    indicators = team_indicators.get(team_key, [])
    
    # Calculate score
    score = 0.0
    keyword_texts = [kw["keyword"].lower() for kw in keywords]
    
    # Check for indicator matches in keywords
    for indicator in indicators:
        for kw_text in keyword_texts:
            if indicator in kw_text:
                # Find the keyword's score
                for kw in keywords:
                    if kw["keyword"].lower() == kw_text:
                        score += kw["score"] * 0.5
                        break
    
    # Check for indicator matches in full text
    full_text_lower = full_text.lower()
    for indicator in indicators:
        if indicator in full_text_lower:
            score += 0.1
    
    # Normalize score to 0-1 range
    score = min(score, 1.0)
    
    return score

@router.get("/stats")
async def get_scout_stats():
    """
    Get scouting statistics
    """
    # TODO: Implement actual stats from database when collection is created
    # For now, return mock data
    return {
        "totalScanned": 0,
        "todayScanned": 0,
        "relevantPages": 0
    }
