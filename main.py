from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
from glossary._search import GlossarySearch

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
    glossary_search = GlossarySearch(request.query_params)
    return await glossary_search.search_term()

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)