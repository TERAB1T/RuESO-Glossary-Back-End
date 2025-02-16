import math
import aiosqlite
from .constants import DB_PATH, TABLE_NAME_BOOKS, TABLE_NAME_CATEGORIES

class Books:
    def __init__(self):
        pass

    async def get_books(self, page: int, page_size: int):
        offset: int = (page - 1) * page_size
        
        async with aiosqlite.connect(DB_PATH) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.cursor()

            await cursor.execute(f"SELECT id, titleEn, titleRu, icon, slug FROM {TABLE_NAME_BOOKS} ORDER BY titleRu ASC LIMIT ? OFFSET ?", (page_size, offset))
            books = await cursor.fetchall()
            books = [dict(book) for book in books]

            await cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME_BOOKS}")
            total_books = (await cursor.fetchone())[0]

            return {
                "books": books,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_books": total_books,
                    "total_pages": math.ceil(total_books / page_size)
                }
            }
        
    async def get_books_with_ids(self, ids: list[int]):
        async with aiosqlite.connect(DB_PATH) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.cursor()

            await cursor.execute(f"SELECT id, titleEn, titleRu, icon, slug FROM {TABLE_NAME_BOOKS} WHERE id IN ({','.join(['?'] * len(ids))}) ORDER BY titleRu ASC", ids)
            books = await cursor.fetchall()
            
            return [dict(book) for book in books]
        
    async def get_book(self, book_id: int):
        async with aiosqlite.connect(DB_PATH) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.cursor()

            await cursor.execute(f"SELECT * FROM {TABLE_NAME_BOOKS} WHERE id = ?", (book_id,))
            book = await cursor.fetchone()

            if not book:
                return {}
            
            book = dict(book)

            await cursor.execute(f"SELECT id, titleEn, titleRu, icon, slug FROM {TABLE_NAME_CATEGORIES} WHERE id = ?", (book["catId"],))
            category = await cursor.fetchone()

            book["category"] = dict(category) if category else {}
            return book