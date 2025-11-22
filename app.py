"""
NSE Stock Performance Tracker - FINAL + 52W Cards on Search
Clean UI | Perfect Search | 52W High/Low Cards when searching
"""
import streamlit as st
import pandas as pd
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Local modules
from config import CUSTOM_CSS, ITEMS_PER_PAGE
from data_fetchers import (
    get_stock_list,
    get_stock_performance,
    fetch_stocks_bulk,
    validate_stock_symbol,
    get_available_nse_indices,
    get_stock_52_week_range,  # <-- This function is used for 52W cards
)
from file_manager import load_all_saved_lists, save_list_to_csv, delete_list_csv
from cache_manager import clear_cache
from ui_components import (
    render_header, render_market_indices, render_sidebar_info,
    render_top_bottom_performers, render_averages, render_pagination_controls,
    render_live_ticker, render_gainer_loser_banner, render_sectoral_yearly_performance
)
from utils import create_html_table
from screenshot_protection import apply_screenshot_protection

warnings.filterwarnings('ignore')

# --------------------------- Admin Password ---------------------------------
def load_admin_password():
    env_file = Path(__file__).parent / '.env'
    if not env_file.exists():
        return None
    with open(env_file, 'r') as f:
        for line in f:
            if line.startswith('ADMIN_PASSWORD='):
                return line.split('=', 1)[1].strip()
    return None

ADMIN_PASSWORD = load_admin_password()

# --------------------------- Session State ----------------------------------
def init_session_state():
    defaults = {
        'saved_lists': {},
        'disk_lists': load_all_saved_lists(),
        'admin_authenticated': False,
        'admin_mode': False,
        'current_list_name': None,
        'current_list_source': None,
        'cached_stocks_data': None,
        'cached_stocks_list': None,
        'last_category': None,
        'current_page': 1,
        'selected_category': 'Nifty 50',
        'search_query': "",
        'last_search_query': "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ----------------------- Sidebar & Upload (same as your clean version) -----------------------
def render_stock_selection_sidebar():
    st.sidebar.markdown("**Stock Selection**")
    available_indices = get_available_nse_indices()
    index_options = list(available_indices.keys()) + ['Upload File']
    current_index = index_options.index(st.session_state.selected_category) if st.session_state.selected_category in index_options else 0

    def on_category_change():
        if st.session_state.selected_category != st.session_state.category_select:
            st.session_state.selected_category = st.session_state.category_select
            st.session_state.cached_stocks_data = None
            st.session_state.cached_stocks_list = None
            st.session_state.current_page = 1
            st.session_state.search_query = ""

    category = st.sidebar.selectbox(
        "Select Category",
        options=index_options,
        index=current_index,
        key='category_select',
        on_change=on_category_change,
    )
    return category

def handle_file_upload():
    st.sidebar.markdown("---")
    st.sidebar.markdown("<p style='color: #ff4444; font-weight: 600;'>Manage Stock Lists</p>", unsafe_allow_html=True)

    # Admin Login
    if ADMIN_PASSWORD and not st.session_state.admin_authenticated:
        with st.sidebar.expander("Admin Login"):
            pwd = st.text_input("Password", type="password", key="admin_pass")
            if st.button("Login"):
                if pwd == ADMIN_PASSWORD:
                    st.session_state.admin_authenticated = True
                    st.session_state.admin_mode = True
                    st.success("Admin access granted!")
                    st.rerun()
                else:
                    st.error("Wrong password")

    if st.session_state.admin_authenticated:
        st.sidebar.markdown("**Admin Mode Active**")
        st.session_state.admin_mode = st.sidebar.checkbox("Save to Disk", value=st.session_state.admin_mode)
        if st.sidebar.button("Logout"):
            st.session_state.admin_authenticated = False
            st.session_state.admin_mode = False
            st.rerun()

    # Disk lists
    for name, stocks in st.session_state.disk_lists.items():
        c1, c2 = st.sidebar.columns([3, 1])
        with c1:
            if st.button(f"{name} ({len(stocks)})", key=f"disk_{name}"):
                st.session_state.current_list_name = name
                st.session_state.current_list_source = 'disk'
                st.session_state.search_query = ""
                st.rerun()
        with c2:
            if st.session_state.admin_mode and st.button("Del", key=f"del_disk_{name}"):
                delete_list_csv(name)
                st.session_state.disk_lists.pop(name, None)
                if st.session_state.current_list_name == name:
                    st.session_state.current_list_name = None
                st.rerun()

    # Session lists
    if st.session_state.saved_lists:
        st.sidebar.markdown("**My Lists (Session):**")
        for name, stocks in st.session_state.saved_lists.items():
            c1, c2 = st.sidebar.columns([3, 1])
            with c1:
                if st.button(f"{name} ({len(stocks)})", key=f"sess_{name}"):
                    st.session_state.current_list_name = name
                    st.session_state.current_list_source = 'session'
                    st.session_state.search_query = ""
                    st.rerun()
            with c2:
                if st.button("Del", key=f"del_sess_{name}"):
                    st.session_state.saved_lists.pop(name, None)
                    if st.session_state.current_list_name == name:
                        st.session_state.current_list_name = None
                    st.rerun()

    if st.session_state.current_list_name:
        lst = (st.session_state.disk_lists if st.session_state.current_list_source == 'disk' else st.session_state.saved_lists).get(st.session_state.current_list_name, [])
        st.sidebar.success(f"Using: **{st.session_state.current_list_name}** ({len(lst)} stocks)")
        return lst, lst

    # Upload new list
    st.sidebar.markdown("**Upload New List**")
    uploaded_file = st.sidebar.file_uploader("TXT/CSV file", type=['txt', 'csv'])
    if uploaded_file:
        content = uploaded_file.read().decode('utf-8')
        stocks = [s.strip().upper() for s in content.splitlines() if s.strip()]
        name = st.sidebar.text_input("List name", value=uploaded_file.name.split('.')[0])
        if st.sidebar.button("Load List"):
            st.session_state.saved_lists[name] = stocks
            st.session_state.current_list_name = name
            st.session_state.current_list_source = 'session'
            if st.session_state.admin_mode:
                save_list_to_csv(name, stocks)
                st.session_state.disk_lists[name] = stocks
                st.session_state.current_list_source = 'disk'
            st.session_state.search_query = ""
            st.rerun()
        return [], []
    return [], []

# ------------------------- Data Fetching ----------------------------------
def fetch_stocks_data(selected_stocks, use_parallel, use_cache=True, status=None):
    if not selected_stocks:
        return []
    if len(selected_stocks) > 100:
        return fetch_stocks_bulk(selected_stocks, max_workers=4, use_cache=use_cache, status_placeholder=status)
    with st.spinner(f"Fetching {len(selected_stocks)} stocks..."):
        data = []
        for t in selected_stocks:
            try:
                res = get_stock_performance(t, use_cache)
                if res:
                    data.append(res)
            except:
                pass
        return data

# ------------------------- MAIN UI (With 52W Cards on Search) ------------------------
def render_main_ui(category, selected_stocks, stocks_data, sort_by, sort_order):
    market_ph = st.empty()
    title_ph = st.empty()
    search_ph = st.empty()
    message_ph = st.empty()
    table_ph = st.empty()
    performers_ph = st.empty()   # This will show Top/Bottom OR 52W cards
    avg_ph = st.empty()
    sect_ph = st.empty()

    with market_ph.container():
        render_market_indices()

    current_name = st.session_state.current_list_name or category
    title = f"{current_name} - Performance Summary ({len(stocks_data)} stocks)"
    with title_ph.container():
        st.markdown(f"<h3 style='color:white; margin:0;'>{title}</h3>", unsafe_allow_html=True)

    # === SEARCH BAR + CLEAR (Perfect working) ===
    with search_ph.container():
        col1, col2 = st.columns([3.5, 1])
        with col1:
            input_key = "search_input_main" if st.session_state.search_query else "search_input_cleared_" + str(hash(st.rerun))
            search_input = st.text_input(
                "Search stocks (name or symbol)",
                value=st.session_state.search_query,
                placeholder="e.g. Reliance, TCS, HDFC Bank",
                key=input_key,
                label_visibility="collapsed",
                help="Case-insensitive search"
            )
            if search_input != st.session_state.search_query:
                st.session_state.search_query = search_input.strip()
                st.session_state.current_page = 1
                st.rerun()
        with col2:
            if st.session_state.search_query.strip():
                if st.button("Clear Search", key="clear_search_fixed"):
                    st.session_state.search_query = ""
                    st.session_state.current_page = 1
                    st.rerun()

    query = st.session_state.search_query.strip().lower()
    df = pd.DataFrame(stocks_data)

    # Sorting
    ascending = sort_order == "Worst to Best"
    if sort_by == "Stock Name":
        df = df.sort_values("Stock Name", ascending=True)
    elif sort_by in df.columns:
        df = df.sort_values(sort_by, ascending=ascending)

    # Apply search
    filtered_df = df
    search_active = len(query) >= 2
    if search_active:
        name_match = df["Stock Name"].astype(str).str.lower().str.contains(query, na=False, regex=False)
        ticker_match = df["Ticker"].astype(str).str.lower().str.contains(query, na=False, regex=False) if "Ticker" in df.columns else False
        filtered_df = df[name_match | ticker_match].copy()

        if filtered_df.empty:
            with message_ph.container():
                st.warning(f"No results for '**{st.session_state.search_query}**'. Showing all stocks.")
        else:
            with message_ph.container():
                st.success(f"Found **{len(filtered_df)}** match(es) for '**{st.session_state.search_query}**'")

    filtered_df = filtered_df.reset_index(drop=True)
    filtered_df.insert(0, "Rank", range(1, len(filtered_df) + 1))

    # === Table with Pagination ===
    with table_ph.container():
        total = len(filtered_df)
        start, end = render_pagination_controls(total, ITEMS_PER_PAGE, "top")
        page_df = filtered_df.iloc[start:end]
        display_df = page_df.drop(columns=["Ticker"], errors="ignore")
        st.markdown(create_html_table(display_df), unsafe_allow_html=True)

    # === Top/Bottom Performers OR 52W Cards ===
    with performers_ph.container():
        if not search_active:
            render_top_bottom_performers(filtered_df)
        else:
            if len(filtered_df) > 0:
                st.markdown("### 52-Week High/Low Snapshot")
                cards_to_show = filtered_df.head(5)  # Top 5 matches
                cols = st.columns(len(cards_to_show))
                for idx, (_, row) in enumerate(cards_to_show.iterrows()):
                    ticker = row.get("Ticker")
                    if not ticker:
                        continue
                    with cols[idx]:
                        info = get_stock_52_week_range(ticker)
                        if info:
                            st.markdown(f"""
                                <div style="background: linear-gradient(135deg, rgba(30,64,175,0.5), rgba(17,24,39,0.8)); 
                                            border: 1px solid rgba(96,165,250,0.4); border-radius: 12px; padding: 12px; color: #e0e7ff;">
                                    <div style="font-weight: 600; font-size: 0.95rem; margin-bottom: 6px;">
                                        {row['Stock Name']} <span style="opacity: 0.7; font-size: 0.8rem;">({ticker})</span>
                                    </div>
                                    <div style="font-size: 0.9rem; margin: 4px 0;">
                                        Current: <strong>₹{info['current_price']:,.2f}</strong>
                                    </div>
                                    <div style="margin: 3px 0;">
                                        52W High: <span style="color: #22c55e; font-weight: 600;">₹{info['high']:,.2f}</span>
                                        <span style="font-size: 0.7rem; opacity: 0.8;"></span>
                                    </div>
                                    <div style="margin: 3px 0;">
                                        52W Low: <span style="color: #f97316; font-weight: 600;">₹{info['low']:,.2f}</span>
                                        <span style="font-size: 0.7rem; opacity: 0.8;"></span>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.caption(f"52W data not available for {row['Stock Name']}")
            else:
                st.info("No matching stocks to show 52-week data.")

    # Averages & Sectoral
    with avg_ph.container():
        render_averages(filtered_df)
    with sect_ph.container():
        render_sectoral_yearly_performance()

# -------------------------- MAIN ---------------------------------
def main():
    st.set_page_config(page_title="NSE Stock Tracker", page_icon="Chart Increasing", layout="wide")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    apply_screenshot_protection()
    init_session_state()

    render_header()
    render_gainer_loser_banner()
    render_live_ticker()

    category = render_stock_selection_sidebar()

    if st.session_state.last_category != category:
        st.session_state.cached_stocks_data = None
        st.session_state.last_category = category
        st.session_state.search_query = ""

    if category == "Upload File":
        selected_stocks, _ = handle_file_upload()
    else:
        with st.spinner("Loading list..."):
            selected_stocks, _ = get_stock_list(category)

    st.sidebar.markdown("---")
    sort_by = st.sidebar.selectbox("Sort by", ['3 Months %', '1 Month %', '1 Week %', 'Today %', 'Stock Name'])
    sort_order = st.sidebar.radio("Order", ["Best to Worst", "Worst to Best"], horizontal=True)
    use_parallel = st.sidebar.checkbox("Parallel fetch", value=False)
    use_cache = st.sidebar.checkbox("Use cache", value=True)

    if st.sidebar.button("Refresh All Data"):
        clear_cache()
        st.session_state.cached_stocks_data = None
        st.rerun()

    render_sidebar_info()

    if not selected_stocks:
        st.warning("Please select or upload a stock list.")
        return

    key = ",".join(sorted(selected_stocks))
    if st.session_state.cached_stocks_data is None or st.session_state.cached_stocks_list != key:
        status = st.empty()
        stocks_data = fetch_stocks_data(selected_stocks, use_parallel, use_cache, status)
        st.session_state.cached_stocks_data = stocks_data
        st.session_state.cached_stocks_list = key
    else:
        stocks_data = st.session_state.cached_stocks_data

    render_main_ui(category, selected_stocks, stocks_data, sort_by, sort_order)

if __name__ == "__main__":
    main()