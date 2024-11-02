import os

DB_PATH_REL = 'db/_main.db'
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_PATH_REL)

TABLE_NAME = 'glossary'
VALID_GAMES = ['eso', 'skyrim', 'oblivion', 'morrowind', 'legends', 'blades', 'castles', 'redguard']
