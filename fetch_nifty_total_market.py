#!/usr/bin/env python3
"""
Fetch Nifty Total Market via NSE live JSON → write pandas-ready JSON.
Outputs:
  • nifty_total_market.json        → flat list of dicts (pd.read_json works)
  • nse_total_market_symbols.json  → ["RELIANCE", "TCS", ...]
  • nifty_total_market_meta.json   → {"date": "15NOV2025", "total": 752}
"""

import json
import time
import pandas as pd
import requests
from datetime import datetime
from pathlib import Path

# ----------------------------------------------------------------------
# 1. NSE live-market endpoint (public, no ZIP)
# ----------------------------------------------------------------------
LIVE_URL = (
    "https://www.nseindia.com/api/equity-stockIndices?"
    "index=NIFTY%20TOTAL%20MARKET"
)

# ----------------------------------------------------------------------
# 2. Browser-like session (cookies + headers)
# ----------------------------------------------------------------------
def _nse_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/129.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.nseindia.com/market-data/live-equity-market",
        "X-Requested-With": "XMLHttpRequest",
    })
    # Warm-up to set cookies
    try:
        s.get("https://www.nseindia.com", timeout=10)
        time.sleep(1)
    except Exception:
        pass
    return s


# ----------------------------------------------------------------------
# 3. Pull data → return a clean DataFrame
# ----------------------------------------------------------------------
def fetch_market_df() -> pd.DataFrame:
    sess = _nse_session()
    for attempt in range(3):
        try:
            r = sess.get(LIVE_URL, timeout=15)
            r.raise_for_status()
            payload = r.json()

            raw = payload.get("data", [])
            df = pd.DataFrame(raw)

            # Rename to match your UI
            df = df.rename(columns={
                "symbol": "symbol",
                "lastPrice": "price",
                "change": "change",
                "pChange": "change_pct",
                "totalTradedVolume": "volume",
            })

            # Keep only needed columns
            df = df[[
                "symbol", "price", "change", "change_pct", "volume"
            ]].copy()

            # Convert types
            for col in ["price", "change", "change_pct", "volume"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            df.dropna(subset=["price"], inplace=True)

            # Rank by % change (descending)
            df = df.sort_values("change_pct", ascending=False) \
                   .reset_index(drop=True)
            df.insert(0, "rank", df.index + 1)

            return df

        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(2 ** attempt)

    raise RuntimeError("Could not fetch Nifty Total Market data")


# ----------------------------------------------------------------------
# 4. Write three JSON files (all pandas-compatible)
# ----------------------------------------------------------------------
def main():
    print("Fetching Nifty Total Market (NSE live JSON)…")
    df = fetch_market_df()
    report_date = datetime.now().strftime("%d%b%Y").upper()

    # 1. Full table – **records orientation**
    out_path = Path("nifty_total_market.json")
    df.to_json(out_path, orient="records", indent=2, force_ascii=False)
    print(f"Wrote {len(df)} rows → {out_path}")

    # 2. Symbol list
    symbols_path = Path("nse_total_market_symbols.json")
    symbols_path.write_text(json.dumps(sorted(df["symbol"].tolist()), indent=2))
    print(f"Wrote symbols → {symbols_path}")

    # 3. Metadata
    meta_path = Path("nifty_total_market_meta.json")
    meta_path.write_text(json.dumps({
        "date": report_date,
        "total_stocks": len(df)
    }, indent=2))
    print(f"Wrote meta → {meta_path}")


if __name__ == "__main__":
    import time   # (fixes the earlier NameError you saw)
    main()
