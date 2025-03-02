import time
import os
import asyncio
import polars as pl
import aiosqlite
from constants import DB_PATH, TABLE_NAME_BOOKS, TABLE_NAME_CATEGORIES

async def create_db():
    creation_query = f'''
    CREATE TABLE IF NOT EXISTS {TABLE_NAME_CATEGORIES} (
        id INTEGER PRIMARY KEY,
        titleEn TEXT NOT NULL,
        titleRu TEXT,
        descEn TEXT,
        descRu TEXT,
        icon TEXT,
        slug TEXT UNIQUE NOT NULL
    ) WITHOUT ROWID;

    CREATE TABLE IF NOT EXISTS {TABLE_NAME_BOOKS} (
        id INTEGER PRIMARY KEY,
        titleEn TEXT NOT NULL,
        titleRu TEXT,
        textEn TEXT,
        textRu TEXT,
        icon TEXT NOT NULL,
        catId INTEGER NOT NULL,
        slug TEXT NOT NULL,
        orderId INTEGER NOT NULL,
        FOREIGN KEY (catId) REFERENCES {TABLE_NAME_CATEGORIES} (id)
    ) WITHOUT ROWID;

    CREATE INDEX IF NOT EXISTS idx_categories_id ON {TABLE_NAME_CATEGORIES} (id);
    CREATE INDEX IF NOT EXISTS idx_books_id ON {TABLE_NAME_BOOKS} (id);
    CREATE INDEX IF NOT EXISTS idx_books_catId ON {TABLE_NAME_BOOKS} (catId);
    CREATE INDEX IF NOT EXISTS idx_books_orderId ON {TABLE_NAME_BOOKS} (orderId);
    '''

    async with aiosqlite.connect(DB_PATH) as conn:
        # await conn.execute("PRAGMA foreign_keys = ON;")
        await conn.executescript(creation_query)
        await conn.commit()

async def populate_db():
    categories_csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/categories.csv')
    categories_csv = pl.read_csv(categories_csv_path, separator=',').rows()
    
    books_csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/books.csv')
    books_csv = pl.read_csv(books_csv_path, separator=',').rows()

    async with aiosqlite.connect(DB_PATH) as conn:
        # await conn.execute("PRAGMA foreign_keys = ON;")
        
        print('Inserting new categories...')
        start_time = time.time()

        await conn.executemany(
            f'''INSERT INTO {TABLE_NAME_CATEGORIES} (id, titleEn, titleRu, descEn, descRu, icon, slug)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    titleEn=excluded.titleEn,
                    titleRu=excluded.titleRu,
                    descEn=excluded.descEn,
                    descRu=excluded.descRu,
                    icon=excluded.icon;
            ''',
            categories_csv
        )

        execution_time = time.time() - start_time
        print(f"Categories inserted: {execution_time:.6f} seconds")

        print('Inserting new books...')
        start_time = time.time()

        await conn.executemany(
            f'''INSERT INTO {TABLE_NAME_BOOKS} (id, titleEn, titleRu, textEn, textRu, icon, catId, slug, orderId)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    titleEn=excluded.titleEn,
                    titleRu=excluded.titleRu,
                    textEn=excluded.textEn,
                    textRu=excluded.textRu,
                    icon=excluded.icon,
                    catId=excluded.catId,
                    orderId=excluded.orderId;
            ''',
            books_csv
        )

        execution_time = time.time() - start_time
        print(f"Books inserted: {execution_time:.6f} seconds")

        await conn.commit()

async def main():
    await create_db()
    await populate_db()

if __name__ == "__main__":
    asyncio.run(main())