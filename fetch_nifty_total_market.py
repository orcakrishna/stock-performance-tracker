"""
Fetch NSE Bhavcopy and filter Nifty Total Market 750 stocks
Runs daily via GitHub Actions to update nifty_total_market.json
"""

import pandas as pd
import requests
import json
import os
from io import BytesIO
from zipfile import ZipFile
from datetime import datetime, timedelta


def get_nifty_total_market_symbols_from_bhavcopy(df):
    """
    Extract Nifty Total Market symbols from Bhavcopy itself
    This avoids needing a separate API call for the symbol list
    Returns all EQ series stocks sorted by market cap/volume
    """
    try:
        # Filter for EQ (equity) series only
        eq_stocks = df[df["SERIES"] == "EQ"].copy()
        
        # Sort by turnover (proxy for market cap) to get the top stocks
        eq_stocks = eq_stocks.sort_values("TOTTRDVAL", ascending=False)
        
        # Take top 750 or all available
        top_stocks = eq_stocks.head(750)
        symbols = top_stocks["SYMBOL"].tolist()
        
        print(f"✅ Extracted {len(symbols)} top stocks from Bhavcopy (by turnover)")
        return symbols
        
    except Exception as e:
        print(f"❌ Error extracting symbols from Bhavcopy: {e}")
        return []


def get_nifty_total_market_symbols():
    """
    Get list of Nifty Total Market symbols from NSE
    Multiple fallback methods for reliability
    """
    # Method 1: Try NSE equity-stockIndices API
    try:
        url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20TOTAL%20MARKET"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.nseindia.com/market-data/live-equity-market",
        }
        
        with requests.Session() as session:
            session.headers.update(headers)
            session.get("https://www.nseindia.com", timeout=10)
            time.sleep(1)
            
            response = session.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                stocks = data.get("data", [])
                symbols = [stock["symbol"] for stock in stocks if "symbol" in stock]
                
                if len(symbols) > 500:  # Valid response should have ~750 stocks
                    print(f"✅ Fetched {len(symbols)} symbols from NSE API")
                    # Save for future fallback
                    with open("nse_total_market_symbols.json", "w") as f:
                        json.dump(symbols, f)
                    return symbols
    except Exception as e:
        print(f"⚠️ NSE equity-stockIndices API failed: {e}")
    
    # Method 2: Try NSE market-data-pre-open API
    try:
        url = "https://www.nseindia.com/api/market-data-pre-open?key=ALL"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": "https://www.nseindia.com/market-data/live-equity-market",
        }
        
        with requests.Session() as session:
            session.headers.update(headers)
            session.get("https://www.nseindia.com", timeout=10)
            time.sleep(1)
            
            response = session.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                stocks = data.get("data", [])
                symbols = [stock["metadata"]["symbol"] for stock in stocks if "metadata" in stock]
                
                if len(symbols) > 100:
                    print(f"✅ Fetched {len(symbols)} symbols from NSE pre-open API")
                    return symbols
    except Exception as e:
        print(f"⚠️ NSE pre-open API failed: {e}")
    
    # Method 3: Load from cached file
    try:
        if os.path.exists("nse_total_market_symbols.json"):
            with open("nse_total_market_symbols.json", "r") as f:
                symbols = json.load(f)
                print(f"✅ Loaded {len(symbols)} symbols from cached file")
                return symbols
    except Exception as e:
        print(f"⚠️ Cached file load failed: {e}")
    
    print("⚠️ All symbol fetch methods failed - will use Bhavcopy to extract symbols")
    return None  # Signal to extract from Bhavcopy


def fetch_nse_bhavcopy(date=None):
    """
    Fetch NSE Bhavcopy (all equity prices) for a given date
    Returns pandas DataFrame
    """
    if date is None:
        date = datetime.now()
    
    # Try current date first, then previous days (market closed on weekends/holidays)
    for days_back in range(5):
        try_date = date - timedelta(days=days_back)
        date_str = try_date.strftime("%d%b%Y").upper()
        year = try_date.strftime("%Y")
        month = try_date.strftime("%b").upper()
        
        url = f"https://www1.nseindia.com/content/historical/EQUITIES/{year}/{month}/cm{date_str}bhav.csv.zip"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.nseindia.com"
        }
        
        try:
            print(f"📥 Trying to fetch data for {date_str}...")
            session = requests.Session()
            session.get("https://www.nseindia.com", headers=headers, timeout=10)
            
            r = session.get(url, headers=headers, timeout=15)
            r.raise_for_status()
            
            z = ZipFile(BytesIO(r.content))
            df = pd.read_csv(z.open(z.namelist()[0]))
            
            print(f"✅ Successfully fetched Bhavcopy for {date_str}")
            print(f"   Total records: {len(df)}")
            return df, try_date
            
        except Exception as e:
            print(f"❌ Failed for {date_str}: {e}")
            continue
    
    raise Exception("Could not fetch Bhavcopy for last 5 days")


def filter_and_save_nifty_750(df, symbols, report_date):
    """
    Filter Bhavcopy for Nifty Total Market symbols and save as JSON
    """
    # Filter only EQ series (equity) and matching symbols
    df_filtered = df[
        (df["SERIES"] == "EQ") & 
        (df["SYMBOL"].isin(symbols))
    ].copy()
    
    print(f"📊 Filtered {len(df_filtered)} / {len(symbols)} symbols")
    
    # Calculate percentage change
    df_filtered["PREV_CLOSE"] = df_filtered["PREVCLOSE"]
    df_filtered["CHANGE"] = df_filtered["CLOSE"] - df_filtered["PREV_CLOSE"]
    df_filtered["CHANGE_PCT"] = (df_filtered["CHANGE"] / df_filtered["PREV_CLOSE"]) * 100
    
    # Select and rename columns for frontend
    result = df_filtered[[
        "SYMBOL",
        "OPEN",
        "HIGH",
        "LOW",
        "CLOSE",
        "PREV_CLOSE",
        "CHANGE",
        "CHANGE_PCT",
        "TOTTRDQTY",  # Total traded quantity (volume)
        "TOTTRDVAL"   # Total traded value
    ]].copy()
    
    result.columns = [
        "symbol",
        "open",
        "high",
        "low",
        "close",
        "prev_close",
        "change",
        "change_pct",
        "volume",
        "turnover"
    ]
    
    # Round numerical values
    result["change_pct"] = result["change_pct"].round(2)
    result["change"] = result["change"].round(2)
    
    # Sort by volume (most traded first)
    result = result.sort_values("volume", ascending=False)
    
    # Create output JSON
    output = {
        "status": "success",
        "date": report_date.strftime("%d-%b-%Y"),
        "fetched_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_stocks": len(result),
        "data": result.to_dict(orient="records")
    }
    
    # Save to JSON
    with open("nifty_total_market.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Saved data to nifty_total_market.json")
    print(f"   Date: {report_date.strftime('%d-%b-%Y')}")
    print(f"   Stocks: {len(result)}")
    print(f"   Top 5 by volume:")
    for idx, row in result.head(5).iterrows():
        print(f"      {row['symbol']}: ₹{row['close']:.2f} ({row['change_pct']:+.2f}%)")
    
    return output


def main():
    """Main execution"""
    print("🚀 Starting Nifty Total Market data fetch...\n")
    
    # Step 1: Fetch NSE Bhavcopy first (needed either way)
    df, report_date = fetch_nse_bhavcopy()
    
    # Step 2: Get Nifty Total Market symbols
    symbols = get_nifty_total_market_symbols()
    
    # If no symbols from API, extract from Bhavcopy itself
    if symbols is None:
        print("📊 Extracting symbols directly from Bhavcopy...")
        symbols = get_nifty_total_market_symbols_from_bhavcopy(df)
    
    if not symbols:
        print("❌ Could not get any symbols!")
        return
    
    # Step 3: Filter and save
    filter_and_save_nifty_750(df, symbols, report_date)
    
    print("\n✅ All done!")


if __name__ == "__main__":
    main()
