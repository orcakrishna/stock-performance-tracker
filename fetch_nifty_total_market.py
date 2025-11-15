#!/usr/bin/env python3
"""
Nifty Total-Market fetcher – uses NSE live-market JSON (no ZIP, no yfinance).
Outputs:
    nifty_total_market.json        – ranked table
    nse_total_market_symbols.json  – list of symbols only
"""

import json
import time
import pandas as pd
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Any

# ----------------------------------------------------------------------
# 1. NSE live-market endpoint (public, no SSL handshake issues)
# ----------------------------------------------------------------------
LIVE_MARKET_URL = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20TOTAL%20MARKET"

# ----------------------------------------------------------------------
# 2. Helper – browser-like session (cookies + headers)
# ----------------------------------------------------------------------
def _nse_session() -> requests.Session:
    sess = requests.Session()
    sess.headers.update({
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/129.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/market-data/live-equity-market",
        "X-Requested-With": "XMLHttpRequest",
    })
    # Warm-up – fetch home page to set cookies (prevents TLS alert)
    try:
        sess.get("https://www.nseindia.com", timeout=10)
        time.sleep(1)
    except Exception:
        pass
    return sess


# ----------------------------------------------------------------------
# 3. Fetch the whole Nifty Total Market in ONE request
# ----------------------------------------------------------------------
def fetch_nse_live_market_data() -> Tuple[pd.DataFrame, str]:
    sess = _nse_session()
    for attempt in range(3):
        try:
            resp = sess.get(LIVE_MARKET_URL, timeout=15)
            resp.raise_for_status()
            payload = resp.json()

            records = payload["data"]
            df = pd.DataFrame(records)

            # Required columns (NSE returns them)
            df = df.rename(columns={
                "symbol": "symbol",
                "open": "open",
                "dayHigh": "high",
                "dayLow": "low",
                "lastPrice": "price",
                "previousClose": "prev_close",
                "change": "change",
                "pChange": "change_pct",
                "totalTradedVolume": "volume",
            })

            # Keep only the columns we need
            df = df[[
                "symbol", "price", "change", "change_pct", "volume"
            ]].copy()

            # Clean & type-cast
            df["price"] = pd.to_numeric(df["price"], errors="coerce")
            df["change"] = pd.to_numeric(df["change"], errors="coerce")
            df["change_pct"] = pd.to_numeric(df["change_pct"], errors="coerce")
            df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
            df.dropna(subset=["price"], inplace=True)

            # Rank by % change (descending)
            df = df.sort_values("change_pct", ascending=False).reset_index(drop=True)
            df.insert(0, "rank", df.index + 1)

            report_date = datetime.now().strftime("%d%b%Y").upper()
            return df, report_date

        except Exception as e:
            print(f"Live API attempt {attempt+1} failed: {e}")
            time.sleep(2 ** attempt)

    raise RuntimeError("NSE live-market API unreachable after 3 tries")


# ----------------------------------------------------------------------
# 4. Main – write JSON files
# ----------------------------------------------------------------------
def main() -> None:
    print("Starting Nifty Total Market fetch (NSE live JSON)…")

    df, report_date = fetch_nse_live_market_data()
    print(f"Fetched {len(df)} stocks for {report_date}")

    # 1. Full table
    out_path = Path("nifty_total_market.json")
    df.to_json(out_path, orient="records", indent=2, force_ascii=False)
    print(f"Saved full table → {out_path}")

    # 2. Symbol list only
    symbols_path = Path("nse_total_market_symbols.json")
    symbols = sorted(df["symbol"].tolist())
    symbols_path.write_text(json.dumps(symbols, indent=2))
    print(f"Saved symbol list → {symbols_path}")

    # 3. Tiny metadata file (optional, helps CI)
    meta = {"date": report_date, "total_stocks": len(df)}
    Path("nifty_total_market_meta.json").write_text(json.dumps(meta, indent=2))


if __name__ == "__main__":
    # Make sure `time` is imported (the error you saw)
    import time
    main()
