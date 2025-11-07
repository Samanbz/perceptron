"""
Frontend API Data Models

Defines the exact JSON structure that the frontend will receive.
Includes mock data generators for frontend development.
"""

from typing import List, Dict, Optional, Literal
from datetime import date, timedelta
from pydantic import BaseModel, Field
import random


# ============================================================================
# API Response Models
# ============================================================================

class SentimentBreakdown(BaseModel):
    """Sentiment distribution."""
    positive: int = Field(description="Number of positive mentions")
    negative: int = Field(description="Number of negative mentions")
    neutral: int = Field(description="Number of neutral mentions")


class KeywordSentiment(BaseModel):
    """Sentiment data for a keyword."""
    score: float = Field(ge=-1, le=1, description="Sentiment score: -1 (negative) to +1 (positive)")
    magnitude: float = Field(ge=0, le=1, description="Sentiment strength: 0 (weak) to 1 (strong)")
    breakdown: SentimentBreakdown


class KeywordMetrics(BaseModel):
    """Statistical metrics for a keyword."""
    frequency: int = Field(description="Total mentions")
    document_count: int = Field(description="Number of documents mentioning this keyword")
    source_diversity: int = Field(description="Number of different sources")
    velocity: float = Field(description="Rate of change vs previous day (percentage)")


class DocumentReference(BaseModel):
    """Reference to a source document."""
    content_id: int
    title: str
    source_name: str
    published_date: str  # ISO format
    url: Optional[str] = None
    snippet: str = Field(description="Text snippet showing keyword in context")


class KeywordData(BaseModel):
    """Complete data for a single keyword on a specific day."""
    keyword: str
    date: str  # ISO format (YYYY-MM-DD)
    importance: float = Field(ge=0, le=100, description="Importance score: 0-100")
    sentiment: KeywordSentiment
    metrics: KeywordMetrics
    documents: List[DocumentReference] = Field(description="Source documents (up to 10)")


class TimePoint(BaseModel):
    """Single point in time series."""
    date: str  # ISO format
    importance: float
    sentiment: float
    frequency: int


class KeywordTimeSeries(BaseModel):
    """Time-series data for word cloud animation."""
    keyword: str
    trend: Literal['rising', 'falling', 'stable', 'emerging']
    data_points: List[TimePoint]
    summary: Dict[str, float] = Field(description="avg_importance, max_importance, etc.")


class WordCloudResponse(BaseModel):
    """Response for word cloud visualization."""
    team_key: str
    team_name: str
    date_range: Dict[str, str]  # {start: "YYYY-MM-DD", end: "YYYY-MM-DD"}
    keywords: List[KeywordData] = Field(description="Top keywords ranked by importance")
    total_keywords: int
    total_documents: int


class TimeSeriesResponse(BaseModel):
    """Response for time-series / trend analysis."""
    team_key: str
    period: Dict[str, str]  # {start: "YYYY-MM-DD", end: "YYYY-MM-DD", granularity: "day"}
    keywords: List[KeywordTimeSeries]


# ============================================================================
# Mock Data Generators (for frontend development)
# ============================================================================

def generate_mock_sentiment() -> KeywordSentiment:
    """Generate realistic mock sentiment data."""
    # Bias towards neutral/slightly positive
    score = random.triangular(-1, 1, 0.2)
    magnitude = random.uniform(0.3, 0.9)
    
    # Generate breakdown based on score
    total = random.randint(5, 50)
    if score > 0.3:
        pos = int(total * random.uniform(0.5, 0.8))
        neg = int(total * random.uniform(0.05, 0.2))
    elif score < -0.3:
        pos = int(total * random.uniform(0.05, 0.2))
        neg = int(total * random.uniform(0.5, 0.8))
    else:
        pos = int(total * random.uniform(0.3, 0.5))
        neg = int(total * random.uniform(0.1, 0.3))
    neu = total - pos - neg
    
    return KeywordSentiment(
        score=round(score, 3),
        magnitude=round(magnitude, 3),
        breakdown=SentimentBreakdown(positive=pos, negative=neg, neutral=neu)
    )


def generate_mock_documents(keyword: str, count: int = 5) -> List[DocumentReference]:
    """Generate mock document references."""
    sources = ["TechCrunch", "Hacker News", "The Verge", "Ars Technica", "Reuters"]
    titles = [
        f"{keyword} emerges as key trend in tech industry",
        f"Analysis: What {keyword} means for the market",
        f"Companies invest heavily in {keyword} technology",
        f"{keyword} sees rapid adoption across sectors",
        f"Expert opinions on {keyword} implications",
    ]
    
    docs = []
    base_date = date.today() - timedelta(days=random.randint(0, 7))
    
    for i in range(count):
        docs.append(DocumentReference(
            content_id=random.randint(1000, 9999),
            title=random.choice(titles),
            source_name=random.choice(sources),
            published_date=(base_date - timedelta(days=i)).isoformat(),
            url=f"https://example.com/article-{random.randint(1000, 9999)}",
            snippet=f"...discussing {keyword} and its impact on the industry. Experts say {keyword} represents..."
        ))
    
    return docs


def generate_mock_keyword_data(keyword: str, day: date) -> KeywordData:
    """Generate mock data for a single keyword."""
    importance = random.uniform(40, 95)
    
    return KeywordData(
        keyword=keyword,
        date=day.isoformat(),
        importance=round(importance, 2),
        sentiment=generate_mock_sentiment(),
        metrics=KeywordMetrics(
            frequency=random.randint(5, 100),
            document_count=random.randint(3, 30),
            source_diversity=random.randint(2, 8),
            velocity=round(random.uniform(-30, 50), 2)
        ),
        documents=generate_mock_documents(keyword, count=random.randint(3, 8))
    )


def generate_mock_word_cloud(
    team_key: str = "regulator",
    days_back: int = 1,
    keyword_count: int = 20
) -> WordCloudResponse:
    """
    Generate complete mock word cloud data.
    
    Use this to give to frontend developers.
    """
    team_names = {
        "regulator": "Regulatory Team",
        "investor": "Investment Team",
        "competitor": "Competitive Intelligence",
        "researcher": "Research Team",
    }
    
    # Sample keywords relevant to each team
    keywords_by_team = {
        "regulator": [
            "federal regulation", "compliance requirements", "policy changes",
            "enforcement action", "regulatory framework", "data privacy",
            "consumer protection", "antitrust investigation", "SEC filing",
            "regulatory approval", "government oversight", "legal compliance",
            "trade restrictions", "financial regulations", "licensing requirements",
            "audit compliance", "regulatory sanctions", "policy enforcement",
            "government mandate", "statutory compliance", "regulatory review",
            "compliance audit", "policy implementation", "regulatory guidance",
            "enforcement penalty", "regulatory update",
        ],
        "investor": [
            "venture capital", "Series A funding", "IPO", "market valuation",
            "revenue growth", "profit margins", "investment opportunity",
            "startup acquisition", "portfolio company", "fund raising",
            "equity stake", "investment round", "cap table", "valuation multiple",
            "exit strategy", "return on investment", "due diligence",
            "investment thesis", "market opportunity", "growth capital",
            "private equity", "seed funding", "convertible note",
        ],
        "competitor": [
            "market share", "product launch", "competitor analysis",
            "pricing strategy", "customer acquisition", "technology stack",
            "business model", "competitive advantage", "market positioning",
            "market entry", "product differentiation", "customer retention",
            "go-to-market strategy", "sales strategy", "brand positioning",
            "competitive intelligence", "market dynamics", "feature comparison",
            "pricing model", "market penetration", "strategic partnership",
        ],
        "researcher": [
            "machine learning", "artificial intelligence", "research paper",
            "breakthrough technology", "scientific study", "innovation",
            "academic research", "technical advancement", "R&D investment",
            "neural networks", "deep learning", "algorithm optimization",
            "data science", "computational research", "experimental design",
            "research methodology", "peer review", "research findings",
            "technology innovation", "scientific discovery", "research collaboration",
        ],
    }
    
    target_date = date.today() - timedelta(days=days_back)
    available_keywords = keywords_by_team.get(team_key, keywords_by_team["regulator"])
    keywords = random.sample(available_keywords, min(keyword_count, len(available_keywords)))
    
    keyword_data = [generate_mock_keyword_data(kw, target_date) for kw in keywords]
    keyword_data.sort(key=lambda x: x.importance, reverse=True)
    
    return WordCloudResponse(
        team_key=team_key,
        team_name=team_names.get(team_key, "Unknown Team"),
        date_range={
            "start": target_date.isoformat(),
            "end": target_date.isoformat()
        },
        keywords=keyword_data,
        total_keywords=keyword_count,
        total_documents=sum(kw.metrics.document_count for kw in keyword_data)
    )


def generate_mock_time_series(
    team_key: str = "regulator",
    keyword: str = "federal regulation",
    days: int = 30
) -> KeywordTimeSeries:
    """Generate mock time-series data for a keyword."""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Generate trend
    trends = ['rising', 'falling', 'stable', 'emerging']
    trend = random.choice(trends)
    
    # Generate data points
    data_points = []
    base_importance = random.uniform(40, 60)
    
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        
        # Apply trend
        if trend == 'rising':
            importance = base_importance + (i / days) * 30 + random.uniform(-5, 5)
        elif trend == 'falling':
            importance = base_importance - (i / days) * 25 + random.uniform(-5, 5)
        elif trend == 'emerging':
            importance = base_importance * (1 + (i / days) * 2) + random.uniform(-5, 5)
        else:  # stable
            importance = base_importance + random.uniform(-8, 8)
        
        importance = max(0, min(100, importance))  # Clamp to 0-100
        
        data_points.append(TimePoint(
            date=current_date.isoformat(),
            importance=round(importance, 2),
            sentiment=round(random.uniform(-0.3, 0.7), 3),
            frequency=int(importance / 2) + random.randint(1, 10)
        ))
    
    return KeywordTimeSeries(
        keyword=keyword,
        trend=trend,
        data_points=data_points,
        summary={
            "avg_importance": round(sum(p.importance for p in data_points) / len(data_points), 2),
            "max_importance": round(max(p.importance for p in data_points), 2),
            "min_importance": round(min(p.importance for p in data_points), 2),
        }
    )


# ============================================================================
# Example usage / Mock data generation
# ============================================================================

if __name__ == "__main__":
    import json
    
    print("="*80)
    print("MOCK DATA FOR FRONTEND")
    print("="*80)
    
    # Generate word cloud for today
    print("\n1. WORD CLOUD DATA (Regulator Team, Today)")
    print("-"*80)
    word_cloud = generate_mock_word_cloud(team_key="regulator", days_back=0, keyword_count=15)
    print(json.dumps(word_cloud.dict(), indent=2))
    
    # Generate time series for a keyword
    print("\n\n2. TIME SERIES DATA (federal regulation, last 30 days)")
    print("-"*80)
    time_series = generate_mock_time_series(
        team_key="regulator",
        keyword="federal regulation",
        days=30
    )
    print(json.dumps(time_series.dict(), indent=2))
    
    print("\n\n3. SAVE MOCK DATA TO FILES")
    print("-"*80)
    
    # Save for different teams
    for team in ["regulator", "investor", "competitor", "researcher"]:
        filename = f"mock_data_{team}_wordcloud.json"
        with open(filename, 'w') as f:
            data = generate_mock_word_cloud(team_key=team, keyword_count=20)
            json.dump(data.dict(), f, indent=2)
        print(f"✓ Saved {filename}")
    
    # Save time series examples
    keywords = ["federal regulation", "venture capital", "artificial intelligence"]
    for kw in keywords:
        filename = f"mock_data_timeseries_{kw.replace(' ', '_')}.json"
        with open(filename, 'w') as f:
            data = generate_mock_time_series(keyword=kw, days=30)
            json.dump(data.dict(), f, indent=2)
        print(f"✓ Saved {filename}")
    
    print("\n✓ Mock data generation complete!")
    print("\nGive these files to your frontend colleague to start development.")
