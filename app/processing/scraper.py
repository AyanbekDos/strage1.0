import aiohttp
import asyncio
from bs4 import BeautifulSoup
import trafilatura
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, timeout: int = 30, max_concurrent: int = 5):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    async def scrape_url(self, url: str) -> Dict[str, Optional[str]]:
        async with self.semaphore:
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            html_content = await response.text()
                            return self._extract_content(html_content, url)
                        else:
                            logger.error(f"Failed to fetch {url}: HTTP {response.status}")
                            return {"error": f"HTTP {response.status}"}
            except Exception as e:
                logger.error(f"Error scraping {url}: {str(e)}")
                return {"error": str(e)}
    
    def _extract_content(self, html: str, url: str) -> Dict[str, Optional[str]]:
        try:
            # Extract clean text using trafilatura
            clean_text = trafilatura.extract(html, include_comments=False, 
                                           include_tables=True, include_links=True)
            
            # Extract title using BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.find('title')
            title_text = title.get_text().strip() if title else None
            
            # Count words
            word_count = len(clean_text.split()) if clean_text else 0
            
            return {
                "title": title_text,
                "rawhtml": html,
                "cleantext": clean_text,
                "wordcount": word_count,
                "error": None
            }
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return {"error": str(e)}
    
    async def scrape_multiple_urls(self, urls: list) -> Dict[str, Dict]:
        tasks = [self.scrape_url(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {url: result for url, result in zip(urls, results)}
