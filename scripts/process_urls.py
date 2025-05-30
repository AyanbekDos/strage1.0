import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import DatabaseManager
from app.processing.scraper import WebScraper
from app.processing.chunker import TextChunker
from app.processing.embedder import EmbeddingGenerator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_urls():
    dataset_id = input("Введите ID датасета: ")
    urls_input = input("Введите URL-адреса через запятую: ")
    urls = [url.strip() for url in urls_input.split(',')]
    
    db = DatabaseManager()
    await db.connect()
    
    try:
        # Get dataset info
        dataset_info = await db.get_dataset_info(dataset_id)
        if not dataset_info:
            print("Датасет не найден!")
            return
        
        print(f"Обрабатываем датасет: {dataset_info['name']}")
        
        # Initialize processors
        scraper = WebScraper()
        chunker = TextChunker(
            chunk_size=dataset_info['chunksize'],
            chunk_overlap=dataset_info['chunkoverlap']
        )
        embedder = EmbeddingGenerator()
        
        for url in urls:
            logger.info(f"Обрабатываем URL: {url}")
            
            # Scrape content
            content = await scraper.scrape_url(url)
            
            if content.get('error'):
                logger.error(f"Ошибка при парсинге {url}: {content['error']}")
                continue
            
            # Add page to database
            page_id = await db.add_page(
                dataset_id=dataset_id,
                url=url,
                title=content.get('title'),
                rawhtml=content.get('rawhtml'),
                cleantext=content.get('cleantext'),
                wordcount=content.get('wordcount')
            )
            
            # Chunk text
            if content.get('cleantext'):
                chunks = chunker.chunk_text(content['cleantext'])
                
                for chunk_data in chunks:
                    # Generate embedding
                    embedding = await embedder.generate_embedding(chunk_data['text'])
                    
                    # Generate summary and context
                    summary = await embedder.generate_summary(chunk_data['text'])
                    context = await embedder.generate_context_retrieval(chunk_data['text'])
                    
                    # Add chunk to database
                    chunk_id = await db.add_chunk(
                        page_id=page_id,
                        text=chunk_data['text'],
                        summary=summary,
                        contextretrieval=context,
                        embedding=embedding,
                        tokencount=chunk_data['tokencount']
                    )
                    
                    logger.info(f"Создан чанк {chunk_id}")
                
                # Update page status
                await db.update_page_status(page_id, 'processed')
                logger.info(f"Страница {url} обработана успешно")
            
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(process_urls())
