import os

DB_PATH_REL = '../db/glossary.db'
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_PATH_REL)

TABLE_NAME = 'glossary'
COLUMNS = ['game', 'type', 'en', 'ru']
VALID_GAMES = ['eso', 'skyrim', 'oblivion', 'morrowind', 'legends', 'blades', 'castles', 'redguard', 'battlespire']
