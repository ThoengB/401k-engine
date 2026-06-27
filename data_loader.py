import os

import pandas as pd
import psycopg2
import streamlit as st


def get_db_url():
    try:
        return st.secrets["DB_URL"]
    except (KeyError, FileNotFoundError):
        return os.environ.get("DB_URL") or os.environ.get("SUPABASE_DB_URL")


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
