import streamlit as st
import pandas as pd
import psycopg2

# 1. Page Configuration
st.set_page_config(page_title="401k SaaS Engine", layout="wide")
st.title("🎯 401k SaaS Lead Generation Engine")

# 2. Database Connection
@st.cache_resource
def get_db_connection():
    try:
        # st.secrets pulls the value you set in Streamlit Cloud -> Manage App -> Settings -> Secrets
        db_url = st.secrets["DB_URL"]
        # connect_timeout is critical to prevent infinite hanging
        return psycopg2.connect(db_url, connect_timeout=10)
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return None

# 3. Data Loading
@st.cache_data(ttl=600)
def load_lead_data():
    conn = get_db_connection()
    if conn:
        try:
            # Query your database
            df = pd.read_sql("SELECT * FROM v_smart_lead_scoring;", conn)
            return df
        except Exception as e:
            st.error(f"Query error: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    return pd.DataFrame()

# 4. Main App Interface
if st.button("Load Lead Data"):
    with st.spinner("Fetching data from Supabase..."):
        data = load_lead_data()
        if not data.empty:
            st.write("Lead Data Loaded Successfully:")
            st.dataframe(data)
        else:
            st.warning("No data found or connection failed.")