import math
import aiosqlite
from .constants import DB_PATH, TABLE_NAME_BOOKS, TABLE_NAME_CATEGORIES

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
        
    async def get_category(self, category_id: int, page: int, page_size: int):
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
            
            await cursor.execute(f'''
                                 SELECT id, titleEn, titleRu, icon, slug
                                 FROM {TABLE_NAME_BOOKS}
                                 WHERE catId = ?
                                 ORDER BY titleRu ASC
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