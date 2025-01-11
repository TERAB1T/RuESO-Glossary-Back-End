from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from db.db_search import search_term
from utils import validate_games
import time

app = FastAPI(docs_url=None, redoc_url=None)

origins = [
    "http://rueso.ru",
    "https://rueso.ru",
    "http://127.0.0.1",
    "http://127.0.0.1:5500",
]

@app.middleware("http")
async def log_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Request took {process_time:.4f} seconds")
    return response

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
    column_3_filter = params.get("columns[3][search][value]")

    order_column = None
    if order_column_index is not None and order_column_index.isnumeric() and order_dir in ["ASC", "DESC"]:
        columns = ["game", "type", "en", "ru"]
        order_column = columns[int(order_column_index)]

    result = await search_term(
        search_value, start=start, length=length, order_column=order_column, order_dir=order_dir, games=validate_games(games), filters=[column_0_filter, column_1_filter, column_2_filter, column_3_filter]
    )

    return {
        "draw": draw,
        "recordsTotal": result["recordsTotal"],
        "recordsFiltered": result["recordsFiltered"],
        "data": result["data"]
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)