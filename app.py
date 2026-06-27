import streamlit as st

from data_loader import load_lead_data, save_hidden_goldmine_flags
from scoring import add_lead_scores

st.set_page_config(page_title="401k Lead Engine", layout="wide")
st.title("🎯 401k SaaS Lead Generation Engine")

try:
    df = load_lead_data()

    if df.empty:
        st.info("No lead data found. Check your database connection and view.")
    else:
        df = add_lead_scores(df)

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
            success, error = save_hidden_goldmine_flags(edited_df)
            if success:
                st.success("Changes saved!")
            else:
                st.error(f"Save failed: {error}")

except Exception as e:
    st.error(f"Failed to load dashboard data: {e}")
