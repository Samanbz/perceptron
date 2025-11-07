# Frontend Integration Guide

## Overview

This document describes the data models and API structure for the keyword analysis word cloud feature.

## System Architecture

```
┌──────────────┐
│  Frontend    │ Selects Team
│  (React/Vue) │ ──────────────┐
└──────────────┘                │
                                ▼
                        ┌──────────────────┐
                        │  Team Selection  │
                        │  (regulator,     │
                        │   investor, etc.)│
                        └──────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │  Backend Filter  │
                        │  - Team sources  │
                        │  - Team config   │
                        └──────────────────┘
                                │
                                ▼
                    ┌──────────────────────────┐
                    │  Keyword Importance &    │
                    │  Sentiment Analysis      │
                    └──────────────────────────┘
                                │
                                ▼
                    ┌──────────────────────────┐
                    │  JSON Response           │
                    │  - Keywords (importance) │
                    │  - Sentiment scores      │
                    │  - Source documents      │
                    │  - Time series data      │
                    └──────────────────────────┘
```

## Teams

Each team represents a different perspective/use case:

### Available Teams

| Team Key     | Team Name                | Focus                           | Example Sources                            |
| ------------ | ------------------------ | ------------------------------- | ------------------------------------------ |
| `regulator`  | Regulatory Team          | Government policy, compliance   | Federal Register, SEC, regulatory news     |
| `investor`   | Investment Team          | Market opportunities, funding   | TechCrunch funding, VC announcements       |
| `competitor` | Competitive Intelligence | Market positioning, competitors | Product launches, market analysis          |
| `researcher` | Research Team            | Technology trends, innovations  | arXiv, research papers, tech breakthroughs |

## API Endpoints

### 1. GET /api/keywords/wordcloud

Get current word cloud data for a team.

**Parameters:**

- `team` (required): Team key (`regulator`, `investor`, etc.)
- `date` (optional): Specific date (YYYY-MM-DD), defaults to today
- `limit` (optional): Max keywords to return, default 50

**Response Example:**

```json
{
  "team_key": "regulator",
  "team_name": "Regulatory Team",
  "date_range": {
    "start": "2025-11-07",
    "end": "2025-11-07"
  },
  "keywords": [
    {
      "keyword": "federal regulation",
      "date": "2025-11-07",
      "importance": 94.23,
      "sentiment": {
        "score": 0.156,
        "magnitude": 0.624,
        "breakdown": {
          "positive": 15,
          "negative": 5,
          "neutral": 12
        }
      },
      "metrics": {
        "frequency": 45,
        "document_count": 18,
        "source_diversity": 6,
        "velocity": 23.5
      },
      "documents": [
        {
          "content_id": 1234,
          "title": "New federal regulations announced",
          "source_name": "Federal Register",
          "published_date": "2025-11-07",
          "url": "https://...",
          "snippet": "...discussing federal regulation and..."
        }
      ]
    }
  ],
  "total_keywords": 50,
  "total_documents": 234
}
```

### 2. GET /api/keywords/timeseries

Get time-series data for trending keywords.

**Parameters:**

- `team` (required): Team key
- `keyword` (optional): Specific keyword to track
- `days` (optional): Number of days back, default 30
- `top_n` (optional): Number of top keywords if keyword not specified

**Response Example:**

```json
{
  "team_key": "regulator",
  "period": {
    "start": "2025-10-08",
    "end": "2025-11-07",
    "granularity": "day"
  },
  "keywords": [
    {
      "keyword": "federal regulation",
      "trend": "rising",
      "data_points": [
        {
          "date": "2025-10-08",
          "importance": 45.2,
          "sentiment": 0.123,
          "frequency": 12
        },
        {
          "date": "2025-10-09",
          "importance": 52.3,
          "sentiment": 0.234,
          "frequency": 18
        }
      ],
      "summary": {
        "avg_importance": 48.5,
        "max_importance": 87.3,
        "min_importance": 12.1
      }
    }
  ]
}
```

### 3. GET /api/teams

List all available teams.

**Response:**

```json
{
  "teams": [
    {
      "key": "regulator",
      "name": "Regulatory Team",
      "description": "Government policy and compliance monitoring",
      "color": "#3B82F6",
      "icon": "shield"
    }
  ]
}
```

## Data Model Details

### Keyword Importance Score (0-100)

Calculated from multiple signals:

- **Frequency** (30%): How often the keyword appears
- **Velocity** (25%): Rate of change vs previous day
- **Source Diversity** (20%): Number of different sources mentioning it
- **Recency** (15%): More recent = more important
- **Sentiment Magnitude** (10%): Stronger sentiment = more notable

### Sentiment Score (-1 to +1)

- `-1.0 to -0.5`: Strongly negative
- `-0.5 to -0.2`: Moderately negative
- `-0.2 to +0.2`: Neutral
- `+0.2 to +0.5`: Moderately positive
- `+0.5 to +1.0`: Strongly positive

### Sentiment Magnitude (0 to 1)

- `0.0 - 0.3`: Weak sentiment (factual/neutral tone)
- `0.3 - 0.6`: Moderate sentiment
- `0.6 - 1.0`: Strong sentiment (opinionated/emotional)

### Trend Classification

- `emerging`: New keyword, rapidly gaining mentions
- `rising`: Steadily increasing importance
- `stable`: Consistent importance over time
- `falling`: Decreasing mentions

## UI Components Needed

### 1. Team Selector (Dropdown)

```jsx
<TeamSelector
  teams={teams}
  selected={currentTeam}
  onChange={handleTeamChange}
/>
```

### 2. Word Cloud Component

**Requirements:**

- Display keywords sized by importance (0-100)
- Color by sentiment (red=negative, gray=neutral, green=positive)
- Opacity/saturation by sentiment magnitude
- Click keyword → show details panel
- Animate changes over time (time slider)

**Props:**

```typescript
interface WordCloudProps {
  keywords: KeywordData[];
  onKeywordClick: (keyword: string) => void;
  colorScheme: "sentiment" | "importance" | "team";
}
```

### 3. Keyword Details Panel

Shows when clicking a keyword:

- Full keyword text
- Importance score + trend indicator
- Sentiment breakdown chart
- List of source documents (clickable)
- Time-series mini chart

### 4. Time Slider

For "word cloud in time" feature:

- Slider from start_date to end_date
- Play/pause animation
- Adjust animation speed
- Shows date label

## Mock Data Files

I've generated realistic mock data for frontend development:

### Word Cloud Data (by team)

- `mock_data_regulator_wordcloud.json` - Regulatory keywords
- `mock_data_investor_wordcloud.json` - Investment keywords
- `mock_data_competitor_wordcloud.json` - Competitive intelligence
- `mock_data_researcher_wordcloud.json` - Research/tech trends

### Time Series Data

- `mock_data_timeseries_federal_regulation.json`
- `mock_data_timeseries_venture_capital.json`
- `mock_data_timeseries_artificial_intelligence.json`

## Example Frontend Code

### Fetching Word Cloud Data

```typescript
async function fetchWordCloud(teamKey: string, date?: string) {
  const params = new URLSearchParams({
    team: teamKey,
    ...(date && { date }),
    limit: "50",
  });

  const response = await fetch(`/api/keywords/wordcloud?${params}`);
  const data: WordCloudResponse = await response.json();
  return data;
}
```

### Rendering Word Cloud

```typescript
function WordCloud({ keywords }: { keywords: KeywordData[] }) {
  return (
    <div className="word-cloud">
      {keywords.map((kw) => {
        // Size based on importance (0-100)
        const fontSize = 12 + (kw.importance / 100) * 48; // 12-60px

        // Color based on sentiment
        const color = getSentimentColor(kw.sentiment.score);

        // Opacity based on sentiment magnitude
        const opacity = 0.3 + kw.sentiment.magnitude * 0.7;

        return (
          <span
            key={kw.keyword}
            style={{
              fontSize: `${fontSize}px`,
              color,
              opacity,
              cursor: "pointer",
              margin: "8px",
            }}
            onClick={() => handleKeywordClick(kw)}
          >
            {kw.keyword}
          </span>
        );
      })}
    </div>
  );
}

function getSentimentColor(score: number): string {
  if (score < -0.2) return "#EF4444"; // red
  if (score > 0.2) return "#10B981"; // green
  return "#6B7280"; // gray
}
```

### Time Series Animation

```typescript
function WordCloudTimeline({ teamKey }: { teamKey: string }) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    if (!isPlaying) return;

    const interval = setInterval(() => {
      setCurrentDate((d) => {
        const next = new Date(d);
        next.setDate(next.getDate() + 1);
        return next;
      });
    }, 1000); // Change every 1 second

    return () => clearInterval(interval);
  }, [isPlaying]);

  const { data } = useQuery(["wordcloud", teamKey, currentDate], () =>
    fetchWordCloud(teamKey, currentDate.toISOString().split("T")[0])
  );

  return (
    <div>
      <WordCloud keywords={data?.keywords || []} />
      <TimeSlider
        date={currentDate}
        onDateChange={setCurrentDate}
        isPlaying={isPlaying}
        onPlayPause={() => setIsPlaying(!isPlaying)}
      />
    </div>
  );
}
```

## Suggested Libraries

### Word Cloud

- `react-wordcloud` - Interactive word cloud component
- `d3-cloud` - D3.js word cloud layout
- Custom SVG implementation for full control

### Charts

- `recharts` - For sentiment breakdown pie charts
- `chart.js` - Time series line charts
- `visx` - Low-level D3 components for React

### Animation

- `framer-motion` - Smooth keyword transitions
- `react-spring` - Spring physics animations

## Development Workflow

1. **Start with mock data**: Use the provided JSON files
2. **Build UI components**: Word cloud, team selector, details panel
3. **Add interactivity**: Keyword clicks, time slider
4. **Connect to real API**: Replace mock data with fetch calls
5. **Polish**: Add animations, responsive design

## Notes

- All dates are in ISO format (YYYY-MM-DD)
- Importance scores are 0-100 (higher = more important)
- Sentiment scores are -1 to +1
- Each keyword can have up to 10 document references
- Time series data can span up to 90 days

## Questions?

Contact the backend team for:

- API endpoint changes
- Additional team configurations
- New data fields
- Performance optimization
