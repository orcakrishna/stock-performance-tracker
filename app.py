"""
NSE Stock Performance Tracker - Main Application
Streamlit app for tracking Indian stock market performance
"""
import streamlit as st
import pandas as pd
import warnings
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# === Custom Modules ===
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
    render_header,
    render_market_indices,
    render_sidebar_info,
    render_top_bottom_performers,
    render_averages,
    render_pagination_controls,
    render_live_ticker,
    render_gainer_loser_banner,
    render_sectoral_yearly_performance,
)
from utils import create_html_table, get_market_session_status, get_current_times
from screenshot_protection import apply_screenshot_protection

warnings.filterwarnings('ignore')


# === Load Admin Password ===
def load_admin_password():
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('ADMIN_PASSWORD='):
                    return line.split('=', 1)[1].strip()
    return "Admin@123"  # Default fallback


ADMIN_PASSWORD = load_admin_password()


# === Page Config ===
st.set_page_config(
    page_title="NSE Stock Performance",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)


# === Sidebar: Stock Selection ===
def render_stock_selection_sidebar():
    st.sidebar.markdown("**Stock Selection**")

    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = 'Nifty 50'

    available_indices = get_available_nse_indices()
    index_options = list(available_indices.keys()) + ['Upload File']
    current_index = index_options.index(st.session_state.selected_category) if st.session_state.selected_category in index_options else 0

    def on_category_change():
        if st.session_state.selected_category != st.session_state.category_select:
            st.session_state.selected_category = st.session_state.category_select
            if 'cached_stocks_data' in st.session_state:
                del st.session_state.cached_stocks_data
            if 'cached_stocks_list' in st.session_state:
                del st.session_state.cached_stocks_list
            st.session_state.current_page = 1

    category = st.sidebar.selectbox(
        "Select Category",
        options=index_options,
        index=current_index,
        key='category_select',
        on_change=on_category_change
    )
    return category


# === File Upload & List Management ===
def handle_file_upload():
    st.sidebar.markdown("---")
    st.sidebar.markdown("<p style='color: #ff4444; font-weight: 600;'>Manage Stock Lists</p>", unsafe_allow_html=True)

    # Admin Auth
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    if 'admin_mode' not in st.session_state:
        st.session_state.admin_mode = False

    if not st.session_state.admin_authenticated:
 adverse:
        with st.sidebar.expander("Admin Login"):
            pwd = st.text_input("Password", type="password", key="admin_pass")
            if st.button("Login"):
                if pwd == ADMIN_PASSWORD:
                    st.session_state.admin_authenticated = True
                    st.session_state.admin_mode = True
                    st.success("Admin access granted!")
                    st.rerun()
                else:
                    st.error("Invalid password")
    else:
        st.sidebar.markdown("**Admin Mode Active**")
        st.session_state.admin_mode = st.sidebar.checkbox(
            "Save to Disk",
            value=st.session_state.admin_mode,
            help="Save lists permanently."
        )
        if st.sidebar.button("Logout"):
            st.session_state.admin_authenticated = False
            st.session_state.admin_mode = False
            st.rerun()

    # Disk Lists
    if st.session_state.disk_lists:
        st.sidebar.markdown("**Permanent Lists:**", unsafe_allow_html=True)
        for name, stocks in st.session_state.disk_lists.items():
            c1, c2 = st.sidebar.columns([3, 1])
            with c1:
                if st.button(f"{name} ({len(stocks)})", key=f"load_{name}"):
                    st.session_state.current_list_name = name
                    st.session_state.current_list_source = 'disk'
                    st.rerun()
            with c2:
                if st.session_state.admin_mode:
                    if st.button("Delete", key=f"del_{name}"):
                        delete_list_csv(name)
                        del st.session_state.disk_lists[name]
                        if st.session_state.current_list_name == name:
                            st.session_state.current_list_name = None
                        st.rerun()

    # Session Lists
    if st.session_state.saved_lists:
        st.sidebar.markdown("<p style='color: #ff4444; font-weight: 600;'>My Lists (Session):</p>", unsafe_allow_html=True)
        for name, stocks in st.session_state.saved_lists.items():
            c1, c2 = st.sidebar.columns([3, 1])
            with c1:
                if st.button(f"{name} ({len(stocks)})", key=f"load_sess_{name}"):
                    st.session_state.current_list_name = name
                    st.session_state.current_list_source = 'session'
                    st.rerun()
            with c2:
                if st.button("Delete", key=f"del_sess_{name}"):
                    del st.session_state.saved_lists[name]
                    if st.session_state.current_list_name == name:
                        st.session_state.current_list_name = None

    # Upload
    st.sidebar.markdown("<p style='color: #ff4444; font-weight: 600;'>Upload New List</p>", unsafe_allow_html=True)
    st.sidebar.download_button(
        "Download Sample",
        "RELIANCE.NS\nTCS.NS\nHDFCBANK.NS",
        "sample_stocks.txt",
        "text/plain"
    )

    if st.session_state.current_list_name:
        source = st.session_state.current_list_source
        name = st.session_state.current_list_name
        stocks = st.session_state.disk_lists.get(name) if source == 'disk' else st.session_state.saved_lists.get(name)
        if stocks:
            st.sidebar.success(f"Using '{name}' ({len(stocks)} stocks)")
            return stocks, stocks

    uploaded = st.sidebar.file_uploader("Choose file", type=['csv', 'txt'])
    exchange = st.sidebar.radio("Exchange", ['Auto-detect', 'NSE (.NS)', 'BSE (.BO)'], index=0)

    if uploaded:
        try:
            content = uploaded.read().decode('utf-8')
            stocks = [s.strip() for s in content.split('\n') if s.strip()]
            suffix = '.BO' if exchange == 'BSE (.BO)' else '.NS'
            if exchange == 'Auto-detect':
                suffix = '.BO' if 'bse' in uploaded.name.lower() else '.NS'

            prepared = [s if '.NS' in s or '.BO' in s else f"{s}{suffix}" for s in stocks]
            name_input = st.sidebar.text_input("List name", value=uploaded.name.split('.')[0])

            skip_val = st.sidebar.checkbox("Skip validation", value=len(prepared) > 500)

            btn_text = "Save to Disk" if st.session_state.admin_mode else "Quick Save"
            if st.sidebar.button(btn_text, type="primary"):
                if name_input.strip():
                    if skip_val:
                        final = prepared
                    else:
                        with st.spinner("Validating..."):
                            final = [s for s in prepared if validate_stock_symbol(s)]
                            invalid = len(prepared) - len(final)
                            if invalid:
                                st.sidebar.warning(f"Skipped {invalid} invalid symbols")

                    st.session_state.saved_lists[name_input.strip()] = final
                    st.session_state.current_list_name = name_input.strip()
                    st.session_state.current_list_source = 'session'

                    if st.session_state.admin_mode:
                        save_list_to_csv(name_input.strip(), final)
                        st.session_state.disk_lists[name_input.strip()] = final
                        st.session_state.current_list_source = 'disk'

                    st.sidebar.success(f"Loaded '{name_input}'")
                    st.rerun()
                else:
                    st.sidebar.error("Enter a name")
            return [], []
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
    return [], []


# === Fetch Stocks Data ===
def fetch_stocks_data(stocks, parallel, cache=True, status=None):
    n = len(stocks)
    if n > 100:
        if status:
            status.info(f"Fetching {n} stocks (bulk mode)")
        return fetch_stocks_bulk(stocks, max_workers=3, use_cache=cache, status_placeholder=status)
    elif parallel or n > 50:
        with st.spinner(f"Fetching {n} stocks..."):
            data = []
            bar = st.progress(0)
            with ThreadPoolExecutor(max_workers=3) as exe:
                futures = {exe.submit(get_stock_performance, t, cache): t for t in stocks}
                for i, f in enumerate(as_completed(futures)):
                    res = f.result(timeout=30)
                    if res:
                        data.append(res)
                    bar.progress((i + 1) / n)
            bar.empty()
            return data
    else:
        with st.spinner(f"Fetching {n} stocks..."):
            data = []
            bar = st.progress(0)
            for i, t in enumerate(stocks):
                res = get_stock_performance(t, cache)
                if res:
                    data.append(res)
                bar.progress((i + 1) / n)
            bar.empty()
            return data


# === Main App ===
def main():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    apply_screenshot_protection()

    # Session State
    for key, val in {
        'saved_lists': {},
        'disk_lists': load_all_saved_lists(),
        'admin_authenticated': False,
        'current_list_name': None,
        'current_list_source': None,
        'cached_stocks_data': None,
        'cached_stocks_list': None,
        'last_category': None,
        'search_clear_requested': False,
        'last_search_query': ""
    }.items():
        if key not in st.session_state:
            st.session_state[key] = val

    render_header()
    fii_dii_source = render_gainer_loser_banner()
    stock_count, adv, dec = render_live_ticker()

    # Ticker Info
    st.markdown(f"""
    <div style='display: flex; justify-content: space-between; font-size: 0.85rem; color: #888; flex-wrap: wrap; gap: 10px;'>
        <div>Live Ticker: {stock_count} stocks</div>
        <div style='text-align: center;'>
            <span style='color: #00ff00;'>Advances: {adv}</span> • 
            <span style='color: #ff4444;'>Declines: {dec}</span>
        </div>
        <div style='text-align: right;'>FII/DII: {fii_dii_source}</div>
    </div>
    """, unsafe_allow_html=True)

    category = render_stock_selection_sidebar()

    if st.session_state.last_category != category:
        st.session_state.cached_stocks_data = None
        st.session_state.last_category = category

    if category == 'Upload File':
        stocks, _ = handle_file_upload()
    else:
        with st.spinner(f"Loading {category}..."):
            stocks, status = get_stock_list(category)
        st.sidebar.markdown(status, unsafe_allow_html=True)

    if not stocks:
        st.warning("No stocks selected. Upload or choose a category.")
        return

    # Controls
    st.sidebar.markdown("---")
    sort_by = st.sidebar.selectbox("Sort by", ['3 Months %', '2 Months %', '1 Month %', '1 Week %', 'Today %', 'Stock Name'])
    sort_order = st.sidebar.radio("Order", ['Best to Worst', 'Worst to Best'], horizontal=True)
    use_parallel = st.sidebar.checkbox("Parallel Fetch", value=False)
    cache_stats = get_cache_stats()
    st.sidebar.text(f"Cache: {cache_stats['valid']}")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Refresh"):
            clear_cache()
            st.session_state.cached_stocks_data = None
            st.rerun()
    with col2:
        use_cache = st.checkbox("Use Cache", value=True)
    render_sidebar_info()

    # Fetch Data
    key = ','.join(sorted(stocks))
    if not st.session_state.cached_stocks_data or st.session_state.cached_stocks_list != key:
        status = st.empty()
        with st.spinner("Loading data..."):
            data = fetch_stocks_data(stocks, use_parallel, use_cache, status)
        if not data:
            st.error("Failed to load data.")
            return
        st.session_state.cached_stocks_data = data
        st.session_state.cached_stocks_list = key
        status.empty()
    else:
        data = st.session_state.cached_stocks_data

    # Title
    title = f"{st.session_state.current_list_name or category} - {len(data)} Stock(s)"
    st.markdown(f"<h3 style='color: white;'>{title}</h3>", unsafe_allow_html=True)

    # DataFrame
    df = pd.DataFrame(data)
    ascending = sort_order == 'Worst to Best'
    df = df.sort_values(by=sort_by, ascending=ascending if sort_by != 'Stock Name' else True)
    df = df.reset_index(drop=True)
    df.insert(0, 'Rank', range(1, len(df) + 1))

    # Search
    search = st.text_input("Search stocks", key="stock_search", placeholder="Type 3+ letters")
    if search and len(search) >= 3:
        df = df[df['Stock Name'].str.contains(search, case=False, na=False)]
        st.markdown(f"**{len(df)} results** for '{search}'")

    if st.session_state.search_clear_requested:
        st.session_state.stock_search = ""
        st.session_state.search_clear_requested = False
        st.rerun()

    # Table
    start, end = render_pagination_controls(len(df), ITEMS_PER_PAGE)
    page = df.iloc[start:end].drop(columns=['Ticker'], errors='ignore')
    st.markdown(create_html_table(page), unsafe_allow_html=True)

    # Performers & Averages
    render_top_bottom_performers(df)
    render_averages(df)
    render_sectoral_yearly_performance()


if __name__ == "__main__":
    main()
