import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import DatabaseManager

async def create_dataset():
    db = DatabaseManager()
    await db.connect()
    
    try:
        name = input("Введите название датасета: ")
        description = input("Введите описание (опционально): ") or None
        domainname = input("Введите домен (опционально): ") or None
        metatag1name = input("Введите название мета-тега 1 (опционально): ") or None
        metatag2name = input("Введите название мета-тега 2 (опционально): ") or None
        
        chunksize = input("Размер чанка (по умолчанию 500): ")
        chunksize = int(chunksize) if chunksize else 500
        
        chunkoverlap = input("Перекрытие чанков (по умолчанию 50): ")
        chunkoverlap = int(chunkoverlap) if chunkoverlap else 50
        
        dataset_id = await db.create_dataset(
            name=name,
            description=description,
            domainname=domainname,
            metatag1name=metatag1name,
            metatag2name=metatag2name,
            chunksize=chunksize,
            chunkoverlap=chunkoverlap
        )
        
        print(f"Датасет создан с ID: {dataset_id}")
        
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(create_dataset())
