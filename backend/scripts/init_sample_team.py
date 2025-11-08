
"""
Script to initialize the team tables and add a sample team for debugging.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from teams.models import create_team_tables, InternalTeamModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
from datetime import datetime

# Path to your teams.db
DB_PATH = "backend/data/teams.db"
DB_URL = f"sqlite:///{DB_PATH}"

def main():
    # Create tables if they don't exist
    create_team_tables(DB_URL)

    # Connect to DB
    engine = create_engine(DB_URL, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Check if any teams exist
    if session.query(InternalTeamModel).count() == 0:
        # Add a sample team
        team = InternalTeamModel(
            team_key="regulator",
            team_name="Regulatory Team",
            description="Handles regulatory and compliance updates.",
            keyword_config=json.dumps({"threshold": 0.3}),
            sentiment_config=json.dumps({"enabled": True}),
            color="#007bff",
            icon="gavel",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(team)
        session.commit()
        print("Sample team added.")
    else:
        print("Teams already exist in the database.")
    session.close()

if __name__ == "__main__":
    main()
