# eia_fetchers.py
import pandas as pd
from EIA_connector import EIAClient
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

# ----------------------------------------------------------------------------

# =============================================
# Daily Hub spot prices
# =============================================
def fetch_HH_spot(years=5) -> pd.Series:
    client = EIAClient()

    records = client.get(
        url="https://api.eia.gov/v2/natural-gas/pri/fut/data/",
        params={
            "frequency": "weekly",
            "data[0]": "value",
            "facets[series][]": "RNGWHHD",  # Henry Hub Natural Gas Spot Price (NYMEX)
            "sort[0][column]": "period",
            "sort[0][direction]": "asc",
            "length": 5000,
        },
    )

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["period"]) # Converting period column to python measurable date
    df["price"] = pd.to_numeric(df["value"], errors="coerce")  #Converting storage_bcf column to numeric values and delete non-sense values

    df = df.set_index("date").sort_index()  # Set date as the time index + sort it chronologically
    cutoff = df.index.max() - pd.DateOffset(years=years) #cutoff = time's window btw most recent date provided & chosen time in years  
    
    # =====================================================================================
    # Timeframe alignment: daily prices vs weekly storage
    # -------------------------------------------------------------------------------------
    # EIA natural gas storage data (Lower 48) are reported on a WEEKLY basis, while
    # Henry Hub spot prices are available at a DAILY frequency.
    #
    # Mixing different temporal granularities in a single model introduces incoherence:
    # a weekly storage level cannot be meaningfully explained by a single daily price
    # observation without creating temporal mismatches or implicit look-ahead bias.
    #
    # To ensure temporal consistency, we voluntarily reduce the price data granularity
    # from daily to weekly. This implies a controlled loss of information, but a clear
    # gain in statistical and economic coherence.
    #
    # The weekly prices are obtained via Natural Gas Spot and Futures Prices (NYMEX) who has a weekly frequency
    
    # As a result:
    # - each storage observation is associated with exactly one price value
    # - both series share the same weekly timeframe
    # - the model structure becomes temporally aligned and economically interpretable
    #
    # In short: less noise, more coherence and fewer lies told by the data.
    # =====================================================================================

    weekly_prices =df["price"] 
    weekly_prices.name = "HH__weekly_spot_prices"
    
    return weekly_prices 






# =============================================
# Weekly gas storage fetch function (Lower 48)
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
        .str.contains("Lower 48 States", case=False, na=False) # returning the complete R48 values as a DF (delete the incomplete rows)
    ]

    df["date"] = pd.to_datetime(df["period"]) # Converting period column to python measurable date
    df["storage_bcf"] = pd.to_numeric(df["value"], errors="coerce") # Converting storage_bcf column to numeric values and delete non-sense values

    df = (
        df[["date", "storage_bcf"]] # Keep only relevant columns (date and storage)
        .dropna()                   # Remove rows with missing date or storage values
        .set_index("date")          # Set date as the time index
        .sort_index()               # Ensure chronological order
    )
    
    df.attrs["source"] = "EIA (U.S. Energy Information Administration)" # Metadata used for data traceability and documentation
    df.attrs["unit"] = "Bcf" # Physical unit associated with the storage values
    df.attrs["price/unit"]="($/MMBtu)"
    df.attrs["stock value"]="($ million)"
    return df


