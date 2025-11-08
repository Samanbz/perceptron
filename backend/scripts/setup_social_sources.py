"""
Add social media sources to your Perceptron configuration.

This script demonstrates how to integrate Reddit and Twitter
into your existing data collection pipeline.
"""

import json
import os
from pathlib import Path


def add_social_sources_to_config():
    """Add social media sources to config.json."""
    
    config_path = Path(__file__).parent.parent / "config.json"
    
    # Load existing config
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        config = {"sources": []}
    
    # Define social media sources
    social_sources = [
        # Reddit - Technology News
        {
            "type": "reddit",
            "enabled": True,
            "name": "Reddit Technology",
            "subreddit": "technology",
            "limit": 100,
            "sort_by": "hot",
            "time_filter": "day",
            "fetch_interval_hours": 2,
            "tags": ["technology", "news", "reddit"]
        },
        
        # Reddit - Machine Learning
        {
            "type": "reddit",
            "enabled": True,
            "name": "Reddit ML",
            "subreddit": "MachineLearning",
            "limit": 50,
            "sort_by": "top",
            "time_filter": "week",
            "fetch_interval_hours": 6,
            "tags": ["ai", "machine-learning", "research", "reddit"]
        },
        
        # Reddit - World News
        {
            "type": "reddit",
            "enabled": True,
            "name": "Reddit World News",
            "subreddit": "worldnews",
            "limit": 100,
            "sort_by": "hot",
            "time_filter": "day",
            "fetch_interval_hours": 1,
            "tags": ["news", "world", "reddit"]
        },
        
        # Reddit - Business
        {
            "type": "reddit",
            "enabled": True,
            "name": "Reddit Business",
            "subreddit": "business",
            "limit": 50,
            "sort_by": "top",
            "time_filter": "day",
            "fetch_interval_hours": 4,
            "tags": ["business", "finance", "reddit"]
        },
        
        # Twitter - AI Regulation
        {
            "type": "twitter",
            "enabled": True,
            "name": "Twitter AI Policy",
            "search_query": "artificial intelligence regulation OR AI policy OR AI governance",
            "mode": "term",
            "max_tweets": 100,
            "fetch_interval_hours": 2,
            "tags": ["ai", "policy", "regulation", "twitter"]
        },
        
        # Twitter - Venture Capital
        {
            "type": "twitter",
            "enabled": True,
            "name": "Twitter VC News",
            "search_query": "venture capital OR startup funding OR Series A",
            "mode": "term",
            "max_tweets": 50,
            "fetch_interval_hours": 4,
            "tags": ["vc", "funding", "startups", "twitter"]
        },
        
        # Twitter - Cybersecurity
        {
            "type": "twitter",
            "enabled": True,
            "name": "Twitter Security",
            "search_query": "cybersecurity OR data breach OR ransomware",
            "mode": "term",
            "max_tweets": 50,
            "fetch_interval_hours": 2,
            "tags": ["security", "cyber", "twitter"]
        },
        
        # Twitter - Industry Leaders
        {
            "type": "twitter",
            "enabled": False,  # Disabled by default
            "name": "Tech Leaders",
            "username": "satyanadella",
            "mode": "user",
            "max_tweets": 20,
            "fetch_interval_hours": 12,
            "tags": ["leaders", "microsoft", "twitter"]
        },
        
        # Twitter - Hashtag Monitoring
        {
            "type": "twitter",
            "enabled": False,  # Disabled by default
            "name": "AI Hashtag",
            "hashtag": "AI",
            "mode": "hashtag",
            "max_tweets": 30,
            "fetch_interval_hours": 6,
            "tags": ["ai", "trending", "twitter"]
        }
    ]
    
    # Add sources (avoid duplicates)
    existing_names = {s.get("name") for s in config.get("sources", [])}
    
    for source in social_sources:
        if source["name"] not in existing_names:
            config.setdefault("sources", []).append(source)
            print(f"✓ Added: {source['name']}")
        else:
            print(f"⊘ Skipped (already exists): {source['name']}")
    
    # Save config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✓ Configuration saved to: {config_path}")
    return config


def create_environment_template():
    """Create .env.example file with required variables."""
    
    env_example = """# Reddit API Credentials
# Get these from: https://www.reddit.com/prefs/apps
# 1. Click "Create App" or "Create Another App"
# 2. Choose "script" type
# 3. Copy client_id and client_secret

REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=Perceptron Intelligence Aggregator v1.0

# LinkedIn via Proxycurl (Optional - Paid Service)
# Get from: https://nubela.co/proxycurl/
# PROXYCURL_API_KEY=your_api_key_here

# Twitter Official API (Optional - if you upgrade from Nitter)
# Get from: https://developer.twitter.com/
# TWITTER_API_KEY=your_api_key_here
# TWITTER_API_SECRET=your_api_secret_here
# TWITTER_BEARER_TOKEN=your_bearer_token_here
"""
    
    env_path = Path(__file__).parent.parent / ".env.example"
    
    with open(env_path, 'w') as f:
        f.write(env_example)
    
    print(f"✓ Created environment template: {env_path}")
    print("\n📝 Next steps:")
    print("1. Copy .env.example to .env")
    print("2. Fill in your Reddit credentials")
    print("3. Run: python scripts/test_social_media.py")


def show_setup_instructions():
    """Display setup instructions."""
    
    instructions = """
╔══════════════════════════════════════════════════════════════════╗
║          SOCIAL MEDIA SOURCES - SETUP COMPLETE                   ║
╚══════════════════════════════════════════════════════════════════╝

✅ Created/Updated:
  • config.json - Added 9 social media sources
  • .env.example - Environment variable template

📋 Sources Added:

  REDDIT (4 sources):
  ├─ r/technology    - Tech news (every 2 hours)
  ├─ r/MachineLearning - AI research (every 6 hours)
  ├─ r/worldnews     - Global events (every hour)
  └─ r/business      - Business trends (every 4 hours)

  TWITTER (5 sources):
  ├─ AI Policy       - Regulation keywords (every 2 hours)
  ├─ VC News         - Funding trends (every 4 hours)
  ├─ Security        - Cyber threats (every 2 hours)
  ├─ Tech Leaders    - @satyanadella [DISABLED]
  └─ AI Hashtag      - #AI monitoring [DISABLED]

🔧 NEXT STEPS:

1. GET REDDIT CREDENTIALS (5 minutes):
   → Go to: https://www.reddit.com/prefs/apps
   → Click "Create App" → Choose "script" type
   → Copy your client_id and client_secret

2. SET ENVIRONMENT VARIABLES:
   
   Windows PowerShell:
   $env:REDDIT_CLIENT_ID="your_client_id"
   $env:REDDIT_CLIENT_SECRET="your_client_secret"
   
   Or create .env file:
   cp .env.example .env
   # Then edit .env with your credentials

3. INSTALL DEPENDENCIES:
   pip install praw ntscraper

4. TEST THE SETUP:
   python scripts/test_social_media.py

5. START COLLECTING:
   python scripts/fetch_social_media.py

📚 DOCUMENTATION:
  • Complete guide: docs/SOCIAL_MEDIA_GUIDE.md
  • Quick summary: docs/SOCIAL_MEDIA_SUMMARY.md

💡 TIPS:
  • Reddit is the easiest to start with (free API)
  • Twitter works without credentials (via Nitter)
  • Adjust fetch intervals based on your needs
  • Enable/disable sources in config.json

⚙️  INTEGRATION OPTIONS:
  1. Manual: Run scripts/fetch_social_media.py periodically
  2. Scheduler: Add to scheduler.py for automation
  3. API: Add endpoints to app.py for on-demand fetching

Need help? Check docs/SOCIAL_MEDIA_GUIDE.md
"""
    
    print(instructions)


def main():
    """Run configuration setup."""
    
    print("\n🚀 Setting up social media data sources...\n")
    
    # Add sources to config
    config = add_social_sources_to_config()
    
    print()
    
    # Create environment template
    create_environment_template()
    
    print()
    
    # Show instructions
    show_setup_instructions()
    
    # Summary
    enabled_sources = [s for s in config.get("sources", []) 
                      if s.get("type") in ["reddit", "twitter"] and s.get("enabled")]
    
    print(f"\n📊 SUMMARY: {len(enabled_sources)} social media sources ready to use")
    print("   (2 sources disabled by default - enable in config.json if needed)")
    
    print("\n✅ Setup complete! Follow the next steps above to start collecting data.")


if __name__ == "__main__":
    main()
