"""
Test FII/DII date checking logic
"""
import json
from datetime import datetime
import pandas as pd

# Load the JSON file
with open('fii_dii_data.json', 'r') as f:
    data = json.load(f)

file_date = data.get('date', '')
print(f"File date: {file_date}")

# Check with UTC time (NEW FIX)
today_utc = datetime.utcnow().strftime('%d-%b-%Y')
yesterday_utc = (datetime.utcnow() - pd.Timedelta(days=1)).strftime('%d-%b-%Y')

print(f"Today (UTC): {today_utc}")
print(f"Yesterday (UTC): {yesterday_utc}")

# Check if file date matches
if file_date == today_utc:
    print("✅ File has TODAY's data (UTC)")
elif file_date == yesterday_utc:
    print("✅ File has YESTERDAY's data (UTC) - This is acceptable!")
else:
    print(f"❌ File data is old: {file_date}")

# Show data
print(f"\nFII Net: ₹{data['fii']['net']} Cr")
print(f"DII Net: ₹{data['dii']['net']} Cr")
print(f"Source: {data['source']}")
print(f"Fetched at: {data['fetched_at']}")
