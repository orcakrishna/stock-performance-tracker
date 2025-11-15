#!/usr/bin/env python3
"""
Nifty Total Market → Perfect JSON for Streamlit
Uses NSE Live JSON API → No SSL errors, no yfinance
"""

import json
import time
import pandas as pd
import requests
from datetime import datetime
from pathlib import Path

# NSE Live Market API (public)
URL = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20TOTAL%20MARKET"


def get_session():
    """Create browser-like session to avoid SSL/TLS blocks"""
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.nseindia.com/market-data/live-equity-market",
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
    })
    try:
        s.get("https://www.nseindia.com", timeout=10)
        time.sleep(1)
    except:
        pass
    return s


def fetch_nifty_data() -> pd.DataFrame:
    """Fetch and clean Nifty Total Market data"""
    try:
        response = get_session().get(URL, timeout=15)
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            print("No data received from NSE.")
            return pd.DataFrame()

        df = pd.DataFrame(data)

        # Rename and select columns
        df = df.rename(columns={
            "symbol": "symbol",
            "lastPrice": "price",
            "change": "change",
            "pChange": "change_pct",
            "totalTradedVolume": "volume"
        })

        df = df[["symbol", "price", "change", "change_pct", "volume"]].copy()

        # Convert to numbers
        for col in ["price", "change", "change_pct", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df.dropna(subset=["price"], inplace=True)

        # Rank by % change
        df = df.sort_values("change_pct", ascending=False).reset_index(drop=True)
        df.insert(0, "rank", df.index + 1)

        return df

    except Exception as e:
        print(f"Fetch error: {e}")
        return pd.DataFrame()


def main():
    print("Fetching Nifty Total Market data...")
    df = fetch_nifty_data()
    date_str = datetime.now().strftime("%d%b%Y").upper()

    if df.empty:
        print("No data to save.")
        return

    # 1. FULL TABLE — CORRECT FORMAT
    Path("nifty_total_market.json").write_text(
        df.to_json(orient="records", indent=2, force_ascii=False)
    )

    # 2. SYMBOLS ONLY
    Path("nse_total_market_symbols.json").write_text(
        json.dumps(sorted(df["symbol"].tolist()), indent=2)
    )

    # 3. METADATA
    Path("nifty_total_market_meta.json").write_text(
        json.dumps({
            "date": date_str,
            "total_stocks": len(df)
        }, indent=2)
    )

    print(f"SUCCESS: Saved {len(df)} stocks → nifty_total_market.json")


if __name__ == "__main__":
    import time
    main()