from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn
from db.db_search import search_term
from utils import prepare_html, validate_games

app = FastAPI(docs_url=None, redoc_url=None)

origins = [
    "http://rueso.ru",
    "https://rueso.ru",
    "http://127.0.0.1",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

@app.get("/search/")
async def search(request: Request):
    params = request.query_params
    draw = params.get("draw", "1")
    start = int(params.get("start", 0))
    length = int(params.get("length", 10))
    search_value = params.get("search[value]", "")
    order_column_index = params.get("order[0][column]")
    order_dir = params.get("order[0][dir]", "asc").upper()
    games = []

    if params.get("games"):
        games = params.get("games").split(",")

    column_0_filter = params.get("columns[0][search][value]")
    column_1_filter = params.get("columns[1][search][value]")
    column_2_filter = params.get("columns[2][search][value]")

    order_column = None
    if order_column_index is not None and order_column_index.isnumeric() and order_dir in ["ASC", "DESC"]:
        columns = ["game", "en", "ru"]
        order_column = columns[int(order_column_index)]

    result = await search_term(
        search_value, start=start, length=length, order_column=order_column, order_dir=order_dir, games=validate_games(games), filters=[column_0_filter, column_1_filter, column_2_filter]
    )

    return {
        "draw": draw,
        "recordsTotal": result["recordsTotal"],
        "recordsFiltered": result["recordsFiltered"],
        "data": [
            [row["game"], prepare_html(row["en"]), prepare_html(row["ru"])]
            for row in result["data"]
        ]
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)