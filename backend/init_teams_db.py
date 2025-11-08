#!/usr/bin/env python3
"""
Initialize the teams database with required tables.
"""

import sqlite3
from pathlib import Path
import json

def init_teams_db():
    """Initialize the teams database with required tables."""

    # Database path
    teams_db_path = Path(__file__).parent / "data" / "teams.db"

    # Connect to database
    conn = sqlite3.connect(teams_db_path)
    cur = conn.cursor()

    # Create internal_teams table matching SQLAlchemy model
    cur.execute("""
        CREATE TABLE IF NOT EXISTS internal_teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_key TEXT NOT NULL UNIQUE,
            team_name TEXT NOT NULL,
            description TEXT,
            keyword_config TEXT NOT NULL,  -- JSON
            sentiment_config TEXT NOT NULL,  -- JSON
            color TEXT,
            icon TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create team_sources table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS team_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            source_type TEXT NOT NULL,
            source_name TEXT NOT NULL,
            source_url TEXT NOT NULL,
            source_config TEXT,  -- JSON
            fetch_interval_minutes INTEGER DEFAULT 60,
            next_fetch_at TIMESTAMP,
            last_fetched_at TIMESTAMP,
            is_enabled INTEGER DEFAULT 1,
            total_items_fetched INTEGER DEFAULT 0,
            last_fetch_count INTEGER DEFAULT 0,
            last_error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES internal_teams (id)
        )
    """)

    # Create indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_team_key ON internal_teams(team_key)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_team_source ON team_sources(team_id, source_name)")

    # Default configs
    default_keyword_config = json.dumps({
        "min_score": 0.1,
        "max_keywords": 100,
        "include_verbs": True,
        "include_nouns": True,
        "exclude_stop_words": True
    })

    default_sentiment_config = json.dumps({
        "model": "vader",
        "threshold_positive": 0.1,
        "threshold_negative": -0.1,
        "include_magnitude": True
    })

    # Insert default teams (ignore if they already exist)
    teams_data = [
        ("tech", "Technology", "Technology and innovation focus", default_keyword_config, default_sentiment_config, "#3B82F6", "cpu", 1),
        ("finance", "Finance", "Financial markets and economics", default_keyword_config, default_sentiment_config, "#10B981", "dollar-sign", 1),
        ("healthcare", "Healthcare", "Healthcare and pharmaceuticals", default_keyword_config, default_sentiment_config, "#F59E0B", "heart", 1),
        ("energy", "Energy", "Energy and utilities sector", default_keyword_config, default_sentiment_config, "#EF4444", "zap", 1),
        ("consumer", "Consumer", "Consumer goods and retail", default_keyword_config, default_sentiment_config, "#8B5CF6", "shopping-bag", 1),
        ("industrial", "Industrial", "Industrial and manufacturing", default_keyword_config, default_sentiment_config, "#6B7280", "cog", 1),
        ("real_estate", "Real Estate", "Real estate and REITs", default_keyword_config, default_sentiment_config, "#EC4899", "home", 1),
        ("materials", "Materials", "Materials and mining", default_keyword_config, default_sentiment_config, "#84CC16", "package", 1),
        ("utilities", "Utilities", "Utilities and infrastructure", default_keyword_config, default_sentiment_config, "#06B6D4", "power", 1),
        ("communication", "Communication", "Communication services", default_keyword_config, default_sentiment_config, "#F97316", "message-circle", 1)
    ]

    cur.executemany("""
        INSERT OR IGNORE INTO internal_teams
        (team_key, team_name, description, keyword_config, sentiment_config, color, icon, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, teams_data)

    # Commit changes
    conn.commit()
    conn.close()

    print("Teams database initialized successfully!")

if __name__ == "__main__":
    init_teams_db()