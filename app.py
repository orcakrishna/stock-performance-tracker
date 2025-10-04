import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import time
import yfinance as yf
import pytz
import os
import json

# Page configuration
st.set_page_config(
    page_title="NSE Stock Performance",
    page_icon="📈",
    layout="wide"
)

# Custom CSS for better appearance with dark background
st.markdown("""
<style>
    .main {
        background-color: #1e1e1e;
        padding: 2rem;
    }
    .stApp {
        background-color: #1e1e1e;
    }
    h1, h2, h3, p, label, div {
        color: #ffffff !important;
    }
    .dataframe {
        background-color: #2d2d2d;
        color: #ffffff;
    }
    thead tr th {
        background-color: #3d3d3d !important;
        color: #ffffff !important;
        font-weight: bold;
        border: 1px solid #555;
    }
    tbody tr td {
        background-color: #2d2d2d !important;
        color: #ffffff !important;
        border: 1px solid #555;
    }
    .positive {
        color: #00ff00 !important;
        font-weight: bold;
    }
    .negative {
        color: #ff4444 !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Title and info boxes on the same row
col_title, col_currency, col_commodities, col_time = st.columns([2, 1, 1, 1])

with col_title:
    st.title("📊 Indian Stock Performance Tracker")
    st.markdown("View 1-month, 2-month, and 3-month performance of NSE/BSE stocks.")

with col_currency:
    # Get exchange rates (using Yahoo Finance)
    exchange_rates = {}
    currencies = {
        'USD': 'USDINR=X',
        'EUR': 'EURINR=X',
        'GBP': 'GBPINR=X',
        'CAD': 'CADINR=X',
        'CHF': 'CHFINR=X'
    }
    
    for currency, ticker_symbol in currencies.items():
        try:
            ticker = yf.Ticker(ticker_symbol)
            rate = ticker.history(period='1d')['Close'].iloc[-1]
            exchange_rates[currency] = f"₹{rate:.2f}"
        except:
            exchange_rates[currency] = "--"
    
    st.markdown("**💱 Currency (to INR)**")
    emoji = {'USD': '💵', 'EUR': '💶', 'GBP': '💷', 'CAD': '🍁', 'CHF': '🇨🇭'}
    currency_html = '<div style="display: flex; flex-wrap: wrap; gap: 5px;">'
    for currency, rate in exchange_rates.items():
        currency_html += f'''
        <div style='padding: 8px; background-color: #2d2d2d; border-radius: 5px; flex: 1; min-width: 45%;'>
            <p style='margin: 0; font-size: 12px; color: #888;'>{emoji[currency]} {currency}</p>
            <p style='margin: 2px 0 0 0; font-size: 14px; color: #fff; font-weight: bold;'>{rate}</p>
        </div>
        '''
    currency_html += '</div>'
    st.markdown(currency_html, unsafe_allow_html=True)

with col_commodities:
    # Get commodities and crypto prices
    commodities = {}
    
    # Oil (WTI Crude)
    try:
        oil = yf.Ticker('CL=F')
        oil_price = oil.history(period='1d')['Close'].iloc[-1]
        commodities['Oil'] = f"${oil_price:.2f}"
    except:
        commodities['Oil'] = "--"
    
    # Gold
    try:
        gold = yf.Ticker('GC=F')
        gold_price = gold.history(period='1d')['Close'].iloc[-1]
        commodities['Gold'] = f"${gold_price:.2f}"
    except:
        commodities['Gold'] = "--"
    
    # Bitcoin
    try:
        btc = yf.Ticker('BTC-USD')
        btc_price = btc.history(period='1d')['Close'].iloc[-1]
        commodities['Bitcoin'] = f"${btc_price:,.0f}"
    except:
        commodities['Bitcoin'] = "--"
    
    st.markdown("**💰 Commodities**")
    st.markdown(f"""
    <div style='padding: 8px; background-color: #2d2d2d; border-radius: 5px; margin-bottom: 5px;'>
        <p style='margin: 0; font-size: 12px; color: #888;'>🛢️ Oil (WTI)</p>
        <p style='margin: 2px 0 0 0; font-size: 14px; color: #fff; font-weight: bold;'>{commodities['Oil']}</p>
    </div>
    <div style='padding: 8px; background-color: #2d2d2d; border-radius: 5px; margin-bottom: 5px;'>
        <p style='margin: 0; font-size: 12px; color: #888;'>🥇 Gold</p>
        <p style='margin: 2px 0 0 0; font-size: 14px; color: #fff; font-weight: bold;'>{commodities['Gold']}</p>
    </div>
    <div style='padding: 8px; background-color: #2d2d2d; border-radius: 5px;'>
        <p style='margin: 0; font-size: 12px; color: #888;'>₿ Bitcoin</p>
        <p style='margin: 2px 0 0 0; font-size: 14px; color: #fff; font-weight: bold;'>{commodities['Bitcoin']}</p>
    </div>
    """, unsafe_allow_html=True)

with col_time:
    # Get current time in different timezones
    ist = pytz.timezone('Asia/Kolkata')
    edt = pytz.timezone('America/New_York')
    
    current_time_utc = datetime.now(pytz.utc)
    ist_time = current_time_utc.astimezone(ist)
    edt_time = current_time_utc.astimezone(edt)
    
    st.markdown("**🕐 Time**")
    st.markdown(f"""
    <div style='padding: 8px; background-color: #2d2d2d; border-radius: 5px; margin-bottom: 5px;'>
        <p style='margin: 0; font-size: 12px; color: #888;'>IST (India)</p>
        <p style='margin: 2px 0 0 0; font-size: 14px; color: #fff; font-weight: bold;'>{ist_time.strftime('%I:%M %p')}</p>
    </div>
    <div style='padding: 8px; background-color: #2d2d2d; border-radius: 5px; margin-bottom: 5px;'>
        <p style='margin: 0; font-size: 12px; color: #888;'>EDT (US East)</p>
        <p style='margin: 2px 0 0 0; font-size: 14px; color: #fff; font-weight: bold;'>{edt_time.strftime('%I:%M %p')}</p>
    </div>
    <div style='padding: 8px; background-color: #2d2d2d; border-radius: 5px;'>
        <p style='margin: 0; font-size: 12px; color: #888;'>Date</p>
        <p style='margin: 2px 0 0 0; font-size: 14px; color: #fff; font-weight: bold;'>{ist_time.strftime('%d %b %Y')}</p>
    </div>
    """, unsafe_allow_html=True)

# Fallback hardcoded lists (used if dynamic fetch fails)
FALLBACK_NIFTY_50 = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'HINDUNILVR.NS',
    'INFY.NS', 'ITC.NS', 'KOTAKBANK.NS', 'BHARTIARTL.NS',
    'LT.NS', 'SBIN.NS', 'BAJFINANCE.NS', 'HCLTECH.NS', 'ASIANPAINT.NS',
    'MARUTI.NS', 'TITAN.NS', 'SUNPHARMA.NS', 'AXISBANK.NS', 'NTPC.NS',
    'NESTLEIND.NS', 'ULTRACEMCO.NS', 'TATAMOTORS.NS', 'POWERGRID.NS',
    'BAJAJ-AUTO.NS', 'TATASTEEL.NS', 'JSWSTEEL.NS', 'GRASIM.NS', 'ADANIPORTS.NS',
    'TECHM.NS', 'BAJAJFINSV.NS', 'WIPRO.NS', 'UPL.NS', 'DRREDDY.NS', 'CIPLA.NS',
    'HINDALCO.NS', 'TATACONSUM.NS', 'BPCL.NS', 'SHREECEM.NS', 'INDUSINDBK.NS',
    'IOC.NS', 'ONGC.NS', 'COALINDIA.NS', 'SBILIFE.NS', 'HDFCLIFE.NS',
    'DIVISLAB.NS', 'EICHERMOT.NS', 'HEROMOTOCO.NS', 'BRITANNIA.NS'
]

FALLBACK_NIFTY_NEXT_50 = [
    'ADANIENT.NS', 'AMBUJACEM.NS', 'BANDHANBNK.NS', 'BERGEPAINT.NS', 'BEL.NS',
    'BOSCHLTD.NS', 'CHOLAFIN.NS', 'COLPAL.NS', 'DABUR.NS', 'DLF.NS',
    'GODREJCP.NS', 'GRASIM.NS', 'HAVELLS.NS', 'HDFCAMC.NS', 'HDFCLIFE.NS',
    'ICICIPRULI.NS', 'IDEA.NS', 'INDIGO.NS', 'JINDALSTEL.NS', 'LICHSGFIN.NS',
    'LUPIN.NS', 'MARICO.NS', 'MCDOWELL-N.NS', 'MUTHOOTFIN.NS', 'NMDC.NS',
    'NYKAA.NS', 'PAGEIND.NS', 'PETRONET.NS', 'PIDILITIND.NS', 'PNB.NS',
    'RECLTD.NS', 'SBICARD.NS', 'SHRIRAMFIN.NS', 'SIEMENS.NS', 'TATAPOWER.NS',
    'TORNTPHARM.NS', 'TRENT.NS', 'VEDL.NS', 'VOLTAS.NS', 'ZOMATO.NS'
]

FALLBACK_BSE_SENSEX = [
    'RELIANCE.BO', 'TCS.BO', 'HDFCBANK.BO', 'ICICIBANK.BO', 'HINDUNILVR.BO',
    'INFY.BO', 'ITC.BO', 'BHARTIARTL.BO', 'LT.BO', 'SBIN.BO',
    'BAJFINANCE.BO', 'HCLTECH.BO', 'ASIANPAINT.BO', 'MARUTI.BO', 'TITAN.BO',
    'SUNPHARMA.BO', 'AXISBANK.BO', 'NTPC.BO', 'ULTRACEMCO.BO', 'TATAMOTORS.BO',
    'POWERGRID.BO', 'BAJAJ-AUTO.BO', 'TATASTEEL.BO', 'JSWSTEEL.BO', 'TECHM.BO',
    'WIPRO.BO', 'NESTLEIND.BO', 'KOTAKBANK.BO', 'ADANIPORTS.BO', 'INDUSINDBK.BO'
]

@st.cache_data(ttl=86400)  # Cache for 24 hours
def fetch_nifty_50_from_nse():
    """Fetch Nifty 50 stocks dynamically from NSE website"""
    try:
        # More complete headers to mimic real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.nseindia.com/market-data/live-equity-market',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        session = requests.Session()
        
        # First request to get cookies
        session.get("https://www.nseindia.com", headers=headers, timeout=15)
        time.sleep(2)
        
        # Second request to API
        url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            stocks = [item['symbol'] + '.NS' for item in data.get('data', []) if 'symbol' in item]
            if len(stocks) > 40:  # Validate we got reasonable data
                print(f"✅ Successfully fetched {len(stocks)} stocks from NSE")
                return stocks[:50]  # Return top 50
        else:
            print(f"NSE API returned status code: {response.status_code}")
    except Exception as e:
        print(f"❌ NSE fetch failed: {str(e)}")
    
    return None

@st.cache_data(ttl=86400)
def fetch_nifty_500_from_wikipedia():
    """Fetch Nifty 500 stocks from Wikipedia as fallback"""
    try:
        url = "https://en.wikipedia.org/wiki/NIFTY_500"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            tables = soup.find_all('table', {'class': 'wikitable'})
            
            stocks = []
            for table in tables:
                rows = table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) > 1:
                        symbol = cols[1].text.strip()
                        if symbol and symbol != '':
                            stocks.append(f"{symbol}.NS")
            
            if len(stocks) > 100:
                return stocks[:500]
    except Exception as e:
        print(f"Wikipedia fetch failed: {str(e)}")
    
    return None

@st.cache_data(ttl=86400)
def get_stock_list(category_name):
    """Get stock list with dynamic fetching and fallback"""
    
    if category_name == 'Nifty 50':
        # Try NSE first
        stocks = fetch_nifty_50_from_nse()
        if stocks:
            return stocks, "✅ Fetched from NSE"
        
        # Fallback to hardcoded
        return FALLBACK_NIFTY_50, "⚠️ Using cached list"
    
    elif category_name == 'Nifty Next 50':
        # For now use fallback, can add dynamic fetch later
        return FALLBACK_NIFTY_NEXT_50, "⚠️ Using cached list"
    
    elif category_name == 'BSE Sensex':
        return FALLBACK_BSE_SENSEX, "⚠️ Using cached list"
    
    elif category_name == 'Nifty 500 (Sample)':
        # Try Wikipedia first
        stocks = fetch_nifty_500_from_wikipedia()
        if stocks:
            return stocks, "✅ Fetched from Wikipedia"
        
        # Fallback
        fallback = FALLBACK_NIFTY_50 + FALLBACK_NIFTY_NEXT_50
        return fallback, "⚠️ Using cached list"
    
    return [], "❌ No data available"

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_nse_index_data(index_name):
    """Fetch index data directly from NSE"""
    try:
        url = "https://www.nseindia.com/api/allIndices"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/'
        }
        
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        time.sleep(0.5)
        
        response = session.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Try exact match first
            for item in data.get('data', []):
                if item.get('index', '').upper() == index_name.upper():
                    current_price = item.get('last', 0)
                    change_pct = item.get('percentChange', 0)
                    return current_price, change_pct
            
            # Try partial match for "Total Market"
            if 'TOTAL' in index_name.upper():
                for item in data.get('data', []):
                    idx_name = item.get('index', '').upper()
                    if 'TOTAL' in idx_name and 'MARKET' in idx_name:
                        current_price = item.get('last', 0)
                        change_pct = item.get('percentChange', 0)
                        return current_price, change_pct
        
        return None, None
    except Exception as e:
        print(f"NSE index fetch error: {str(e)}")
        return None, None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_index_performance(index_symbol, index_name=None):
    """Fetch index performance from Yahoo Finance or NSE"""
    # Try NSE first for specific indices
    if index_name:
        nse_price, nse_change = get_nse_index_data(index_name)
        if nse_price and nse_change:
            return nse_price, nse_change
    
    # Fallback to Yahoo Finance only if symbol is provided
    if index_symbol:
        try:
            index = yf.Ticker(index_symbol)
            hist = index.history(period='5d')
            
            if hist.empty or len(hist) < 2:
                return None, None
            
            current_price = hist['Close'].iloc[-1]
            previous_price = hist['Close'].iloc[-2]
            change_pct = ((current_price - previous_price) / previous_price) * 100
            
            return current_price, change_pct
        except:
            return None, None
    
    return None, None

def get_stock_performance(ticker):
    """Fetch accurate stock performance using Yahoo Finance"""
    symbol = ticker.replace('.NS', '').replace('.BO', '')
    
    try:
        # Fetch historical data for 4 months
        stock = yf.Ticker(ticker)
        hist = stock.history(period='4mo')
        
        if hist.empty or len(hist) < 20:
            return None
        
        # Remove timezone info for easier comparison
        hist.index = hist.index.tz_localize(None)
        
        # Get current price (most recent close)
        current_price = hist['Close'].iloc[-1]
        current_date = hist.index[-1]
        
        # Calculate target dates
        date_1w = current_date - pd.Timedelta(days=7)
        date_1m = current_date - pd.Timedelta(days=30)
        date_2m = current_date - pd.Timedelta(days=60)
        date_3m = current_date - pd.Timedelta(days=90)
        
        # Find closest available prices
        def get_closest_price(target_date):
            # Find the closest date in history
            idx = hist.index.get_indexer([target_date], method='nearest')[0]
            return hist['Close'].iloc[idx]
        
        price_1w = get_closest_price(date_1w)
        price_1m = get_closest_price(date_1m)
        price_2m = get_closest_price(date_2m)
        price_3m = get_closest_price(date_3m)
        
        # Calculate percentage changes
        change_1w = ((current_price - price_1w) / price_1w) * 100
        change_1m = ((current_price - price_1m) / price_1m) * 100
        change_2m = ((current_price - price_2m) / price_2m) * 100
        change_3m = ((current_price - price_3m) / price_3m) * 100
        
        return {
            'Stock Name': symbol,
            'Current Price': f"₹{current_price:.2f}",
            '1 Week %': round(change_1w, 2),
            '1 Month %': round(change_1m, 2),
            '2 Months %': round(change_2m, 2),
            '3 Months %': round(change_3m, 2)
        }
        
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None

def color_percentage(val):
    """Color code percentage values"""
    try:
        num_val = float(val)
        if num_val > 0:
            return f'<span style="color: #00ff00; font-weight: bold;">+{num_val}%</span>'
        elif num_val < 0:
            return f'<span style="color: #ff4444; font-weight: bold;">{num_val}%</span>'
        else:
            return f'<span style="color: #ffffff;">{num_val}%</span>'
    except:
        return val

# Directory for saved lists
SAVED_LISTS_DIR = "saved_stock_lists"

def ensure_saved_lists_dir():
    """Create directory for saved lists if it doesn't exist"""
    if not os.path.exists(SAVED_LISTS_DIR):
        os.makedirs(SAVED_LISTS_DIR)

def save_list_to_csv(list_name, stocks):
    """Save a stock list to CSV file"""
    ensure_saved_lists_dir()
    filename = os.path.join(SAVED_LISTS_DIR, f"{list_name}.csv")
    df = pd.DataFrame({'Symbol': stocks})
    df.to_csv(filename, index=False)

def load_list_from_csv(list_name):
    """Load a stock list from CSV file"""
    filename = os.path.join(SAVED_LISTS_DIR, f"{list_name}.csv")
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        return df['Symbol'].tolist()
    return None

def delete_list_csv(list_name):
    """Delete a stock list CSV file"""
    filename = os.path.join(SAVED_LISTS_DIR, f"{list_name}.csv")
    if os.path.exists(filename):
        os.remove(filename)

def load_all_saved_lists():
    """Load all saved lists from CSV files"""
    ensure_saved_lists_dir()
    saved_lists = {}
    if os.path.exists(SAVED_LISTS_DIR):
        for filename in os.listdir(SAVED_LISTS_DIR):
            if filename.endswith('.csv'):
                list_name = filename[:-4]  # Remove .csv extension
                stocks = load_list_from_csv(list_name)
                if stocks:
                    saved_lists[list_name] = stocks
    return saved_lists

def main():
    # Initialize session state for multiple saved lists
    if 'saved_lists' not in st.session_state:
        # Load saved lists from CSV files on startup
        st.session_state.saved_lists = load_all_saved_lists()
    if 'current_list_name' not in st.session_state:
        st.session_state.current_list_name = None
    
    # Sidebar for stock selection
    st.sidebar.header("📋 Stock Selection")
    
    # Category selection
    category = st.sidebar.selectbox(
        "Select Category",
        options=['Nifty 50', 'Nifty Next 50', 'BSE Sensex', 'Nifty 500 (Sample)', 'Custom Selection', 'Upload File'],
        index=0
    )
    
    # Determine stock list based on category
    if category in ['Nifty 50', 'Nifty Next 50', 'BSE Sensex', 'Nifty 500 (Sample)']:
        # Fetch stocks dynamically
        with st.spinner(f"Fetching {category} stock list..."):
            selected_stocks, fetch_status = get_stock_list(category)
            available_stocks = selected_stocks
        
        # Show fetch status
        if "✅" in fetch_status:
            st.sidebar.success(fetch_status)
        else:
            st.sidebar.warning(fetch_status)
    
    elif category == 'Upload File':
        st.sidebar.markdown("---")
        st.sidebar.markdown("**📤 Manage Stock Lists**")
        
        # Show saved lists
        if st.session_state.saved_lists:
            st.sidebar.markdown("**💾 Saved Lists:**")
            for list_name, stocks in st.session_state.saved_lists.items():
                col1, col2 = st.sidebar.columns([3, 1])
                with col1:
                    if st.button(f"📋 {list_name} ({len(stocks)})", key=f"load_{list_name}"):
                        st.session_state.current_list_name = list_name
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"del_{list_name}"):
                        # Delete from session state
                        del st.session_state.saved_lists[list_name]
                        # Delete CSV file
                        delete_list_csv(list_name)
                        if st.session_state.current_list_name == list_name:
                            st.session_state.current_list_name = None
                        st.rerun()
            st.sidebar.markdown("---")
        
        # Upload new list section
        st.sidebar.markdown("**📤 Upload New List**")
        
        # Download sample template
        sample_content = "RELIANCE.NS\nTCS.NS\nHDFCBANK.NS\nICICIBANK.NS\nINFY.NS"
        st.sidebar.download_button(
            label="📥 Download Sample Template",
            data=sample_content,
            file_name="sample_stocks.txt",
            mime="text/plain"
        )
        
        uploaded_file = st.sidebar.file_uploader(
            "Choose a file",
            type=['csv', 'txt'],
            help="Upload a file with stock symbols (one per line)"
        )
        
        # Process newly uploaded file
        if uploaded_file is not None:
            try:
                # Read the file
                content = uploaded_file.read().decode('utf-8')
                # Split by lines and clean up
                uploaded_stocks = [line.strip() for line in content.split('\n') if line.strip()]
                
                # Validate symbols
                valid_stocks = []
                for symbol in uploaded_stocks:
                    if '.NS' in symbol or '.BO' in symbol:
                        valid_stocks.append(symbol)
                    else:
                        # Default to .NS if no suffix
                        valid_stocks.append(f"{symbol}.NS")
                
                # Ask for list name
                list_name = st.sidebar.text_input(
                    "Enter a name for this list:",
                    value=uploaded_file.name.replace('.txt', '').replace('.csv', ''),
                    key="new_list_name"
                )
                
                if st.sidebar.button("💾 Save List"):
                    if list_name.strip():
                        # Save to session state
                        st.session_state.saved_lists[list_name.strip()] = valid_stocks
                        st.session_state.current_list_name = list_name.strip()
                        # Save to CSV file
                        save_list_to_csv(list_name.strip(), valid_stocks)
                        st.sidebar.success(f"✅ Saved '{list_name}' with {len(valid_stocks)} stocks to CSV")
                        st.rerun()
                    else:
                        st.sidebar.error("Please enter a list name")
                
                # Use uploaded stocks temporarily
                selected_stocks = valid_stocks
                available_stocks = valid_stocks
                
            except Exception as e:
                st.sidebar.error(f"Error reading file: {str(e)}")
                selected_stocks = []
                available_stocks = []
        
        # Use currently selected saved list
        elif st.session_state.current_list_name and st.session_state.current_list_name in st.session_state.saved_lists:
            selected_stocks = st.session_state.saved_lists[st.session_state.current_list_name]
            available_stocks = selected_stocks
            st.sidebar.success(f"✅ Using '{st.session_state.current_list_name}' ({len(selected_stocks)} stocks)")
        
        # No list selected
        else:
            st.sidebar.info(
                "📋 **Upload a stock list:**\n\n"
                "**Format:**\n"
                "- One symbol per line\n"
                "- Add .NS for NSE stocks\n"
                "- Add .BO for BSE stocks\n\n"
                "**Example:**\n"
                "```\n"
                "RELIANCE.NS\n"
                "TCS.NS\n"
                "INFY.BO\n"
                "```"
            )
            selected_stocks = []
            available_stocks = []
    else:  # Custom Selection
        # Get all available stocks from all categories
        all_nifty_50, _ = get_stock_list('Nifty 50')
        all_nifty_next_50, _ = get_stock_list('Nifty Next 50')
        all_bse, _ = get_stock_list('BSE Sensex')
        
        available_stocks = all_nifty_50 + all_nifty_next_50 + all_bse
        selected_stocks = st.sidebar.multiselect(
            "Select stocks",
            options=available_stocks,
            default=all_nifty_50[:10],
            format_func=lambda x: x.replace('.NS', '').replace('.BO', '')
        )
    
    # Sorting options
    st.sidebar.markdown("---")
    st.sidebar.header("Sorting Options")
    sort_by = st.sidebar.selectbox(
        "Sort by",
        options=['3 Months %', '2 Months %', '1 Month %', '1 Week %', 'Stock Name'],
        index=0
    )
    sort_order = st.sidebar.radio(
        "Order",
        options=['Best to Worst', 'Worst to Best'],
        index=0
    )
    
    if not selected_stocks:
        st.warning("⚠️ Please select at least one stock to view performance.")
        return
    
    # Display Market Indices at the top with custom styling
    st.markdown("### 📈 Market Indices - Today's Performance")
    
    # Custom CSS for smaller font and MUCH darker colors in metrics
    st.markdown("""
    <style>
        [data-testid="stMetricValue"] {
            font-size: 20px !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 14px !important;
        }
        [data-testid="stMetricDelta"] {
            font-size: 14px !important;
            font-weight: bold !important;
        }
        /* GREEN for positive (up arrow) */
        [data-testid="stMetricDelta"]:has(svg[data-testid="stMetricDeltaIcon-Up"]) {
            color: #00ff00 !important;
        }
        [data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Up"] {
            fill: #00ff00 !important;
        }
        /* RED for negative (down arrow) */
        [data-testid="stMetricDelta"]:has(svg[data-testid="stMetricDeltaIcon-Down"]) {
            color: #ff4444 !important;
        }
        [data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Down"] {
            fill: #ff4444 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Row 1: Major Indices (name: (yahoo_symbol, nse_name))
    indices_row1 = {
        'Nifty 50': ('^NSEI', 'NIFTY 50'),
        'Sensex': ('^BSESN', None),
        'Bank Nifty': ('^NSEBANK', 'NIFTY BANK'),
        'Nifty Midcap 50': ('^NSEMDCP50', 'NIFTY MIDCAP 50'),
        'Dow Jones': ('^DJI', None),
        'NASDAQ': ('^IXIC', None),
        'India VIX': ('^INDIAVIX', 'INDIA VIX')
    }
    
    cols1 = st.columns(len(indices_row1))
    for idx, (name, (symbol, nse_name)) in enumerate(indices_row1.items()):
        with cols1[idx]:
            price, change = get_index_performance(symbol, nse_name)
            if price and change:
                # Determine color based on change (same for all indices)
                # Green for positive, Red for negative
                color = "#00ff00" if change > 0 else "#ff4444"
                arrow = "↑" if change > 0 else "↓"
                
                # Display with HTML for colored percentage
                st.markdown(f"""
                <div style='padding: 10px; background-color: #2d2d2d; border-radius: 5px;'>
                    <p style='margin: 0; font-size: 14px; color: #888;'>{name}</p>
                    <p style='margin: 5px 0; font-size: 20px; color: #fff; font-weight: bold;'>{price:,.2f}</p>
                    <p style='margin: 0; font-size: 14px; font-weight: bold;'><span style='color: {color};'>{arrow} {change:+.2f}%</span></p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.metric(label=name, value="--", delta="--")
    
    # Row 2: Sectoral Indices
    st.markdown("**Sectoral Indices:**")
    indices_row2 = {
        'Nifty IT': '^CNXIT',
        'Nifty Pharma': '^CNXPHARMA',
        'Nifty Auto': '^CNXAUTO',
        'Nifty FMCG': '^CNXFMCG',
        'Nifty Metal': '^CNXMETAL'
    }
    
    cols2 = st.columns(len(indices_row2))
    for idx, (name, symbol) in enumerate(indices_row2.items()):
        with cols2[idx]:
            price, change = get_index_performance(symbol)
            if price and change:
                # Color based on change
                color = "#00ff00" if change > 0 else "#ff4444"
                arrow = "↑" if change > 0 else "↓"
                
                # Display with HTML for colored percentage
                st.markdown(f"""
                <div style='padding: 10px; background-color: #2d2d2d; border-radius: 5px;'>
                    <p style='margin: 0; font-size: 14px; color: #888;'>{name}</p>
                    <p style='margin: 5px 0; font-size: 20px; color: #fff; font-weight: bold;'>{price:,.2f}</p>
                    <p style='margin: 0; font-size: 14px; font-weight: bold;'><span style='color: {color};'>{arrow} {change:+.2f}%</span></p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.metric(label=name, value="--", delta="--")
    
    st.markdown("---")
    
    # Fetch data for selected stocks
    # Display title based on category
    if category == 'Upload File' and st.session_state.current_list_name:
        display_title = f"📊 {st.session_state.current_list_name} - Performance Summary ({len(selected_stocks)} Stock(s))"
    else:
        display_title = f"📊 {category} - Performance Summary ({len(selected_stocks)} Stock(s))"
    
    st.subheader(display_title)
    st.caption(f"🔽 Sorted by: **{sort_by}** ({sort_order})")
    
    with st.spinner(f"Fetching data for {len(selected_stocks)} stocks..."):
        stocks_data = []
        progress_bar = st.progress(0)
        
        for idx, ticker in enumerate(selected_stocks):
            data = get_stock_performance(ticker)
            if data:
                stocks_data.append(data)
            progress_bar.progress((idx + 1) / len(selected_stocks))
        
        progress_bar.empty()
    
    if not stocks_data:
        st.error("❌ Failed to fetch data for the selected stocks. Please try again later.")
        return
    
    # Create DataFrame
    df = pd.DataFrame(stocks_data)
    
    # Apply sorting based on user selection
    ascending = True if sort_order == 'Worst to Best' else False
    
    if sort_by == 'Stock Name':
        df = df.sort_values(by='Stock Name', ascending=True)
    else:
        df = df.sort_values(by=sort_by, ascending=ascending)
    
    # Add rank column
    df.insert(0, 'Rank', range(1, len(df) + 1))
    
    # Pagination
    ITEMS_PER_PAGE = 10
    total_items = len(df)
    total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE  # Ceiling division
    
    # Initialize page number in session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    
    # Pagination controls
    col1, col2, col3 = st.columns([1, 6, 1])
    
    with col1:
        if st.button("⬅️ Previous", disabled=(st.session_state.current_page == 1)):
            st.session_state.current_page -= 1
            st.rerun()
    
    with col2:
        st.markdown(f"<h4 style='text-align: center; margin-top: 5px;'>Page {st.session_state.current_page} of {total_pages}</h4>", unsafe_allow_html=True)
    
    with col3:
        if st.button("Next ➡️", disabled=(st.session_state.current_page == total_pages)):
            st.session_state.current_page += 1
            st.rerun()
    
    # Calculate start and end indices for current page
    start_idx = (st.session_state.current_page - 1) * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, total_items)
    
    # Get data for current page
    df_page = df.iloc[start_idx:end_idx]
    
    # Create HTML table with colored percentages
    html_table = '<table style="width:100%; border-collapse: collapse; background-color: #2d2d2d;">'
    html_table += '<thead><tr style="background-color: #3d3d3d;">'
    
    # Add headers
    for col in df_page.columns:
        html_table += f'<th style="padding: 12px; text-align: left; border: 1px solid #555; color: #ffffff; font-weight: bold;">{col}</th>'
    html_table += '</tr></thead><tbody>'
    
    # Add rows
    for _, row in df_page.iterrows():
        html_table += '<tr>'
        for col in df_page.columns:
            value = row[col]
            if col in ['1 Week %', '1 Month %', '2 Months %', '3 Months %']:
                colored_value = color_percentage(value)
                html_table += f'<td style="padding: 12px; border: 1px solid #555; color: #ffffff;">{colored_value}</td>'
            else:
                html_table += f'<td style="padding: 12px; border: 1px solid #555; color: #ffffff;">{value}</td>'
        html_table += '</tr>'
    
    html_table += '</tbody></table>'
    
    # Display the HTML table
    st.markdown(html_table, unsafe_allow_html=True)
    
    # Show items range
    st.caption(f"Showing {start_idx + 1} to {end_idx} of {total_items} stocks")
    
    # Display statistics and top/bottom performers
    st.markdown("---")
    
    # Top and Bottom performers
    st.subheader("🏆 Top & Bottom Performers (3 Months)")
    col_top, col_bottom = st.columns(2)
    
    with col_top:
        st.markdown("**🔝 Top 3 Performers**")
        top_3 = df.nlargest(3, '3 Months %')[['Stock Name', '3 Months %']]
        for idx, row in top_3.iterrows():
            st.success(f"**{row['Stock Name']}**: +{row['3 Months %']}%")
    
    with col_bottom:
        st.markdown("**🔻 Bottom 3 Performers**")
        bottom_3 = df.nsmallest(3, '3 Months %')[['Stock Name', '3 Months %']]
        for idx, row in bottom_3.iterrows():
            st.error(f"**{row['Stock Name']}**: {row['3 Months %']}%")
    
    st.markdown("---")
    
    # Average statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_1w = df['1 Week %'].mean()
        st.metric("Average 1-Week Change", f"{avg_1w:.2f}%", delta=None)
    
    with col2:
        avg_1m = df['1 Month %'].mean()
        st.metric("Average 1-Month Change", f"{avg_1m:.2f}%", delta=None)
    
    with col3:
        avg_2m = df['2 Months %'].mean()
        st.metric("Average 2-Month Change", f"{avg_2m:.2f}%", delta=None)
    
    with col4:
        avg_3m = df['3 Months %'].mean()
        st.metric("Average 3-Month Change", f"{avg_3m:.2f}%", delta=None)
    
    # Add some useful information
    st.sidebar.markdown("---")
    st.sidebar.info(
        "ℹ️ **Data Sources:**\n"
        "- Stock Lists: NSE, Wikipedia (dynamic)\n"
        "- Price Data: Yahoo Finance\n"
        "- Fallback: Cached lists\n\n"
        "**Performance Calculation:**\n"
        "- 1 Week: Last 7 days\n"
        "- 1 Month: Last 30 days\n"
        "- 2 Months: Last 60 days\n"
        "- 3 Months: Last 90 days\n\n"
        "**Features:**\n"
        "- 🌐 Dynamic stock list fetching\n"
        "- 📊 Multiple categories\n"
        "- 📤 Upload custom lists\n"
        "- 🔽 Sortable by any period\n"
        "- 🏆 Top/Bottom performers\n"
        "- 🟢 Green = Positive returns\n"
        "- 🔴 Red = Negative returns\n"
        "- 🔄 Auto-updates daily"
    )

if __name__ == "__main__":
    main()
