import time
import os
import asyncio
import polars as pl
import aiosqlite
from constants import TABLE_NAME, DB_PATH, VALID_GAMES

async def create_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    async with aiosqlite.connect(DB_PATH) as conn:
        print('Creating table...')
        start_time = time.time()

        await conn.execute(f'''
            CREATE VIRTUAL TABLE {TABLE_NAME} USING fts5(
                game,
                en,
                ru,
                type,
                tag,
                tokenize="trigram"
            )
        ''')

        execution_time = time.time() - start_time
        print(f"Table created: {execution_time:.6f} seconds")

async def add_game(game: str):
    async with aiosqlite.connect(DB_PATH) as conn:
        data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'data/{game}.csv')
        data = pl.read_csv(data_path, separator=',').rows()
        
        print(f'Inserting new data for {game}...')
        start_time = time.time()

        await conn.executemany(
            f'''INSERT INTO {TABLE_NAME} (game, en, ru, type, tag)
            VALUES (?, ?, ?, ?, ?)''',
            data
        )

        execution_time = time.time() - start_time
        print(f"Data for {game} inserted: {execution_time:.6f} seconds")

        await conn.commit()

async def main():
    await create_db()

    for game in VALID_GAMES:
        await add_game(game)

if __name__ == "__main__":
    asyncio.run(main())
