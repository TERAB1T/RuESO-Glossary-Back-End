from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
from utils import is_integer, parse_ids

from glossary._search import GlossarySearch
from library._categories import Categories
from library._patches import Patches
from library._books import Books

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
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/glossary")
async def glossary_search(request: Request):
    glossary_search = GlossarySearch(request.query_params)
    return await glossary_search.search_term()


@app.get("/library/categories")
async def api_categories(request: Request):
    categories = Categories()
    return await categories.get_categories()


@app.get("/library/categories/{category_id}")
async def api_category(request: Request):
    categories = Categories()

    category_id = request.path_params["category_id"]
    page = request.query_params.get("page")
    page_size = request.query_params.get("page_size")

    if not is_integer(page):
        page = 1
    if not is_integer(page_size):
        page_size = 50

    if not is_integer(category_id):
        return {}
    else:
        return await categories.get_category(
            int(category_id), int(page), int(page_size)
        )


@app.get("/library/patches")
async def api_patches(request: Request):
    patches = Patches()
    return await patches.get_patches()


@app.get("/library/patches/{patch_version}")
async def api_patch(request: Request):
    patches = Patches()

    patch_version = request.path_params["patch_version"]
    page = request.query_params.get("page")
    page_size = request.query_params.get("page_size")

    if not is_integer(page):
        page = 1
    if not is_integer(page_size):
        page_size = 50

    return await patches.get_patch(
        patch_version, int(page), int(page_size)
    )


@app.get("/library/books")
async def api_books(request: Request):
    books = Books()

    page = request.query_params.get("page")
    page_size = request.query_params.get("page_size")
    ids = parse_ids(request.query_params.get("ids"))

    if not is_integer(page):
        page = 1
    if not is_integer(page_size):
        page_size = 50

    if len(ids):
        return await books.get_books_with_ids(ids)
    else:
        return await books.get_books(int(page), int(page_size))


@app.get("/library/books/{books_id}")
async def api_book(request: Request):
    books = Books()

    book_id = request.path_params["books_id"]

    if not is_integer(book_id):
        return {}

    return await books.get_book(int(book_id))


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
