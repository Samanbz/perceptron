"""
Playwright-based web scraper for handling bot protection and JavaScript-rendered content.

This scraper uses a headless browser to:
- Bypass bot protection (403 errors)
- Render JavaScript content
- Handle dynamic loading
- Avoid rate limiting with realistic user behavior
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class PlaywrightScraper:
    """
    Advanced web scraper using Playwright headless browser.
    
    Features:
    - Bypasses bot protection with realistic browser fingerprint
    - Handles JavaScript-rendered content
    - Implements delays and scrolling for natural behavior
    - Supports custom selectors for flexible parsing
    """
    
    def __init__(
        self,
        headless: bool = True,
        user_agent: Optional[str] = None,
        timeout: int = 30000
    ):
        """
        Initialize Playwright scraper.
        
        Args:
            headless: Run browser in headless mode
            user_agent: Custom user agent string
            timeout: Page load timeout in milliseconds
        """
        self.headless = headless
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def start(self):
        """Start the browser."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )
        logger.info("Playwright browser started")
    
    async def close(self):
        """Close the browser."""
        if self.browser:
            await self.browser.close()
            await self.playwright.stop()
            logger.info("Playwright browser closed")
    
    async def scrape_blog(
        self,
        url: str,
        selectors: Dict[str, str],
        max_items: int = 10,
        wait_for_selector: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Scrape blog articles using Playwright.
        
        Args:
            url: Blog URL to scrape
            selectors: Dict with keys: item, link, title, content, date
            max_items: Maximum number of items to scrape
            wait_for_selector: Optional selector to wait for before scraping
            
        Returns:
            List of scraped articles with title, url, content, published_date
        """
        if not self.browser:
            await self.start()
        
        context = await self.browser.new_context(
            user_agent=self.user_agent,
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
        )
        
        page = await context.new_page()
        
        try:
            logger.info(f"Navigating to {url}")
            # Try to load page with more lenient timeout
            await page.goto(url, wait_until='domcontentloaded', timeout=self.timeout)
            
            # Wait for specific selector if provided
            if wait_for_selector:
                try:
                    await page.wait_for_selector(wait_for_selector, timeout=10000)
                except:
                    logger.warning(f"Wait selector '{wait_for_selector}' not found, continuing anyway")
            else:
                # Default wait for content to load (longer for dynamic sites)
                await page.wait_for_timeout(5000)
            
            # Scroll to load lazy content
            await self._scroll_page(page)
            
            # Wait a bit more after scrolling
            await page.wait_for_timeout(2000)
            
            # Get page content
            content = await page.content()
            soup = BeautifulSoup(content, 'lxml')
            
            # Debug: log some info about the page
            logger.info(f"Page title: {soup.title.string if soup.title else 'No title'}")
            logger.info(f"Page has {len(soup.find_all('article'))} article tags")
            logger.info(f"Page has {len(soup.find_all('a'))} links")
            
            # Parse articles (pass base URL for relative links)
            articles = self._parse_articles(soup, selectors, max_items, base_url=url)
            
            logger.info(f"Scraped {len(articles)} articles from {url}")
            return articles
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return []
        finally:
            await page.close()
            await context.close()
    
    async def _scroll_page(self, page: Page, scrolls: int = 3):
        """Scroll page to trigger lazy loading."""
        for i in range(scrolls):
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(500)
    
    def _parse_articles(
        self,
        soup: BeautifulSoup,
        selectors: Dict[str, str],
        max_items: int,
        base_url: str = ''
    ) -> List[Dict[str, Any]]:
        """Parse articles from soup using selectors."""
        articles = []
        
        item_selector = selectors.get('item', 'article')
        items = soup.select(item_selector)
        
        logger.info(f"Found {len(items)} items with selector '{item_selector}'")
        
        for item in items[:max_items]:
            try:
                article = self._parse_single_article(item, selectors, base_url)
                if article and article.get('title') and article.get('url'):
                    articles.append(article)
            except Exception as e:
                logger.debug(f"Error parsing article: {e}")
                continue
        
        return articles
    
    def _parse_single_article(
        self,
        item: Any,
        selectors: Dict[str, str],
        base_url: str = ''
    ) -> Optional[Dict[str, Any]]:
        """Parse a single article element."""
        from urllib.parse import urljoin
        
        # Extract link
        link_elem = item.select_one(selectors.get('link', 'a'))
        if not link_elem:
            return None
        
        url = link_elem.get('href', '')
        if not url:
            return None
        
        # Make URL absolute
        if base_url:
            url = urljoin(base_url, url)
        
        # Extract title
        title_elem = item.select_one(selectors.get('title', 'h2, h3'))
        title = title_elem.get_text(strip=True) if title_elem else ''
        
        # Extract content/excerpt
        content_elem = item.select_one(selectors.get('content', 'p, div.excerpt'))
        content = content_elem.get_text(strip=True) if content_elem else ''
        
        # Extract date
        date_elem = item.select_one(selectors.get('date', 'time, span.date'))
        date_str = None
        if date_elem:
            # Try datetime attribute first
            date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
        
        return {
            'title': title,
            'url': url,
            'content': content or title,  # Use title if no content
            'published_date': date_str,
            'scraped_at': datetime.utcnow().isoformat()
        }
    
    async def scrape_with_pagination(
        self,
        url: str,
        selectors: Dict[str, str],
        max_pages: int = 3,
        next_button_selector: str = 'a.next, button.next'
    ) -> List[Dict[str, Any]]:
        """
        Scrape multiple pages by clicking next button.
        
        Args:
            url: Starting URL
            selectors: Article selectors
            max_pages: Maximum pages to scrape
            next_button_selector: Selector for next page button
            
        Returns:
            All articles from all pages
        """
        if not self.browser:
            await self.start()
        
        all_articles = []
        context = await self.browser.new_context(
            user_agent=self.user_agent,
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        try:
            await page.goto(url, wait_until='networkidle', timeout=self.timeout)
            
            for page_num in range(max_pages):
                logger.info(f"Scraping page {page_num + 1}")
                
                # Scroll and wait
                await self._scroll_page(page)
                await page.wait_for_timeout(1000)
                
                # Parse current page
                content = await page.content()
                soup = BeautifulSoup(content, 'lxml')
                articles = self._parse_articles(soup, selectors, 50)
                all_articles.extend(articles)
                
                # Try to find and click next button
                next_button = await page.query_selector(next_button_selector)
                if not next_button:
                    logger.info("No next button found, stopping pagination")
                    break
                
                # Click next and wait for navigation
                await next_button.click()
                await page.wait_for_load_state('networkidle')
                await page.wait_for_timeout(1000)
            
            logger.info(f"Total articles scraped: {len(all_articles)}")
            return all_articles
            
        except Exception as e:
            logger.error(f"Error in pagination scraping: {e}")
            return all_articles
        finally:
            await page.close()
            await context.close()


async def test_playwright_scraper():
    """Test the Playwright scraper."""
    logging.basicConfig(level=logging.INFO)
    
    test_cases = [
        {
            'name': 'VentureBeat',
            'url': 'https://venturebeat.com/',
            'selectors': {
                'item': 'div.ArticleListing, article',
                'link': 'a',
                'title': 'h2, h3',
                'content': 'p, div.excerpt',
                'date': 'time'
            }
        },
        {
            'name': 'Ars Technica',
            'url': 'https://arstechnica.com/',
            'selectors': {
                'item': 'article, div.article',
                'link': 'a',
                'title': 'h2, h3',
                'content': 'p.excerpt',
                'date': 'time'
            }
        }
    ]
    
    async with PlaywrightScraper(timeout=60000) as scraper:
        for test in test_cases:
            print(f"\n{'='*60}")
            print(f"Testing: {test['name']}")
            print(f"URL: {test['url']}")
            print(f"{'='*60}")
            
            articles = await scraper.scrape_blog(
                test['url'],
                test['selectors'],
                max_items=5
            )
            
            print(f"\nScraped {len(articles)} articles:")
            for i, article in enumerate(articles, 1):
                print(f"\n{i}. {article['title'][:80]}")
                print(f"   URL: {article['url'][:100]}")
                if article.get('published_date'):
                    print(f"   Date: {article['published_date']}")


if __name__ == '__main__':
    # Test the scraper
    asyncio.run(test_playwright_scraper())
