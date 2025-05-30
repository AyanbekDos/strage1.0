import asyncpg
import asyncio
from typing import List, Dict, Any, Optional
import uuid
from app.config import Config

class DatabaseManager:
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        self.pool = await asyncpg.create_pool(Config.DATABASE_URL)
    
    async def close(self):
        if self.pool:
            await self.pool.close()
    
    async def create_dataset(self, name: str, description: str = None, 
                           domainname: str = None, metatag1name: str = None, 
                           metatag2name: str = None, chunksize: int = 500, 
                           chunkoverlap: int = 50) -> str:
        async with self.pool.acquire() as conn:
            dataset_id = await conn.fetchval("""
                INSERT INTO smart_datasets (name, description, domainname, 
                                          metatag1name, metatag2name, chunksize, chunkoverlap)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
            """, name, description, domainname, metatag1name, metatag2name, chunksize, chunkoverlap)
            return str(dataset_id)
    
    async def add_page(self, dataset_id: str, url: str, title: str = None, 
                      rawhtml: str = None, cleantext: str = None, 
                      wordcount: int = None) -> str:
        async with self.pool.acquire() as conn:
            page_id = await conn.fetchval("""
                INSERT INTO smart_pages (datasetid, url, title, rawhtml, cleantext, wordcount)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            """, uuid.UUID(dataset_id), url, title, rawhtml, cleantext, wordcount)
            return str(page_id)
    
    async def add_chunk(self, page_id: str, text: str, summary: str = None,
                       contextretrieval: str = None, domainmeta1: str = None,
                       domainmeta2: str = None, embedding: List[float] = None,
                       tokencount: int = None) -> str:
        async with self.pool.acquire() as conn:
            chunk_id = await conn.fetchval("""
                INSERT INTO smart_chunks (pageid, text, summary, contextretrieval,
                                        domainmeta1, domainmeta2, embedding, tokencount)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
            """, uuid.UUID(page_id), text, summary, contextretrieval, 
                domainmeta1, domainmeta2, embedding, tokencount)
            return str(chunk_id)
    
    async def search_similar_chunks(self, query_embedding: List[float], 
                                  dataset_id: str = None, limit: int = 10) -> List[Dict]:
        async with self.pool.acquire() as conn:
            if dataset_id:
                results = await conn.fetch("""
                    SELECT c.id, c.text, c.summary, c.contextretrieval,
                           c.domainmeta1, c.domainmeta2, p.url, p.title,
                           1 - (c.embedding <=> $1) as similarity
                    FROM smart_chunks c
                    JOIN smart_pages p ON c.pageid = p.id
                    WHERE p.datasetid = $2
                    ORDER BY c.embedding <=> $1
                    LIMIT $3
                """, query_embedding, uuid.UUID(dataset_id), limit)
            else:
                results = await conn.fetch("""
                    SELECT c.id, c.text, c.summary, c.contextretrieval,
                           c.domainmeta1, c.domainmeta2, p.url, p.title,
                           1 - (c.embedding <=> $1) as similarity
                    FROM smart_chunks c
                    JOIN smart_pages p ON c.pageid = p.id
                    ORDER BY c.embedding <=> $1
                    LIMIT $2
                """, query_embedding, limit)
            
            return [dict(row) for row in results]
    
    async def get_dataset_info(self, dataset_id: str) -> Dict:
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow("""
                SELECT * FROM smart_datasets WHERE id = $1
            """, uuid.UUID(dataset_id))
            return dict(result) if result else None
    
    async def update_page_status(self, page_id: str, status: str, error_message: str = None):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE smart_pages SET status = $1, errormessage = $2 WHERE id = $3
            """, status, error_message, uuid.UUID(page_id))
