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
    'Nifty Metal': '^CNXMETAL'
}

# Commodities tickers
COMMODITIES = {
    'oil': 'CL=F',
    'gold': 'GC=F',
    'btc': 'BTC-USD'
}

# Custom CSS for dark theme
CUSTOM_CSS = """
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
