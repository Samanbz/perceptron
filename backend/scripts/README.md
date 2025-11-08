# Scripts Directory

Essential scripts for managing the Signal Radar backend.

## Setup & Initialization

### `initialize_system.py`

Initialize all databases and load configuration from `config.json`.

```bash
python scripts/initialize_system.py
```

### `reset_databases.py`

Reset all databases (WARNING: deletes all data).

```bash
python scripts/reset_databases.py
```

## Data Pipeline

### `fetch_all_sources.py`

Fetch documents from all configured RSS sources.

```bash
PYTHONPATH=$PWD python scripts/fetch_all_sources.py
```

### `process_all_content.py`

Process unprocessed documents and extract keywords using NLP.

```bash
PYTHONPATH=$PWD python scripts/process_all_content.py
```

## Data Export

### `export_keywords_json.py`

Export keyword data for the last 7 days as JSON files (daily + time-series).

```bash
python scripts/export_keywords_json.py
```

Output: `generated_keywords/` directory with daily and time-series data.

## Testing

### `test_keywords_api.py`

Test all API endpoints with FastAPI TestClient.

```bash
python scripts/test_keywords_api.py
```

## Workflow

1. **Initial Setup**: `initialize_system.py`
2. **Fetch Data**: `fetch_all_sources.py`
3. **Process Data**: `process_all_content.py`
4. **Start API**: `python app.py` or `uvicorn app:app`
5. **Export Data** (optional): `export_keywords_json.py`
6. **Test** (optional): `test_keywords_api.py`
