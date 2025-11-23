#!/usr/bin/env python3
"""
Test the fixed commodity fetching function
"""
import sys
sys.path.insert(0, '.')

from data_fetchers import _fetch_commodities_individual
from config import COMMODITIES

print("=" * 60)
print("TESTING FIXED COMMODITY FUNCTION")
print("=" * 60)

tickers_list = [
    COMMODITIES['oil'],
    COMMODITIES['gold'],
    COMMODITIES['silver'],
    COMMODITIES['btc'],
    COMMODITIES['ethereum'],
    'INR=X'
]

prices = _fetch_commodities_individual(tickers_list)

print("\n" + "=" * 60)
print("RESULTS:")
print("=" * 60)

for key, value in sorted(prices.items()):
    print(f"{key:25} = {value}")

print("\n" + "=" * 60)
print("KEY CHECKS:")
print("=" * 60)
print(f"✓ USD/INR shows real price: {prices.get('usd_inr', 'MISSING')}")
print(f"✓ Oil has price: {prices.get('oil', 'MISSING')}")
print(f"✓ Gold has price: {prices.get('gold', 'MISSING')}")
print(f"✓ BTC has price: {prices.get('btc', 'MISSING')}")

if prices.get('usd_inr', '') != '₹84.55' and prices.get('usd_inr', '') != '--':
    print("\n✅ SUCCESS: USD/INR is fetching live data!")
else:
    print("\n❌ FAIL: USD/INR still using fallback")

if prices.get('oil', '') != '--':
    print("✅ SUCCESS: Oil price is being fetched!")
else:
    print("❌ FAIL: Oil price is blank")
