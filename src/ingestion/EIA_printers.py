from EIA_fetchers import fetch_HH_weekly_storage, fetch_HH_spot
import pandas as pd
from EIA_connector import EIAClient

import requests
import os
from pathlib import Path
from dotenv import load_dotenv

# =============================================
#               Printing fuctions
# =============================================

def print_storage_and_price(df: pd.DataFrame, n=20):
    df = df.copy()
    df.index.name = "Date (EIA Week)"

    df["stock_valuation"] = df["stock_valuation"].round(2)

    # Rename for display
    df = df.rename(
        columns={
            "storage_bcf": "Working Gas Storage (Bcf)",
            "HH__weekly_spot_prices": "Henry Hub Price ($/MMBtu)",
            "stock_valuation": "Stock Valuation ($bn)"
        }
    )

    print("\nWeekly Working Gas in Underground Storage & Henry Hub Spot Price — Lower 48")
    print("Source :", df.attrs.get("source"))
    print("Unit   :", df.attrs.get("unit"))
    print("Price/Unit :", df.attrs.get("price/unit"))
    print("Stock Valuation :", df.attrs.get("stock value"))
    print("=" * 60)

    print(
        df
        .tail(n)
        .to_string(
            justify="right",
            col_space=18,
        )
    )
    
    
    
    
    
    

# =============================================
#                    MAIN       
# =============================================
if __name__ == "__main__":
    
    # Function calls
    storage = fetch_HH_weekly_storage(start="2015-01-01")
    price=fetch_HH_spot(years=5)
    
    #Join method to watch storage & price depending on date
    df =storage.join(price, how="inner")
    
    
    #Displaying stock valuation ins Millions $
    df["stock_valuation"] = (df["storage_bcf"] * 1.03* 1e-3* df["HH__weekly_spot_prices"]
    )



    # Defining again attrs bc pandas is ignoring them if joint is made
    df.attrs["source"] = "EIA (U.S. Energy Information Administration)"
    df.attrs["unit"] = "Bcf"
    df.attrs["price/unit"] = "$/MMBtu"
    df.attrs["stock value"]="($ million)"
    print_storage_and_price(df, n=12)

    print("\n" + "=" * 60)
    print("\n1 Bcf ≈ 1.03 million MMBtu")