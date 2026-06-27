import os
import tomllib
from pathlib import Path

import pandas as pd
import psycopg2
import streamlit as st

SECRETS_PATH = Path(__file__).resolve().parent / ".streamlit" / "secrets.toml"


def _read_secrets_file() -> dict:
    if not SECRETS_PATH.exists():
        return {}
    with SECRETS_PATH.open("rb") as secrets_file:
        return tomllib.load(secrets_file)


def get_db_url():
    url = None
    try:
        if "DB_URL" in st.secrets:
            url = st.secrets["DB_URL"]
        elif "SUPABASE_DB_URL" in st.secrets:
            url = st.secrets["SUPABASE_DB_URL"]
    except FileNotFoundError:
        pass

    if not url:
        secrets = _read_secrets_file()
        url = secrets.get("DB_URL") or secrets.get("SUPABASE_DB_URL")

    if not url:
        url = os.environ.get("DB_URL") or os.environ.get("SUPABASE_DB_URL")

    return url.strip() if url else None


@st.cache_resource
def get_db_connection():
    db_url = get_db_url()
    if not db_url:
        st.error("DB_URL not configured. Set it in Streamlit secrets or your environment.")
        return None
    try:
        return psycopg2.connect(db_url, connect_timeout=10)
    except Exception as e:
        st.error(f"Could not connect to DB: {e}")
        return None


@st.cache_data(ttl=600)
def load_lead_data():
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        return pd.read_sql("SELECT * FROM v_smart_lead_scoring;", conn)
    finally:
        conn.close()


def save_hidden_goldmine_flags(df: pd.DataFrame) -> tuple[bool, str | None]:
    conn = get_db_connection()
    if conn is None:
        return False, "Could not connect to save changes."
    try:
        with conn.cursor() as cur:
            for _, row in df.iterrows():
                cur.execute(
                    "UPDATE v_smart_lead_scoring SET is_hidden_goldmine = %s WHERE id = %s",
                    (row["is_hidden_goldmine"], row["id"]),
                )
        conn.commit()
        st.cache_data.clear()
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()
