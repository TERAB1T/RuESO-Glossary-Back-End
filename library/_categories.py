import math
import aiosqlite
from .constants import DB_PATH, TABLE_NAME_BOOKS, TABLE_NAME_CATEGORIES
from utils import escape_query

class Categories:
    def __init__(self):
        pass

    async def get_categories(self):
        async with aiosqlite.connect(DB_PATH) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.cursor()

            await cursor.execute(f"SELECT id, titleEn, titleRu, icon, slug FROM {TABLE_NAME_CATEGORIES} ORDER BY titleRu ASC")
            categories = await cursor.fetchall()

            return [dict(category) for category in categories]
        
    async def get_category(self, category_id: int, page: int, page_size: int, filter: str = None):
        offset: int = (page - 1) * page_size

        async with aiosqlite.connect(DB_PATH) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.cursor()

            await cursor.execute(f'''
                SELECT *
                FROM {TABLE_NAME_CATEGORIES}
                WHERE id = ?
            ''', (category_id,))
            category = await cursor.fetchone()

            if not category:
                return {}
            
            category = dict(category)
            
            if filter and len(filter) > 2:
                filter = escape_query(filter)

                await cursor.execute(f'''
                    SELECT b.id, b.titleEn, b.titleRu, b.icon, b.slug
                    FROM {TABLE_NAME_BOOKS} b
                    JOIN books_fts ON books_fts.id = b.id
                    WHERE books_fts MATCH ? AND catId = ?
                    ORDER BY orderId ASC
                    LIMIT ? OFFSET ?
                ''', (filter, category_id, page_size, offset))
                
                books = await cursor.fetchall()

                await cursor.execute(f'''
                    SELECT COUNT(*) AS count
                    FROM books_fts
                    JOIN {TABLE_NAME_BOOKS} b ON books_fts.id = b.id
                    WHERE books_fts MATCH ? AND catId = ?
                ''', (filter, category_id))
                total_books = (await cursor.fetchone())[0]

            else:
                await cursor.execute(f'''
                    SELECT id, titleEn, titleRu, icon, slug
                    FROM {TABLE_NAME_BOOKS}
                    WHERE catId = ?
                    ORDER BY orderId ASC
                    LIMIT ? OFFSET ?
                ''', (category_id, page_size, offset))
                
                books = await cursor.fetchall()

                await cursor.execute(f'''
                    SELECT COUNT(*)
                    FROM {TABLE_NAME_BOOKS}
                    WHERE catId = ?
                ''', (category_id,))
                total_books = (await cursor.fetchone())[0]

            
            category["books"] = [dict(book) for book in books]
            category["pagination"] = {
                    "page": page,
                    "page_size": page_size,
                    "total_books": total_books,
                    "total_pages": math.ceil(total_books / page_size)
                }

            return category