import os

TES_DB_PATH_REL = '../db/glossary.db'
TES_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), TES_DB_PATH_REL)

FALLOUT_DB_PATH_REL = '../db/glossary_fallout.db'
FALLOUT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), FALLOUT_DB_PATH_REL)

TABLE_NAME = 'glossary'
COLUMNS = ['game', 'type', 'en', 'ru']
TES_VALID_GAMES = ['eso', 'skyrim', 'oblivion', 'morrowind', 'legends', 'blades', 'castles', 'redguard', 'battlespire', 'travels', 'arena', 'daggerfall']
FALLOUT_VALID_GAMES = ['shelter', 'fallout 76']
