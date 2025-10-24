"""
Configuration and Constants for NSE Stock Performance Tracker
"""

# Directory for saved lists
SAVED_LISTS_DIR = "saved_stock_lists"

# Pagination settings
ITEMS_PER_PAGE = 10

# Fallback stock lists (refined)
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

# Custom CSS for dark theme and responsive UI
CUSTOM_CSS = """<style>
/* ✅ Mobile viewport optimization */
@viewport { width: device-width; zoom: 1.0; }

/* Global background */
.main, .stApp { background-color: #1e1e1e; }
.block-container {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}

/* Hide GitHub or Streamlit badges */
.viewerBadge_container__1QSob, .viewerBadge_link__1S137,
a[href*="github.com"][target="_blank"]:has(svg),
header a[href*="github"] { display: none !important; }

/* Buttons */
button[kind="header"] {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    font-weight: bold !important;
}
button[kind="header"]:hover {
    background: linear-gradient(135deg, #5568d3, #6a3f8f) !important;
    transform: scale(1.05) !important;
}

/* Font & layout */
html { font-size: 13px; }
@media (min-width: 1920px) { html { font-size: 14px; } }
@media (max-width: 768px) {
    html { font-size: 12px; }
    .main { padding: 0.25rem 0.5rem; width: 100% !important; }
}

/* Typography */
h1, h2, h3, p, label, div { color: #fff !important; }
h1 { font-size: 1.75rem !important; font-weight: 600 !important; }
@media (max-width: 768px) {
    h1 { font-size: 1.4rem !important; }
}

/* Tables */
.dataframe { background-color: #2d2d2d; color: #fff; }
thead tr th, tbody tr td {
    border: 1px solid #555 !important;
    padding: 6px 8px !important;
}
thead tr th { background-color: #3d3d3d !important; }

/* Ticker */
.ticker-container {
    background: linear-gradient(90deg,#1a1a2e,#16213e,#1a1a2e);
    border: 2px solid #0f3460;
    border-radius: 8px;
    padding: 6px 0;
    margin-bottom: 10px;
    overflow: hidden;
}
.ticker-wrapper {
    display: inline-flex;
    animation: ticker-scroll 120s linear infinite;
    white-space: nowrap;
}
@keyframes ticker-scroll {
    0% { transform: translateX(0%); }
    100% { transform: translateX(-50%); }
}
.ticker-container:hover .ticker-wrapper { animation-play-state: paused; }
.ticker-item {
    display: inline-flex; align-items: center;
    margin: 0 30px; padding: 6px 18px;
    background: rgba(255,255,255,0.05);
    border-radius: 6px;
    transition: 0.3s ease;
}
.ticker-symbol { color: #00d4ff; font-weight: bold; margin-right: 8px; }
.ticker-price { color: #fff; margin-right: 8px; }
.ticker-change-positive { color: #00ff00; }
.ticker-change-negative { color: #ff4444; }

/* ✅ Mobile ticker */
@media (max-width: 768px) {
    .ticker-container { padding: 4px 0; }
    .ticker-item { margin: 0 15px; padding: 4px 12px; }
    .ticker-symbol, .ticker-price { font-size: 0.813rem; }
}

/* ✅ Sidebar */
[data-testid="stSidebar"] {
    background-color: #262730 !important;
}
[data-testid="stSidebar"] p, label, span {
    color: #e0e0e0 !important;
    font-size: 0.938rem !important;
}

/* ✅ Metrics */
[data-testid="stMetricValue"] { font-size: 1.125rem !important; }
[data-testid="stMetricLabel"] { font-size: 0.875rem !important; }
[data-testid="stMetricDelta"]:has(svg[data-testid="stMetricDeltaIcon-Up"]) {
    color: #00ff00 !important;
}
[data-testid="stMetricDelta"]:has(svg[data-testid="stMetricDeltaIcon-Down"]) {
    color: #ff4444 !important;
}
</style>
"""

# Metric styling CSS
METRIC_CSS = """<style>
[data-testid="stMetricValue"] { font-size: 1.375rem !important; }
[data-testid="stMetricLabel"] { font-size: 0.938rem !important; }
[data-testid="stMetricDelta"]:has(svg[data-testid="stMetricDeltaIcon-Up"]) {
    color: #00ff00 !important;
}
[data-testid="stMetricDelta"]:has(svg[data-testid="stMetricDeltaIcon-Down"]) {
    color: #ff4444 !important;
}
</style>
"""