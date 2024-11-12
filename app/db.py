# db.py
import sqlite3
import os
from config import DB_NAME

def connect_db():
    db_path = os.path.join(os.path.dirname(__file__), '..', DB_NAME)
    return sqlite3.connect(db_path)
