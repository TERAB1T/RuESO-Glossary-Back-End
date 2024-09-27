import re
import time
import aiosqlite
from constants import DB_PATH, TABLE_NAME

def escape_query(query):
    escaped_query = query.replace('"', '""')
    return f'"{escaped_query}"'

async def build_query(term, filters, game, is_count_query=False):
    base_query = f"SELECT * FROM {TABLE_NAME}" if not is_count_query else f"SELECT COUNT(*) FROM {TABLE_NAME}"
    query_conditions = []
    params = []

    if re.search(r'[а-яА-Я]', term):
        query_conditions.append("ru MATCH ?")
        params.append(escape_query(term))
    else:
        query_conditions.append(f"{TABLE_NAME} MATCH ?")
        params.extend([f'en:{escape_query(term)} OR ru:{escape_query(term)}'])

    if filters[0]:
        query_conditions.append("game MATCH ?")
        params.append(escape_query(filters[0]))

    if filters[1]:
        query_conditions.append("en MATCH ?")
        params.append(escape_query(filters[1]))

    if filters[2]:
        query_conditions.append("ru MATCH ?")
        params.append(escape_query(filters[2]))

    if game:
        query_conditions.append("game = ?")
        params.append(game)

    if query_conditions:
        base_query += " WHERE " + " AND ".join(query_conditions)

    return f"{base_query} ", params

async def search_term(term, start=0, length=10, order_column="en", order_dir="ASC", game=None, filters=None):
    if filters is None:
        filters = [None, None, None]

    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.cursor()

        query, params = await build_query(term, filters, game)
        query += f" ORDER BY {order_column} {order_dir} LIMIT ? OFFSET ?"
        params.extend([length, start])

        start_time = time.time()
        await cursor.execute(query, params)
        results = await cursor.fetchall()
        execution_time = time.time() - start_time
        print(f"Execution time: {execution_time:.6f} seconds")

        count_query, count_params = await build_query(term, filters, game, is_count_query=True)
        await cursor.execute(count_query, count_params)
        total_records = await cursor.fetchone()
        total_records = total_records[0] if total_records else 0

        return {
            "data": [
                {"en": res[1], "game": res[0], "ru": res[2]} for res in results
            ],
            "recordsFiltered": total_records,
            "recordsTotal": total_records
        }
