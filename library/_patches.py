import math
import aiosqlite
from .constants import DB_PATH, TABLE_NAME_BOOKS, TABLE_NAME_PATCHES
from utils import escape_query

class Patches:
    def __init__(self):
        pass

    async def get_patches(self):
        async with aiosqlite.connect(DB_PATH) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.cursor()

            await cursor.execute(f"SELECT version, nameEn, nameRu, slug FROM {TABLE_NAME_PATCHES} ORDER BY id DESC")
            patches = await cursor.fetchall()

            return [dict(patch) for patch in patches]
        
    async def get_patch(self, patch_version: str, page: int, page_size: int, filter: str = None):
        offset: int = (page - 1) * page_size

        async with aiosqlite.connect(DB_PATH) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.cursor()

            await cursor.execute(f'''
                SELECT *
                FROM {TABLE_NAME_PATCHES}
                WHERE version = ?
            ''', (patch_version,))
            patch = await cursor.fetchone()

            if not patch:
                return {}
            
            patch = dict(patch)
            
            if filter and len(filter) > 2:
                filter = escape_query(filter)

                await cursor.execute(f'''
                    SELECT b.id, b.titleEn, b.titleRu, b.icon, b.slug
                    FROM {TABLE_NAME_BOOKS} b
                    JOIN books_fts ON books_fts.id = b.id
                    WHERE books_fts MATCH ? AND created = ?
                    ORDER BY orderId ASC
                    LIMIT ? OFFSET ?
                ''', (filter, patch_version, page_size, offset))
                
                books = await cursor.fetchall()

                await cursor.execute(f'''
                    SELECT COUNT(*) AS count
                    FROM books_fts
                    JOIN {TABLE_NAME_BOOKS} b ON books_fts.id = b.id
                    WHERE books_fts MATCH ? AND created = ?
                ''', (filter, patch_version))
                total_books = (await cursor.fetchone())[0]
            else:
                await cursor.execute(f'''
                    SELECT id, titleEn, titleRu, icon, slug
                    FROM {TABLE_NAME_BOOKS}
                    WHERE created = ?
                    ORDER BY orderId ASC
                    LIMIT ? OFFSET ?
                ''', (patch_version, page_size, offset))
                
                books = await cursor.fetchall()

                await cursor.execute(f'''
                    SELECT COUNT(*)
                    FROM {TABLE_NAME_BOOKS}
                    WHERE created = ?
                ''', (patch_version,))
                total_books = (await cursor.fetchone())[0]

            
            patch["books"] = [dict(book) for book in books]
            patch["pagination"] = {
                    "page": page,
                    "page_size": page_size,
                    "total_books": total_books,
                    "total_pages": math.ceil(total_books / page_size)
                }

            return patch