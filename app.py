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
from data_fetchers import get_stock_list, get_stock_performance, fetch_stocks_bulk, validate_stock_symbol, get_available_nse_indices
from file_manager import load_all_saved_lists, save_list_to_csv, delete_list_csv
from cache_manager import get_cache_stats, clear_cache
from ui_components import (
    render_header, render_market_indices, render_sidebar_info,
    render_top_bottom_performers, render_averages, render_pagination_controls,
    render_live_ticker, render_gainer_loser_banner, render_sectoral_yearly_performance
)
from utils import create_html_table

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
    initial_sidebar_state="auto"  # Auto-collapse on mobile
)


def render_stock_selection_sidebar():
    """Render sidebar for stock selection and options"""
    st.sidebar.markdown("**📋 Stock Selection**")
    
    # Get dynamic list of available indices
    available_indices = get_available_nse_indices()
    index_options = list(available_indices.keys()) + ['Upload File']
    
    # Category selection
    category = st.sidebar.selectbox(
        "Select Category",
        options=index_options,
        index=0
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


def fetch_stocks_data(selected_stocks, use_parallel, use_cache=True):
    """Fetch stock data using parallel or sequential method with caching"""
    num_stocks = len(selected_stocks)
    
    # For large datasets (>100 stocks), always use bulk fetch with caching
    if num_stocks > 100:
        st.info(f"🚀 Optimized mode: Fetching {num_stocks} stocks with caching (3 parallel workers)")
        return fetch_stocks_bulk(selected_stocks, max_workers=3, use_cache=use_cache)
    
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
    
    # Render header
    render_header()
    
    # Render gainer/loser banner and get FII/DII source
    fii_dii_source = render_gainer_loser_banner()
    
    # Render live ticker
    stock_count = render_live_ticker()
    
    # Display ticker caption with FII/DII source at extreme right
    col_left, col_right = st.columns([5, 1])
    with col_left:
        st.caption(f"📊 Live Ticker: {stock_count} stocks • Updates every 60 seconds • Hover to pause")
    with col_right:
        if fii_dii_source:
            st.markdown(f"<p style='text-align: right; font-size: 0.8rem; color: #888;'>📊 FII/DII: {fii_dii_source}</p>", unsafe_allow_html=True)
    
    # Sidebar: Stock selection
    category = render_stock_selection_sidebar()
    
    # Clear cache if category changed
    if st.session_state.last_category != category:
        st.session_state.cached_stocks_data = None
        st.session_state.cached_stocks_list = None
        st.session_state.last_category = category
    
    # Determine stock list based on category
    if category == 'Upload File':
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
    
    # Display Market Indices
    render_market_indices()
    
    # Display title
    if category == 'Upload File' and st.session_state.current_list_name:
        display_title = f"📊 {st.session_state.current_list_name} - Performance Summary ({len(selected_stocks)} Stock(s))"
    else:
        display_title = f"📊 {category} - Performance Summary ({len(selected_stocks)} Stock(s))"
    
    st.subheader(display_title)
    st.caption(f"🔽 Sorted by: **{sort_by}** ({sort_order})")
    
    # Check if we need to fetch data (only if stocks list changed)
    stocks_list_key = ','.join(sorted(selected_stocks))  # Create unique key for current stock list
    
    if (st.session_state.cached_stocks_data is None or 
        st.session_state.cached_stocks_list != stocks_list_key):
        # Fetch stock data only when needed
        with st.spinner("🔄 Fetching stock data..."):
            stocks_data = fetch_stocks_data(selected_stocks, use_parallel, use_cache)
        
        if not stocks_data:
            st.error("❌ Failed to fetch data for the selected stocks. Please try again later.")
            return
        
        # Cache the fetched data
        st.session_state.cached_stocks_data = stocks_data
        st.session_state.cached_stocks_list = stocks_list_key
    else:
        # Use cached data (no re-fetch needed for sorting)
        stocks_data = st.session_state.cached_stocks_data
    
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
    total_items = len(df)
    start_idx, end_idx = render_pagination_controls(total_items, ITEMS_PER_PAGE)
    df_page = df.iloc[start_idx:end_idx]
    
    # Display table
    html_table = create_html_table(df_page)
    st.markdown(html_table, unsafe_allow_html=True)
    st.caption(f"Showing {start_idx + 1} to {end_idx} of {total_items} stocks")
    
    # Top/Bottom performers
    render_top_bottom_performers(df)
    
    # Averages
    render_averages(df)
    
    # Sectoral yearly performance
    render_sectoral_yearly_performance()


if __name__ == "__main__":
    main()
