
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
from io import StringIO
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
warnings.filterwarnings('ignore')  # Suppress yf deprecations

# Don't use custom session - let yfinance handle it internally

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

# Title and time in header
col_title, col_time = st.columns([3, 1])

with col_title:
    st.title("📊 Indian Stock Performance Tracker")
    st.markdown("View 1-month, 2-month, and 3-month performance of NSE/BSE stocks.")

with col_time:
    # Get current time in different timezones
    ist = pytz.timezone('Asia/Kolkata')
    edt = pytz.timezone('America/New_York')
    
    current_time_utc = datetime.now(pytz.utc)
    ist_time = current_time_utc.astimezone(ist)
    edt_time = current_time_utc.astimezone(edt)
    
    # Get commodities prices
    try:
        oil = yf.Ticker('CL=F')
        oil_price = oil.history(period='1d')['Close'].iloc[-1]
        oil_str = f"${oil_price:.2f}"
    except:
        oil_str = "--"
    
    try:
        gold = yf.Ticker('GC=F')
        gold_price = gold.history(period='1d')['Close'].iloc[-1]
        gold_str = f"${gold_price:.2f}"
    except:
        gold_str = "--"
    
    try:
        btc = yf.Ticker('BTC-USD')
        btc_price = btc.history(period='1d')['Close'].iloc[-1]
        btc_str = f"${btc_price:,.0f}"
    except:
        btc_str = "--"
    
    st.markdown(f"""
    <div style='text-align: right; padding-top: 20px;'>
        <p style='margin: 0; font-size: 14px; color: #fff;'>🕐 IST: <strong>{ist_time.strftime('%I:%M %p')}</strong></p>
        <p style='margin: 0; font-size: 14px; color: #fff;'>🕐 EDT: <strong>{edt_time.strftime('%I:%M %p')}</strong></p>
        <p style='margin: 5px 0 0 0; font-size: 13px; color: #888;'>🛢️ Oil: <strong>{oil_str}</strong></p>
        <p style='margin: 0; font-size: 13px; color: #888;'>🥇 Gold: <strong>{gold_str}</strong></p>
        <p style='margin: 0; font-size: 13px; color: #888;'>₿ BTC: <strong>{btc_str}</strong></p>
        <p style='margin: 5px 0 0 0; font-size: 12px; color: #888;'>{ist_time.strftime('%d %b %Y')}</p>
    </div>
    """, unsafe_allow_html=True)

# Fallback hardcoded lists (refined: no duplicates, exact 50)
FALLBACK_NIFTY_50 = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'HINDUNILVR.NS',
    'INFY.NS', 'ITC.NS', 'KOTAKBANK.NS', 'BHARTIARTL.NS', 'LT.NS', 'SBIN.NS',
    'BAJFINANCE.NS', 'HCLTECH.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'TITAN.NS',
    'SUNPHARMA.NS', 'AXISBANK.NS', 'NTPC.NS', 'NESTLEIND.NS', 'ULTRACEMCO.NS',
    'TATAMOTORS.NS', 'POWERGRID.NS', 'BAJAJ-AUTO.NS', 'TATASTEEL.NS', 'JSWSTEEL.NS',
    'GRASIM.NS', 'ADANIPORTS.NS', 'TECHM.NS', 'BAJAJFINSV.NS', 'WIPRO.NS',
    'UPL.NS', 'DRREDDY.NS', 'CIPLA.NS', 'HINDALCO.NS', 'TATACONSUM.NS',
    'BPCL.NS', 'SHREECEM.NS', 'INDUSINDBK.NS', 'IOC.NS', 'ONGC.NS',
    'COALINDIA.NS', 'SBILIFE.NS', 'HDFCLIFE.NS', 'DIVISLAB.NS', 'EICHERMOT.NS',
    'HEROMOTOCO.NS', 'BRITANNIA.NS'
]

FALLBACK_NIFTY_NEXT_50 = [
    'ADANIENT.NS', 'AMBUJACEM.NS', 'BANDHANBNK.NS', 'BERGEPAINT.NS', 'BEL.NS',
    'BOSCHLTD.NS', 'CHOLAFIN.NS', 'COLPAL.NS', 'DABUR.NS', 'DLF.NS',
    'GODREJCP.NS', 'HAVELLS.NS', 'HDFCAMC.NS', 'ICICIPRULI.NS', 'IDEA.NS',
    'INDIGO.NS', 'JINDALSTEL.NS', 'LICHSGFIN.NS', 'LUPIN.NS', 'MARICO.NS',
    'MCDOWELL-N.NS', 'MUTHOOTFIN.NS', 'NMDC.NS', 'NYKAA.NS', 'PAGEIND.NS',
    'PETRONET.NS', 'PIDILITIND.NS', 'PNB.NS', 'RECLTD.NS', 'SBICARD.NS',
    'SHRIRAMFIN.NS', 'SIEMENS.NS', 'TATAPOWER.NS', 'TORNTPHARM.NS', 'TRENT.NS',
    'VEDL.NS', 'VOLTAS.NS', 'ZOMATO.NS'
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
def fetch_nse_csv_list(csv_filename):
    """Fetch stock list from NSE CSV endpoint (stable, avoids API 421 errors)"""
    try:
        url = f"https://nsearchives.nseindia.com/content/indices/{csv_filename}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/market-data/live-equity-market'
        }
        
        with requests.Session() as session:
            session.headers.update(headers)
            # Warm-up: Visit homepage to set cookies (prevents blocks)
            session.get("https://www.nseindia.com", timeout=10)
            time.sleep(1)  # Brief pause for stability
            
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                csv_content = response.content.decode('utf-8')
                df = pd.read_csv(StringIO(csv_content))
                stocks = [f"{symbol}.NS" for symbol in df['Symbol'].tolist() if pd.notna(symbol)]
                if len(stocks) >= 40:  # Validate
                    return stocks
                else:
                    return None
            else:
                return None
    except Exception as e:
        return None
    
    return None

@st.cache_data(ttl=86400)
def fetch_nifty_50_from_nse():
    return fetch_nse_csv_list('ind_nifty50list.csv')

@st.cache_data(ttl=86400)
def fetch_nifty_next_50_from_nse():
    return fetch_nse_csv_list('ind_niftynext50list.csv')

@st.cache_data(ttl=86400)
def fetch_nifty_total_market_from_nse():
    return fetch_nse_csv_list('ind_niftytotalmarket_list.csv')


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_index_performance(index_symbol, index_name=None):
    """Fetch index performance - prioritize info dict to avoid hist bugs"""
    if index_symbol:
        try:
            ticker = yf.Ticker(index_symbol)
            
            # Try info first (faster, no hist download)
            info = ticker.info
            current_price = info.get('regularMarketPrice') or info.get('previousClose')
            prev_price = info.get('regularMarketPreviousClose') or info.get('open')
            
            if current_price and prev_price and current_price != prev_price:
                change_pct = ((current_price - prev_price) / prev_price) * 100
                return current_price, change_pct
            
            # Fallback to hist if info incomplete
            hist = ticker.history(period='5d')
            if not hist.empty and len(hist) >= 2:
                current_price = hist['Close'].iloc[-1]
                previous_price = hist['Close'].iloc[-2]
                change_pct = ((current_price - previous_price) / previous_price) * 100
                return current_price, change_pct
                
        except Exception as e:
            print(f"yfinance debug for {index_symbol}: {e}")  # Silent log, no st.error
            return None, None
    return None, None

def get_stock_performance(ticker):
    """Fetch stock performance with semi-live current price"""
    symbol = ticker.replace('.NS', '').replace('.BO', '')
    
    # Retry logic for rate limiting
    max_retries = 3
    for attempt in range(max_retries):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='4mo')
            
            if hist.empty or len(hist) < 20:
                if attempt < max_retries - 1:
                    time.sleep(1)  # Wait before retry
                    continue
                return None
            break  # Success, exit retry loop
        except Exception as e:
            if "Rate" in str(e) or "429" in str(e):
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    st.warning(f"⚠️ Rate limited on {symbol}, skipping...")
                    return None
            else:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                st.warning(f"⚠️ Error fetching {symbol}: {str(e)}")
                return None
    
    try:
        
        # Remove timezone
        hist.index = hist.index.tz_localize(None)
        
        # Get semi-live current price via info
        try:
            info = stock.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or hist['Close'].iloc[-1]
        except:
            current_price = hist['Close'].iloc[-1]
        current_date = hist.index[-1]
        
        # Calculate prices for different periods
        # For 1 week: go back 5 trading days (1 week of trading)
        if len(hist) >= 5:
            price_1w = hist['Close'].iloc[-6]  # 5 trading days ago
        else:
            price_1w = hist['Close'].iloc[0]
        
        # For longer periods: use date-based lookup
        def get_price_by_days_back(days):
            target_date = current_date - pd.Timedelta(days=days)
            # Find the closest date in history
            idx = hist.index.get_indexer([target_date], method='nearest')[0]
            return hist['Close'].iloc[max(0, min(idx, len(hist)-1))]
        
        price_1m = get_price_by_days_back(30)
        price_2m = get_price_by_days_back(60)
        price_3m = get_price_by_days_back(90)
        
        # Changes
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
        st.warning(f"⚠️ Error fetching {symbol}: {str(e)}")  # Show error to user
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
    if not os.path.exists(SAVED_LISTS_DIR):
        os.makedirs(SAVED_LISTS_DIR)
        with open(os.path.join(SAVED_LISTS_DIR, '.gitkeep'), 'w') as f:
            f.write('')

def save_list_to_csv(list_name, stocks):
    ensure_saved_lists_dir()
    filename = os.path.join(SAVED_LISTS_DIR, f"{list_name}.csv")
    df = pd.DataFrame({'Symbol': stocks})
    df.to_csv(filename, index=False)

def load_list_from_csv(list_name):
    filename = os.path.join(SAVED_LISTS_DIR, f"{list_name}.csv")
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        return df['Symbol'].tolist()
    return None

def delete_list_csv(list_name):
    filename = os.path.join(SAVED_LISTS_DIR, f"{list_name}.csv")
    if os.path.exists(filename):
        os.remove(filename)

def load_all_saved_lists():
    ensure_saved_lists_dir()
    saved_lists = {}
    if os.path.exists(SAVED_LISTS_DIR):
        for filename in os.listdir(SAVED_LISTS_DIR):
            if filename.endswith('.csv'):
                list_name = filename[:-4]
                stocks = load_list_from_csv(list_name)
                if stocks:
                    saved_lists[list_name] = stocks
    return saved_lists

def get_stock_list(category_name):
    """Get stock list with dynamic fetching and fallback"""
    
    if category_name == 'Nifty 50':
        stocks = fetch_nifty_50_from_nse()
        if stocks:
            return stocks, f"✅ Fetched {len(stocks)} stocks from {category_name}"
        return FALLBACK_NIFTY_50, f"⚠️ Using cached {category_name} list"
    
    elif category_name == 'Nifty Next 50':
        stocks = fetch_nifty_next_50_from_nse()
        if stocks:
            return stocks, f"✅ Fetched {len(stocks)} stocks from {category_name}"
        return FALLBACK_NIFTY_NEXT_50, f"⚠️ Using cached {category_name} list"
    
    elif category_name == 'Nifty Total Market':
        stocks = fetch_nifty_total_market_from_nse()
        if stocks:
            return stocks, f"✅ Fetched {len(stocks)} stocks from {category_name}"
        fallback = list(set(FALLBACK_NIFTY_50 + FALLBACK_NIFTY_NEXT_50))[:100]  # Sample fallback
        return fallback, f"⚠️ Using cached {category_name} sample"
    
    
    return [], "❌ No data available"

def main():
    # Initialize session state
    if 'saved_lists' not in st.session_state:
        st.session_state.saved_lists = load_all_saved_lists()
    if 'current_list_name' not in st.session_state:
        st.session_state.current_list_name = None
    
    # Sidebar for stock selection
    st.sidebar.header("📋 Stock Selection")
    
    # Category selection (added Nifty Total Market)
    category = st.sidebar.selectbox(
        "Select Category",
        options=['Nifty 50', 'Nifty Next 50', 'Nifty Total Market', 'Custom Selection', 'Upload File'],
        index=0
    )
    
    # Determine stock list based on category
    if category in ['Nifty 50', 'Nifty Next 50', 'Nifty Total Market', 'BSE Sensex', 'Nifty 500 (Sample)']:
        with st.spinner(f"Fetching {category} stock list..."):
            selected_stocks, fetch_status = get_stock_list(category)
            available_stocks = selected_stocks
        
        if "✅" in fetch_status:
            st.sidebar.success(fetch_status)
        else:
            st.sidebar.warning(fetch_status)
    
    elif category == 'Upload File':
        st.sidebar.markdown("---")
        st.sidebar.markdown("**📤 Manage Stock Lists**")
        
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
                        del st.session_state.saved_lists[list_name]
                        delete_list_csv(list_name)
                        if st.session_state.current_list_name == list_name:
                            st.session_state.current_list_name = None
                        st.rerun()
            st.sidebar.markdown("---")
        
        st.sidebar.markdown("**📤 Upload New List**")
        
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
        
        if uploaded_file is not None:
            try:
                content = uploaded_file.read().decode('utf-8')
                uploaded_stocks = [line.strip() for line in content.split('\n') if line.strip()]
                
                valid_stocks = []
                for symbol in uploaded_stocks:
                    if '.NS' in symbol or '.BO' in symbol:
                        valid_stocks.append(symbol)
                    else:
                        valid_stocks.append(f"{symbol}.NS")
                
                list_name = st.sidebar.text_input(
                    "Enter a name for this list:",
                    value=uploaded_file.name.replace('.txt', '').replace('.csv', ''),
                    key="new_list_name"
                )
                
                if st.sidebar.button("💾 Save List"):
                    if list_name.strip():
                        st.session_state.saved_lists[list_name.strip()] = valid_stocks
                        st.session_state.current_list_name = list_name.strip()
                        save_list_to_csv(list_name.strip(), valid_stocks)
                        st.sidebar.success(f"✅ Saved '{list_name}' with {len(valid_stocks)} stocks")
                    else:
                        st.sidebar.error("Please enter a list name")
                
                selected_stocks = valid_stocks
                available_stocks = valid_stocks
                
            except Exception as e:
                st.sidebar.error(f"Error reading file: {str(e)}")
                selected_stocks = []
                available_stocks = []
        
        elif st.session_state.current_list_name and st.session_state.current_list_name in st.session_state.saved_lists:
            selected_stocks = st.session_state.saved_lists[st.session_state.current_list_name]
            available_stocks = selected_stocks
            st.sidebar.success(f"✅ Using '{st.session_state.current_list_name}' ({len(selected_stocks)} stocks)")
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
        all_nifty_50, _ = get_stock_list('Nifty 50')
        all_nifty_next_50, _ = get_stock_list('Nifty Next 50')
        all_bse, _ = get_stock_list('BSE Sensex')
        
        available_stocks = list(set(all_nifty_50 + all_nifty_next_50 + all_bse))  # No dups
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
    
    # Performance options
    st.sidebar.markdown("---")
    st.sidebar.header("⚡ Performance")
    use_parallel = st.sidebar.checkbox(
        "Use Parallel Fetching (3x faster)",
        value=False,
        help="Fetch 5 stocks at once (rate-limit safe). Keep unchecked for sequential mode (slower but more reliable)."
    )
    
    if not selected_stocks:
        st.warning("⚠️ Please select at least one stock to view performance.")
        return
    
    # Display Market Indices - Use metric for consistency, no distortion on error
    st.markdown("### 📈 Market Indices - Today's Performance")
    
    st.markdown("""
    <style>
        [data-testid="stMetricValue"] { font-size: 20px !important; }
        [data-testid="stMetricLabel"] { font-size: 14px !important; }
        [data-testid="stMetricDelta"] { font-size: 14px !important; font-weight: bold !important; }
        [data-testid="stMetricDelta"]:has(svg[data-testid="stMetricDeltaIcon-Up"]) { color: #00ff00 !important; }
        [data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Up"] { fill: #00ff00 !important; }
        [data-testid="stMetricDelta"]:has(svg[data-testid="stMetricDeltaIcon-Down"]) { color: #ff4444 !important; }
        [data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Down"] { fill: #ff4444 !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # Row 1: Major Indices (added Nifty Total Market)
    indices_row1 = {
        'Nifty 50': '^NSEI',
        'Sensex': '^BSESN',
        'Bank Nifty': '^NSEBANK',
        'Nifty Midcap 50': '^NSEMDCP50',
        'Nifty Total Market': 'NIFTY_TOTAL_MKT.NS',
        'Dow Jones': '^DJI',
        'NASDAQ': '^IXIC',
        'India VIX': '^INDIAVIX'
    }
    
    cols1 = st.columns(len(indices_row1))
    for idx, (name, symbol) in enumerate(indices_row1.items()):
        with cols1[idx]:
            price, change = get_index_performance(symbol)
            if price and change:
                st.metric(
                    label=name,
                    value=f"{price:,.2f}",
                    delta=f"{change:+.2f}%"
                )
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
                st.metric(
                    label=name,
                    value=f"{price:,.2f}",
                    delta=f"{change:+.2f}%"
                )
            else:
                st.metric(label=name, value="--", delta="--")
    
    st.markdown("---")
    
    # Fetch data for selected stocks
    if category == 'Upload File' and st.session_state.current_list_name:
        display_title = f"📊 {st.session_state.current_list_name} - Performance Summary ({len(selected_stocks)} Stock(s))"
    else:
        display_title = f"📊 {category} - Performance Summary ({len(selected_stocks)} Stock(s))"
    
    st.subheader(display_title)
    st.caption(f"🔽 Sorted by: **{sort_by}** ({sort_order})")
    
    # Fetch data with chosen method
    if use_parallel:
        with st.spinner(f"⚡ Fetching {len(selected_stocks)} stocks in parallel (5 at a time to avoid rate limits)..."):
            stocks_data = []
            progress_bar = st.progress(0)
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_ticker = {executor.submit(get_stock_performance, ticker): ticker for ticker in selected_stocks}
                completed = 0
                
                for future in as_completed(future_to_ticker):
                    completed += 1
                    try:
                        data = future.result(timeout=30)
                        if data:
                            stocks_data.append(data)
                    except Exception as e:
                        ticker = future_to_ticker[future]
                        print(f"Error fetching {ticker}: {e}")
                    progress_bar.progress(completed / len(selected_stocks))
            
            progress_bar.empty()
    else:
        # Original sequential method
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
    
    # Apply sorting
    ascending = True if sort_order == 'Worst to Best' else False
    
    if sort_by == 'Stock Name':
        df = df.sort_values(by='Stock Name', ascending=True)
    else:
        df = df.sort_values(by=sort_by, ascending=ascending)
    
    # Add rank
    df.insert(0, 'Rank', range(1, len(df) + 1))
    
    # Pagination
    ITEMS_PER_PAGE = 10
    total_items = len(df)
    total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    
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
    
    # Current page data
    start_idx = (st.session_state.current_page - 1) * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, total_items)
    df_page = df.iloc[start_idx:end_idx]
    
    # HTML table
    html_table = '<table style="width:100%; border-collapse: collapse; background-color: #2d2d2d;">'
    html_table += '<thead><tr style="background-color: #3d3d3d;">'
    for col in df_page.columns:
        html_table += f'<th style="padding: 12px; text-align: left; border: 1px solid #555; color: #ffffff; font-weight: bold;">{col}</th>'
    html_table += '</tr></thead><tbody>'
    
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
    st.markdown(html_table, unsafe_allow_html=True)
    
    st.caption(f"Showing {start_idx + 1} to {end_idx} of {total_items} stocks")
    
    # Top/Bottom performers
    st.markdown("---")
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
    
    # Averages
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_1w = df['1 Week %'].mean()
        st.metric("Average 1-Week Change", f"{avg_1w:.2f}%")
    
    with col2:
        avg_1m = df['1 Month %'].mean()
        st.metric("Average 1-Month Change", f"{avg_1m:.2f}%")
    
    with col3:
        avg_2m = df['2 Months %'].mean()
        st.metric("Average 2-Month Change", f"{avg_2m:.2f}%")
    
    with col4:
        avg_3m = df['3 Months %'].mean()
        st.metric("Average 3-Month Change", f"{avg_3m:.2f}%")
    
    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.info(
        "ℹ️ **Data Sources:**\n"
        "- Stock Lists: NSE CSV (dynamic, no API blocks)\n"
        "- Prices: yfinance (semi-live, ~15min delay)\n\n"
        "**Performance Modes:**\n"
        "- ⚡ Parallel: 3x faster (5 stocks at once, rate-limit safe)\n"
        "- 🐢 Sequential: Original mode (default, slower but reliable)\n\n"
        "**Features:**\n"
        "- Nifty Total Market (~750 stocks)\n"
        "- Upload custom stock lists\n"
        "- Real-time commodities & indices\n"
        "- Auto-retry with rate limit protection"
    )

if __name__ == "__main__":
    main()