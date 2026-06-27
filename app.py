import streamlit as st
import pandas as pd
import psycopg2

# 1. Page Configuration
st.set_page_config(page_title="401k SaaS Engine", layout="wide")
st.title("🎯 401k SaaS Lead Generation Engine")

# 2. Database Connection
@st.cache_resource
def get_db_connection():
    """
    Connects to Supabase using the DB_URL stored in Streamlit Cloud Secrets.
    """
    try:
        # st.secrets["DB_URL"] is the secure way to hold your database password.
        # You will set this in the Streamlit Cloud Dashboard (not in this file).
        db_url = st.secrets["DB_URL"]
        conn = psycopg2.connect(db_url, connect_timeout=10)
        return conn
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return None

# 3. Data Loading
@st.cache_data(ttl=600)
def load_lead_data():
    conn = get_db_connection()
    if conn:
        try:
            # Fetch data from your database
            df = pd.read_sql("SELECT * FROM v_smart_lead_scoring;", conn)
            return df
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    return pd.DataFrame()

# 4. Main App Logic
if st.button("Load Lead Data"):
    with st.spinner("Fetching data from Supabase..."):
        data = load_lead_data()
        if not data.empty:
            st.write("Lead Data Loaded Successfully:")
            st.dataframe(data)
        else:
            st.warning("No data found.")