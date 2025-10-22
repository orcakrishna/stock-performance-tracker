"""
Test script to verify FII/DII data fetching
"""
import requests
import time
import json

def test_nse_api():
    """Test NSE API directly"""
    print("Testing NSE API...")
    
    url = "https://www.nseindia.com/api/fiidiiTradeReact"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.nseindia.com/reports/fii-dii',
        'Accept-Encoding': 'gzip, deflate, br'
    }
    
    try:
        with requests.Session() as session:
            session.headers.update(headers)
            # Set cookies
            print("Setting cookies...")
            session.get("https://www.nseindia.com", timeout=10)
            time.sleep(2)
            
            print("Fetching FII/DII data...")
            response = session.get(url, timeout=15)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\nResponse Type: {type(data)}")
                print(f"\nFull Response:")
                print(json.dumps(data, indent=2))
                
                if isinstance(data, list) and len(data) > 0:
                    print(f"\nFirst item keys: {data[0].keys() if isinstance(data[0], dict) else 'Not a dict'}")
                    print(f"\nFirst item:")
                    print(json.dumps(data[0], indent=2))
                
                return True
            else:
                print(f"Failed with status: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_nse_api()
