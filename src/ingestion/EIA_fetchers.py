# eia_fetchers.py
import pandas as pd
from EIA_connector import EIAClient



# =============================================
# Daily Hub spot prices
# =============================================
def fetch_HH_spot(years=5) -> pd.Series:
    client = EIAClient()

    records = client.get(
        url="https://api.eia.gov/v2/natural-gas/pri/sum/data/",
        params={
            "frequency": "daily",
            "data[0]": "value",
            "facets[series][]": "RNGWHHD",
            "sort[0][column]": "period",
            "sort[0][direction]": "asc",
            "length": 5000,
        },
    )

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["period"])
    df["price"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.set_index("date").sort_index()

    cutoff = df.index.max() - pd.DateOffset(years=years)
    return df.loc[df.index > cutoff]["price"]





# =============================================
# Weekly gas storage fetch function(Lower 48)
# =============================================
def fetch_HH_weekly_storage(start="2015-01-01") -> pd.DataFrame:
    client = EIAClient()

    records = client.get(
        url="https://api.eia.gov/v2/natural-gas/stor/wkly/data/",
        params={
            "frequency": "weekly",
            "data[0]": "value",
            "start": start,
            "sort[0][column]": "period",
            "sort[0][direction]": "asc",
            "length": 5000,
        },
    )

    df = pd.DataFrame(records)
    df = df[
        df["series-description"]
        .str.contains("Lower 48 States", case=False, na=False) # Contrainged by EIA (Lower 48 states = most reliable path with complete data)
    ]

    df["date"] = pd.to_datetime(df["period"])
    df["storage_bcf"] = pd.to_numeric(df["value"], errors="coerce")

    df = (
        df[["date", "storage_bcf"]]
        .dropna()
        .set_index("date")
        .sort_index()
    )
    return df






# =============================================
#               Printing fuction
# =============================================
def print_storage_and_price(df: pd.DataFrame, n=20):
    """
    Affichage propre du stockage gaz US (Lower 48)
    """
    print_df = df.copy()

    print_df.index.name = "Date (EIA Week)"
    pretty_df = print_df.rename(
        columns={"storage_bcf": "Working Gas Storage (Bcf)"}
    )

    print("\n Weekly Working Gas in Underground Storage — Lower 48 States")
    print("Source :", df.attrs.get("source"))
    print("Unité  :", df.attrs.get("unit"))
    print("=" * 60)

    print(
        pretty_df
        .tail(n)
        .to_string(
            justify="right",
            col_space=18,
            float_format=lambda x: f"{x:,.0f}"
        )
    )


if __name__ == "__main__":
    storage = fetch_HH_weekly_storage(start="2015-01-01")

    # Affichage esthétique
    print_storage_and_price(storage, n=12)
    print("\n" + "=" * 60)
    print("\n1 Bcf ≈ 0,293 TWh")
