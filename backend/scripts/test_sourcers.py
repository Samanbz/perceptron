"""
Quick tests for the sourcer pipeline.

Run with: python test_sourcers.py
"""

import asyncio
from sourcers import RSSSourcer, BaseSourcer, SourcedContent


def test_sourced_content():
    """Test SourcedContent model."""
    print("Testing SourcedContent...")
    
    content = SourcedContent(
        title="Test Article",
        content="This is test content",
        url="https://example.com",
        author="Test Author"
    )
    
    assert content.title == "Test Article"
    assert content.content == "This is test content"
    assert content.url == "https://example.com"
    assert content.author == "Test Author"
    
    # Test to_dict
    data = content.to_dict()
    assert data["title"] == "Test Article"
    assert "retrieved_at" in data
    
    print("✓ SourcedContent works correctly\n")


def test_rss_sourcer_validation():
    """Test RSS sourcer validation."""
    print("Testing RSS sourcer validation...")
    
    # Valid URL should work
    try:
        sourcer = RSSSourcer(feed_url="https://techcrunch.com/feed/")
        print("✓ Valid URL accepted")
    except ValueError:
        print("✗ Valid URL rejected (unexpected)")
        return
    
    # Invalid URL should fail
    try:
        sourcer = RSSSourcer(feed_url="not-a-url")
        print("✗ Invalid URL accepted (unexpected)")
    except ValueError as e:
        print(f"✓ Invalid URL rejected: {e}")
    
    # Missing URL should fail
    try:
        sourcer = RSSSourcer(feed_url="")
        print("✗ Empty URL accepted (unexpected)")
    except ValueError as e:
        print(f"✓ Empty URL rejected: {e}")
    
    print()


async def test_rss_sourcer_fetch():
    """Test RSS sourcer fetch functionality."""
    print("Testing RSS sourcer fetch...")
    
    sourcer = RSSSourcer(
        feed_url="https://news.ycombinator.com/rss",
        name="Test HN",
        max_entries=3
    )
    
    contents = await sourcer.fetch()
    
    assert len(contents) > 0, "No content fetched"
    assert len(contents) <= 3, "Too many entries fetched"
    
    for content in contents:
        assert isinstance(content, SourcedContent)
        assert content.title, "Content missing title"
        assert content.url, "Content missing URL"
        print(f"  ✓ Fetched: {content.title[:60]}...")
    
    print(f"✓ Successfully fetched {len(contents)} entries\n")


async def test_multiple_feeds():
    """Test fetching from multiple feeds concurrently."""
    print("Testing multiple feeds concurrently...")
    
    feeds = [
        ("https://news.ycombinator.com/rss", "HN", 2),
        ("https://techcrunch.com/feed/", "TC", 2),
    ]
    
    tasks = [
        RSSSourcer(url, name, max_entries).fetch()
        for url, name, max_entries in feeds
    ]
    
    results = await asyncio.gather(*tasks)
    
    total_items = sum(len(result) for result in results)
    print(f"✓ Fetched {total_items} total items from {len(feeds)} feeds\n")


def run_all_tests():
    """Run all tests."""
    print("=" * 70)
    print("Running Sourcer Pipeline Tests")
    print("=" * 70)
    print()
    
    # Synchronous tests
    test_sourced_content()
    test_rss_sourcer_validation()
    
    # Async tests
    asyncio.run(test_rss_sourcer_fetch())
    asyncio.run(test_multiple_feeds())
    
    print("=" * 70)
    print("All tests passed! ✓")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()
