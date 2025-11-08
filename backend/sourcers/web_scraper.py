"""
Web scraper base class and implementations for extracting content from various sources
"""
import asyncio
import aiohttp
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

from storage.models import SourcedContentModel


class WebScraper(ABC):
    """Base class for web scrapers"""
    
    def __init__(self, base_url: str, name: str, max_pages: int = 10):
        self.base_url = base_url
        self.name = name
        self.max_pages = max_pages
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
        return self.session
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch HTML content from URL"""
        try:
            session = await self._get_session()
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"Failed to fetch {url}: HTTP {response.status}")
                    return None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters
        text = text.strip()
        return text
    
    def extract_date(self, soup: BeautifulSoup, selectors: List[str]) -> Optional[datetime]:
        """Try to extract date from common selectors"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                date_text = element.get_text().strip()
                # Try common date formats
                for fmt in ['%Y-%m-%d', '%B %d, %Y', '%d %B %Y', '%m/%d/%Y']:
                    try:
                        return datetime.strptime(date_text, fmt)
                    except ValueError:
                        continue
        return None
    
    @abstractmethod
    async def scrape(self) -> List[SourcedContentModel]:
        """Implement scraping logic in subclasses"""
        pass


class BlogScraper(WebScraper):
    """Generic blog scraper - works with most WordPress/Medium-style blogs"""
    
    def __init__(self, base_url: str, name: str, 
                 article_selector: str = "article",
                 title_selector: str = "h1, h2.entry-title, .post-title",
                 content_selector: str = ".entry-content, .post-content, article p",
                 link_selector: str = "a[href]",
                 date_selector: str = "time, .published, .post-date",
                 max_pages: int = 5):
        super().__init__(base_url, name, max_pages)
        self.article_selector = article_selector
        self.title_selector = title_selector
        self.content_selector = content_selector
        self.link_selector = link_selector
        self.date_selector = date_selector
    
    async def scrape(self) -> List[SourcedContentModel]:
        """Scrape blog posts"""
        contents = []
        
        # Fetch main page
        html = await self.fetch_page(self.base_url)
        if not html:
            return contents
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find all article links
        articles = soup.select(self.article_selector)[:self.max_pages]
        
        for article in articles:
            try:
                # Extract article URL
                link = article.select_one(self.link_selector)
                if not link:
                    continue
                
                article_url = urljoin(self.base_url, link.get('href'))
                
                # Fetch article page
                article_html = await self.fetch_page(article_url)
                if not article_html:
                    continue
                
                article_soup = BeautifulSoup(article_html, 'html.parser')
                
                # Extract title
                title_elem = article_soup.select_one(self.title_selector)
                title = title_elem.get_text().strip() if title_elem else "No Title"
                
                # Extract content
                content_elems = article_soup.select(self.content_selector)
                content = ' '.join([self.clean_text(p.get_text()) for p in content_elems])
                
                # Extract date
                date_elem = article_soup.select_one(self.date_selector)
                published_date = None
                if date_elem:
                    date_str = date_elem.get('datetime') or date_elem.get_text()
                    try:
                        published_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except:
                        pass
                
                if content:
                    contents.append(SourcedContentModel(
                        title=title,
                        content=content[:5000],  # Limit content length
                        url=article_url,
                        published_date=published_date,
                        retrieved_at=datetime.utcnow(),
                        metadata={
                            'source': self.name,
                            'scraper_type': 'blog'
                        }
                    ))
                
            except Exception as e:
                print(f"Error scraping article: {e}")
                continue
        
        await self.close()
        return contents


class NewsScraper(WebScraper):
    """Scraper for news websites"""
    
    def __init__(self, base_url: str, name: str,
                 article_list_selector: str = ".article-list .article",
                 max_pages: int = 10):
        super().__init__(base_url, name, max_pages)
        self.article_list_selector = article_list_selector
    
    async def scrape(self) -> List[SourcedContentModel]:
        """Scrape news articles"""
        contents = []
        
        html = await self.fetch_page(self.base_url)
        if not html:
            return contents
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find article links
        article_items = soup.select(self.article_list_selector)[:self.max_pages]
        
        for item in article_items:
            try:
                # Find link
                link = item.find('a', href=True)
                if not link:
                    continue
                
                article_url = urljoin(self.base_url, link['href'])
                
                # Fetch article
                article_html = await self.fetch_page(article_url)
                if not article_html:
                    continue
                
                article_soup = BeautifulSoup(article_html, 'html.parser')
                
                # Extract title
                title = article_soup.find('h1')
                title_text = title.get_text().strip() if title else "No Title"
                
                # Extract content from paragraphs
                paragraphs = article_soup.find_all('p')
                content = ' '.join([self.clean_text(p.get_text()) for p in paragraphs if len(p.get_text()) > 50])
                
                # Try to find date
                date_elem = article_soup.find('time')
                published_date = None
                if date_elem and date_elem.get('datetime'):
                    try:
                        published_date = datetime.fromisoformat(date_elem['datetime'].replace('Z', '+00:00'))
                    except:
                        pass
                
                if content:
                    contents.append(SourcedContentModel(
                        title=title_text,
                        content=content[:5000],
                        url=article_url,
                        published_date=published_date,
                        retrieved_at=datetime.utcnow(),
                        metadata={
                            'source': self.name,
                            'scraper_type': 'news'
                        }
                    ))
                
            except Exception as e:
                print(f"Error scraping news article: {e}")
                continue
        
        await self.close()
        return contents


class GenericWebScraper(WebScraper):
    """Generic web scraper with configurable selectors"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize with configuration
        
        config should contain:
        - base_url: str
        - name: str
        - max_pages: int
        - selectors: dict with title, content, link, date selectors
        """
        super().__init__(
            config['base_url'],
            config['name'],
            config.get('max_pages', 10)
        )
        self.selectors = config.get('selectors', {})
    
    async def scrape(self) -> List[SourcedContentModel]:
        """Scrape using configured selectors"""
        contents = []
        
        html = await self.fetch_page(self.base_url)
        if not html:
            return contents
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find items using item_selector
        items = soup.select(self.selectors.get('item', 'article'))[:self.max_pages]
        
        for item in items:
            try:
                # Extract link
                link_elem = item.select_one(self.selectors.get('link', 'a[href]'))
                if not link_elem:
                    continue
                
                url = urljoin(self.base_url, link_elem.get('href'))
                
                # Extract title (from current page or fetch article)
                title_elem = item.select_one(self.selectors.get('title', 'h2, h3'))
                title = self.clean_text(title_elem.get_text()) if title_elem else "No Title"
                
                # Fetch full article if needed
                article_html = await self.fetch_page(url)
                if article_html:
                    article_soup = BeautifulSoup(article_html, 'html.parser')
                    
                    # Extract content
                    content_elems = article_soup.select(self.selectors.get('content', 'p'))
                    content = ' '.join([self.clean_text(p.get_text()) for p in content_elems if len(p.get_text()) > 30])
                    
                    # Extract date
                    published_date = None
                    date_elem = article_soup.select_one(self.selectors.get('date', 'time'))
                    if date_elem:
                        date_str = date_elem.get('datetime') or date_elem.get_text()
                        try:
                            published_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        except:
                            pass
                    
                    if content:
                        contents.append(SourcedContentModel(
                            title=title,
                            content=content[:5000],
                            url=url,
                            published_date=published_date,
                            retrieved_at=datetime.utcnow(),
                            metadata={
                                'source': self.name,
                                'scraper_type': 'generic_web'
                            }
                        ))
            
            except Exception as e:
                print(f"Error scraping item: {e}")
                continue
        
        await self.close()
        return contents
