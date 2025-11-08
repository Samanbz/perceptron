#!/usr/bin/env python3
"""
Initialize the keywords database with required tables.
"""

import sqlite3
from pathlib import Path

def init_keywords_db():
    """Initialize the keywords database with required tables."""

    # Database path
    keywords_db_path = Path(__file__).parent / "data" / "keywords.db"

    # Connect to database
    conn = sqlite3.connect(keywords_db_path)
    cur = conn.cursor()

    # Create keyword_importance table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS keyword_importance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            team_key TEXT NOT NULL,
            date DATE NOT NULL,
            importance_score REAL NOT NULL,
            sentiment_score REAL,
            sentiment_magnitude REAL,
            frequency INTEGER DEFAULT 0,
            document_count INTEGER DEFAULT 0,
            source_diversity REAL DEFAULT 0.0,
            velocity REAL DEFAULT 0.0,
            positive_mentions INTEGER DEFAULT 0,
            negative_mentions INTEGER DEFAULT 0,
            neutral_mentions INTEGER DEFAULT 0,
            content_ids TEXT,  -- JSON array of content IDs
            sample_snippets TEXT,  -- JSON array of sample text snippets
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(keyword, team_key, date)
        )
    """)

    # Create indexes for better performance
    cur.execute("CREATE INDEX IF NOT EXISTS idx_keyword_date ON keyword_importance(date)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_keyword_team ON keyword_importance(team_key)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_keyword_score ON keyword_importance(importance_score DESC)")

    # Insert some sample data for testing
    sample_data = [
        ("artificial intelligence", "tech", "2024-11-15", 8.5, 0.3, 0.7, 45, 12, 0.8, 2.1, 15, 5, 25, "[1,2,3]", '["AI is transforming our industry", "Machine learning applications growing"]'),
        ("earnings growth", "finance", "2024-11-15", 7.8, 0.6, 0.8, 32, 8, 0.9, 1.8, 20, 2, 10, "[4,5]", '["Strong earnings performance", "Revenue growth exceeds expectations"]'),
        ("renewable energy", "energy", "2024-11-15", 6.9, 0.4, 0.6, 28, 15, 0.7, 1.5, 18, 3, 7, "[6,7,8]", '["Shift to renewable sources", "Clean energy investments rising"]'),
        ("supply chain", "industrial", "2024-11-15", 7.2, -0.2, 0.5, 38, 20, 0.6, -0.8, 12, 15, 11, "[9,10]", '["Supply chain disruptions continue", "Logistics challenges persist"]'),
        ("digital transformation", "tech", "2024-11-15", 8.1, 0.5, 0.9, 41, 18, 0.85, 2.3, 22, 4, 15, "[11,12,13]", '["Digital initiatives accelerating", "Technology adoption increasing"]'),
    ]

    # Insert sample data (ignore if already exists due to UNIQUE constraint)
    cur.executemany("""
        INSERT OR IGNORE INTO keyword_importance
        (keyword, team_key, date, importance_score, sentiment_score, sentiment_magnitude,
         frequency, document_count, source_diversity, velocity, positive_mentions,
         negative_mentions, neutral_mentions, content_ids, sample_snippets)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_data)

    # Commit changes
    conn.commit()
    conn.close()

    print("Keywords database initialized successfully!")

if __name__ == "__main__":
    init_keywords_db()