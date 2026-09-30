import bcrypt
import psycopg2
import psycopg2.errors
import streamlit as st

from db import execute, fetch_one


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:
        return False


def login_user(username: str, password: str) -> bool:
    row = fetch_one(
        "SELECT id, username, password_hash FROM users WHERE username = %s",
        (username.strip(),),
    )
    if row and verify_password(password, row["password_hash"]):
        st.session_state["auth"] = {"role": "user", "id": row["id"], "username": row["username"]}
        return True
    return False


def login_admin(username: str, password: str) -> bool:
    row = fetch_one(
        "SELECT id, username, password_hash FROM admins WHERE username = %s",
        (username.strip(),),
    )
    if row and verify_password(password, row["password_hash"]):
        st.session_state["auth"] = {"role": "admin", "id": row["id"], "username": row["username"]}
        return True
    return False


def register_user(username: str, email: str, password: str) -> tuple[bool, str]:
    username, email = username.strip(), email.strip().lower()
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if "@" not in email or "." not in email:
        return False, "Enter a valid email address."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    try:
        execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, hash_password(password)),
        )
        return True, "Registration successful. You can now log in."
    except psycopg2.errors.UniqueViolation:
        return False, "Username or email already exists."


def logout():
    st.session_state.pop("auth", None)
    st.session_state["page"] = "Home"


def current_auth():
    return st.session_state.get("auth")
