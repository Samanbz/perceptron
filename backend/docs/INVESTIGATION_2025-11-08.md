# Investigation: Missing Keywords (2025-11-08)

## Problem

- `investor` team has no `keyword_importance` rows on 2025-11-08
- `regulator` team has no content/keywords at all
- Generated API outputs show ArXiv content for investor team (wrong!)

## Root Causes

### 1. Investor Team (Missing 2025-11-08 Data)

**Status**: 18 unprocessed documents available but not processed

**Available Content**:

- TechCrunch: 9 unprocessed docs
- Crunchbase News: 9 unprocessed docs

**Issue**: `generate_demo_data.py` script wasn't run for 2025-11-08, OR it was run but only processed competitor/researcher teams.

**Fix**: Run the demo data generation script to process the unprocessed content.

### 2. Regulator Team (Zero Content)

**Status**: No documents in `sourced_content` table for any regulator sources

**Configured Sources**:

1. ✅ **Federal Register** - RSS works perfectly

   - URL: `https://www.federalregister.gov/documents/search.rss`
   - Status: Successfully fetched 200 entries in test
   - Issue: Never fetched by sourcer

2. ✅ **SEC Newsroom** - RSS works perfectly

   - URL: `https://www.sec.gov/news/pressreleases.rss`
   - Status: Successfully fetched 25 entries in test
   - Issue: Never fetched by sourcer

3. ❌ **Reuters Regulatory** - RSS feed discontinued
   - URL: `https://www.reuters.com/business/finance/rss`
   - Status: HTTP 401 Forbidden
   - Issue: Reuters discontinued their RSS feeds in 2024

**Fix**:

- Remove or replace Reuters Regulatory source
- Ensure Federal Register and SEC feeds are actually being fetched by the sourcer

## Data Status (2025-11-08)

| Team       | Keywords | Status        |
| ---------- | -------- | ------------- |
| competitor | 27       | ✅ OK         |
| researcher | 50       | ✅ OK         |
| investor   | 0        | ❌ Missing    |
| regulator  | 0        | ❌ No content |

## Historical Data

| Date       | competitor | investor | regulator | researcher |
| ---------- | ---------- | -------- | --------- | ---------- |
| 2025-11-08 | 27         | 0        | 0         | 50         |
| 2025-11-07 | 2652       | 1526     | 155       | 2542       |
| 2025-11-06 | 64         | 97       | 50        | 70         |

## Unprocessed Content Available

| Team       | Source          | Unprocessed Docs |
| ---------- | --------------- | ---------------- |
| competitor | Product Hunt    | 33               |
| competitor | TechRadar       | 3                |
| investor   | TechCrunch      | 9                |
| investor   | Crunchbase News | 9                |
| regulator  | (all sources)   | 0                |
| researcher | ArXiv CS        | 50               |
| researcher | Ars Technica    | 8                |
| researcher | Hacker News     | 14               |
| researcher | MIT Tech Review | 10               |

## RESOLUTION ✅

### Actions Taken

1. ✅ **Fixed Federal Register URL** in `config.json`:

   - Changed from: `https://www.federalregister.gov/documents/search.rss` (returns HTML)
   - Changed to: `https://www.federalregister.gov/api/v1/documents.rss` (proper RSS)
   - Result: Successfully fetched 50 Federal Register documents

2. ✅ **Disabled Reuters Regulatory** in `config.json`:

   - Added `"is_enabled": false`
   - Added note explaining Reuters discontinued RSS feeds in 2024
   - Result: Regulator team now has 2 working sources (Federal Register + SEC)

3. ✅ **Reloaded teams database**:

   - Populated `data/teams.db` with corrected source configurations
   - Result: All teams properly configured with correct source URLs

4. ✅ **Fetched fresh content**:
   - Federal Register: 50 new documents
   - Product Hunt: 1 new document
   - Total: 51 new documents, 233 duplicates skipped
   - Result: Regulator team now has content available!

### Recommendations

### Immediate Actions

1. **Run demo data generation** to process all unprocessed docs:

   ```bash
   cd /Users/samanb/dev/perceptron/backend
   PYTHONPATH=$PWD python3 scripts/generate_demo_data.py
   ```

2. **Regenerate API outputs** after processing:
   ```bash
   PYTHONPATH=$PWD python3 scripts/generate_api_outputs.py --output-dir generated_data --date 2025-11-08
   ```

### Alternative Regulatory Sources

Since Reuters RSS is dead, consider:

- **Bloomberg Law**: (requires subscription)
- **Politico Regulation**: (check if RSS available)
- **JD Supra Regulatory**: https://www.jdsupra.com/legalnews/
- **Compliance Week**: (check RSS feeds)
- **Keep only Federal Register + SEC**: Both work perfectly and provide comprehensive regulatory coverage

### Long-term Fixes

1. Add monitoring/alerting when sources fail to fetch
2. Add "last successful fetch" timestamp to source configs
3. Implement fallback sources for critical teams
4. Add validation that each team has fetched content before processing
