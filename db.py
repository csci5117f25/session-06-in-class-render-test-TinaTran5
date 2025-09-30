""" database access
docs:
* http://initd.org/psycopg/docs/
* http://initd.org/psycopg/docs/pool.html
* http://initd.org/psycopg/docs/extras.html#dictionary-like-cursor
"""

from contextlib import contextmanager
import logging
import os

from flask import current_app, g

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor

pool = None


def setup():
    global pool
    DATABASE_URL = os.environ["DATABASE_URL"]
    # current_app.logger.info(f"creating db connection pool")
    pool = ThreadedConnectionPool(1, 100, dsn=DATABASE_URL, sslmode="require")


@contextmanager
def get_db_connection():
    try:
        connection = pool.getconn()
        yield connection
    finally:
        pool.putconn(connection)


@contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as connection:
        cursor = connection.cursor(cursor_factory=DictCursor)
        # cursor = connection.cursor()
        try:
            yield cursor
            if commit:
                connection.commit()
        finally:
            cursor.close()


def add_post(name, text):
    # Insert a new row in guest_book_entires table
    # get_db_cursor(True) ensures insertion is saved
    with get_db_cursor(True) as cur:
        # current_app.logger.info("Adding guestbook post %s, %s", name, text)
        cur.execute(
            "INSERT INTO guest_book_entries(name, content) values (%s, %s);",
            (name, text),
        )


def get_guestbook():
    # Retreives guestbook entries from table 
    retval = []
    with get_db_cursor(False) as cur: # no commit, just read
        with get_db_cursor() as cur:
            cur.execute("SELECT * from guest_book_entries")
            for row in cur:
                retval.append({"name": row["name"], "text": row["content"]})
    return retval