"""
NSE Stock Performance Tracker - Main Application
Streamlit app for tracking Indian stock market performance
"""

import streamlit as st
import pandas as pd
import warnings
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Import custom modules
from config import CUSTOM_CSS, ITEMS_PER_PAGE
from data_fetchers import (
    get_stock_list,
    get_stock_performance,
    fetch_stocks_bulk,
    validate_stock_symbol,
    get_available_nse_indices,
    get_stock_52_week_range,
)
from file_manager import load_all_saved_lists, save_list_to_csv, delete_list_csv
from cache_manager import get_cache_stats, clear_cache
from ui_components import (
    render_header, render_market_indices, render_sidebar_info,
    render_top_bottom_performers, render_averages, render_pagination_controls,
    render_live_ticker, render_gainer_loser_banner, render_sectoral_yearly_performance
)
from utils import create_html_table, get_market_session_status, get_current_times
from screenshot_protection import apply_screenshot_protection

warnings.filterwarnings('ignore')

# Load admin password from .env file
def load_admin_password():
    """Load admin password from .env file"""
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('ADMIN_PASSWORD='):
                    return line.split('=', 1)[1].strip()
    return "Admin@123"  # Default fallback

ADMIN_PASSWORD = load_admin_password()

# Page configuration
st.set_page_config(
    page_title="NSE Stock Performance",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",  # Expanded on desktop, collapsible on mobile
    menu_items=None  # Hide Fork/Deploy/Settings menu
)


def render_stock_selection_sidebar():
    """Render sidebar for stock selection and options"""
    st.sidebar.markdown("**📋 Stock Selection**")
    
    # Initialize session state for category if not exists
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = 'Nifty 50'  # Default value
    
    # Get dynamic list of available indices
    available_indices = get_available_nse_indices()
    index_options = list(available_indices.keys()) + ['Upload File']
    
    # Get the current index to maintain selection
    current_index = index_options.index(st.session_state.selected_category) if st.session_state.selected_category in index_options else 0
    
    # Category selection with on_change handler
    def on_category_change():
        # Only clear cache if category actually changed
        if st.session_state.selected_category != st.session_state.category_select:
            st.session_state.selected_category = st.session_state.category_select
            # Clear stock data cache when category changes
            if 'cached_stocks_data' in st.session_state:
                del st.session_state.cached_stocks_data
            if 'cached_stocks_list' in st.session_state:
                del st.session_state.cached_stocks_list
            # Reset pagination to first page when switching lists
            st.session_state.current_page = 1
    
    # Create the selectbox with the current value from session state
    category = st.sidebar.selectbox(
        "Select Category",
        options=index_options,
        index=current_index,
        key='category_select',
        on_change=on_category_change
    )
    
    return category


def handle_file_upload():
    """Handle file upload and saved lists management"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("<p style='color: #ff4444; font-weight: 600;'>📤 Manage Stock Lists</p>", unsafe_allow_html=True)
    
    # Admin authentication
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    if 'admin_mode' not in st.session_state:
        st.session_state.admin_mode = False
    
    # Admin login section
    if not st.session_state.admin_authenticated:
        with st.sidebar.expander("🔐 Admin Login"):
            admin_password = st.text_input("Admin Password", type="password", key="admin_pass")
            if st.button("Login"):
                if admin_password == ADMIN_PASSWORD:
                    st.session_state.admin_authenticated = True
                    st.session_state.admin_mode = True
                    st.success("✅ Admin access granted!")
                    st.rerun()
                else:
                    st.error("❌ Invalid password")
    else:
        # Show admin controls if authenticated
        st.sidebar.markdown("**🔓 Admin Mode Active**")
        st.session_state.admin_mode = st.sidebar.checkbox(
            "💾 Save to Disk",
            value=st.session_state.admin_mode,
            help="Enable to save lists permanently to disk."
        )
        if st.sidebar.button("🚪 Logout"):
            st.session_state.admin_authenticated = False
            st.session_state.admin_mode = False
            st.rerun()
    
    # Display disk lists (available to all users)
    if st.session_state.disk_lists:
        st.sidebar.markdown(f"**💾 Permanent Lists:**", unsafe_allow_html=True)
        for list_name, stocks in st.session_state.disk_lists.items():
            col1, col2 = st.sidebar.columns([3, 1])
            with col1:
                if st.button(f"📋 {list_name} ({len(stocks)})", key=f"load_disk_{list_name}"):
                    st.session_state.current_list_name = list_name
                    st.session_state.current_list_source = 'disk'
                    st.rerun()
            with col2:
                # Only show delete button for admins
                if st.session_state.admin_mode:
                    if st.button("🗑️", key=f"del_disk_{list_name}"):
                        del st.session_state.disk_lists[list_name]
                        delete_list_csv(list_name)
                        if st.session_state.current_list_name == list_name:
                            st.session_state.current_list_name = None
                            st.session_state.current_list_source = None
                        st.rerun()
        st.sidebar.markdown("---")
    
    # Display session lists (temporary uploads by non-admin users)
    if st.session_state.saved_lists:
        st.sidebar.markdown(f"<p style='color: #ff4444; font-weight: 600; margin-bottom: 0.75rem;'>📝 My Lists (This Session):</p>", unsafe_allow_html=True)
        for list_name, stocks in st.session_state.saved_lists.items():
            col1, col2 = st.sidebar.columns([3, 1])
            with col1:
                if st.button(f"📋 {list_name} ({len(stocks)})", key=f"load_session_{list_name}"):
                    st.session_state.current_list_name = list_name
                    st.session_state.current_list_source = 'session'
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_session_{list_name}"):
                    del st.session_state.saved_lists[list_name]
                    if st.session_state.current_list_name == list_name:
                        st.session_state.current_list_name = None
                        st.session_state.current_list_source = None
                    # Don't rerun, just remove from list
        st.sidebar.markdown("---")
    
    # Upload new list
    st.sidebar.markdown("<p style='color: #ff4444; font-weight: 600; margin-top: 0.5rem;'>📤 Upload New List</p>", unsafe_allow_html=True)
    
    sample_content = "RELIANCE.NS\nTCS.NS\nHDFCBANK.NS\nICICIBANK.NS\nINFY.NS"
    st.sidebar.download_button(
        label="📥 Download Sample Template",
        data=sample_content,
        file_name="sample_stocks.txt",
        mime="text/plain"
    )
    
    # Check if a list is already selected (after Quick Save)
    if st.session_state.current_list_name:
        # Check both disk and session lists
        if st.session_state.current_list_source == 'disk' and st.session_state.current_list_name in st.session_state.disk_lists:
            selected_stocks = st.session_state.disk_lists[st.session_state.current_list_name]
            st.sidebar.success(f"✅ Using '{st.session_state.current_list_name}' ({len(selected_stocks)} stocks)")
            return selected_stocks, selected_stocks
        elif st.session_state.current_list_source == 'session' and st.session_state.current_list_name in st.session_state.saved_lists:
            selected_stocks = st.session_state.saved_lists[st.session_state.current_list_name]
            st.sidebar.success(f"✅ Using '{st.session_state.current_list_name}' ({len(selected_stocks)} stocks)")
            return selected_stocks, selected_stocks
    
    uploaded_file = st.sidebar.file_uploader(
        "Choose a file",
        type=['csv', 'txt'],
        help="One symbol per line. Add .NS for NSE or .BO for BSE (e.g., RELIANCE.NS, INFY.BO)"
    )
    
    # Exchange selector
    exchange = st.sidebar.radio(
        "Select Exchange",
        options=['Auto-detect', 'NSE (.NS)', 'BSE (.BO)'],
        index=0,
        help="Auto-detect uses filename (e.g., 'bse.txt' → BSE)"
    )
    
    if uploaded_file is not None:
        try:
            content = uploaded_file.read().decode('utf-8')
            uploaded_stocks = [line.strip() for line in content.split('\n') if line.strip()]
            
            # Determine suffix based on selection
            if exchange == 'BSE (.BO)':
                suffix = '.BO'
            elif exchange == 'NSE (.NS)':
                suffix = '.NS'
            else:  # Auto-detect
                is_bse = 'bse' in uploaded_file.name.lower()
                suffix = '.BO' if is_bse else '.NS'
            
            st.sidebar.markdown(f"📍 Using suffix: **{suffix}**")
            
            # Prepare stock symbols
            prepared_stocks = []
            for symbol in uploaded_stocks:
                if '.NS' in symbol or '.BO' in symbol:
                    prepared_stocks.append(symbol)
                else:
                    prepared_stocks.append(f"{symbol}{suffix}")
            
            list_name = st.sidebar.text_input(
                "Enter a name for this list:",
                value=uploaded_file.name.replace('.txt', '').replace('.csv', ''),
                key="new_list_name"
            )
            
            # Option to skip validation for large lists
            skip_validation = st.sidebar.checkbox(
                "⚡ Skip validation (faster for large lists)",
                value=len(prepared_stocks) > 500,
                help="Skip symbol validation to load faster. Invalid symbols will be filtered during data fetch."
            )
            
            # Dynamic button text based on admin mode
            if st.session_state.admin_mode:
                button_text = "💾 Save to Disk"
                button_help = "Save permanently to disk (available to all users)"
                button_type = "primary"
            else:
                button_text = "⚡ Quick Save"
                button_help = "Save for this session (temporary, lost on browser close)"
                button_type = "primary"
            
            if st.sidebar.button(button_text, help=button_help, type=button_type):
                if list_name.strip():
                    if skip_validation:
                        # Save without validation
                        st.session_state.saved_lists[list_name.strip()] = prepared_stocks
                        st.session_state.current_list_name = list_name.strip()
                        
                        # Save to disk if admin mode is enabled
                        if st.session_state.admin_mode:
                            save_list_to_csv(list_name.strip(), prepared_stocks)
                            st.session_state.disk_lists[list_name.strip()] = prepared_stocks
                            st.session_state.current_list_source = 'disk'
                        else:
                            st.session_state.current_list_source = 'session'
                        
                        st.sidebar.success(f"✅ Loaded '{list_name}' with {len(prepared_stocks)} stocks!")
                        st.rerun()
                    else:
                        # Validate stocks before saving
                        with st.spinner("🔍 Validating stocks..."):
                            valid_stocks = []
                            invalid_stocks = []
                            
                            for symbol in prepared_stocks:
                                if validate_stock_symbol(symbol):
                                    valid_stocks.append(symbol)
                                else:
                                    invalid_stocks.append(symbol)
                            
                            if valid_stocks:
                                # Save to session
                                st.session_state.saved_lists[list_name.strip()] = valid_stocks
                                st.session_state.current_list_name = list_name.strip()
                                
                                # Save to disk if admin mode is enabled
                                if st.session_state.admin_mode:
                                    save_list_to_csv(list_name.strip(), valid_stocks)
                                    st.session_state.disk_lists[list_name.strip()] = valid_stocks
                                    st.session_state.current_list_source = 'disk'
                                else:
                                    st.session_state.current_list_source = 'session'
                                
                                if invalid_stocks:
                                    st.sidebar.warning(f"⚠️ Loaded {len(valid_stocks)} valid stocks. Skipped {len(invalid_stocks)} invalid: {', '.join(invalid_stocks[:5])}")
                                else:
                                    st.sidebar.success(f"✅ Loaded '{list_name}' with {len(valid_stocks)} stocks!")
                                st.rerun()
                            else:
                                st.sidebar.error("❌ No valid stocks found. Please check your symbols.")
                else:
                    st.sidebar.error("Please enter a list name")
            
            # Show preview but don't process until saved
            save_btn_text = "Quick Save" if not st.session_state.admin_mode else "Save to Disk"
            st.sidebar.markdown(f"<p style='font-size: 0.875rem; color: #e0e0e0;'>📋 Preview: <strong>{len(prepared_stocks)} stocks</strong> ready. Click '{save_btn_text}' to load.</p>", unsafe_allow_html=True)
            return [], []  # Return empty until saved
            
        except Exception as e:
            st.sidebar.error(f"Error reading file: {str(e)}")
            return [], []
    
    # No list selected or uploaded
    return [], []


def fetch_stocks_data(selected_stocks, use_parallel, use_cache=True, status_placeholder=None):
    """Fetch stock data using parallel or sequential method with caching"""
    num_stocks = len(selected_stocks)
    
    # Show cache status message
    from smart_cache_utils import get_cache_info_message
    cache_msg = get_cache_info_message()
    
    # For large datasets (>100 stocks), always use bulk fetch with caching
    if num_stocks > 100:
        if status_placeholder:
            status_placeholder.info(f"🚀 Optimized mode: Fetching {num_stocks} stocks with caching (4 parallel workers)\n\n{cache_msg}")
        return fetch_stocks_bulk(selected_stocks, max_workers=4, use_cache=use_cache, status_placeholder=status_placeholder)
    
    # For medium datasets (50-100), use parallel with caching
    elif use_parallel or num_stocks > 50:
        with st.spinner(f"⚡ Fetching {num_stocks} stocks in parallel (3 workers)..."):
            stocks_data = []
            progress_bar = st.progress(0)
            
            with ThreadPoolExecutor(max_workers=3) as executor:
                future_to_ticker = {
                    executor.submit(get_stock_performance, ticker, use_cache): ticker 
                    for ticker in selected_stocks
                }
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
            return stocks_data
    
    else:
        # Sequential method for small datasets
        with st.spinner(f"Fetching data for {num_stocks} stocks..."):
            stocks_data = []
            progress_bar = st.progress(0)
            
            for idx, ticker in enumerate(selected_stocks):
                data = get_stock_performance(ticker, use_cache)
                if data:
                    stocks_data.append(data)
                progress_bar.progress((idx + 1) / len(selected_stocks))
            
            progress_bar.empty()
            return stocks_data


def main():
    """Main application logic"""
    # Apply custom CSS first
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # Apply screenshot protection (cloud only)
    environment = apply_screenshot_protection()
    
    # Initialize session state
    if 'saved_lists' not in st.session_state:
        st.session_state.saved_lists = {}  # Session-only lists
    if 'disk_lists' not in st.session_state:
        st.session_state.disk_lists = load_all_saved_lists()  # Disk lists (read-only for non-admins)
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    if 'current_list_name' not in st.session_state:
        st.session_state.current_list_name = None
    if 'current_list_source' not in st.session_state:
        st.session_state.current_list_source = None  # 'disk' or 'session'
    if 'cached_stocks_data' not in st.session_state:
        st.session_state.cached_stocks_data = None
    if 'cached_stocks_list' not in st.session_state:
        st.session_state.cached_stocks_list = None
    if 'last_category' not in st.session_state:
        st.session_state.last_category = None
    if 'search_clear_requested' not in st.session_state:
        st.session_state.search_clear_requested = False
    if 'last_search_query' not in st.session_state:
        st.session_state.last_search_query = ""
    
    # Render header
    render_header()
    
    # Render gainer/loser banner and get FII/DII source
    fii_dii_source = render_gainer_loser_banner()
    
    # Render live ticker (volume stocks now in header)
    stock_count, advances, declines = render_live_ticker()
    
    # Display ticker caption with FII/DII source and advances/declines - mobile friendly
    st.markdown("""
    <style>
        .ticker-info-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            gap: 15px;
        }
        .ticker-info-left {
            font-size: 0.85rem;
            color: #888;
            line-height: 1.5;
            flex: 1;
        }
        .ticker-info-center {
            font-size: 0.85rem;
            color: #888;
            line-height: 1.5;
            text-align: center;
            white-space: nowrap;
            flex: 0 0 auto;
        }
        .ticker-info-right {
            font-size: 0.85rem;
            color: #888;
            line-height: 1.5;
            text-align: right;
            white-space: nowrap;
            flex: 1;
        }
        .adv-dec-positive {
            color: #00ff00;
            font-weight: bold;
        }
        .adv-dec-negative {
            color: #ff4444;
            font-weight: bold;
        }
        @media (max-width: 768px) {
            .ticker-info-container {
                flex-direction: column;
                align-items: flex-start;
                gap: 5px;
            }
            .ticker-info-left {
                font-size: 0.7rem !important;
                line-height: 1.6 !important;
            }
            .ticker-info-center {
                font-size: 0.7rem !important;
                line-height: 1.6 !important;
                text-align: left;
            }
            .ticker-info-right {
                font-size: 0.7rem !important;
                line-height: 1.6 !important;
                text-align: left;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    ticker_left = f"📊 Live Ticker: {stock_count} stocks • Updates every 60 seconds • Hover to pause" if stock_count else ""
    ticker_center = f"📈 <span class='adv-dec-positive'>Advances: {advances}</span> • <span class='adv-dec-negative'>Declines: {declines}</span>" if advances is not None and declines is not None else ""
    ticker_right = f"📊 FII/DII: {fii_dii_source}" if fii_dii_source else ""
    
    st.markdown(f"""
    <div class='ticker-info-container'>
        <div class='ticker-info-left'>{ticker_left}</div>
        <div class='ticker-info-center'>{ticker_center}</div>
        <div class='ticker-info-right'>{ticker_right}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar: Stock selection
    category = render_stock_selection_sidebar()
    
    # Clear cache if category changed (but don't force a rerun - let Streamlit handle it naturally)
    if st.session_state.last_category != category:
        st.session_state.cached_stocks_data = None
        st.session_state.last_category = category
    
    # Special handling for Nifty Total Market (direct JSON load)
    if category == 'Nifty Total Market':
        # Load pre-calculated data from JSON (zero Yahoo API calls!)
        import json
        import os
        json_file = os.path.join(os.path.dirname(__file__), "nifty_total_market.json")
        
        try:
            if os.path.exists(json_file):
                with open(json_file, "r") as f:
                    nse_data = json.load(f)
                
                if nse_data and isinstance(nse_data, dict) and nse_data.get("status") == "success" and nse_data.get("data"):
                    st.sidebar.markdown(f"<span style='color: #00c853;'>✅ Loaded {len(nse_data['data'])} stocks from NSE Bhavcopy ({nse_data.get('date', '')}) - Zero Yahoo API calls!</span>", unsafe_allow_html=True)
                    
                    # Convert to DataFrame directly
                    df_nse = pd.DataFrame(nse_data['data'])
                    
                    # Rename columns to match app format
                    df_nse = df_nse.rename(columns={
                        'symbol': 'Stock Name',
                        'close': 'Current Price',
                        'change_pct': 'Today %',
                        'volume': 'Volume',
                        'open': 'Open',
                        'high': 'High',
                        'low': 'Low',
                        'prev_close': 'Prev Close'
                    })
                    
                    # Add placeholder columns for other timeframes (NSE Bhavcopy is daily only)
                    df_nse['1 Week %'] = 0.0
                    df_nse['1 Month %'] = 0.0
                    df_nse['2 Months %'] = 0.0
                    df_nse['3 Months %'] = 0.0
                    df_nse['Sparkline'] = ''
                    
                    # Store in session for display
                    st.session_state.nifty_total_market_df = df_nse
                    selected_stocks = df_nse['Stock Name'].tolist()
                    available_stocks = selected_stocks
                else:
                    st.sidebar.error("❌ Invalid Nifty Total Market data format.")
                    st.sidebar.info("📋 **Action Required:** Trigger GitHub Actions workflow 'Fetch Nifty Total Market Daily Data' to generate the data file.")
                    return
            else:
                st.sidebar.error("❌ Nifty Total Market data file not found.")
                st.sidebar.info("📋 **Action Required:**\n1. Update `.github/workflows/fetch_nifty_total_market.yml` in your repo\n2. Trigger the workflow manually to generate data\n3. Or run locally: `python fetch_nifty_total_market.py`")
                return
        except Exception as e:
            st.sidebar.error(f"❌ Error loading Nifty Total Market: {str(e)}")
            st.sidebar.info("📋 Please ensure the GitHub Actions workflow has run successfully to generate `nifty_total_market.json`")
            return
    
    # Determine stock list based on category
    elif category == 'Upload File':
        selected_stocks, available_stocks = handle_file_upload()
    else:
        # Dynamic category - fetch from NSE
        with st.spinner(f"Fetching {category} stock list..."):
            selected_stocks, fetch_status = get_stock_list(category)
            available_stocks = selected_stocks
        
        if "✅" in fetch_status:
            st.sidebar.markdown(f"<span style='color: #00c853;'>{fetch_status}</span>", unsafe_allow_html=True)
        else:
            st.sidebar.markdown(f"<span style='color: #ff9800;'>⚠️ {fetch_status}</span>", unsafe_allow_html=True)
    
    # Sorting options
    st.sidebar.markdown("---")
    sort_by = st.sidebar.selectbox(
        "Sort by",
        options=['3 Months %', '2 Months %', '1 Month %', '1 Week %', 'Today %', 'Stock Name'],
        index=0
    )
    sort_order = st.sidebar.radio(
        "Order By",
        options=['Best to Worst', 'Worst to Best'],
        index=0,
        horizontal=True
    )
    
    # Performance options
    st.sidebar.markdown("---")
    st.sidebar.markdown("<p style='color: #ff4444; font-weight: 600;'>⚡ Performance</p>", unsafe_allow_html=True)
    use_parallel = st.sidebar.checkbox(
        "Use Parallel Fetching (3x faster)",
        value=False,
        help="Fetch 5 stocks at once (rate-limit safe). Keep unchecked for sequential mode (slower but more reliable)."
    )
    
    # Cache management
    st.sidebar.markdown("---")
    cache_stats = get_cache_stats()
    st.sidebar.text(f"Cached Stocks: {cache_stats['valid']}")
    st.sidebar.caption(f"Expired: {cache_stats['expired']} | Total: {cache_stats['total']}")
    
    # Stack buttons vertically on mobile
    st.sidebar.markdown("""
    <style>
        @media (max-width: 768px) {
            [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
                display: block !important;
            }
            [data-testid="stSidebar"] [data-testid="column"] {
                width: 100% !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        refresh_button = st.button("🔄 Refresh All", type="secondary")
        if refresh_button:
            clear_cache()
            st.session_state.cached_stocks_data = None  # Clear session cache
            st.session_state.cached_stocks_list = None
            st.rerun()
    with col2:
        use_cache = st.checkbox("Use Cache", value=True, help="Use cached data (6hr expiry)")
    
    # Sidebar info
    render_sidebar_info()
    
    # Check if stocks are selected
    if not selected_stocks:
        if category == 'Upload File':
            # Check if there are any saved lists
            has_permanent_lists = bool(st.session_state.disk_lists)
            has_session_lists = bool(st.session_state.saved_lists)
            
            if has_permanent_lists or has_session_lists:
                st.warning("⚠️ **Select a stock list:** Click on a list from the sidebar (💾 Permanent Lists or 📝 My Lists) to view performance.")
            else:
                st.warning("⚠️ **Get started:** Upload a file from the sidebar and click 'Quick Save' to view stock performance.")
        else:
            st.warning(f"⚠️ No stocks found in {category}. Please try another category.")
        return
    
    # Create placeholder containers to maintain layout during loading
    market_indices_placeholder = st.empty()
    title_placeholder = st.empty()
    summary_placeholder = st.empty()
    search_placeholder = st.empty()
    table_placeholder = st.empty()
    performers_placeholder = st.empty()
    averages_placeholder = st.empty()
    sectoral_placeholder = st.empty()
    
    # Display Market Indices (always show first)
    with market_indices_placeholder.container():
        render_market_indices()
    
    # Special fast path for Nifty Total Market (pre-loaded data)
    if category == 'Nifty Total Market' and hasattr(st.session_state, 'nifty_total_market_df'):
        df = st.session_state.nifty_total_market_df.copy()
        actual_count = len(df)
        
        with title_placeholder.container():
            st.markdown(f"""
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;'>
                <h3 style='margin: 0; color: white;'>📊 {category} - Performance Summary ({actual_count} Stock(s))</h3>
                <span style='color: #00c853; font-size: 0.75rem; white-space: nowrap;'>⚡ Instant Load - NSE Bhavcopy</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Display summary
        summary_text = f"🔽 Sorted by: <strong>{sort_by}</strong> ({sort_order}) | 📅 NSE Daily Data"
        
        with summary_placeholder.container():
            st.markdown(f"""
            <div style='display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 1rem;'>
                <div style='font-size: 0.95rem; color: #95e1d3;'>
                    {summary_text}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Standard Yahoo Finance fetch for other categories
        # Check if we need to fetch data (only if stocks list changed)
        stocks_list_key = ','.join(sorted(selected_stocks))  # Create unique key for current stock list
        
        if (st.session_state.cached_stocks_data is None or 
            st.session_state.cached_stocks_list != stocks_list_key):
            # Create a status placeholder for temporary messages
            status_placeholder_top = st.empty()
            
            # Show clean loading spinner
            with title_placeholder.container():
                st.markdown("""
                    <div style='text-align: center; padding: 40px 0;'>
                        <div class='spinner'></div>
                        <p style='color: #95e1d3; margin-top: 20px; font-size: 1.1rem;'>Loading...</p>
                    </div>
                    <style>
                        .spinner {
                            border: 3px solid rgba(255, 255, 255, 0.1);
                            border-left-color: #00d4ff;
                            border-radius: 50%;
                            width: 24px;
                            height: 24px;
                            animation: spin 1s linear infinite;
                            margin: 0 auto;
                        }
                        @keyframes spin {
                            0% { transform: rotate(0deg); }
                            100% { transform: rotate(360deg); }
                        }
                    </style>
                """, unsafe_allow_html=True)
            
            # Fetch stock data only when needed
            stocks_data = fetch_stocks_data(selected_stocks, use_parallel, use_cache, status_placeholder=status_placeholder_top)
            
            if not stocks_data:
                status_placeholder_top.empty()  # Clear status messages
                with title_placeholder.container():
                    st.error("❌ Failed to fetch data for the selected stocks. Please try again later.")
                return
            
            # Cache the fetched data
            st.session_state.cached_stocks_data = stocks_data
            st.session_state.cached_stocks_list = stocks_list_key
            
            # Clear status messages after successful load
            status_placeholder_top.empty()
        else:
            # Use cached data (no re-fetch needed for sorting)
            stocks_data = st.session_state.cached_stocks_data
        
        # Display title with actual fetched count
        actual_count = len(stocks_data)
        if category == 'Upload File' and st.session_state.current_list_name:
            display_title = f"📊 {st.session_state.current_list_name} - Performance Summary ({actual_count} Stock(s))"
        else:
            display_title = f"📊 {category} - Performance Summary ({actual_count} Stock(s))"
        
        # Log failed stocks (without displaying in title)
        if actual_count < len(selected_stocks):
            fetched_symbols = {data['Stock Name'] for data in stocks_data}
            failed_symbols = [s.replace('.NS', '').replace('.BO', '') for s in selected_stocks 
                             if s.replace('.NS', '').replace('.BO', '') not in fetched_symbols]
            if failed_symbols:
                print(f"⚠️ Failed to fetch data for: {', '.join(failed_symbols)}")
        
        with title_placeholder.container():
            st.markdown(f"""
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;'>
                <h3 style='margin: 0; color: white;'>{display_title}</h3>
                <span style='color: #ffc107; font-size: 0.75rem; white-space: nowrap;'>ⓘ Weekly/Monthly % may vary ±2%</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Get market session status and current time
        market_status, status_color = get_market_session_status()
        ist_time, _ = get_current_times()
        last_updated = ist_time.strftime('%d %b %Y, %I:%M %p IST')
        
        # Display summary of current view (will be updated after search if needed)
        summary_text = f"🔽 Sorted by: <strong>{sort_by}</strong> ({sort_order}) | 📅 Range: <strong>1M / 2M / 3M</strong>"
        
        with summary_placeholder.container():
            st.markdown(f"""
            <div style='display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 1rem;'>
                <div style='font-size: 0.95rem; color: #95e1d3;'>
                    {summary_text}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Create DataFrame
        df = pd.DataFrame(stocks_data)
    
    # Apply sorting
    ascending = True if sort_order == 'Worst to Best' else False
    
    if sort_by == 'Stock Name':
        df = df.sort_values(by='Stock Name', ascending=True)
    else:
        df = df.sort_values(by=sort_by, ascending=ascending)
    
    # Handle search clear request before rendering the search input
    if st.session_state.search_clear_requested:
        st.session_state.stock_search = ""
        clear_cache()  # Clear the cache as per user request
        st.session_state.search_clear_requested = False
    
    # Search functionality - Add search box above table
    with search_placeholder.container():
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            search_query = st.text_input(
                "🔍 Search stocks (type 3+ letters)",
                key="stock_search",
                placeholder="Type stock name or symbol (e.g., 'inf' for Infosys",
                help="Search filters by Stock Name. Type at least 3 characters to search."
            )
            if search_query != st.session_state.last_search_query:
                st.session_state.last_search_query = search_query
                st.session_state.current_page = 1
        with search_col2:
            # Add custom CSS for the clear button - navy blue, smaller size
            st.markdown("""
                <style>
                div[data-testid="column"]:nth-child(2) div[data-testid="stButton"] > button {
                    padding: 0.3rem 0.3rem !important;
                    font-size: 0.75rem !important;
                    background-color: #1e3a8a !important;
                    color: white !important;
                    border: 1px solid #2563eb !important;
                    border-radius: 4px !important;
                    margin-top: 1.85rem !important;
                    height: 2.2rem !important;
                }
                div[data-testid="column"]:nth-child(2) div[data-testid="stButton"] > button:hover {
                    background-color: #2563eb !important;
                    color: white !important;
                    border-color: #3b82f6 !important;
                }
                </style>
            """, unsafe_allow_html=True)
            if search_query:
                if st.button("✖ Clear", key="clear_search"):
                    st.session_state.search_clear_requested = True
                    st.rerun()
    
    # Apply search filter if query length >= 3
    original_count = len(df)
    search_active = search_query and len(search_query) >= 3
    search_results_52w = []

    if search_active:
        # Case-insensitive search in Stock Name column (handles partial matches)
        # regex=False ensures literal string matching (not regex patterns)
        df_filtered = df[df['Stock Name'].str.lower().str.contains(search_query.lower(), case=False, na=False, regex=False)]
        
        if len(df_filtered) == 0:
            # Show warning but don't exit - display the message in table area
            with table_placeholder.container():
                st.warning(f"⚠️ No stocks found matching '{search_query}'. Try a different search term or click 'Clear' to see all stocks.")
            # Display performers and averages with original data
            with performers_placeholder.container():
                df_temp = df.copy()
                df_temp = df_temp.reset_index(drop=True)
                df_temp.insert(0, 'Rank', range(1, len(df_temp) + 1))
                render_top_bottom_performers(df_temp)
            with averages_placeholder.container():
                df_temp = df.copy()
                df_temp = df_temp.reset_index(drop=True)
                df_temp.insert(0, 'Rank', range(1, len(df_temp) + 1))
                render_averages(df_temp)
            with sectoral_placeholder.container():
                render_sectoral_yearly_performance()
            return
        
        df = df_filtered
        
        # Update summary to show search results
        filtered_count = len(df)
        summary_text = f"🔍 <strong>{filtered_count} of {original_count}</strong> stocks match '<strong>{search_query}</strong>' | 🔽 Sorted by: <strong>{sort_by}</strong> ({sort_order})"
        with summary_placeholder.container():
            st.markdown(f"""
            <div style='display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 1rem;'>
                <div style='font-size: 0.95rem; color: #ffc107;'>
                    {summary_text}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Gather 52-week stats for top matches (limit to 5 for performance)
        max_cards = min(filtered_count, 5)
        subset = df.iloc[:max_cards]
        for _, row in subset.iterrows():
            ticker = row.get('Ticker')
            if not ticker:
                continue
            details = get_stock_52_week_range(ticker)
            if details:
                search_results_52w.append({
                    'stock': row['Stock Name'],
                    'ticker': ticker,
                    'current_price': details['current_price'],
                    'high': details['high'],
                    'low': details['low'],
                    'high_date': details['high_date'],
                    'low_date': details['low_date'],
                })

    # Add rank after filtering
    df = df.reset_index(drop=True)
    df.insert(0, 'Rank', range(1, len(df) + 1))

    # Display table and pagination in placeholder
    with table_placeholder.container():
        # Pagination - get page range
        total_items = len(df)
        if search_query != st.session_state.last_search_query:
            st.session_state.current_page = 1
        start_idx, end_idx = render_pagination_controls(total_items, ITEMS_PER_PAGE, position="top")

        df_page = df.iloc[start_idx:end_idx]
        df_page_display = df_page.drop(columns=['Ticker']) if 'Ticker' in df_page.columns else df_page
        
        # Display table
        html_table = create_html_table(df_page_display)
        st.markdown(html_table, unsafe_allow_html=True)

    # Top/Bottom performers in placeholder
    if not search_active:
        with performers_placeholder.container():
            render_top_bottom_performers(df)
    else:
        with performers_placeholder.container():
            if search_results_52w:
                st.markdown("---")
                st.subheader("📈 52-Week Snapshot")

                cols = st.columns(len(search_results_52w))
                for idx, info in enumerate(search_results_52w):
                    with cols[idx]:
                        st.markdown(f"""
                            <div style='background: linear-gradient(135deg, rgba(30, 64, 175, 0.45) 0%, rgba(17, 24, 39, 0.6) 100%); border: 1px solid rgba(96, 165, 250, 0.35); border-radius: 10px; padding: 0.75rem; color: #e5edff; font-size: 0.82rem;'>
                                <div style='font-weight: 600; font-size: 0.9rem; margin-bottom: 0.35rem;'>{info['stock']} <span style='opacity: 0.7;'>({info['ticker']})</span></div>
                                <div style='margin-bottom: 0.25rem;'>Current: <span style='font-weight: 600;'>₹{info['current_price']:,.2f}</span></div>
                                <div style='margin-bottom: 0.2rem;'>52W High: <span style='color: #22c55e; font-weight: 600;'>₹{info['high']:,.2f}</span></div>
                                <div style='font-size: 0.7rem; opacity: 0.8; margin-bottom: 0.4rem;'>on {info['high_date'] or '—'}</div>
                                <div style='margin-bottom: 0.2rem;'>52W Low: <span style='color: #f97316; font-weight: 600;'>₹{info['low']:,.2f}</span></div>
                                <div style='font-size: 0.7rem; opacity: 0.8;'>on {info['low_date'] or '—'}</div>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No 52-week statistics available for the filtered stocks.")

    # Averages in placeholder
    with averages_placeholder.container():
        render_averages(df)
    
    # Sectoral yearly performance in placeholder
    with sectoral_placeholder.container():
        render_sectoral_yearly_performance()


if __name__ == "__main__":
    main()
