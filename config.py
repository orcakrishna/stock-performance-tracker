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

# Custom CSS for mobile-optimized UI
CUSTOM_CSS = """<style>
/* Mobile viewport optimization */
@viewport { width: device-width; zoom: 1.0; }

/* Global styles */
.main, .stApp { 
    background-color: #1e1e1e;
    padding: 0.5rem 0.75rem !important;
}

/* Grid layout for sectors and indices */
.stHorizontalBlock {
    display: flex;
    flex-wrap: wrap;
    margin: 0 -0.25rem;
}

.stHorizontalBlock > div {
    padding: 0 0.25rem;
    margin-bottom: 0.5rem;
}

/* Mobile-first typography */
html { font-size: 12px; }
@media (min-width: 768px) { 
    html { font-size: 13px; }
    .main { padding: 0.5rem 1rem !important; }
}
@media (min-width: 1920px) { 
    html { font-size: 14px; }
}

/* Headers and text */
h1, h2, h3, p, label, div { 
    color: #fff !important; 
    margin: 0.25rem 0;
}
h1 { 
    font-size: 1.4rem !important; 
    font-weight: 600 !important;
    margin-bottom: 0.5rem !important;
}
@media (min-width: 768px) {
    h1 { 
        font-size: 1.75rem !important;
        margin-bottom: 1rem !important;
    }
}

/* Tables */
.dataframe { 
    background-color: #2d2d2d; 
    color: #fff; 
    font-size: 0.9rem;
}
thead tr th, tbody tr td {
    border: 1px solid #555 !important;
    padding: 4px 6px !important;
}
thead tr th { 
    background-color: #3d3d3d !important; 
    font-size: 0.9rem;
}

/* Mobile-specific styles */
@media (max-width: 767px) {
    .block-container {
        padding: 0.25rem 0.5rem !important;
        width: 100% !important;
        max-width: 100% !important;
    }
    
    /* Top section - 4 lines layout */
    .stHorizontalBlock:first-of-type > div {
        width: 100% !important;
        margin-bottom: 0.5rem;
    }
    
    /* Sector and Indices - 4 columns */
    .stHorizontalBlock:not(:first-of-type) > div {
        width: 50% !important;
        padding: 0 0.25rem;
        margin-bottom: 0.5rem;
    }
    
    /* Make buttons more touch-friendly */
    button {
        padding: 0.5rem 0.75rem !important;
        font-size: 0.9rem !important;
        min-height: 2.5rem;
        width: 100%;
        margin: 0.25rem 0;
    }
    
    /* Adjust form elements */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div {
        padding: 0.5rem !important;
        font-size: 0.9rem !important;
    }
    
    /* Ensure tables are scrollable */
    .dataframe {
        display: block;
        max-width: 100%;
        overflow-x: auto;
        font-size: 0.85rem;
    }
    
    /* Metric cards in top section */
    .stMetric {
        margin: 0.25rem 0;
    }
}

/* Hide GitHub/Streamlit badges on mobile */
.viewerBadge_container__1QSob, 
.viewerBadge_link__1S137,
a[href*="github.com"][target="_blank"]:has(svg),
header a[href*="github"] { 
    display: none !important; 
}

/* Metric cards */
[data-testid="stMetricValue"] { 
    font-size: 1.125rem !important; 
}
[data-testid="stMetricLabel"] { 
    font-size: 0.875rem !important; 
}
[data-testid="stMetricDelta"] { 
    font-size: 0.875rem !important; 
}

/* Color indicators */
.positive { color: #00ff00 !important; }
.negative { color: #ff4444 !important; }
[data-testid="stMetricDelta"]:has(svg[data-testid="stMetricDeltaIcon-Up"]) {
    color: #00ff00 !important;
}
[data-testid="stMetricDelta"]:has(svg[data-testid="stMetricDeltaIcon-Down"]) {
    color: #ff4444 !important;
}
</style>
"""

# Metric styling CSS (kept for backward compatibility)
METRIC_CSS = """<style>
[data-testid="stMetricValue"] { font-size: 1.25rem !important; }
[data-testid="stMetricLabel"] { font-size: 0.938rem !important; }
[data-testid="stMetricDelta"]:has(svg[data-testid="stMetricDeltaIcon-Up"]) {
    color: #00ff00 !important;
}
[data-testid="stMetricDelta"]:has(svg[data-testid="stMetricDeltaIcon-Down"]) {
    color: #ff4444 !important;
}
</style>
"""