"""
Daily FII/DII Data Fetcher for GitHub Actions
Fetches data and saves to JSON file for cloud deployment
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
                
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            category = item.get('category', '').upper()
                            
                            if 'FII' in category or 'FPI' in category:
                                fii_buy = float(str(item.get('buyValue', 0) or 0).replace(',', ''))
                                fii_sell = float(str(item.get('sellValue', 0) or 0).replace(',', ''))
                                fii_net = float(str(item.get('netValue', 0) or 0).replace(',', ''))
                                fii_data = {
                                    'buy': round(fii_buy, 2),
                                    'sell': round(fii_sell, 2),
                                    'net': round(fii_net, 2)
                                }
                            
                            elif 'DII' in category:
                                dii_buy = float(str(item.get('buyValue', 0) or 0).replace(',', ''))
                                dii_sell = float(str(item.get('sellValue', 0) or 0).replace(',', ''))
                                dii_net = float(str(item.get('netValue', 0) or 0).replace(',', ''))
                                dii_data = {
                                    'buy': round(dii_buy, 2),
                                    'sell': round(dii_sell, 2),
                                    'net': round(dii_net, 2)
                                }
                
                if fii_data or dii_data:
                    print("✅ Fetched from NSE API")
                    return {
                        'fii': fii_data,
                        'dii': dii_data,
                        'status': 'success',
                        'source': 'NSE API',
                        'fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
                        'date': item.get('date', 'Unknown') if isinstance(data, list) and len(data) > 0 else 'Unknown'
                    }
    except Exception as e:
        print(f"❌ NSE API failed: {e}")
    
    return None


def fetch_fii_dii_from_moneycontrol():
    """Try to fetch from MoneyControl"""
    try:
        from bs4 import BeautifulSoup
        
        url = "https://www.moneycontrol.com/stocks/marketstats/fii_dii_activity/index.php"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.find_all('table', class_=['tbldata14', 'mctable1'])
            
            fii_data = None
            dii_data = None
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 4:
                        row_text = cells[0].get_text().strip()
                        
                        try:
                            if 'FII' in row_text or 'FPI' in row_text:
                                buy_val = float(cells[1].get_text().strip().replace(',', ''))
                                sell_val = float(cells[2].get_text().strip().replace(',', ''))
                                net_val = float(cells[3].get_text().strip().replace(',', ''))
                                fii_data = {
                                    'buy': round(buy_val, 2),
                                    'sell': round(sell_val, 2),
                                    'net': round(net_val, 2)
                                }
                            
                            if 'DII' in row_text:
                                buy_val = float(cells[1].get_text().strip().replace(',', ''))
                                sell_val = float(cells[2].get_text().strip().replace(',', ''))
                                net_val = float(cells[3].get_text().strip().replace(',', ''))
                                dii_data = {
                                    'buy': round(buy_val, 2),
                                    'sell': round(sell_val, 2),
                                    'net': round(net_val, 2)
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
                    'fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
                    'date': datetime.now().strftime('%d-%b-%Y')
                }
    except Exception as e:
        print(f"❌ MoneyControl failed: {e}")
    
    return None


def main():
    """Main function to fetch and save FII/DII data"""
    print("🔄 Fetching FII/DII data...")
    
    # Try NSE first
    data = fetch_fii_dii_from_nse()
    
    # Fallback to MoneyControl
    if not data:
        print("⚠️ NSE failed, trying MoneyControl...")
        data = fetch_fii_dii_from_moneycontrol()
    
    if data:
        # Save to JSON file
        with open('fii_dii_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Data saved successfully!")
        print(f"   FII Net: ₹{data['fii']['net'] if data.get('fii') else 'N/A'} Cr")
        print(f"   DII Net: ₹{data['dii']['net'] if data.get('dii') else 'N/A'} Cr")
        print(f"   Source: {data['source']}")
        print(f"   Date: {data.get('date', 'Unknown')}")
    else:
        print("❌ All sources failed!")
        # Create placeholder file
        placeholder = {
            'fii': {'buy': 0.0, 'sell': 0.0, 'net': 0.0},
            'dii': {'buy': 0.0, 'sell': 0.0, 'net': 0.0},
            'status': 'error',
            'source': 'None',
            'fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'date': 'Unknown'
        }
        with open('fii_dii_data.json', 'w') as f:
            json.dump(placeholder, f, indent=2)
        print("⚠️ Placeholder data saved")


if __name__ == "__main__":
    main()
