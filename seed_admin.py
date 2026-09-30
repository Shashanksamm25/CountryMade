"""Run once, locally or inside the app container:
    docker compose exec app python seed_admin.py
Creates the default admin with a properly hashed password."""
import getpass
import os

import bcrypt
import psycopg2


def _load_config():
    if "DB_HOST" in os.environ:
        return {
            "host": os.environ["DB_HOST"],
            "port": int(os.environ.get("DB_PORT", "5432")),
            "dbname": os.environ.get("DB_NAME", "jeans"),
            "user": os.environ.get("DB_USER", "postgres"),
            "password": os.environ.get("DB_PASSWORD", ""),
        }
    import tomllib
    with open(".streamlit/secrets.toml", "rb") as f:
        cfg = tomllib.load(f)["postgres"]
    return {
        "host": cfg["host"],
        "port": cfg.get("port", 5432),
        "dbname": cfg["dbname"],
        "user": cfg["user"],
        "password": cfg["password"],
    }


cfg = _load_config()

username = input("Admin username [admin]: ").strip() or "admin"
password = getpass.getpass("Admin password: ")
pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

conn = psycopg2.connect(**cfg)
with conn, conn.cursor() as cur:
    cur.execute(
        "INSERT INTO admins (username, password_hash) VALUES (%s, %s) "
        "ON CONFLICT (username) DO UPDATE SET password_hash = EXCLUDED.password_hash",
        (username, pw_hash),
    )
conn.close()
print(f"Admin '{username}' is ready.")
