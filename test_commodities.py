#!/usr/bin/env python3
"""
Quick test script to debug commodity fetching
"""
import yfinance as yf
import math

print("=" * 60)
print("TESTING COMMODITY DATA FETCHING")
print("=" * 60)

tickers = ['INR=X', 'CL=F', 'GC=F', 'SI=F', 'BTC-USD', 'ETH-USD']

print("\n1. Testing BULK download:")
print("-" * 60)
try:
    data = yf.download(tickers, period='5d', interval='1d', progress=False, group_by='ticker')
    print(f"✓ Bulk download successful")
    print(f"  Data shape: {data.shape}")
    print(f"  Columns: {data.columns.tolist()[:10]}...")  # First 10 columns
    
    # Try to extract one ticker
    if len(tickers) > 1:
        if 'INR=X' in data.columns.get_level_values(0):
            inr_data = data['INR=X']
            print(f"\n✓ INR=X found in bulk data")
            print(f"  Latest close: {inr_data['Close'].iloc[-1]}")
        else:
            print(f"\n❌ INR=X NOT found in bulk data")
            print(f"  Available tickers: {data.columns.get_level_values(0).unique().tolist()}")
except Exception as e:
    print(f"❌ Bulk download failed: {e}")
    import traceback
    traceback.print_exc()

print("\n\n2. Testing INDIVIDUAL fetches:")
print("-" * 60)

for ticker in tickers:
    try:
        print(f"\nFetching {ticker}...")
        t = yf.Ticker(ticker)
        hist = t.history(period='5d')
        
        if hist.empty:
            print(f"  ❌ Empty data")
        elif len(hist) < 2:
            print(f"  ⚠️  Only {len(hist)} data point(s)")
        else:
            current = float(hist['Close'].iloc[-1])
            previous = float(hist['Close'].iloc[-2])
            
            if math.isnan(current) or math.isnan(previous):
                print(f"  ❌ NaN values")
            else:
                change = ((current - previous) / previous) * 100
                print(f"  ✓ Current: {current:.4f}")
                print(f"  ✓ Previous: {previous:.4f}")
                print(f"  ✓ Change: {change:+.2f}%")
                
                # Special handling for INR=X
                if ticker == 'INR=X' and current < 1:
                    inverted = 1 / current
                    print(f"  ℹ️  Inverted rate: ₹{inverted:.2f}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
