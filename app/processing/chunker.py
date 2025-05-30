from semantic_text_splitter import TextSplitter
import tiktoken
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class TextChunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding("cl100k_base")
        
    def chunk_text(self, text: str) -> List[Dict[str, any]]:
        if not text or not text.strip():
            return []
        
        try:
            # Create text splitter
            splitter = TextSplitter.from_tiktoken_model(
                "gpt-3.5-turbo",
                capacity=self.chunk_size,
                overlap=self.chunk_overlap
            )
            
            # Split text into chunks
            chunks = splitter.chunks(text)
            
            result = []
            for i, chunk in enumerate(chunks):
                token_count = len(self.encoding.encode(chunk))
                result.append({
                    "text": chunk,
                    "tokencount": token_count,
                    "chunk_index": i
                })
            
            logger.info(f"Created {len(result)} chunks from text of {len(text)} characters")
            return result
            
        except Exception as e:
            logger.error(f"Error chunking text: {str(e)}")
            return []
    
    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))
