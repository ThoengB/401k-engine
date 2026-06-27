import os

import pandas as pd
import psycopg2
import streamlit as st

st.set_page_config(page_title="401k Lead Engine", layout="wide")
st.title("🎯 401k SaaS Lead Generation Engine")


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


try:
    df = load_lead_data()

    if df.empty:
        st.info("No lead data found. Check your database connection and view.")
    else:
        df["lead_score"] = (
            (df["total_assets"] / df["total_assets"].max()) * 50
            + (1 - (df["total_fees"] / (df["total_assets"] + 1))) * 50
        ).round(0)

        st.sidebar.header("Filter Prospects")

        min_p = int(df["active_participants"].min())
        max_p = int(df["active_participants"].max())
        p_range = st.sidebar.slider(
            "Active Participants", min_p, max_p, (min_p, max_p)
        )

        min_a = int(df["total_assets"].min())
        max_a = int(df["total_assets"].max())
        a_range = st.sidebar.slider(
            "Total Assets ($)", min_a, max_a, (min_a, max_a)
        )

        filtered_df = df[
            (df["active_participants"] >= p_range[0])
            & (df["active_participants"] <= p_range[1])
            & (df["total_assets"] >= a_range[0])
            & (df["total_assets"] <= a_range[1])
        ].sort_values(by="lead_score", ascending=False)

        st.write(f"Showing {len(filtered_df)} of {len(df)} prospects")

        edited_df = st.data_editor(
            filtered_df,
            column_config={
                "is_hidden_goldmine": st.column_config.CheckboxColumn(
                    "Hidden Goldmine?", default=False
                ),
            },
            column_order=[
                "is_hidden_goldmine",
                "lead_score",
                "company_name",
                "total_assets",
                "active_participants",
                "total_fees",
            ],
            disabled=[
                "id",
                "company_name",
                "total_assets",
                "total_fees",
                "active_participants",
                "asset_growth_rate_pct",
                "lead_score",
            ],
            use_container_width=True,
        )

        if st.button("Save Changes to Database"):
            conn = get_db_connection()
            if conn is None:
                st.error("Could not connect to save changes.")
            else:
                try:
                    with conn.cursor() as cur:
                        for _, row in edited_df.iterrows():
                            cur.execute(
                                "UPDATE v_smart_lead_scoring SET is_hidden_goldmine = %s WHERE id = %s",
                                (row["is_hidden_goldmine"], row["id"]),
                            )
                    conn.commit()
                    st.success("Changes saved!")
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"Save failed: {e}")
                finally:
                    conn.close()

except Exception as e:
    st.error(f"Failed to load dashboard data: {e}")
