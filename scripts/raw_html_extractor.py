import asyncio
import aiohttp
import trafilatura
from aiohttp import ClientTimeout
from bs4 import BeautifulSoup
import logging
import sys
import json
import uuid
import asyncpg
from datetime import datetime
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("raw_html_extractor")

class RawHTMLExtractor:
    def __init__(self, dataset_id: str):
        self.dataset_id = dataset_id
        self.session = None
        self.db_pool = None
        
    async def __aenter__(self):
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise Exception("DATABASE_URL not found in environment variables")
        self.db_pool = await asyncpg.create_pool(database_url)
        timeout = ClientTimeout(total=30)
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; RawHTMLExtractor/1.0)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive"
        }
        self.session = aiohttp.ClientSession(timeout=timeout, headers=headers)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        if self.db_pool:
            await self.db_pool.close()

    async def fetch_and_save(self, url: str) -> dict:
        logger.info(f"Fetching URL: {url}")
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                html = await response.text()
            
            title = self.extract_title(html)
            word_count = self.count_words(html)
            page_id = await self.save_to_db(url, title, html, word_count)
            logger.info(f"Saved page {page_id} for URL: {url}")
            return {"url": url, "page_id": page_id, "title": title, "word_count": word_count, "status": "success"}
            
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            await self.save_to_db(url, "Error", "", 0, status="error", error_message=str(e))
            return {"url": url, "status": "error", "error": str(e)}

    def extract_title(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        title_tag = soup.find('title')
        if title_tag and title_tag.text.strip():
            return title_tag.text.strip()[:500]
        h1_tag = soup.find('h1')
        if h1_tag and h1_tag.text.strip():
            return h1_tag.text.strip()[:500]
        return "No title"

    def count_words(self, html: str) -> int:
        text = trafilatura.extract(html) or ""
        return len(text.split())

    async def save_to_db(self, url: str, title: str, rawhtml: str, word_count: int, status: str = "pending", error_message: str = None) -> str:
        async with self.db_pool.acquire() as conn:
            page_id = await conn.fetchval("""
                INSERT INTO smart_pages (datasetid, url, title, rawhtml, cleantext, wordcount, status, errormessage, createdat)
                VALUES ($1, $2, $3, $4, '', $5, $6, $7, NOW())
                RETURNING id
            """, uuid.UUID(self.dataset_id), url, title, rawhtml, word_count, status, error_message)
            return str(page_id)

async def main():
    if len(sys.argv) < 2:
        print("Usage: python raw_html_extractor.py <dataset_id> <urls_json>")
        sys.exit(1)
    
    dataset_id = sys.argv[1]
    urls_json = sys.argv[2] if len(sys.argv) > 2 else '[]'
    
    try:
        urls = json.loads(urls_json)
    except Exception:
        urls = [urls_json]
    
    async with RawHTMLExtractor(dataset_id) as extractor:
        results = []
        for url in urls:
            result = await extractor.fetch_and_save(url)
            results.append(result)
        print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
