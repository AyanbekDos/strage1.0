# Strage - RAG System

Система для парсинга веб-страниц, создания эмбеддингов и семантического поиска.

## Установка

1. Клонируйте репозиторий
2. Установите зависимости: `pip install -r requirements.txt`
3. Скопируйте `.env.example` в `.env` и заполните переменные
4. Создайте датасет: `python scripts/create_dataset.py`
5. Обработайте URL: `python scripts/process_urls.py`
6. Выполните поиск: `python scripts/search.py`

## Структура базы данных

- `smart_datasets` - датасеты
- `smart_pages` - страницы
- `smart_chunks` - чанки с эмбеддингами
