import os

DB_PATH_REL = '../db/library.db'
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_PATH_REL)

TABLE_NAME_BOOKS = 'books'
TABLE_NAME_CATEGORIES = 'categories'