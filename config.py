"""
Configuration and Constants for NSE Stock Performance Tracker
"""

# Directory for saved lists
SAVED_LISTS_DIR = "saved_stock_lists"

# Pagination settings
ITEMS_PER_PAGE = 10

# Fallback stock lists (Latest Nifty 50 composition - Updated Nov 2025)
FALLBACK_NIFTY_50 = [
    'ADANIENT.NS', 'ADANIPORTS.NS', 'APOLLOHOSP.NS', 'ASIANPAINT.NS', 'AXISBANK.NS',
    'BAJAJ-AUTO.NS', 'BAJFINANCE.NS', 'BAJAJFINSV.NS', 'BEL.NS', 'BHARTIARTL.NS',
    'CIPLA.NS', 'COALINDIA.NS', 'DRREDDY.NS', 'EICHERMOT.NS', 'ETERNAL.NS', 'GRASIM.NS',
    'HCLTECH.NS', 'HDFCBANK.NS', 'HDFCLIFE.NS', 'HINDALCO.NS', 'HINDUNILVR.NS',
    'ICICIBANK.NS', 'ITC.NS', 'INDUSINDBK.NS', 'INFY.NS', 'JSWSTEEL.NS',
    'KOTAKBANK.NS', 'LT.NS', 'M&M.NS', 'MARUTI.NS', 'MAXHEALTH.NS', 'NTPC.NS',
    'NESTLEIND.NS', 'ONGC.NS', 'POWERGRID.NS', 'RELIANCE.NS', 'SBILIFE.NS',
    'SHRIRAMFIN.NS', 'SBIN.NS', 'SUNPHARMA.NS', 'TCS.NS', 'TATACONSUM.NS', 'TMPV.NS',
    'TATASTEEL.NS', 'TECHM.NS', 'TITAN.NS', 'TRENT.NS', 'ULTRACEMCO.NS', 'WIPRO.NS'
]

FALLBACK_NIFTY_NEXT_50 = [
    'ADANIENT.NS', 'AMBUJACEM.NS', 'BANDHANBNK.NS', 'BERGEPAINT.NS', 'BEL.NS',
    'BOSCHLTD.NS', 'CHOLAFIN.NS', 'COLPAL.NS', 'DABUR.NS', 'DLF.NS',
    'GODREJCP.NS', 'HAVELLS.NS', 'HDFCAMC.NS', 'ICICIPRULI.NS', 'IDEA.NS',
    'INDIGO.NS', 'JINDALSTEL.NS', 'LICHSGFIN.NS', 'LUPIN.NS', 'MARICO.NS',
    'MCDOWELL-N.NS', 'MUTHOOTFIN.NS', 'NMDC.NS', 'NYKAA.NS', 'PAGEIND.NS',
    'PETRONET.NS', 'PIDILITIND.NS', 'PNB.NS', 'RECLTD.NS', 'SBICARD.NS',
    'SHRIRAMFIN.NS', 'SIEMENS.NS', 'TATAPOWER.NS', 'TORNTPHARM.NS', 'TRENT.NS',
    'VEDL.NS', 'VOLTAS.NS', 'ETERNAL.NS'
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
    'ethereum': 'ETH-USD',
    'btc': 'BTC-USD'
}

# Custom CSS for dark theme
CUSTOM_CSS = """
<style>
    /* ========== COPY PROTECTION ========== */
    /* Disable text selection */
    * {
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        user-select: none !important;
        -webkit-touch-callout: none !important;
    }
    
    /* Prevent drag and drop of images */
    img {
        pointer-events: none !important;
        -webkit-user-drag: none !important;
        -khtml-user-drag: none !important;
        -moz-user-drag: none !important;
        -o-user-drag: none !important;
        user-drag: none !important;
    }
    
    /* Disable copy/paste context menu */
    body {
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        user-select: none !important;
    }
    
    /* Mobile viewport optimization */
    @viewport {
        width: device-width;
        zoom: 1.0;
    }
    
    .main {
        background: linear-gradient(135deg, #0a1929 0%, #1a237e 50%, #0d1b2a 100%) !important;
        padding: 0.5rem 1rem 1rem 1rem;
    }
    .stApp {
        background: linear-gradient(135deg, #0a1929 0%, #1a237e 50%, #0d1b2a 100%) !important;
    }
    
    /* Page-wide background */
    body {
        background: linear-gradient(135deg, #0a1929 0%, #1a237e 50%, #0d1b2a 100%) !important;
    }
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }
    header {
        background-color: transparent !important;
    }
    
    /* Hide GitHub fork button and all menu items */
    .viewerBadge_container__1QSob,
    .viewerBadge_link__1S137,
    a[href*="github.com"][target="_blank"]:has(svg),
    header a[href*="github"] {
        display: none !important;
    }
    
    /* Hide Streamlit menu buttons (Share, Fork, Deploy, Settings) */
    header[data-testid="stHeader"] button[kind="header"]:not([data-testid="collapsedControl"]) {
        display: none !important;
    }
    
    /* Hide main menu completely */
    #MainMenu {
        display: none !important;
    }
    
    /* Hide the three dots menu in header */
    header button[aria-label*="menu"],
    header button[aria-label*="Menu"] {
        display: none !important;
    }
    
    /* Style sidebar toggle button */
    button[kind="header"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: 2px solid #ffffff !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.6) !important;
    }
    button[kind="header"]:hover {
        background: linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.8) !important;
        transform: scale(1.05) !important;
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
        
        /* Make info boxes stack vertically on mobile */
        [data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: column !important;
            gap: 0.5rem !important;
        }
        
        [data-testid="stHorizontalBlock"] > div {
            flex: 1 1 100% !important;
            min-width: 100% !important;
            max-width: 100% !important;
        }
        
        /* Info boxes - Full width and scrollable tables */
        .info-box {
            width: 100% !important;
            overflow-x: auto !important;
            margin-bottom: 0.5rem !important;
            max-width: 100vw !important;
        }
        
        .info-box table {
            min-width: 500px !important;
            width: 100% !important;
            font-size: 0.75rem !important;
        }
        
        .info-box td, .info-box th {
            padding: 0.4rem 0.5rem !important;
            font-size: 0.75rem !important;
            white-space: nowrap !important;
            min-width: 80px !important;
        }
        
        .info-box td:first-child, .info-box th:first-child {
            min-width: 120px !important;
        }
        
        .info-box-title {
            font-size: 0.85rem !important;
            padding: 0.4rem !important;
        }
        
        /* Scroll indicator for mobile */
        .info-box:after {
            content: '← Swipe to see more →';
            display: block;
            text-align: center;
            color: rgba(66, 165, 245, 0.6);
            font-size: 0.7rem;
            padding: 0.2rem;
            font-style: italic;
        }
        
        /* Main data tables - Scrollable on mobile */
        .dataframe, 
        .stDataFrame,
        [data-testid="stDataFrame"] {
            overflow-x: auto !important;
            display: block !important;
            max-width: 100vw !important;
        }
        
        .dataframe table,
        [data-testid="stDataFrame"] table {
            font-size: 0.7rem !important;
            min-width: 600px !important;
        }
        
        .dataframe th,
        .dataframe td,
        [data-testid="stDataFrame"] th,
        [data-testid="stDataFrame"] td {
            padding: 0.3rem 0.25rem !important;
            font-size: 0.7rem !important;
        }
        
        /* Metrics - Smaller on mobile */
        [data-testid="stMetric"] {
            padding: 0.3rem !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.7rem !important;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1rem !important;
        }
        
        /* Make metrics wrap to 2 columns only for market indices */
        .metric-row [data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-wrap: wrap !important;
            flex-direction: row !important;
        }
        
        .metric-row [data-testid="stHorizontalBlock"] > div {
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
    /* Dataframe/Table Styling - Match High Volume Stocks */
    .dataframe, 
    .stDataFrame,
    [data-testid="stDataFrame"],
    table {
        background: linear-gradient(135deg, rgba(26, 35, 126, 0.3) 0%, rgba(13, 27, 42, 0.5) 100%) !important;
        border: 1px solid rgba(66, 165, 245, 0.3) !important;
        border-radius: 8px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4), 0 0 20px rgba(66, 165, 245, 0.1) !important;
    }
    
    thead tr th,
    .dataframe thead tr th,
    [data-testid="stDataFrame"] thead tr th {
        background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%) !important;
        color: #42a5f5 !important;
        font-weight: 600 !important;
        border: 1px solid rgba(66, 165, 245, 0.3) !important;
        padding: 0.5rem !important;
        font-size: 0.875rem !important;
    }
    
    tbody tr td,
    .dataframe tbody tr td,
    [data-testid="stDataFrame"] tbody tr td {
        background-color: rgba(13, 27, 42, 0.4) !important;
        color: #ffffff;
        border: 1px solid rgba(66, 165, 245, 0.2) !important;
        padding: 0.5rem !important;
    }
    
    tbody tr:hover td,
    .dataframe tbody tr:hover td,
    [data-testid="stDataFrame"] tbody tr:hover td {
        background: linear-gradient(135deg, rgba(26, 35, 126, 0.5) 0%, rgba(13, 71, 161, 0.3) 100%) !important;
    }
    
    tbody tr:nth-child(even) td {
        background-color: rgba(13, 27, 42, 0.5) !important;
    }
    .positive {
        color: #00ff00 !important;
        font-weight: bold;
    }
    .negative {
        color: #ff4444 !important;
        font-weight: bold;
    }
    
    /* Sidebar Styling - Navy Blue Theme */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1b2a 0%, #1a237e 100%) !important;
        border-right: 2px solid rgba(66, 165, 245, 0.3) !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }
    .sidebar .sidebar-content {
        background: transparent !important;
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
        
        /* 3-column layout for market indices and sectors on mobile */
        /* Note: Top/Bottom performers override this in their own CSS */
        [data-testid="stHorizontalBlock"] {
            display: grid !important;
            grid-template-columns: repeat(3, 1fr) !important;
            gap: 0.25rem !important;
        }
        [data-testid="stHorizontalBlock"] [data-testid="column"] {
            width: 100% !important;
            flex: none !important;
            min-width: 0 !important;
        }
        /* Reduce font size for mobile metrics */
        [data-testid="stMetric"] {
            font-size: 0.75rem !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.7rem !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 0.85rem !important;
        }
        
        /* Single line ticker on mobile */
        .ticker-container {
            white-space: nowrap !important;
            overflow-x: auto !important;
        }
        .ticker-wrapper {
            display: inline-flex !important;
            flex-wrap: nowrap !important;
        }
        .ticker-item {
            flex-shrink: 0 !important;
        }
        
        /* 2-column grid for header commodities on mobile */
        .header-info {
            display: grid !important;
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 0.25rem !important;
        }
        .header-info p {
            margin: 0.25rem 0 !important;
            font-size: 10px !important;
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
    
    /* Rolling Ticker Styles - Navy Blue Theme */
    .ticker-container {
        background: linear-gradient(90deg, rgba(13, 27, 42, 0.8) 0%, rgba(26, 35, 126, 0.6) 50%, rgba(13, 27, 42, 0.8) 100%);
        border: 1px solid rgba(66, 165, 245, 0.3);
        border-radius: 8px;
        padding: 8px 0;
        margin: 0 0 15px 0;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4), 0 0 20px rgba(66, 165, 245, 0.1);
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

# Metric styling CSS - Beautiful box design for indices
METRIC_CSS = """
<style>
    /* Beautiful box styling for metrics - Navy Blue Theme - Compact */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(26, 35, 126, 0.3) 0%, rgba(13, 27, 42, 0.5) 100%) !important;
        border: 1px solid rgba(66, 165, 245, 0.3) !important;
        border-radius: 8px !important;
        padding: 0.5rem 0.75rem !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3), 0 0 15px rgba(66, 165, 245, 0.08) !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stMetric"]:hover {
        background: linear-gradient(135deg, rgba(26, 35, 126, 0.5) 0%, rgba(13, 71, 161, 0.3) 100%) !important;
        border-color: rgba(66, 165, 245, 0.6) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4), 0 0 20px rgba(66, 165, 245, 0.15) !important;
    }
    
    [data-testid="stMetricLabel"] { 
        font-size: 0.7rem !important; 
        line-height: 1.3 !important;
        color: rgba(255, 255, 255, 0.7) !important;
        font-weight: 500 !important;
        margin-bottom: 0.25rem !important;
        display: block !important;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #ffffff !important;
        line-height: 1.2 !important;
        margin-bottom: 0.2rem !important;
        font-family: 'JetBrains Mono', monospace !important;
        display: block !important;
    }
    
    [data-testid="stMetricDelta"] { 
        font-size: 0.7rem !important; 
        font-weight: 600 !important; 
        line-height: 1.2 !important;
        padding: 2px 5px !important;
        border-radius: 3px !important;
        display: inline-block !important;
        margin-bottom: 0 !important;
        white-space: nowrap !important;
    }
    
    /* Positive change - green box */
    [data-testid="stMetricDelta"]:has(svg[data-testid="stMetricDeltaIcon-Up"]) { 
        color: #00ff00 !important;
        background-color: rgba(0, 255, 0, 0.15) !important;
        border: 1px solid rgba(0, 255, 0, 0.3) !important;
    }
    
    [data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Up"] { 
        fill: #00ff00 !important; 
    }
    
    /* Negative change - red box */
    [data-testid="stMetricDelta"]:has(svg[data-testid="stMetricDeltaIcon-Down"]) { 
        color: #ff4444 !important;
        background-color: rgba(255, 68, 68, 0.15) !important;
        border: 1px solid rgba(255, 68, 68, 0.3) !important;
    }
    
    [data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Down"] { 
        fill: #ff4444 !important; 
    }
</style>

<script>
    // ========== COPY PROTECTION JAVASCRIPT ==========
    
    // Disable right-click context menu
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        return false;
    }, false);
    
    // Disable keyboard shortcuts for copy/paste/view source
    document.addEventListener('keydown', function(e) {
        // Ctrl+C, Ctrl+X, Ctrl+V (Copy, Cut, Paste)
        if ((e.ctrlKey || e.metaKey) && (e.key === 'c' || e.key === 'x' || e.key === 'v')) {
            e.preventDefault();
            return false;
        }
        // Ctrl+U (View Source)
        if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
            e.preventDefault();
            return false;
        }
        // Ctrl+S (Save Page)
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            return false;
        }
        // F12 (Developer Tools)
        if (e.key === 'F12') {
            e.preventDefault();
            return false;
        }
        // Ctrl+Shift+I (Inspect Element)
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'I') {
            e.preventDefault();
            return false;
        }
        // Ctrl+Shift+C (Inspect Element)
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'C') {
            e.preventDefault();
            return false;
        }
        // Ctrl+Shift+J (Console)
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'J') {
            e.preventDefault();
            return false;
        }
    }, false);
    
    // Disable text selection on copy attempt
    document.addEventListener('copy', function(e) {
        e.preventDefault();
        return false;
    }, false);
    
    // Disable cut
    document.addEventListener('cut', function(e) {
        e.preventDefault();
        return false;
    }, false);
    
    // Disable paste
    document.addEventListener('paste', function(e) {
        e.preventDefault();
        return false;
    }, false);
    
    // Disable drag events
    document.addEventListener('dragstart', function(e) {
        e.preventDefault();
        return false;
    }, false);
    
    // Disable select all
    document.addEventListener('selectstart', function(e) {
        e.preventDefault();
        return false;
    }, false);
    
    // Console warning message
    console.log('%c⚠️ WARNING: Content Protection Enabled', 'color: red; font-size: 20px; font-weight: bold;');
    console.log('%cThis website is protected. Unauthorized copying is prohibited.', 'color: orange; font-size: 14px;');
</script>
"""
