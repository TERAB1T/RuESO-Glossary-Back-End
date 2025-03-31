import math
import aiosqlite
from .constants import DB_PATH, TABLE_NAME_BOOKS, TABLE_NAME_CATEGORIES, TABLE_NAME_PATCHES
from utils import escape_query

class Books:
    def __init__(self):
        pass

    async def get_books(self, page: int, page_size: int, filter: str = None):
        offset: int = (page - 1) * page_size
        
        async with aiosqlite.connect(DB_PATH) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.cursor()

            if filter and len(filter) > 2:
                filter = escape_query(filter)
                
                await cursor.execute(f'''
                    SELECT b.id, b.titleEn, b.titleRu, b.icon, b.slug
                    FROM {TABLE_NAME_BOOKS} b
                    JOIN books_fts ON books_fts.id = b.id
                    WHERE books_fts MATCH ? AND catId != 2000
                    ORDER BY orderId ASC
                    LIMIT ? OFFSET ?
                ''', (filter, page_size, offset))
                books = await cursor.fetchall()
                books = [dict(book) for book in books]

                await cursor.execute(f'''
                    SELECT COUNT(*) AS count
                    FROM books_fts
                    JOIN {TABLE_NAME_BOOKS} b ON books_fts.id = b.id
                    WHERE books_fts MATCH ? AND catId != 2000
                ''', (filter,))
                total_books = (await cursor.fetchone())[0]
            else:
                await cursor.execute(f'''
                    SELECT id, titleEn, titleRu, icon, slug
                    FROM {TABLE_NAME_BOOKS}
                    WHERE catId != 2000
                    ORDER BY orderId ASC
                    LIMIT ? OFFSET ?
                ''', (page_size, offset))
                books = await cursor.fetchall()
                books = [dict(book) for book in books]

                await cursor.execute(f'''
                    SELECT COUNT(*) AS count
                    FROM {TABLE_NAME_BOOKS}
                    WHERE catId != 2000
                ''')
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

            await cursor.execute(f"SELECT id, titleEn, titleRu, icon, slug FROM {TABLE_NAME_BOOKS} WHERE id IN ({','.join(['?'] * len(ids))}) ORDER BY orderId ASC", ids)
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


            isSameVersion = book["created"] == book["updated"]


            await cursor.execute(f"SELECT id, titleEn, titleRu, icon, slug FROM {TABLE_NAME_CATEGORIES} WHERE id = ?", (book["catId"],))
            category = await cursor.fetchone()

            book["category"] = dict(category) if category else {}


            await cursor.execute(f"SELECT version, nameEn, nameRu, date, slug FROM {TABLE_NAME_PATCHES} WHERE version = ?", (book["created"],))
            created = await cursor.fetchone()

            book["created"] = dict(created) if created else {}


            if isSameVersion:
                book["updated"] = book["created"]
                return book
            

            await cursor.execute(f"SELECT version, nameEn, nameRu, date, slug FROM {TABLE_NAME_PATCHES} WHERE version = ?", (book["updated"],))
            updated = await cursor.fetchone()

            book["updated"] = dict(updated) if updated else {}


            return book