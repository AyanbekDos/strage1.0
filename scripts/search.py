import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import DatabaseManager
from app.processing.embedder import EmbeddingGenerator

async def search():
    query = input("Введите поисковый запрос: ")
    dataset_id = input("Введите ID датасета (опционально): ") or None
    limit = input("Количество результатов (по умолчанию 10): ")
    limit = int(limit) if limit else 10
    
    db = DatabaseManager()
    embedder = EmbeddingGenerator()
    
    await db.connect()
    
    try:
        # Generate embedding for query
        query_embedding = await embedder.generate_embedding(query)
        
        if not query_embedding:
            print("Ошибка при создании эмбеддинга запроса")
            return
        
        # Search similar chunks
        results = await db.search_similar_chunks(
            query_embedding=query_embedding,
            dataset_id=dataset_id,
            limit=limit
        )
        
        print(f"\nНайдено {len(results)} результатов:\n")
        
        for i, result in enumerate(results, 1):
            print(f"--- Результат {i} (Similarity: {result['similarity']:.4f}) ---")
            print(f"URL: {result['url']}")
            print(f"Заголовок: {result['title']}")
            print(f"Резюме: {result['summary']}")
            print(f"Текст: {result['text'][:200]}...")
            print()
    
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(search())
