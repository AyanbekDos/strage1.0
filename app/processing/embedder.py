import openai
import asyncio
from typing import List, Dict
import logging
from app.config import Config

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.EMBEDDING_MODEL
        self.semaphore = asyncio.Semaphore(10)  # Limit concurrent requests
    
    async def generate_embedding(self, text: str) -> List[float]:
        async with self.semaphore:
            try:
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=text
                )
                return response.data[0].embedding
            except Exception as e:
                logger.error(f"Error generating embedding: {str(e)}")
                return None
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        tasks = [self.generate_embedding(text) for text in texts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        embeddings = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error generating embedding for text {i}: {str(result)}")
                embeddings.append(None)
            else:
                embeddings.append(result)
        
        return embeddings
    
    async def generate_summary(self, text: str, max_length: int = 150) -> str:
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Создай краткое резюме текста на русском языке."},
                    {"role": "user", "content": f"Текст: {text}"}
                ],
                max_tokens=max_length,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return None
    
    async def generate_context_retrieval(self, text: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Создай контекстное описание для поиска по этому тексту. Включи ключевые слова и темы."},
                    {"role": "user", "content": f"Текст: {text}"}
                ],
                max_tokens=100,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating context retrieval: {str(e)}")
            return None
