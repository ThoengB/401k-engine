import streamlit as st
import pandas as pd
import psycopg2

# 1. Database Configuration
# Using your direct connection string (Port 5432)
db_url = "postgresql://postgres:ShanCam8102@db.glrmdxmrxgeijucftblf.supabase.co:5432/postgres?sslmode=require"

# 2. Database Connection Helper
def get_db_connection():
    return psycopg2.connect(db_url)

# 3. Data Loading Function
@st.cache_data(ttl=600)
def load_lead_data():
    conn = get_db_connection()
    try:
        query = "SELECT * FROM v_smart_lead_scoring LIMIT 1000;"
        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()

# 4. Main Page Layout
st.set_page_config(page_title="401k Lead Engine", layout="wide")
st.title("🎯 401k SaaS Lead Generation Engine")

# 5. Load and Display Data
try:
    df = load_lead_data()

    # Sidebar Filters
    st.sidebar.header("Filter Prospects")
    
    # Filter by Participants
    min_p = int(df['active_participants'].min())
    max_p = int(df['active_participants'].max())
    p_range = st.sidebar.slider("Active Participants", min_p, max_p, (min_p, max_p))

    # Filter by Assets
    min_a = int(df['total_assets'].min())
    max_a = int(df['total_assets'].max())
    a_range = st.sidebar.slider("Total Assets ($)", min_a, max_a, (min_a, max_a))

    # Apply Filters
    filtered_df = df[
        (df['active_participants'] >= p_range[0]) & 
        (df['active_participants'] <= p_range[1]) &
        (df['total_assets'] >= a_range[0]) & 
        (df['total_assets'] <= a_range[1])
    ]

    st.write(f"Showing {len(filtered_df)} prospects")
    
    # Actionable Table
    edited_df = st.data_editor(
        filtered_df,
        column_config={
            "is_hidden_goldmine": st.column_config.CheckboxColumn("Hidden Goldmine?", default=False),
        },
        disabled=["id", "company_name", "total_assets", "total_fees", "active_participants", "asset_growth_rate_pct", "lead_score"],
        use_container_width=True,
    )

    # Save button
    if st.button("Save Changes to Database"):
        conn = get_db_connection()
        try:
            for index, row in edited_df.iterrows():
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE v_smart_lead_scoring SET is_hidden_goldmine = %s WHERE id = %s",
                        (row['is_hidden_goldmine'], row['id'])
                    )
            conn.commit()
            st.success("Changes saved!")
        except Exception as e:
            st.error(f"Save failed: {e}")
        finally:
            conn.close()

except Exception as e:
    st.error(f"Failed to load dashboard data: {e}")