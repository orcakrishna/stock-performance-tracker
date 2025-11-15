#!/usr/bin/env python3
"""
Nifty Total Market → pandas-ready JSON
"""

import json
import time
import pandas as pd
import requests
from datetime import datetime
from pathlib import Path

URL = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20TOTAL%20MARKET"

def get_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.nseindia.com/market-data/live-equity-market",
    })
    try:
        s.get("https://www.nseindia.com", timeout=10)
        time.sleep(1)
    except:
        pass
    return s

def fetch():
    try:
        r = get_session().get(URL, timeout=15)
        r.raise_for_status()
        data = r.json().get("data", [])
        df = pd.DataFrame(data)
        df = df.rename(columns={
            "symbol": "symbol",
            "lastPrice": "price",
            "change": "change",
            "pChange": "change_pct",
            "totalTradedVolume": "volume"
        })
        df = df[["symbol", "price", "change", "change_pct", "volume"]].copy()
        for c in ["price", "change", "change_pct", "volume"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df.dropna(subset=["price"], inplace=True)
        df = df.sort_values("change_pct", ascending=False).reset_index(drop=True)
        df.insert(0, "rank", df.index + 1)
        return df
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()  # return empty DF

def main():
    df = fetch()
    date_str = datetime.now().strftime("%d%b%Y").upper()

    # CRITICAL: orient="records"
    Path("nifty_total_market.json").write_text(
        df.to_json(orient="records", indent=2, force_ascii=False)
    )
    Path("nse_total_market_symbols.json").write_text(
        json.dumps(sorted(df["symbol"].tolist() if not df.empty else []), indent=2)
    )
    Path("nifty_total_market_meta.json").write_text(
        json.dumps({"date": date_str, "total_stocks": len(df)}, indent=2)
    )
    print(f"Success: {len(df)} stocks")

if __name__ == "__main__":
    import time
    main()
