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

# Custom CSS for dark theme
CUSTOM_CSS = """
<style>
    /* Mobile viewport optimization */
    @viewport {
        width: device-width;
        zoom: 1.0;
    }
    
    .main {
        background-color: #1e1e1e;
        padding: 0.5rem 1rem 1rem 1rem;
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
    
    /* Hide GitHub fork button */
    .viewerBadge_container__1QSob,
    .viewerBadge_link__1S137,
    a[href*="github.com"][target="_blank"]:has(svg),
    header a[href*="github"] {
        display: none !important;
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
    /* Base font size for better cross-platform consistency */
    /* Reduced to 13px to prevent need for 90% zoom on Windows */
    html {
        font-size: 13px;
    }
    
    /* Responsive scaling for larger screens */
    @media (min-width: 1920px) {
        html {
            font-size: 14px;
        }
    }
    
    /* Mobile responsive adjustments */
    @media (max-width: 768px) {
        html {
            font-size: 12px;
        }
        
        .main {
            padding: 0.25rem 0.5rem 0.5rem 0.5rem;
            margin-left: 0 !important;
            width: 100% !important;
        }
        
        .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            max-width: 100% !important;
        }
        
        /* Make metrics wrap to 2 columns on mobile */
        [data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-wrap: wrap !important;
        }
        
        [data-testid="stHorizontalBlock"] > div {
            flex: 0 0 48% !important;
            min-width: 48% !important;
            max-width: 48% !important;
        }
        
        /* Exception: Keep pagination controls horizontal - CRITICAL */
        .pagination-container [data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
            flex-direction: row !important;
            display: flex !important;
        }
        
        .pagination-container [data-testid="stHorizontalBlock"] > div {
            flex: 0 0 auto !important;
            min-width: 50px !important;
            max-width: none !important;
        }
        
        .pagination-container [data-testid="stHorizontalBlock"] > div:first-child {
            flex: 0 0 12.5% !important;
            min-width: 50px !important;
            max-width: 80px !important;
        }
        
        .pagination-container [data-testid="stHorizontalBlock"] > div:nth-child(2) {
            flex: 1 1 75% !important;
            min-width: 0 !important;
        }
        
        .pagination-container [data-testid="stHorizontalBlock"] > div:last-child {
            flex: 0 0 12.5% !important;
            min-width: 50px !important;
            max-width: 80px !important;
        }
        
        /* Force pagination buttons to stay in their columns */
        .pagination-container button {
            width: 100% !important;
            max-width: 100% !important;
        }
        
        /* Make metrics display properly in their containers */
        [data-testid="stMetric"] {
            width: 100% !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Ensure main content area is not affected by sidebar */
        section[data-testid="stMain"] {
            margin-left: 0 !important;
            width: 100% !important;
        }
    }
    
    h1, h2, h3, p, label, div {
        color: #ffffff !important;
    }
    h1 {
        margin-top: 0 !important;
        padding-top: 0 !important;
        color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.75rem !important;
        line-height: 1.3 !important;
    }
    h2, h3 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.35rem !important;
        line-height: 1.4 !important;
    }
    h3 {
        font-size: 1.15rem !important;
    }
    
    /* Mobile heading adjustments */
    @media (max-width: 768px) {
        h1 {
            font-size: 1.4rem !important;
        }
        h2, h3 {
            font-size: 1.15rem !important;
        }
        h3 {
            font-size: 1rem !important;
        }
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
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #262730 !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        background-color: #262730 !important;
    }
    .sidebar .sidebar-content {
        background-color: #262730 !important;
    }
    /* Sidebar Headers */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
        padding: 0.5rem 0 !important;
        border-bottom: 2px solid #3d3d4d;
    }
    /* Sidebar Markdown Bold (for section headers) */
    [data-testid="stSidebar"] strong {
        color: #ffffff !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        display: inline !important;
    }
    /* Sidebar section headers (standalone bold text) */
    [data-testid="stSidebar"] p:has(> strong:only-child) strong {
        display: block !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.75rem !important;
    }
    /* Sidebar Text */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: #e0e0e0 !important;
        font-size: 0.938rem !important;
        line-height: 1.6 !important;
    }
    /* Sidebar Selectbox - Fixed for Windows visibility */
    [data-testid="stSidebar"] [data-baseweb="select"] {
        background-color: #1e1e2e !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background-color: #1e1e2e !important;
        color: #ffffff !important;
        border: 1px solid #3d3d4d !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] input {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] svg {
        fill: #ffffff !important;
    }
    /* Dropdown menu styling */
    [data-baseweb="popover"] {
        background-color: #1e1e2e !important;
    }
    [data-baseweb="menu"] {
        background-color: #1e1e2e !important;
        border: 1px solid #3d3d4d !important;
    }
    [data-baseweb="menu"] li {
        background-color: #1e1e2e !important;
        color: #ffffff !important;
    }
    [data-baseweb="menu"] li:hover {
        background-color: #2d2d3d !important;
        color: #ffffff !important;
    }
    [role="option"] {
        background-color: #1e1e2e !important;
        color: #ffffff !important;
    }
    [role="option"]:hover {
        background-color: #2d2d3d !important;
        color: #ffffff !important;
    }
    /* Sidebar Radio Buttons */
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        font-size: 0.938rem !important;
        padding: 0.25rem 0 !important;
    }
    /* Sidebar Checkbox */
    [data-testid="stSidebar"] [data-testid="stCheckbox"] label {
        font-size: 0.938rem !important;
    }
    /* Sidebar Buttons */
    [data-testid="stSidebar"] button {
        font-size: 0.875rem !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        min-height: 44px !important; /* Touch-friendly size */
    }
    
    /* Mobile sidebar adjustments */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            min-width: 100% !important;
            z-index: 999999 !important;
        }
        
        [data-testid="stSidebar"] button {
            width: 100% !important;
            padding: 0.75rem 1rem !important;
        }
        
        /* Ensure sidebar doesn't overlay content when collapsed */
        [data-testid="stSidebar"][aria-expanded="false"] {
            display: none !important;
        }
        
        /* Main content should take full width when sidebar is collapsed */
        [data-testid="stSidebar"][aria-expanded="false"] ~ [data-testid="stMain"] {
            margin-left: 0 !important;
        }
    }
    /* Sidebar Info Box */
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        background-color: #1e1e2e !important;
        border-left: 4px solid #4a9eff !important;
        border-radius: 6px !important;
        padding: 1rem !important;
        font-size: 0.875rem !important;
        line-height: 1.6 !important;
    }
    /* Sidebar Success Box */
    [data-testid="stSidebar"] [data-testid="stSuccess"] {
        background-color: #1e2e1e !important;
        border-left: 4px solid #00c853 !important;
        border-radius: 6px !important;
        padding: 0.75rem !important;
        font-size: 0.875rem !important;
    }
    /* Sidebar Metrics */
    [data-testid="stSidebar"] [data-testid="stMetric"] {
        background-color: #1e1e2e !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        border: 1px solid #3d3d4d !important;
    }
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: #4a9eff !important;
    }
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        font-size: 0.813rem !important;
        color: #b0b0b0 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    /* Sidebar Caption */
    [data-testid="stSidebar"] .stCaption {
        font-size: 0.75rem !important;
        color: #888 !important;
    }
    
    /* Top Gainer/Loser Banner */
    .gainer-loser-banner {
        display: flex;
        justify-content: flex-start;
        gap: 40px;
        padding: 10px 0;
        margin: 0 0 12px 0;
        font-size: 0.938rem;
        font-weight: bold;
        line-height: 1.5;
    }
    
    .gainer-item {
        color: #00ff00;
        white-space: nowrap;
    }
    
    .loser-item {
        color: #ff4444;
        white-space: nowrap;
    }
    
    /* Mobile banner adjustments */
    @media (max-width: 768px) {
        .gainer-loser-banner {
            flex-direction: column;
            gap: 10px;
            font-size: 0.813rem;
        }
    }
    
    /* Compact Gainer/Loser Metrics - Using rem for better scaling */
    [data-testid="stMetricValue"] {
        font-size: 1.125rem !important;
        line-height: 1.4 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem !important;
        line-height: 1.5 !important;
    }
    .gainer-loser-metric [data-testid="stMetricValue"] {
        display: inline !important;
        font-size: 1rem !important;
    }
    .gainer-loser-metric [data-testid="stMetricDelta"] {
        display: inline !important;
        margin-left: 8px !important;
        font-size: 1rem !important;
    }
    
    /* Rolling Ticker Styles - Fixed for all 50 stocks */
    .ticker-container {
        background: linear-gradient(90deg, #1a1a2e 0%, #16213e 50%, #1a1a2e 100%);
        border: 2px solid #0f3460;
        border-radius: 8px;
        padding: 6px 0;
        margin: 0 0 10px 0;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        width: 100%;
        position: relative;
    }
    
    .ticker-wrapper {
        display: inline-flex;
        animation: ticker-scroll 120s linear infinite;
        white-space: nowrap;
        will-change: transform;
    }
    
    .ticker-item {
        display: inline-flex;
        align-items: center;
        margin: 0 30px;
        padding: 6px 18px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 6px;
        border-left: 3px solid #00d4ff;
        transition: all 0.3s ease;
        min-height: 32px;
    }
    
    .ticker-item:hover {
        background: rgba(255, 255, 255, 0.1);
        transform: scale(1.05);
    }
    
    .ticker-symbol {
        font-weight: bold;
        font-size: 0.938rem;
        color: #00d4ff;
        margin-right: 8px;
        line-height: 1.5;
    }
    
    .ticker-price {
        font-size: 0.938rem;
        color: #ffffff;
        margin-right: 8px;
        line-height: 1.5;
    }
    
    .ticker-change-positive {
        font-size: 0.875rem;
        color: #00ff00;
        font-weight: bold;
        line-height: 1.5;
    }
    
    .ticker-change-negative {
        font-size: 0.875rem;
        color: #ff4444;
        font-weight: bold;
        line-height: 1.5;
    }
    
    @keyframes ticker-scroll {
        0% {
            transform: translateX(0%);
        }
        100% {
            transform: translateX(-50%);
        }
    }
    
    .ticker-container:hover .ticker-wrapper {
        animation-play-state: paused;
    }
    
    /* Custom button colors */
    /* Refresh All button - green */
    button[kind="secondary"]:has(p:contains("Refresh All")) {
        background-color: #00c853 !important;
        color: white !important;
        border: none !important;
    }
    button[kind="secondary"]:has(p:contains("Refresh All")):hover {
        background-color: #00e676 !important;
    }
    
    /* Mobile table responsiveness */
    @media (max-width: 768px) {
        table {
            display: block;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            white-space: nowrap;
        }
        
        table th,
        table td {
            padding: 8px !important;
            font-size: 12px !important;
        }
        
        /* Hide chart column on very small screens */
        @media (max-width: 480px) {
            table th:nth-child(3),
            table td:nth-child(3) {
                display: none;
            }
        }
    }
    
    /* Touch-friendly buttons */
    @media (max-width: 768px) {
        button {
            min-height: 44px !important;
            padding: 0.75rem 1rem !important;
        }
    }
    
    /* Mobile ticker adjustments */
    @media (max-width: 768px) {
        .ticker-container {
            padding: 4px 0;
            margin: 0 0 8px 0;
        }
        
        .ticker-item {
            margin: 0 15px;
            padding: 4px 12px;
            min-height: 28px;
        }
        
        .ticker-symbol,
        .ticker-price {
            font-size: 0.813rem;
        }
        
        .ticker-change-positive,
        .ticker-change-negative {
            font-size: 0.75rem;
        }
    }
</style>
"""

# Metric styling CSS - Using rem for better cross-platform consistency
METRIC_CSS = """
<style>
    [data-testid="stMetricValue"] { font-size: 1.375rem !important; line-height: 1.4 !important; }
    [data-testid="stMetricLabel"] { font-size: 0.938rem !important; line-height: 1.5 !important; }
    [data-testid="stMetricDelta"] { font-size: 0.938rem !important; font-weight: bold !important; line-height: 1.5 !important; }
    [data-testid="stMetricDelta"]:has(svg[data-testid="stMetricDeltaIcon-Up"]) { color: #00ff00 !important; }
    [data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Up"] { fill: #00ff00 !important; }
    [data-testid="stMetricDelta"]:has(svg[data-testid="stMetricDeltaIcon-Down"]) { color: #ff4444 !important; }
    [data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Down"] { fill: #ff4444 !important; }
</style>
"""
