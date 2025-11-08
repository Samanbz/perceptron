"""Example usage of the sourcer pipeline."""

import asyncio
from sourcers import RSSSourcer


async def main():
    """Demonstrate RSS sourcer usage."""
    
    print("=" * 70)
    print("RSS Sourcer Example")
    print("=" * 70)
    
    # Example 1: TechCrunch RSS Feed
    print("\n📰 Fetching from TechCrunch RSS Feed...")
    print("-" * 70)
    
    techcrunch_sourcer = RSSSourcer(
        feed_url="https://techcrunch.com/feed/",
        name="TechCrunch",
        max_entries=5
    )
    
    try:
        contents = await techcrunch_sourcer.fetch()
        print(f"✓ Successfully fetched {len(contents)} entries\n")
        
        for i, content in enumerate(contents, 1):
            print(f"{i}. {content.title}")
            print(f"   URL: {content.url}")
            print(f"   Published: {content.published_date}")
            print(f"   Author: {content.author or 'N/A'}")
            print(f"   Content preview: {content.content[:100]}...")
            print()
    except Exception as e:
        print(f"✗ Error fetching TechCrunch: {e}\n")
    
    # Example 2: Hacker News RSS Feed
    print("\n💻 Fetching from Hacker News RSS Feed...")
    print("-" * 70)
    
    hn_sourcer = RSSSourcer(
        feed_url="https://news.ycombinator.com/rss",
        name="Hacker News",
        max_entries=5
    )
    
    try:
        contents = await hn_sourcer.fetch()
        print(f"✓ Successfully fetched {len(contents)} entries\n")
        
        for i, content in enumerate(contents, 1):
            print(f"{i}. {content.title}")
            print(f"   URL: {content.url}")
            print(f"   Published: {content.published_date}")
            print()
    except Exception as e:
        print(f"✗ Error fetching Hacker News: {e}\n")
    
    # Example 3: Using to_dict() for JSON serialization
    print("\n📊 Demonstrating JSON serialization...")
    print("-" * 70)
    
    if contents:
        sample = contents[0]
        import json
        print(json.dumps(sample.to_dict(), indent=2, default=str))
    
    print("\n" + "=" * 70)
    print("Example complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
