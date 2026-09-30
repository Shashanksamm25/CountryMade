import os
from contextlib import contextmanager

import psycopg2
import streamlit as st
from psycopg2.extras import RealDictCursor


def _get_db_config():
    if "DB_HOST" in os.environ:
        return {
            "host": os.environ["DB_HOST"],
            "port": int(os.environ.get("DB_PORT", "5432")),
            "dbname": os.environ.get("DB_NAME", "jeans"),
            "user": os.environ.get("DB_USER", "postgres"),
            "password": os.environ.get("DB_PASSWORD", ""),
        }
    cfg = st.secrets["postgres"]
    return {
        "host": cfg["host"],
        "port": cfg.get("port", 5432),
        "dbname": cfg["dbname"],
        "user": cfg["user"],
        "password": cfg["password"],
    }


def get_conn():
    return psycopg2.connect(**_get_db_config())


@contextmanager
def cursor():
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fetch_all(sql, params=None):
    with cursor() as cur:
        cur.execute(sql, params or ())
        return cur.fetchall()


def fetch_one(sql, params=None):
    with cursor() as cur:
        cur.execute(sql, params or ())
        return cur.fetchone()


def execute(sql, params=None, returning=False):
    """Run INSERT/UPDATE/DELETE. If returning=True, returns the first row (or None)."""
    with cursor() as cur:
        cur.execute(sql, params or ())
        if returning:
            return cur.fetchone()
        return cur.rowcount
