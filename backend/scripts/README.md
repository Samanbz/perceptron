# Scripts Directory

Utility scripts for setup, testing, and demonstration.

## Setup Scripts

### `setup_teams.py`
Initialize teams database from `config.json` (single source of truth).

```bash
python scripts/setup_teams.py validate  # Validate config.json
python scripts/setup_teams.py init      # Initialize database
python scripts/setup_teams.py show      # Show all teams
python scripts/setup_teams.py stats     # Show statistics
python scripts/setup_teams.py export    # Export to config_backup.json
```

### `setup_data_lake.py`
Initialize content storage database and fetch initial data.

```bash
python scripts/setup_data_lake.py init    # Create database & add sources
python scripts/setup_data_lake.py fetch   # Fetch from all sources
python scripts/setup_data_lake.py stats   # Show statistics
python scripts/setup_data_lake.py recent  # Show recent content
python scripts/setup_data_lake.py sources # List sources
```

### `setup_keywords.py`
Initialize keywords database and manage configurations.

```bash
python scripts/setup_keywords.py init            # Initialize database
python scripts/setup_keywords.py add-config NAME # Add extraction config
python scripts/setup_keywords.py show-configs    # List configurations
python scripts/setup_keywords.py stats           # Show statistics
```

### `reset_databases.py`
Reset all databases to start fresh.

```bash
python scripts/reset_databases.py
```

## Test Scripts

### `test_team_config.py`
Test team repository and config.json integration.

```bash
python scripts/test_team_config.py
```

### `test_keyword_extraction.py`
Test keyword extraction with sample text.

```bash
python scripts/test_keyword_extraction.py
```

### `test_sourcers.py`
Test RSS feed sourcing functionality.

```bash
python scripts/test_sourcers.py
```

## Demo Scripts

### `demo_keyword_pipeline.py`
Demonstrate end-to-end keyword extraction pipeline.

```bash
python scripts/demo_keyword_pipeline.py
```

### `example_usage.py`
Example usage of sourcing and storage.

```bash
python scripts/example_usage.py
```

### `example_nlp_processing.py`
Example NLP processing with spaCy.

```bash
python scripts/example_nlp_processing.py
```

## Architecture Documentation

### `ARCHITECTURE.py`
ASCII diagram of system architecture (executable).

```bash
python scripts/ARCHITECTURE.py
```

### `SYSTEM_DIAGRAM.py`
Visual system diagram generator.

```bash
python scripts/SYSTEM_DIAGRAM.py
```

## Common Workflows

### Initial Setup
```bash
# 1. Validate configuration
python scripts/setup_teams.py validate

# 2. Initialize all databases
python scripts/setup_teams.py init
python scripts/setup_data_lake.py init
python scripts/setup_keywords.py init

# 3. Fetch initial content
python scripts/setup_data_lake.py fetch
```

### Add New Team
```bash
# 1. Edit config.json
vim config.json

# 2. Validate and apply
python scripts/setup_teams.py validate
python scripts/setup_teams.py init
```

### Check System Status
```bash
python scripts/setup_teams.py stats
python scripts/setup_data_lake.py stats
python scripts/setup_keywords.py stats
```

### Reset and Start Over
```bash
python scripts/reset_databases.py
python scripts/setup_teams.py init
python scripts/setup_data_lake.py init fetch
python scripts/setup_keywords.py init
```
