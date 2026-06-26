import streamlit as st
import pandas as pd
import psycopg2

# 1. Database Configuration
DB_URL = "postgresql://postgres:ShanCam8102@db.glrmdxmrxgeijucftblf.supabase.co:5432/postgres?sslmode=require"

# This helper function ensures we get a fresh connection when needed
def get_db_connection():
    return psycopg2.connect(DB_URL)

@st.cache_data(ttl=600)
def load_lead_data():
    """Fetches ALL data without a limit."""
    conn = get_db_connection()
    try:
        # Removed 'LIMIT 1000' to get all data
        query = "SELECT * FROM v_smart_lead_scoring;"
        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()

# 2. Main Page Layout
st.set_page_config(page_title="401k Lead Engine", layout="wide")
st.title("🎯 401k SaaS Lead Generation Engine")

# 3. Load and Display
try:
    df = load_lead_data()
    
    # Calculate Lead Score
    df['lead_score'] = (
        (df['total_assets'] / df['total_assets'].max()) * 50 + 
        (1 - (df['total_fees'] / (df['total_assets'] + 1))) * 50
    ).round(0)

    # Sidebar Filters
    st.sidebar.header("Filter Prospects")
    p_range = st.sidebar.slider("Participants", int(df['active_participants'].min()), int(df['active_participants'].max()), (int(df['active_participants'].min()), int(df['active_participants'].max())))
    a_range = st.sidebar.slider("Assets ($)", int(df['total_assets'].min()), int(df['total_assets'].max()), (int(df['total_assets'].min()), int(df['total_assets'].max())))

    # Filtering
    filtered_df = df[
        (df['active_participants'] >= p_range[0]) & (df['active_participants'] <= p_range[1]) &
        (df['total_assets'] >= a_range[0]) & (df['total_assets'] <= a_range[1])
    ].sort_values(by='lead_score', ascending=False)

    st.write(f"Showing {len(filtered_df)} total prospects")

    # Actionable Table
    edited_df = st.data_editor(
        filtered_df,
        column_order=["is_hidden_goldmine", "lead_score", "company_name", "total_assets", "active_participants", "total_fees"],
        disabled=["id", "company_name", "total_assets", "total_fees", "active_participants", "lead_score"],
        use_container_width=True,
    )

    if st.button("Save Changes"):
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            for _, row in edited_df.iterrows():
                cur.execute("UPDATE v_smart_lead_scoring SET is_hidden_goldmine = %s WHERE id = %s", (row['is_hidden_goldmine'], row['id']))
            conn.commit()
            cur.close()
            st.success("Changes saved!")
        finally:
            conn.close()
except Exception as e:
    st.error(f"Error: {e}")
