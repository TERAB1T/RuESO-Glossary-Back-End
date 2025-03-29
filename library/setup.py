import time
import os
import asyncio
import polars as pl
import aiosqlite
from constants import DB_PATH, TABLE_NAME_BOOKS, TABLE_NAME_CATEGORIES, TABLE_NAME_PATCHES

async def create_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    creation_query = f'''
    CREATE TABLE {TABLE_NAME_CATEGORIES} (
        id INTEGER PRIMARY KEY,
        titleEn TEXT,
        titleRu TEXT,
        descEn TEXT,
        descRu TEXT,
        icon TEXT,
        slug TEXT
    ) WITHOUT ROWID;

    CREATE TABLE {TABLE_NAME_PATCHES} (
        id INTEGER PRIMARY KEY,
        version TEXT,
        nameEn TEXT,
        nameRu TEXT,
        image TEXT,
        date TEXT,
        slug TEXT
    ) WITHOUT ROWID;

    CREATE INDEX idx_patches_version ON {TABLE_NAME_PATCHES} (version);

    CREATE TABLE {TABLE_NAME_BOOKS} (
        id INTEGER NOT NULL,
        titleEn TEXT,
        titleRu TEXT,
        textEn TEXT,
        textRu TEXT,
        icon TEXT,
        catId INTEGER NOT NULL,
        slug TEXT,
        created TEXT,
        updated TEXT,
        orderId INTEGER NOT NULL PRIMARY KEY,
        FOREIGN KEY (catId) REFERENCES {TABLE_NAME_CATEGORIES} (id)
    ) WITHOUT ROWID;

    CREATE INDEX idx_books_id ON {TABLE_NAME_BOOKS} (id);
    CREATE INDEX idx_books_catId_order ON {TABLE_NAME_BOOKS} (catId, orderId);
    '''

    async with aiosqlite.connect(DB_PATH) as conn:
        # await conn.execute("PRAGMA foreign_keys = ON;")
        await conn.executescript(creation_query)
        await conn.commit()

async def populate_db():
    categories_csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/categories.csv')
    categories_csv = pl.read_csv(categories_csv_path, separator=',').rows()

    patches_csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/patches.csv')
    patches_csv = pl.read_csv(patches_csv_path, separator=',').rows()
    
    books_csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/books.csv')
    books_csv = pl.read_csv(books_csv_path, separator=',').rows()

    async with aiosqlite.connect(DB_PATH) as conn:
        # await conn.execute("PRAGMA foreign_keys = ON;")
        
        print('Inserting new categories...')
        start_time = time.time()

        await conn.executemany(
            f'''INSERT INTO {TABLE_NAME_CATEGORIES} (id, titleEn, titleRu, descEn, descRu, icon, slug)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            categories_csv
        )

        execution_time = time.time() - start_time
        print(f"Categories inserted: {execution_time:.6f} seconds")


        print('Inserting new patches...')
        start_time = time.time()

        await conn.executemany(
            f'''INSERT INTO {TABLE_NAME_PATCHES} (id, version, nameEn, nameRu, image, date, slug)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            patches_csv
        )

        execution_time = time.time() - start_time
        print(f"Patches inserted: {execution_time:.6f} seconds")


        print('Inserting new books...')
        start_time = time.time()

        await conn.executemany(
            f'''INSERT INTO {TABLE_NAME_BOOKS} (id, titleEn, titleRu, textEn, textRu, icon, catId, slug, created, updated, orderId)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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