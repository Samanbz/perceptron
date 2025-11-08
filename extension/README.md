# Perceptron Scout Browser Extension

## Quick Start (2 minutes)

### 1. Load Extension in Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `extension` folder
5. Extension icon will appear in toolbar

### 2. Start Backend

Make sure your backend is running:
```bash
cd backend
python -m uvicorn app:app --reload --port 8000
```

### 3. Use the Extension

- Click the extension icon to open popup
- Toggle "Scouting Mode" ON/OFF
- Click "Scan Current Page" to manually analyze any page
- Browse normally - extension auto-scans pages
- See relevance scores and team assignments in real-time

## Features

✅ **Auto-Scan Mode** - Automatically analyzes every page you visit
✅ **Smart Categorization** - Uses your existing keyword extraction (TF-IDF, YAKE)
✅ **Team Assignment** - Auto-assigns to: Regulator, Investor, Competitor, Researcher
✅ **Real-time Notifications** - In-page toast when relevant content found
✅ **Privacy Controls** - Easy ON/OFF toggle, no data sent when disabled
✅ **Local Caching** - Stores analysis results for 1 hour

## How It Works

1. **Content Script** (`content.js`) - Extracts page text, title, headings
2. **Background Worker** (`background.js`) - Sends to backend API
3. **Backend Analysis** (`scout_routes.py`) - Uses existing keyword extraction
4. **Team Matching** - Calculates relevance scores using indicator keywords
5. **Results Display** - Shows in popup + optional in-page notification

## Icon Setup (Optional)

Create icons at these sizes:
- 16x16px for toolbar
- 48x48px for extension management
- 128x128px for Chrome Web Store

Place in `extension/icons/` as `icon16.png`, `icon48.png`, `icon128.png`

Or use online icon generator: https://icon.kitchen/

## Backend API

New endpoint added: `POST /api/scout/analyze`

Accepts:
```json
{
  "url": "https://example.com",
  "title": "Page Title",
  "content": "Main page content...",
  "headings": ["H1", "H2", "H3"],
  "timestamp": "2025-11-08T..."
}
```

Returns:
```json
{
  "team": "investor",
  "relevance_score": 0.75,
  "top_keywords": [
    {"keyword": "funding", "score": 0.8},
    {"keyword": "venture capital", "score": 0.7}
  ]
}
```

## Customization

### Adjust Relevance Threshold
In `content.js`, line 103:
```javascript
if (!result.team || result.relevance_score < 0.3) {
  return; // Change 0.3 to your preferred threshold
}
```

### Change Notification Duration
In `content.js`, line 154:
```javascript
setTimeout(() => {
  // ... remove notification
}, 5000); // Change 5000 (5 seconds) to preferred duration
```

### Add More Team Indicators
In `scout_routes.py`, line 109:
```python
team_indicators = {
    "regulator": ["regulation", "compliance", ...],
    # Add your custom keywords here
}
```

## Troubleshooting

**Extension not loading?**
- Check Chrome version (requires v88+)
- Verify all files are in `extension/` folder
- Look for errors in `chrome://extensions/`

**No analysis results?**
- Ensure backend is running on port 8000
- Check browser console (F12) for errors
- Verify CORS settings in `app.py`

**Low relevance scores?**
- Add more indicator keywords in `scout_routes.py`
- Lower threshold in `content.js`
- Test with pages related to your teams

## Next Steps

- [ ] Add user authentication (store token in extension)
- [ ] Create database table for scouted content
- [ ] Build dashboard page to view all scouted pages
- [ ] Add domain whitelist/blacklist
- [ ] Export to CSV functionality
- [ ] Submit to Chrome Web Store

## Performance

- **Lightweight**: < 100KB total size
- **Fast**: Analysis completes in < 1 second
- **Efficient**: Caches results for 1 hour
- **Privacy**: No tracking, no external requests (except your backend)

Enjoy scouting! 🎯
