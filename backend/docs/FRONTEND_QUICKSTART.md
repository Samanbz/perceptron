# Quick Start for Frontend Developer

## What You're Building

A **word cloud visualization** that shows trending keywords with:

- Size = importance (how significant/trending)
- Color = sentiment (red=negative, gray=neutral, green=positive)
- Animation over time (time slider to see trends)

## Files You Need

I've created **7 mock data files** in JSON format. Use these to build your UI:

### Word Cloud Data (one per team):

1. `mock_data_regulator_wordcloud.json`
2. `mock_data_investor_wordcloud.json`
3. `mock_data_competitor_wordcloud.json`
4. `mock_data_researcher_wordcloud.json`

### Time Series Data (for animation):

5. `mock_data_timeseries_federal_regulation.json`
6. `mock_data_timeseries_venture_capital.json`
7. `mock_data_timeseries_artificial_intelligence.json`

## Quick Example

### Load Mock Data

```typescript
// In your component
import regulatorData from "./mock_data_regulator_wordcloud.json";

const keywords = regulatorData.keywords; // Array of keyword objects
```

### Render Word Cloud

```typescript
{
  keywords.map((kw) => (
    <span
      key={kw.keyword}
      style={{
        fontSize: `${12 + (kw.importance / 100) * 48}px`, // Bigger = more important
        color:
          kw.sentiment.score < 0
            ? "red"
            : kw.sentiment.score > 0
            ? "green"
            : "gray",
        opacity: 0.3 + kw.sentiment.magnitude * 0.7,
        margin: "8px",
      }}
    >
      {kw.keyword}
    </span>
  ));
}
```

## UI Components Needed

### 1. Team Selector (Dropdown)

```
[Regulator ▼]
├── Regulator
├── Investor
├── Competitor
└── Researcher
```

### 2. Word Cloud Display

- Keywords sized by importance
- Colored by sentiment
- Clickable for details

### 3. Time Slider

```
[◀] [▶] [Today ─────────────────o──] [30 days ago]
```

### 4. Keyword Details Panel

Shows when clicking a keyword:

- Sentiment breakdown chart
- List of source articles
- Mini trend chart

## Data Structure

Each keyword object looks like:

```json
{
  "keyword": "federal regulation",
  "importance": 94.23,           // 0-100 (use for font size)
  "sentiment": {
    "score": 0.156,              // -1 to +1 (use for color)
    "magnitude": 0.624,          // 0-1 (use for opacity)
    "breakdown": {
      "positive": 15,
      "negative": 5,
      "neutral": 12
    }
  },
  "metrics": {
    "frequency": 45,             // Total mentions
    "document_count": 18,        // Number of articles
    "velocity": 23.5             // % change (for trend arrow)
  },
  "documents": [...]             // Array of source articles
}
```

## Visual Guidelines

### Font Size

```
importance 0   → 12px
importance 50  → 36px
importance 100 → 60px
```

### Color

```
sentiment < -0.2 → #EF4444 (red)
sentiment  -0.2 to +0.2 → #6B7280 (gray)
sentiment > +0.2 → #10B981 (green)
```

### Opacity

```
magnitude 0.0 → opacity 0.3
magnitude 0.5 → opacity 0.65
magnitude 1.0 → opacity 1.0
```

## Recommended Libraries

- **Word Cloud**: `react-wordcloud` or custom D3
- **Charts**: `recharts` for sentiment breakdown
- **Animation**: `framer-motion` for smooth transitions

## Full Documentation

See `FRONTEND_GUIDE.md` for:

- Complete API specs
- TypeScript interfaces
- More code examples
- All data fields explained

## Questions?

Ask backend team for:

- API endpoint URL (when ready)
- Additional mock data
- Data model changes
