import streamlit as st
import pandas as pd
import psycopg2
import time

# 1. Database Configuration
# Explicitly adding connect_timeout to handle cloud network latency
DB_URL = "postgresql://postgres:ShanCam8102@db.glrmdxmrxgeijucftblf.supabase.co:5432/postgres?sslmode=require&connect_timeout=10"

@st.cache_resource
def get_db_connection():
    """Create a persistent connection with a retry mechanism."""
    try:
        return psycopg2.connect(DB_URL)
    except Exception as e:
        st.error(f"Could not connect to DB: {e}")
        return None

@st.cache_data(ttl=600)
def load_lead_data():
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        query = "SELECT * FROM v_smart_lead_scoring;"
        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close() # Safely close after fetch

# 2. Page UI
st.set_page_config(page_title="401k Lead Engine", layout="wide")
st.title("🎯 401k SaaS Lead Generation Engine")

# 3. Load Data
df = load_lead_data()

if not df.empty:
    # Lead Scoring
    df['lead_score'] = (
        (df['total_assets'] / df['total_assets'].max()) * 50 + 
        (1 - (df['total_fees'] / (df['total_assets'] + 1))) * 50
    ).round(0)

    # Sidebar
    st.sidebar.header("Filter Prospects")
    # Using defaults to prevent errors on empty df
    min_p, max_p = int(df['active_participants'].min()), int(df['active_participants'].max())
    p_range = st.sidebar.slider("Participants", min_p, max_p, (min_p, max_p))
    min_a, max_a = int(df['total_assets'].min()), int(df['total_assets'].max())
    a_range = st.sidebar.slider("Assets ($)", min_a, max_a, (min_a, max_a))

    # Table
    filtered_df = df[
        (df['active_participants'] >= p_range[0]) & (df['active_participants'] <= p_range[1]) &
        (df['total_assets'] >= a_range[0]) & (df['total_assets'] <= a_range[1])
    ].sort_values(by='lead_score', ascending=False)

    edited_df = st.data_editor(
        filtered_df,
        column_order=["is_hidden_goldmine", "lead_score", "company_name", "total_assets", "active_participants", "total_fees"],
        use_container_width=True,
    )

    if st.button("Save Changes"):
        conn = get_db_connection()
        cur = conn.cursor()
        for _, row in edited_df.iterrows():
            cur.execute("UPDATE v_smart_lead_scoring SET is_hidden_goldmine = %s WHERE id = %s", (row['is_hidden_goldmine'], row['id']))
        conn.commit()
        cur.close()
        conn.close()
        st.success("Changes saved!")
else:
    st.info("Loading engine...")
