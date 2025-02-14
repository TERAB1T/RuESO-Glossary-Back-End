import re
import time
import aiosqlite
from .constants import COLUMNS, VALID_GAMES, DB_PATH, TABLE_NAME
from utils import prepare_html

class GlossarySearch:
    def __init__(self, params):
        self.draw = params.get("draw", "1")
        self.start = int(params.get("start", 0))
        self.length = int(params.get("length", 10))
        self.search_value = params.get("search[value]", "")
        self.games = self.__validate_games(params.get("games", '').split(","))
        self.filters = [
            params.get(f"columns[{index}][search][value]")
            for index in range(len(COLUMNS))
        ]

        self.order_dir = params.get("order[0][dir]", "asc").upper()
        self.order_column = None
        self.order_column_index = params.get("order[0][column]")
        if (
            self.order_column_index is not None
            and self.order_column_index.isnumeric()
            and self.order_dir in ["ASC", "DESC"]
        ):
            self.order_column = COLUMNS[int(self.order_column_index)]

    def __validate_games(self, games: list) -> list:
        return set(games).intersection(VALID_GAMES)
    
    def __escape_query(self, query: str) -> str:
        escaped_query = query.replace('"', '""').replace(' ', ' ')
        escaped_query = re.sub(r'[‘’]', '\'', escaped_query)
        escaped_query = re.sub(r'[“”„]', '""', escaped_query)
        return f'"{escaped_query}"'

    async def search_term(self) -> dict[str, int | list[dict[str, str]]]:
        async with aiosqlite.connect(DB_PATH) as conn:
            cursor = await conn.cursor()

            query, params = await self.__build_query()

            if self.order_column:
                query += f" ORDER BY {self.order_column} {self.order_dir}"

            query += " LIMIT ? OFFSET ?"
            params.extend([self.length, self.start])

            start_time = time.time()
            await cursor.execute(query, params)
            results = await cursor.fetchall()
            
            execution_time = time.time() - start_time
            print(f"Fetching data: {execution_time:.6f} seconds")

            start_time = time.time()

            count_query, count_params = await self.__build_query(True)
            await cursor.execute(count_query, count_params)
            total_records = await cursor.fetchone()
            total_records = total_records[0] if total_records else 0
            
            execution_time = time.time() - start_time
            print(f"Fetching total records: {execution_time:.6f} seconds")

            return {
                "draw": self.draw,
                "recordsTotal": total_records,
                "recordsFiltered": total_records,
                "data": [
                    {
                        "game": res[0],
                        "en": prepare_html(res[1]),
                        "ru": prepare_html(res[2]),
                        "type": res[3],
                        "tag": res[4]
                    } for res in results
                ]
            }

    async def __build_query(self, is_count_query=False) -> tuple[str, list[str]]:
        base_query = f"SELECT * FROM {TABLE_NAME}" if not is_count_query else f"SELECT COUNT(*) FROM {TABLE_NAME}"
        query_conditions: list[str] = []
        params: list[str] = []

        if re.search(r'[а-яА-Я]', self.search_value):
            query_conditions.append("ru MATCH ?")
            params.append(self.__escape_query(self.search_value))
        else:
            query_conditions.append(f"{TABLE_NAME} MATCH ?")
            params.append(f'en:{self.__escape_query(self.search_value)} OR ru:{self.__escape_query(self.search_value)}')

        if self.filters[1]:
            query_conditions.append("type MATCH ?")
            params.append(self.__escape_query(self.filters[1]))

        if self.filters[2]:
            query_conditions.append("en MATCH ?")
            params.append(self.__escape_query(self.filters[2]))

        if self.filters[3]:
            query_conditions.append("ru MATCH ?")
            params.append(self.__escape_query(self.filters[3]))

        if self.games:
            query_conditions.append(f"{TABLE_NAME} MATCH ?")
            params.append(" OR ".join([f"game:^{game}" for game in self.games]))

        if query_conditions:
            base_query += " WHERE " + " AND ".join(query_conditions)

        return f"{base_query} ", params
