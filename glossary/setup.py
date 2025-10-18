import time
import os
import asyncio
import polars as pl
import aiosqlite
import argparse
from constants import (
    TABLE_NAME,
    TES_DB_PATH,
    TES_VALID_GAMES,
    FALLOUT_DB_PATH,
    FALLOUT_VALID_GAMES,
)

async def create_db(db_path: str):
    if os.path.exists(db_path):
        os.remove(db_path)

    async with aiosqlite.connect(db_path) as conn:
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

async def add_game(game: str, db_path: str):
    async with aiosqlite.connect(db_path) as conn:
        data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'data/{game.replace(" ", "")}.csv')
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

async def main(db_path: str, valid_games: list[str]):
    await create_db(db_path)

    for game in valid_games:
        await add_game(game, db_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create and populate FTS database for TES or Fallout strings.")
    parser.add_argument(
        "-t", "--type",
        choices=["tes", "fallout"],
        required=True,
        help="Specify which database to build: 'tes' or 'fallout'."
    )
    args = parser.parse_args()

    if args.type == "tes":
        db_path = TES_DB_PATH
        valid_games = TES_VALID_GAMES
    else:
        db_path = FALLOUT_DB_PATH
        valid_games = FALLOUT_VALID_GAMES

    asyncio.run(main(db_path, valid_games))
