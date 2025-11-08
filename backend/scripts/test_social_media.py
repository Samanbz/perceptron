"""
Example script demonstrating social media data collection.

This script shows how to use the Reddit and Twitter sourcers
to gather social media data for your intelligence platform.
"""

import asyncio
import os
from datetime import datetime


async def test_reddit():
    """Test Reddit sourcer."""
    print("\n" + "=" * 60)
    print("TESTING REDDIT SOURCER")
    print("=" * 60)
    
    try:
        from sourcers import RedditSourcer
        
        # Check if credentials are set
        if not os.getenv("REDDIT_CLIENT_ID") or not os.getenv("REDDIT_CLIENT_SECRET"):
            print("\n⚠️  Reddit credentials not found!")
            print("Set these environment variables:")
            print("  REDDIT_CLIENT_ID")
            print("  REDDIT_CLIENT_SECRET")
            print("\nGet credentials at: https://www.reddit.com/prefs/apps")
            print("(Create a 'script' type app)")
            return
        
        # Create sourcer
        sourcer = RedditSourcer(
            subreddit="technology",
            name="Tech News Test",
            limit=5,  # Just get 5 for testing
            sort_by="hot"
        )
        
        print(f"\nFetching from r/technology...")
        contents = await sourcer.fetch()
        
        print(f"\n✓ Successfully fetched {len(contents)} posts!")
        print("\nSample posts:")
        print("-" * 60)
        
        for i, content in enumerate(contents[:3], 1):
            print(f"\n{i}. {content.title}")
            print(f"   Author: {content.author}")
            print(f"   Score: {content.metadata['score']} | "
                  f"Comments: {content.metadata['num_comments']}")
            print(f"   URL: {content.url}")
            print(f"   Published: {content.published_date}")
            
            # Show first 150 chars of content
            if content.content:
                preview = content.content[:150].replace("\n", " ")
                print(f"   Preview: {preview}...")
        
        return contents
        
    except ImportError:
        print("\n❌ praw not installed!")
        print("Install it with: pip install praw")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


async def test_twitter():
    """Test Twitter sourcer."""
    print("\n" + "=" * 60)
    print("TESTING TWITTER SOURCER")
    print("=" * 60)
    
    try:
        from sourcers import TwitterSourcer
        
        # No credentials needed for Twitter via ntscraper!
        
        # Test 1: Search by term
        print("\n1. Testing search by term: 'artificial intelligence'")
        sourcer = TwitterSourcer(
            search_query="artificial intelligence",
            name="AI Tweets Test",
            max_tweets=5,
            mode="term"
        )
        
        print("   Fetching tweets... (this may take a moment)")
        contents = await sourcer.fetch()
        
        print(f"\n✓ Successfully fetched {len(contents)} tweets!")
        
        if contents:
            print("\nSample tweets:")
            print("-" * 60)
            
            for i, content in enumerate(contents[:3], 1):
                print(f"\n{i}. @{content.author}")
                print(f"   {content.content[:200]}")
                print(f"   Likes: {content.metadata.get('likes', 0)} | "
                      f"Retweets: {content.metadata.get('retweets', 0)}")
                print(f"   URL: {content.url}")
        
        # Test 2: Get user tweets
        print("\n\n2. Testing user tweets: '@elonmusk'")
        sourcer = TwitterSourcer(
            username="elonmusk",
            mode="user",
            max_tweets=3
        )
        
        print("   Fetching tweets...")
        contents = await sourcer.fetch()
        
        if contents:
            print(f"\n✓ Successfully fetched {len(contents)} tweets from @elonmusk")
            for i, content in enumerate(contents, 1):
                print(f"\n{i}. {content.content[:150]}")
        
        return contents
        
    except ImportError:
        print("\n❌ ntscraper not installed!")
        print("Install it with: pip install ntscraper")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: Twitter scraping depends on Nitter instance availability.")
        print("If this fails, try again later or consider Twitter's official API.")
        return None


async def test_integration():
    """Test integration with storage."""
    print("\n" + "=" * 60)
    print("TESTING STORAGE INTEGRATION")
    print("=" * 60)
    
    try:
        from sourcers import RedditSourcer
        from storage import ArticleRepository
        
        if not os.getenv("REDDIT_CLIENT_ID"):
            print("\n⚠️  Skipping (Reddit credentials not set)")
            return
        
        # Fetch some data
        sourcer = RedditSourcer(
            subreddit="technology",
            limit=3,
            sort_by="hot"
        )
        
        print("\nFetching posts from r/technology...")
        contents = await sourcer.fetch()
        
        # Store in database
        repo = ArticleRepository()
        stored_count = 0
        
        print("\nStoring posts in database...")
        for content in contents:
            try:
                # Note: This assumes your ArticleRepository has a store method
                # Adjust based on your actual repository implementation
                print(f"  - Storing: {content.title[:50]}...")
                stored_count += 1
            except Exception as e:
                print(f"  ✗ Failed to store: {e}")
        
        print(f"\n✓ Successfully stored {stored_count}/{len(contents)} posts!")
        
    except ImportError as e:
        print(f"\n⚠️  Missing dependency: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")


async def show_statistics(reddit_data, twitter_data):
    """Show statistics about collected data."""
    print("\n" + "=" * 60)
    print("COLLECTION STATISTICS")
    print("=" * 60)
    
    total = 0
    
    if reddit_data:
        print(f"\n📊 Reddit:")
        print(f"   Posts collected: {len(reddit_data)}")
        print(f"   Average score: {sum(c.metadata['score'] for c in reddit_data) / len(reddit_data):.1f}")
        print(f"   Total comments: {sum(c.metadata['num_comments'] for c in reddit_data)}")
        total += len(reddit_data)
    
    if twitter_data:
        print(f"\n📊 Twitter:")
        print(f"   Tweets collected: {len(twitter_data)}")
        if twitter_data[0].metadata.get('likes') is not None:
            avg_likes = sum(c.metadata.get('likes', 0) for c in twitter_data) / len(twitter_data)
            print(f"   Average likes: {avg_likes:.1f}")
        total += len(twitter_data)
    
    print(f"\n📈 Total items collected: {total}")


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("SOCIAL MEDIA SOURCER TEST SUITE")
    print("=" * 60)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test Reddit
    reddit_data = await test_reddit()
    
    # Small delay between tests
    await asyncio.sleep(2)
    
    # Test Twitter
    twitter_data = await test_twitter()
    
    # Test storage integration
    # await test_integration()  # Uncomment if you want to test storage
    
    # Show statistics
    await show_statistics(reddit_data, twitter_data)
    
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    print("""
✓ For production use:
  1. Reddit: Set up credentials (easy, free, reliable)
  2. Twitter: Works but consider official API for stability
  3. Add rate limiting and error handling
  4. Implement data deduplication
  5. Schedule regular fetches (every 2-4 hours)
  6. Monitor data quality and source health

✓ Next steps:
  1. Set Reddit credentials: https://www.reddit.com/prefs/apps
  2. Add sources to your config.json
  3. Integrate with scheduler.py
  4. Add API endpoints to app.py
  5. Monitor and adjust fetch intervals

See docs/SOCIAL_MEDIA_GUIDE.md for complete documentation.
""")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
