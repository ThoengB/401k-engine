import streamlit as st
import pandas as pd
import psycopg2
import time

# 1. Database Configuration
# We use st.secrets so your password isn't exposed in the code
# You will add the DB_URL to the Streamlit Cloud Dashboard "Secrets" settings
@st.cache_resource
def get_db_connection():
    db_url = st.secrets["DB_URL"]
    try:
        # connect_timeout helps the app fail gracefully instead of freezing
        return psycopg2.connect(db_url, connect_timeout=10)
    except Exception as e:
        st.error(f"Could not connect to DB: {e}")
        return None

# 2. UI and Logic
st.set_page_config(page_title="401k SaaS Engine", layout="wide")
st.title("🎯 401k SaaS Lead Generation Engine")

@st.cache_data(ttl=600)
def load_lead_data():
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql("SELECT * FROM v_smart_lead_scoring;", conn)
            return df
        except Exception as e:
            st.error(f"Query error: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    return pd.DataFrame()

# Main App Display
if st.button("Loading engine..."):
    data = load_lead_data()
    if not data.empty:
        st.write("Lead Data Loaded Successfully:")
        st.dataframe(data)
    else:
        st.warning("No data found or connection failed.")