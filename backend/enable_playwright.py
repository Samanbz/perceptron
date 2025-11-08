"""
Mark sources that need Playwright to bypass bot protection.

This script updates sources that consistently return HTTP 403 or need JavaScript
rendering to use the Playwright-based scraper instead of regular HTTP requests.
"""

from storage.repository import SourceConfigRepository
from storage.models import SourceConfigModel

# Sources that need Playwright due to bot protection or JavaScript requirements
PLAYWRIGHT_SOURCES = [
    # Bot Protected (HTTP 403)
    "SEC Blog",
    "PitchBook Blog",
    "Insight Partners Blog",
    "The Information",
    "Gartner Blog",
    "Product Hunt Blog",
    "Capterra Blog",
    "OpenAI Blog",
    "The Block",
    "Coinbase Blog",
    "Revolut Blog",
    "Chime Blog",
    "Affirm Blog",
    
    # JavaScript-Heavy Sites
    "TechCrunch Blog",
    "The Verge",
    "Google AI Blog",
    "Meta AI Blog",
    "a16z Blog",
    "Y Combinator Blog",
    "CB Insights Blog",
    "Bloomberg Technology",
    "CNBC Technology",
    "MIT Technology Review",
    "The Gradient",
    "Towards Data Science",
    "Stanford HAI News",
    "Berkeley AI Research",
    "Amazon Science Blog",
    "Apple Machine Learning Research",
    "NVIDIA Developer Blog",
]


def main():
    """Mark sources to use Playwright."""
    repo = SourceConfigRepository()
    
    print(f"\n🎭 Marking {len(PLAYWRIGHT_SOURCES)} sources to use Playwright...\n")
    
    updated = 0
    not_found = 0
    
    for source_name in PLAYWRIGHT_SOURCES:
        # Find source by name
        sources = repo.session.query(SourceConfigModel).filter(
            SourceConfigModel.source_name == source_name
        ).all()
        
        if not sources:
            print(f"❌ Source not found: {source_name}")
            not_found += 1
            continue
        
        source = sources[0]
        
        # Update config to use Playwright
        if not source.config:
            source.config = {}
        
        source.config["use_playwright"] = True
        # Mark the object as modified for SQLAlchemy
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(source, "config")
        
        updated += 1
        print(f"✅ {source_name}: Enabled Playwright")
    
    repo.session.commit()
    
    print(f"\n✅ Updated {updated} sources to use Playwright")
    if not_found > 0:
        print(f"⚠️  Could not find {not_found} sources")
    print(f"\nThese sources will now bypass bot protection and handle JavaScript!\n")

if __name__ == "__main__":
    main()
