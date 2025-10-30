"""
Daily FII/DII Data Fetcher for GitHub Actions
Fetches data and saves to both dated and current JSON files
Keeps compatibility with workflow that maintains last 2 days
"""

import requests
import json
import time
from datetime import datetime


def fetch_fii_dii_from_nse():
    """Try to fetch from NSE API"""
    try:
        url = "https://www.nseindia.com/api/fiidiiTradeReact"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/reports/fii-dii',
            'Accept-Encoding': 'gzip, deflate, br'
        }
        
        with requests.Session() as session:
            session.headers.update(headers)
            session.get("https://www.nseindia.com", timeout=10)
            time.sleep(2)
            
            response = session.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                fii_data = None
                dii_data = None
                report_date = None
                
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            category = item.get('category', '').upper()
                            report_date = item.get('date', report_date)

                            if 'FII' in category or 'FPI' in category:
                                fii_data = {
                                    'buy': float(str(item.get('buyValue', 0)).replace(',', '') or 0),
                                    'sell': float(str(item.get('sellValue', 0)).replace(',', '') or 0),
                                    'net': float(str(item.get('netValue', 0)).replace(',', '') or 0)
                                }

                            elif 'DII' in category:
                                dii_data = {
                                    'buy': float(str(item.get('buyValue', 0)).replace(',', '') or 0),
                                    'sell': float(str(item.get('sellValue', 0)).replace(',', '') or 0),
                                    'net': float(str(item.get('netValue', 0)).replace(',', '') or 0)
                                }

                if fii_data or dii_data:
                    print("✅ Fetched from NSE API")
                    return {
                        'fii': fii_data,
                        'dii': dii_data,
                        'status': 'success',
                        'source': 'NSE API',
                        'fetched_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
                        'date': report_date or datetime.utcnow().strftime('%d-%b-%Y')
                    }
    except Exception as e:
        print(f"❌ NSE API failed: {e}")
    
    return None


def fetch_fii_dii_from_moneycontrol():
    """Fallback: Fetch from MoneyControl if NSE fails"""
    try:
        from bs4 import BeautifulSoup
        
        url = "https://www.moneycontrol.com/stocks/marketstats/fii_dii_activity/index.php"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.find_all('table', class_=['tbldata14', 'mctable1'])
            
            fii_data = None
            dii_data = None

            for table in tables:
                for row in table.find_all('tr'):
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 4:
                        row_text = cells[0].get_text().strip()
                        try:
                            if 'FII' in row_text or 'FPI' in row_text:
                                fii_data = {
                                    'buy': float(cells[1].get_text().strip().replace(',', '') or 0),
                                    'sell': float(cells[2].get_text().strip().replace(',', '') or 0),
                                    'net': float(cells[3].get_text().strip().replace(',', '') or 0)
                                }
                            elif 'DII' in row_text:
                                dii_data = {
                                    'buy': float(cells[1].get_text().strip().replace(',', '') or 0),
                                    'sell': float(cells[2].get_text().strip().replace(',', '') or 0),
                                    'net': float(cells[3].get_text().strip().replace(',', '') or 0)
                                }
                        except:
                            pass

            if fii_data or dii_data:
                print("✅ Fetched from MoneyControl")
                return {
                    'fii': fii_data,
                    'dii': dii_data,
                    'status': 'success',
                    'source': 'MoneyControl',
                    'fetched_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
                    'date': datetime.utcnow().strftime('%d-%b-%Y')
                }
    except Exception as e:
        print(f"❌ MoneyControl failed: {e}")
    
    return None


def main():
    """Main function to fetch and save FII/DII data"""
    print("🔄 Fetching FII/DII data...")
    
    # Try NSE first, fallback to MoneyControl
    data = fetch_fii_dii_from_nse() or fetch_fii_dii_from_moneycontrol()
    
    if not data:
        print("❌ All sources failed!")
        data = {
            'fii': {'buy': 0.0, 'sell': 0.0, 'net': 0.0},
            'dii': {'buy': 0.0, 'sell': 0.0, 'net': 0.0},
            'status': 'error',
            'source': 'None',
            'fetched_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'date': 'Unknown'
        }

    # File naming (date-based and latest)
    today_str = datetime.utcnow().strftime('%Y-%m-%d')
    dated_filename = f"fii_dii_data_{today_str}.json"
    latest_filename = "fii_dii_data.json"

    # Save both
    with open(dated_filename, 'w') as f:
        json.dump(data, f, indent=2)
    with open(latest_filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Data saved successfully!")
    print(f"   Dated file: {dated_filename}")
    print(f"   Latest file: {latest_filename}")
    print(f"   FII Net: ₹{data['fii']['net'] if data.get('fii') else 'N/A'} Cr")
    print(f"   DII Net: ₹{data['dii']['net'] if data.get('dii') else 'N/A'} Cr")
    print(f"   Source: {data['source']}")
    print(f"   Date: {data.get('date', 'Unknown')}")


if __name__ == "__main__":
    main()
