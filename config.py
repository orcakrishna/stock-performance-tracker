"""
Configuration and Constants for NSE Stock Performance Tracker
"""

# Directory for saved lists
SAVED_LISTS_DIR = "saved_stock_lists"

# Pagination settings
ITEMS_PER_PAGE = 10

# Fallback stock lists (refined: no duplicates, exact 50)
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

# Market indices configuration
INDICES_ROW1 = {
    'Nifty 50': '^NSEI',
    'Sensex': '^BSESN',
    'Bank Nifty': '^NSEBANK',
    'Nifty Midcap 50': '^NSEMDCP50',
    'Nifty Total Market': 'NIFTY_TOTAL_MKT.NS',
    'Dow Jones': '^DJI',
    'NASDAQ': '^IXIC',
    'India VIX': '^INDIAVIX'
}

INDICES_ROW2 = {
    'Nifty IT': '^CNXIT',
    'Nifty Pharma': '^CNXPHARMA',
    'Nifty Auto': '^CNXAUTO',
    'Nifty FMCG': '^CNXFMCG',
    'Nifty Metal': '^CNXMETAL',
    'Nifty Realty': '^CNXREALTY',
    'Nifty Energy': '^CNXENERGY'
}

# Commodities tickers
COMMODITIES = {
    'oil': 'CL=F',
    'gold': 'GC=F',
    'silver': 'SI=F',
    'btc': 'BTC-USD'
}

# Ticker stocks - all Nifty 50 stocks for rolling ticker
TICKER_STOCKS = FALLBACK_NIFTY_50

# Custom CSS for dark theme
CUSTOM_CSS = """
<style>
    .main {
        background-color: #1e1e1e;
        padding: 0.5rem 2rem 2rem 2rem;
    }
    .stApp {
        background-color: #1e1e1e;
    }
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }
    header {
        background-color: transparent !important;
    }
    .main > div:first-child {
        padding-top: 0 !important;
    }
    [data-testid="stVerticalBlock"] {
        gap: 0.25rem !important;
    }
    [data-testid="stHorizontalBlock"] {
        gap: 0.5rem !important;
    }
    h1, h2, h3, p, label, div {
        color: #ffffff !important;
    }
    h1 {
        margin-top: 0 !important;
        padding-top: 0 !important;
        color: #4a90e2 !important;
    }
    h2, h3 {
        margin-top: 0.25rem !important;
        margin-bottom: 0.25rem !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        color: #4a90e2 !important;
    }
    hr {
        margin: 0.25rem 0 !important;
    }
    .element-container {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    .stMarkdown {
        margin-bottom: 0.25rem !important;
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
    
    /* Top Gainer/Loser Banner */
    .gainer-loser-banner {
        display: flex;
        justify-content: flex-start;
        gap: 40px;
        padding: 8px 0;
        margin: 0 0 10px 0;
        font-size: 14px;
        font-weight: bold;
    }
    
    .gainer-item {
        color: #00ff00;
        white-space: nowrap;
    }
    
    .loser-item {
        color: #ff4444;
        white-space: nowrap;
    }
    
    /* Compact Gainer/Loser Metrics */
    [data-testid="stMetricValue"] {
        font-size: 16px !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 12px !important;
    }
    .gainer-loser-metric [data-testid="stMetricValue"] {
        display: inline !important;
        font-size: 15px !important;
    }
    .gainer-loser-metric [data-testid="stMetricDelta"] {
        display: inline !important;
        margin-left: 8px !important;
        font-size: 15px !important;
    }
    
    /* Rolling Ticker Styles */
    .ticker-container {
        background: linear-gradient(90deg, #1a1a2e 0%, #16213e 50%, #1a1a2e 100%);
        border: 2px solid #0f3460;
        border-radius: 8px;
        padding: 10px 0;
        margin: 0 0 15px 0;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .ticker-wrapper {
        display: flex;
        animation: scroll 15s linear infinite;
        white-space: nowrap;
    }
    
    .ticker-item {
        display: inline-flex;
        align-items: center;
        margin: 0 30px;
        padding: 8px 16px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 6px;
        border-left: 3px solid #00d4ff;
        transition: all 0.3s ease;
    }
    
    .ticker-item:hover {
        background: rgba(255, 255, 255, 0.1);
        transform: scale(1.05);
    }
    
    .ticker-symbol {
        font-weight: bold;
        font-size: 14px;
        color: #00d4ff;
        margin-right: 8px;
    }
    
    .ticker-price {
        font-size: 14px;
        color: #ffffff;
        margin-right: 8px;
    }
    
    .ticker-change-positive {
        font-size: 13px;
        color: #00ff00;
        font-weight: bold;
    }
    
    .ticker-change-negative {
        font-size: 13px;
        color: #ff4444;
        font-weight: bold;
    }
    
    @keyframes scroll {
        0% {
            transform: translateX(0);
        }
        100% {
            transform: translateX(-50%);
        }
    }
    
    .ticker-container:hover .ticker-wrapper {
        animation-play-state: paused;
    }
</style>
"""

# Metric styling CSS
METRIC_CSS = """
<style>
    [data-testid="stMetricValue"] { font-size: 20px !important; }
    [data-testid="stMetricLabel"] { font-size: 14px !important; }
    [data-testid="stMetricDelta"] { font-size: 14px !important; font-weight: bold !important; }
    [data-testid="stMetricDelta"]:has(svg[data-testid="stMetricDeltaIcon-Up"]) { color: #00ff00 !important; }
    [data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Up"] { fill: #00ff00 !important; }
    [data-testid="stMetricDelta"]:has(svg[data-testid="stMetricDeltaIcon-Down"]) { color: #ff4444 !important; }
    [data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Down"] { fill: #ff4444 !important; }
</style>
"""
