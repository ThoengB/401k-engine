import pandas as pd


def add_lead_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Score prospects for Hidden Goldmine potential from assets and fees."""
    scored = df.copy()
    scored["lead_score"] = (
        (scored["total_assets"] / scored["total_assets"].max()) * 50
        + (1 - (scored["total_fees"] / (scored["total_assets"] + 1))) * 50
    ).round(0)
    return scored
