import streamlit as st
import pandas as pd
import psycopg2

st.set_page_config(page_title="401k SaaS Engine", layout="wide")
st.title("🎯 401k SaaS Lead Generation Engine")

@st.cache_resource
def get_db_connection():
    try:
        # This now pulls from the correctly formatted TOML secret
        db_url = st.secrets["DB_URL"]
        return psycopg2.connect(db_url, connect_timeout=10)
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return None

if st.button("Load Lead Data"):
    with st.spinner("Connecting to database..."):
        conn = get_db_connection()
        if conn:
            try:
                df = pd.read_sql("SELECT * FROM v_smart_lead_scoring;", conn)
                st.dataframe(df)
            except Exception as e:
                st.error(f"Query error: {e}")
            finally:
                conn.close()
        else:
            st.error("Could not establish database connection.")