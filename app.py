"""
Refactored NSE Stock Performance Tracker - v2.1
- Functional behavior preserved (Option A) — no feature removal
- Code reorganized for clarity, smaller helper functions, safer rerun trigger, improved env handling
- Left comments where behavior intentionally preserved
"""

import os
import logging
import hashlib
import time
import uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st
import pandas as pd
import warnings

# Optional: dotenv for local development
try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

warnings.filterwarnings("ignore")


# -------------------- Local modules --------------------
from config import CUSTOM_CSS, ITEMS_PER_PAGE
from data_fetchers import (
    get_stock_list,
    get_stock_performance,
    fetch_stocks_bulk,
    validate_stock_symbol,
    get_available_nse_indices,
    get_stock_52_week_range,
)
from file_manager import (
    load_all_saved_lists, save_list_to_csv, delete_list_csv,
    load_portfolio, save_portfolio, delete_holding, clear_portfolio
)
from cache_manager import clear_cache as clear_cache_manager
from portfolio_manager import (
    calculate_portfolio_metrics, validate_holding_input,
    format_currency, format_percentage, get_pnl_color,
    get_top_performers, get_worst_performers
)
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
from utils import create_html_table
from screenshot_protection import apply_screenshot_protection
from security_fixes import secure_password_compare, LoginRateLimiter, sanitize_html, sanitize_dataframe_for_csv

# -------------------- Logging --------------------
logger = logging.getLogger("nse_tracker")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# -------------------- Admin Password --------------------
def load_admin_password():
    """Load admin password from environment, st.secrets, or local .env.
    Note: path handling improved to be robust in multiple deploy environments.
    """
    # Prefer direct environment
    pw = os.getenv("ADMIN_PASSWORD")
    if pw:
        return pw.strip()

    # Try Streamlit secrets
    try:
        if hasattr(st, "secrets") and "ADMIN_PASSWORD" in st.secrets:
            return st.secrets["ADMIN_PASSWORD"].strip()
    except Exception:
        # fall through
        pass

    # Local .env — try script directory first, then fallback to CWD
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        env_path = Path(".env")  # Fallback to CWD
    
    if env_path.exists() and load_dotenv:
        try:
            load_dotenv(env_path)
            pw = os.getenv("ADMIN_PASSWORD")
            if pw:
                return pw.strip()
        except Exception as e:
            logger.exception("Failed to load .env: %s", e)

    return None

ADMIN_PASSWORD = load_admin_password()

# -------------------- Session State --------------------
def init_session_state():
    defaults = {
        "saved_lists": {},
        "disk_lists": None,
        "admin_authenticated": False,
        "admin_mode": False,
        "current_list_name": None,
        "current_list_source": None,
        "cached_stocks_data": None,
        "cached_stocks_list_key": None,
        "last_category": None,
        "current_page": 1,
        "selected_category": "Nifty 50",
        "search_query": "",
        "search_version": 0,
        "last_updated_ts": None,
        # Use a nonce string for rerun trigger to avoid race-condition toggles
        "trigger_rerun_nonce": None,
        # Portfolio state
        "portfolio_holdings": [],
        "portfolio_loaded": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# -------------------- Helper Functions --------------------
def reset_search_and_pagination():
    """Helper to reset search and pagination state - DRY principle"""
    st.session_state.current_page = 1
    st.session_state.search_query = ""
    st.session_state.search_version += 1

# -------------------- Cache Helpers --------------------
def make_list_key(stocks):
    if not stocks:
        return "empty"
    joined = ",".join(sorted(stocks))
    return hashlib.sha1(joined.encode("utf-8")).hexdigest()

@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def cached_load_all_saved_lists():
    try:
        return load_all_saved_lists()
    except Exception as e:
        logger.exception("Error loading saved lists: %s", e)
        return {}

@st.cache_data(ttl=60 * 60 * 6, show_spinner=False)
def cached_get_stock_list(category):
    try:
        return get_stock_list(category)
    except Exception as e:
        logger.exception("Error fetching stock list for %s: %s", category, e)
        return ([], None)

# -------------------- Safe Rerun Trigger --------------------
def trigger_rerun():
    """Set a fresh nonce in session_state to indicate a rerun is desired.
    Main loop watches the nonce and calls st.rerun() exactly once.
    """
    st.session_state.trigger_rerun_nonce = uuid.uuid4().hex

# -------------------- Sidebar: Selection & Upload --------------------
def render_stock_selection_sidebar():
    st.sidebar.markdown("**Index List**")
    try:
        available_indices = get_available_nse_indices() or {}
    except Exception as e:
        logger.exception("get_available_nse_indices failed: %s", e)
        available_indices = {}

    # Build selectbox options
    index_options = list(available_indices.keys())
    
    # Add Upload File option for everyone (not admin-only)
    index_options.append("Upload File")

    # Check if current category is still valid
    current_cat = st.session_state.selected_category
    if current_cat not in index_options:
        # Reset to first if invalid
        current_cat = index_options[0] if index_options else None
        st.session_state.selected_category = current_cat

    current_index = index_options.index(current_cat) if current_cat in index_options else 0

    # If user changes category, reset pagination
    if current_cat != st.session_state.last_category:
        if st.session_state.last_category is not None:
            reset_search_and_pagination()

    category = st.sidebar.selectbox(
        "Choose:",
        options=index_options,
        index=current_index,
        key="category_select",
        label_visibility="collapsed",
    )
    
    return category


def _render_disk_and_session_lists():
    # Helper to render saved lists (both disk & session) and return when selection changes
    if st.session_state.disk_lists is None:
        st.session_state.disk_lists = cached_load_all_saved_lists()

    # Disk Lists
    if st.session_state.disk_lists:
        st.sidebar.markdown("**Saved Lists (Disk):**")
        for name, stocks in list(st.session_state.disk_lists.items()):
            c1, c2 = st.sidebar.columns([3, 1])
            with c1:
                if st.button(f"{name} ({len(stocks)})", key=f"disk_{name}"):
                    st.session_state.current_list_name = name
                    st.session_state.current_list_source = "disk"
                    reset_search_and_pagination()
                    st.session_state.cached_stocks_data = None
                    st.session_state.cached_stocks_list_key = None
            with c2:
                if st.session_state.admin_mode and st.button("Del", key=f"del_disk_{name}"):
                    try:
                        delete_list_csv(name)
                        cached_load_all_saved_lists.clear()
                        st.session_state.disk_lists = cached_load_all_saved_lists()
                        if st.session_state.current_list_name == name:
                            st.session_state.current_list_name = None
                            st.session_state.current_list_source = None
                        st.success(f"Deleted {name}")
                        trigger_rerun()
                    except Exception as e:
                        logger.exception("Delete failed: %s", e)
                        st.error("Failed to delete")

    # Session Lists
    if st.session_state.saved_lists:
        st.sidebar.markdown("**My Lists (Session):**")
        for name, stocks in list(st.session_state.saved_lists.items()):
            c1, c2 = st.sidebar.columns([3, 1])
            with c1:
                if st.button(f"{name} ({len(stocks)})", key=f"sess_{name}"):
                    st.session_state.current_list_name = name
                    st.session_state.current_list_source = "session"
                    reset_search_and_pagination()
                    st.session_state.cached_stocks_data = None
                    st.session_state.cached_stocks_list_key = None
            with c2:
                if st.button("Del", key=f"del_sess_{name}"):
                    st.session_state.saved_lists.pop(name, None)
                    if st.session_state.current_list_name == name:
                        st.session_state.current_list_name = None


def render_admin_login():
    """Render admin login/logout in sidebar (always visible)"""
    st.sidebar.markdown("---")
    
    # Admin Login with rate limiting
    if ADMIN_PASSWORD and not st.session_state.admin_authenticated:
        st.sidebar.markdown("<p style='color: #42a5f5; font-weight: 600; margin-bottom: 5px;'>🔐 Admin</p>", unsafe_allow_html=True)
        
        limiter = LoginRateLimiter(max_attempts=5, lockout_minutes=15)
        is_locked, remaining_mins = limiter.is_locked_out()
        
        if is_locked:
            st.sidebar.error(f"🔒 Locked {remaining_mins}m")
        else:
            # Use form so Enter key submits login (without page reload)
            with st.sidebar.form("admin_login_form", clear_on_submit=False, border=False):
                pwd = st.text_input("Password", type="password", key="admin_pass_input", label_visibility="collapsed", placeholder="Password")
                
                # Two columns: empty space + Login button (keeps it compact)
                col1, col2 = st.columns([0.01, 1])
                with col2:
                    submitted = st.form_submit_button("🔓 Login", use_container_width=True, type="primary")
                
                if submitted:
                    if not pwd or pwd.strip() == "":
                        st.sidebar.error("❌ Enter password")
                    else:
                        # Use timing-safe comparison
                        if secure_password_compare(pwd, ADMIN_PASSWORD):
                            limiter.reset()
                            st.session_state.admin_authenticated = True
                            st.session_state.admin_mode = True
                            st.rerun()  # Direct rerun to show portfolio tab
                        else:
                            if limiter.record_failure():
                                st.sidebar.error("🔒 Locked!")
                            else:
                                st.sidebar.error("❌ Wrong")

    # Show Admin controls when authenticated
    if st.session_state.admin_authenticated:
        st.sidebar.markdown("<p style='color: #42a5f5; font-weight: 600; margin-bottom: 5px;'>🔐 Admin</p>", unsafe_allow_html=True)
        # Compact side-by-side buttons
        col1, col2 = st.sidebar.columns([1, 1])
        with col1:
            st.markdown('<p style="color: #00ff00; font-size: 0.75rem; margin: 0; padding: 5px 0;">✅ Active</p>', unsafe_allow_html=True)
        with col2:
            if st.button("Logout", key="admin_logout_btn", help="Logout", type="secondary"):
                st.session_state.admin_authenticated = False
                st.session_state.admin_mode = False
                st.rerun()
        
        # Admin mode checkbox (compact)
        st.session_state.admin_mode = st.sidebar.checkbox("Save to disk", value=st.session_state.admin_mode)


def handle_file_upload():
    st.sidebar.markdown("---")
    st.sidebar.markdown("<p style='color: #ff4444; font-weight: 600;'>Manage Stock Lists</p>", unsafe_allow_html=True)

    # Render lists
    _render_disk_and_session_lists()

    # Current Active List Indicator
    if st.session_state.current_list_name:
        source = "disk" if st.session_state.current_list_source == "disk" else "session"
        lst = st.session_state.disk_lists if source == "disk" else st.session_state.saved_lists
        count = len(lst.get(st.session_state.current_list_name, []))
        # SECURITY FIX: Sanitize list name to prevent XSS
        safe_list_name = sanitize_html(st.session_state.current_list_name)
        st.sidebar.success(f"**Active → {safe_list_name}** ({count} stocks)")

    # Upload New List
    st.sidebar.markdown("**Upload New List**")
    uploaded_file = st.sidebar.file_uploader("TXT/CSV file with symbols", type=["txt", "csv"], key="uploader", accept_multiple_files=False, help="Upload a file with stock symbols (max 2MB)")

    if uploaded_file:
        MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
        file_size = uploaded_file.size
        if file_size > MAX_FILE_SIZE:
            st.sidebar.error(f"❌ File too large! Maximum size is 2MB. Your file is {file_size / (1024 * 1024):.2f}MB")
            return [], None

        try:
            content = uploaded_file.read().decode("utf-8")
        except Exception:
            content = uploaded_file.getvalue().decode("utf-8", errors="ignore")

        raw_ticks = [s.strip().upper() for s in content.splitlines() if s.strip()]
        seen = set()
        stocks = []
        for t in raw_ticks:
            tt = t.replace(".", "-").strip()
            if tt and tt not in seen:
                seen.add(tt)
                stocks.append(tt)

        invalid = []
        validated = []
        for t in stocks:
            try:
                if not validate_stock_symbol(t):
                    invalid.append(t)
                else:
                    validated.append(t)
            except Exception as e:
                # Preserve original behavior of accepting when validation fails, but log it
                logger.exception("validate_stock_symbol raised for %s: %s", t, e)
                validated.append(t)

        if invalid:
            st.sidebar.warning(f"Removed {len(invalid)} invalid: {', '.join(invalid[:10])}...")

        name = st.sidebar.text_input("List name", value=uploaded_file.name.split(".")[0], key="upload_name")

        if st.sidebar.button("Load This List", type="primary"):
            if not name.strip():
                st.sidebar.error("Enter a name")
            else:
                st.session_state.saved_lists[name] = validated
                st.session_state.current_list_name = name
                st.session_state.current_list_source = "session"
                reset_search_and_pagination()
                st.session_state.cached_stocks_data = None
                st.session_state.cached_stocks_list_key = None

                if st.session_state.admin_mode:
                    try:
                        save_list_to_csv(name, validated)
                        cached_load_all_saved_lists.clear()
                        st.session_state.disk_lists = cached_load_all_saved_lists()
                        st.session_state.current_list_source = "disk"
                        st.success(f"Saved permanently as **{name}**")
                    except Exception as e:
                        logger.exception("Disk save failed: %s", e)
                        st.sidebar.error("Saved to session only")

                # Only one safe rerun at the end
                trigger_rerun()

    # Return active list
    if st.session_state.current_list_name:
        source = st.session_state.current_list_source or "session"
        lst = st.session_state.disk_lists if source == "disk" else st.session_state.saved_lists
        return lst.get(st.session_state.current_list_name, []), source

    return [], None

# -------------------- Data Fetching --------------------
def fetch_stocks_data(selected_stocks, use_parallel, use_cache=True, status=None):
    if not selected_stocks:
        return []

    # Prefer bulk when available and large lists
    if len(selected_stocks) > 100 and "fetch_stocks_bulk" in globals():
        try:
            # CONSISTENCY FIX: Use same worker logic as individual fetch
            bulk_workers = min(8, max(1, len(selected_stocks) // 20))
            return fetch_stocks_bulk(selected_stocks, max_workers=bulk_workers, use_cache=use_cache, status_placeholder=status)
        except Exception as e:
            logger.exception("Bulk fetch failed: %s", e)
            # fall through to threaded fetch

    # SECURITY FIX: Reduced max workers to prevent memory issues and rate limiting
    # Aligned with bulk mode for consistency
    max_workers = min(4, max(1, len(selected_stocks) // 20))
    data = []

    if use_parallel and max_workers > 1:
        with st.spinner(f"Fetching {len(selected_stocks)} stocks (parallel)..."):
            with ThreadPoolExecutor(max_workers=max_workers) as ex:
                futures = {ex.submit(get_stock_performance, t, use_cache): t for t in selected_stocks}
                done = 0
                for fut in as_completed(futures):
                    stock = futures.get(fut)
                    try:
                        res = fut.result()
                        if res:
                            data.append(res)
                    except Exception as e:
                        logger.exception("Fetch failed for %s: %s", stock, e)
                    done += 1
                    if status:
                        status.text(f"Fetched {done}/{len(futures)}")
    else:
        with st.spinner(f"Fetching {len(selected_stocks)} stocks..."):
            for i, t in enumerate(selected_stocks, 1):
                try:
                    res = get_stock_performance(t, use_cache)
                    if res:
                        data.append(res)
                except Exception as e:
                    logger.exception("Failed for %s: %s", t, e)
                if status:
                    status.text(f"Fetched {i}/{len(selected_stocks)}")

    return data

# -------------------- Main UI Renderer --------------------
def render_main_ui(category, selected_stocks, stocks_data, sort_by, sort_order):
    title_ph = st.empty()
    search_ph = st.empty()
    message_ph = st.empty()
    table_ph = st.empty()
    performers_ph = st.empty()
    avg_ph = st.empty()
    sect_ph = st.empty()

    current_name = st.session_state.current_list_name or category or "Selected Stocks"
    # SECURITY FIX: Sanitize user-provided list name to prevent XSS
    safe_current_name = sanitize_html(current_name)
    title = f"{safe_current_name} - Performance Summary ({len(stocks_data)} stocks)"
    with title_ph.container():
        # Add compact CSS for smaller search input with sectoral card border color
        st.markdown("""
        <style>
        /* Target the outer container of the text input */
        div[data-testid="stTextInput"] {
        width: 500px !important;      /* adjust this (overall rectangle length) */
    }
        div[data-testid="stTextInput"] > div > div > input {
            height: 32px !important;
            min-height: 32px !important;
            padding: 4px 10px !important;
            font-size: 0.85rem !important;
            border: 1px solid rgba(66, 165, 245, 0.3) !important;
        }
        div[data-testid="stTextInput"] > div > div > input:focus {
            border: 1px solid rgba(66, 165, 245, 0.6) !important;
            outline: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        col_title, col_search, col_clear = st.columns([1.25, 1.75, 0.5])
        
        with col_title:
            # Title - left aligned
            st.markdown(f"<h3 style='color:white; margin:0; padding-top:4px;'>{title}</h3>", unsafe_allow_html=True)
        
        with col_search:
            search_key = f"search_v{st.session_state.search_version}"
            new_query = st.text_input(
                "Search stocks (name or symbol)",
                value=st.session_state.search_query,
                placeholder="🔍 Search your favourite stocks like HDFC Bank, Reliance etc",
                key=search_key,
                label_visibility="collapsed",
                help="Case-insensitive search"
            )
            if new_query != st.session_state.search_query:
                st.session_state.search_query = new_query.strip()
                st.session_state.current_page = 1
        
        with col_clear:
            # Show Clear button when there's a search query (checks updated value)
            st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
            if st.session_state.search_query.strip():
                if st.button("Clear", key="clear_search", help="Clear search"):
                    # Use immediate st.rerun() for user actions (not deferred trigger)
                    st.session_state.search_query = ""
                    st.session_state.current_page = 1
                    st.session_state.search_version += 1
                    st.rerun()

    query = st.session_state.search_query.strip().lower()
    df = pd.DataFrame(stocks_data)
    ascending = sort_order == "Worst to Best"

    try:
        if sort_by == "Stock Name":
            df = df.sort_values("Stock Name", ascending=True, na_position="last")
        elif sort_by in df.columns:
            df = df.sort_values(sort_by, ascending=ascending, na_position="last")
    except Exception as e:
        logger.exception("Sort failed: %s", e)

    filtered_df = df
    search_active = len(query) >= 2
    if search_active and not df.empty:
        name_match = df["Stock Name"].astype(str).str.contains(query, case=False, na=False)
        ticker_match = df["Ticker"].astype(str).str.contains(query, case=False, na=False) if "Ticker" in df.columns else False
        filtered_df = df[name_match | ticker_match].copy()

        with message_ph.container():
            if filtered_df.empty:
                # SECURITY FIX: Sanitize search query display
                safe_query = sanitize_html(st.session_state.search_query)
                st.warning(f"No matches for '**{safe_query}**'. Showing all.")
            else:
                st.success(f"Found **{len(filtered_df)}** match(es)")

    filtered_df = filtered_df.reset_index(drop=True)
    filtered_df.insert(0, "Rank", range(1, len(filtered_df) + 1))

    # Use @st.fragment to avoid full app rerun on pagination/sort changes
    @st.fragment
    def render_table_fragment():
        """Fragment that only reruns when pagination changes, not the entire app"""
        # Prepare CSV export data (remove Ticker and sparkline_data columns)
        export_df = filtered_df.drop(columns=["Ticker", "sparkline_data"], errors="ignore").copy()
        
        # Add % symbol to percentage columns for Excel display
        percentage_columns = ['Today %', '1 Week %', '1 Month %', '2 Months %', '3 Months %']
        for col in percentage_columns:
            if col in export_df.columns:
                # Format: add % symbol (e.g., "2.5" → "2.5%")
                export_df[col] = export_df[col].apply(lambda x: f"{x}%" if pd.notna(x) and x != '' else x)
        
        # SECURITY FIX: Prevent CSV formula injection
        safe_df = sanitize_dataframe_for_csv(export_df)
        csv_data = safe_df.to_csv(index=False).encode('utf-8')
        
        # Create filename based on current list/category
        download_name = st.session_state.current_list_name or category or "stock_data"
        filename = f"{download_name}_performance.csv"
        
        total = len(filtered_df)
        start, end = render_pagination_controls(total, ITEMS_PER_PAGE, "top", csv_data=csv_data, csv_filename=filename)
        page_df = filtered_df.iloc[start:end]
        display_df = page_df.drop(columns=["Ticker"], errors="ignore")
        st.markdown(create_html_table(display_df), unsafe_allow_html=True)
    
    with table_ph.container():
        render_table_fragment()

    with performers_ph.container():
        if not search_active:
            render_top_bottom_performers(filtered_df)
        elif len(filtered_df) > 0:
            st.markdown("### 52-Week High/Low Snapshot")
            cards = filtered_df.head(5)
            cols = st.columns(min(5, len(cards)))
            for idx, (_, row) in enumerate(cards.iterrows()):
                col = cols[idx % len(cols)]
                ticker = row.get("Ticker")
                name = row.get("Stock Name", "Unknown")
                if not ticker:
                    col.caption(f"No ticker")
                    continue
                try:
                    info = get_stock_52_week_range(ticker) or {}
                    current = info.get("current_price")
                    high = info.get("high")
                    low = info.get("low")
                except Exception as e:
                    logger.exception("52W failed for %s: %s", ticker, e)
                    info = {}

                if None in (current, high, low):
                    col.markdown(f"<div style='padding:15px; background:#1e293b; border-radius:10px;'><small>{name} ({ticker})</small><br><i>52W data unavailable</i></div>", unsafe_allow_html=True)
                else:
                    col.markdown(f"""
                    <div style="background: linear-gradient(135deg, rgba(30,64,175,0.6), rgba(17,24,39,0.9));
                                border: 1px solid rgba(96,165,250,0.4); border-radius: 12px; padding: 14px; color: #e0e7ff;">
                        <div style="font-weight: 600; font-size: 0.95rem;">{name} <span style="opacity:0.7; font-size:0.8rem;">({ticker})</span></div>
                        <div style="margin:6px 0; font-size:0.9rem;">Current: <strong>₹{current:,.2f}</strong></div>
                        <div>52W High: <span style="color:#22c55e;">₹{high:,.2f}</span></div>
                        <div>52W Low: <span style="color:#f97316;">₹{low:,.2f}</span></div>
                    </div>
                    """, unsafe_allow_html=True)

    with avg_ph.container():
        try:
            render_averages(filtered_df)
        except Exception as e:
            logger.exception("Averages failed: %s", e)

    with sect_ph.container():
        try:
            render_sectoral_yearly_performance()
        except Exception as e:
            logger.exception("Sectoral failed: %s", e)

# -------------------- Portfolio UI --------------------
def render_portfolio_ui():
    """Render the portfolio tracker interface (admin-only)"""
    
    # Load portfolio if not loaded
    if not st.session_state.portfolio_loaded:
        st.session_state.portfolio_holdings = load_portfolio()
        st.session_state.portfolio_loaded = True
    
    st.title("💼 My Portfolio")
    
    # Get current prices for all holdings
    current_prices = {}
    price_fetch_errors = []
    if st.session_state.portfolio_holdings:
        symbols = [h['stock_symbol'] for h in st.session_state.portfolio_holdings]
        with st.spinner("Fetching current prices..."):
            for symbol in symbols:
                try:
                    data = get_stock_performance(symbol, use_cache=True)
                    if data and 'Current Price' in data:
                        # Extract numeric value from formatted string like "₹1,234.56"
                        price_str = data['Current Price'].replace('₹', '').replace(',', '')
                        current_prices[symbol] = float(price_str)
                    else:
                        # API returned data but no current price
                        price_fetch_errors.append(f"{symbol}: No price data available")
                        holding = next(h for h in st.session_state.portfolio_holdings if h['stock_symbol'] == symbol)
                        current_prices[symbol] = holding['buy_price']
                except Exception as e:
                    # API call failed
                    price_fetch_errors.append(f"{symbol}: {str(e)}")
                    holding = next(h for h in st.session_state.portfolio_holdings if h['stock_symbol'] == symbol)
                    current_prices[symbol] = holding['buy_price']
        
        # Show warning if any prices failed to fetch
        if price_fetch_errors:
            with st.expander("⚠️ Price Fetch Issues", expanded=False):
                st.warning("Some stock prices could not be fetched. Using buy price as fallback:")
                for error in price_fetch_errors:
                    st.text(f"• {error}")
    
    # Calculate portfolio metrics
    metrics = calculate_portfolio_metrics(st.session_state.portfolio_holdings, current_prices)
    
    # Portfolio Summary Cards
    if metrics['total_invested'] > 0:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📊 Total Invested",
                value=format_currency(metrics['total_invested'])
            )
        
        with col2:
            st.metric(
                label="💰 Current Value",
                value=format_currency(metrics['current_value'])
            )
        
        with col3:
            st.metric(
                label="💵 Total P&L",
                value=f"{format_currency(metrics['total_pnl'])} ({format_percentage(metrics['total_pnl_pct'])})",
                delta=None
            )
        
        with col4:
            st.metric(
                label="📈 Holdings",
                value=f"{len(st.session_state.portfolio_holdings)} stocks"
            )
    
    st.markdown("---")
    
    # Add Stock Form (collapsed by default for clean UI)
    with st.expander("➕ Add Stock to Portfolio", expanded=False):
        # Get all available stocks for autocomplete (cached)
        @st.cache_data(ttl=3600, show_spinner=False)
        def get_all_nse_stocks():
            """Get comprehensive list of NSE stocks from all indices (display names only)"""
            all_stocks = set()
            try:
                # Get stocks from major indices
                for idx in ["Nifty 50", "Nifty 100", "Nifty 200", "Nifty 500"]:
                    stocks, _ = get_stock_list(idx)
                    if stocks:
                        # Remove .NS extension for display
                        clean_stocks = [s.replace('.NS', '') for s in stocks]
                        all_stocks.update(clean_stocks)
            except Exception:
                pass
            return sorted(list(all_stocks))
        
        available_stocks = get_all_nse_stocks()
        
        with st.form("add_stock_form", clear_on_submit=True):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
            
            with col1:
                # Searchable dropdown with autocomplete (display without .NS)
                symbol_dropdown = st.selectbox(
                    "Stock Symbol",
                    options=[""] + available_stocks,
                    index=0,
                    help="Start typing to search (e.g., INFY, RELIANCE, TCS)"
                )
                
                # Use dropdown selection first
                symbol = symbol_dropdown.strip().upper() if symbol_dropdown else ""
                # Remove .NS if user somehow enters it
                if symbol:
                    symbol = symbol.replace('.NS', '')
            
            with col2:
                quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
            
            with col3:
                buy_price = st.number_input("Buy Price (₹)", min_value=0.01, value=100.0, step=0.01)
            
            with col4:
                buy_date = st.date_input("Buy Date", value=pd.Timestamp.now())
            
            # Manual entry and Notes on same line to save space
            col_manual, col_notes = st.columns(2)
            with col_manual:
                symbol_manual = st.text_input("Or enter manually", placeholder="e.g., RELIANCE")
                # Override with manual entry if provided
                if symbol_manual and symbol_manual.strip():
                    symbol = symbol_manual.strip().upper().replace('.NS', '')
            
            with col_notes:
                notes = st.text_input("Notes (optional)", placeholder="e.g., Long-term hold")
            
            submitted = st.form_submit_button("Add Stock", type="primary")
        
            if submitted:
                # Check if symbol is provided
                if not symbol or symbol.strip() == "":
                    st.error("❌ Please select or enter a stock symbol")
                else:
                    # Validate input
                    is_valid, error_msg = validate_holding_input(
                        symbol, quantity, buy_price, buy_date.strftime("%Y-%m-%d")
                    )
                    
                    if not is_valid:
                        st.error(f"❌ {error_msg}")
                    else:
                        # Add .NS extension for API validation (internally needed)
                        symbol_with_ns = symbol if symbol.endswith('.NS') else f"{symbol}.NS"
                        
                        # Validate stock symbol with .NS extension
                        if not validate_stock_symbol(symbol_with_ns):
                            st.error(f"❌ Invalid stock symbol: {symbol}")
                        else:
                            # Check for duplicate: same stock, same date
                            buy_date_str = buy_date.strftime("%Y-%m-%d")
                            duplicate_found = False
                            
                            for i, holding in enumerate(st.session_state.portfolio_holdings):
                                if holding['stock_symbol'] == symbol_with_ns and holding['buy_date'] == buy_date_str:
                                    # Duplicate found - merge quantities and average price
                                    old_qty = holding['quantity']
                                    old_price = holding['buy_price']
                                    new_qty = old_qty + quantity
                                    # Weighted average price
                                    avg_price = ((old_qty * old_price) + (quantity * buy_price)) / new_qty
                                    
                                    st.session_state.portfolio_holdings[i]['quantity'] = new_qty
                                    st.session_state.portfolio_holdings[i]['buy_price'] = round(avg_price, 2)
                                    st.session_state.portfolio_holdings[i]['notes'] = notes if notes else holding['notes']
                                    
                                    duplicate_found = True
                                    st.info(f"ℹ️ Merged with existing {symbol} entry: {old_qty} + {quantity} = {new_qty} shares @ avg ₹{avg_price:.2f}")
                                    break
                            
                            if not duplicate_found:
                                # Add new holding
                                new_holding = {
                                    'stock_symbol': symbol_with_ns,
                                    'quantity': quantity,
                                    'buy_price': buy_price,
                                    'buy_date': buy_date_str,
                                    'notes': notes
                                }
                                st.session_state.portfolio_holdings.append(new_holding)
                            
                            # Save to file
                            if save_portfolio(st.session_state.portfolio_holdings):
                                # Force reload of portfolio
                                st.session_state.portfolio_loaded = False
                                st.toast(f"✅ Added {symbol}", icon="📈")
                                # Use experimental rerun to avoid full page flash
                                st.rerun()
                            else:
                                st.error("❌ Failed to save portfolio")
    
    st.markdown("---")
    
    # Holdings Table - Use fragment to avoid full page refresh on delete
    @st.fragment
    def render_holdings_fragment():
        if not st.session_state.portfolio_holdings:
            st.info("📭 Your portfolio is empty. Add your first stock above!")
            return
        
        # Recalculate metrics inside fragment (fetch live prices)
        current_prices_frag = {}
        for h in st.session_state.portfolio_holdings:
            try:
                data = get_stock_performance(h['stock_symbol'], use_cache=True)
                if data and 'Current Price' in data:
                    # Extract numeric value from formatted string like "₹1,234.56"
                    price_str = data['Current Price'].replace('₹', '').replace(',', '')
                    current_prices_frag[h['stock_symbol']] = float(price_str)
                else:
                    # No current price in API response
                    current_prices_frag[h['stock_symbol']] = h['buy_price']
            except Exception as e:
                # API call failed, use buy price
                current_prices_frag[h['stock_symbol']] = h['buy_price']
        
        metrics_frag = calculate_portfolio_metrics(st.session_state.portfolio_holdings, current_prices_frag)
        
        st.subheader(f"📈 Holdings ({len(st.session_state.portfolio_holdings)} stocks)")
        
        # Column headers
        header_cols = st.columns([0.5, 1, 0.8, 1, 1, 1.2, 1.2, 1.5, 1.2, 1.5, 0.6])
        headers = ['#', 'STOCK', 'QTY', 'BUY PRICE', 'CURRENT PRICE', 'INVESTED', 'CURRENT VALUE', 'P&L', 'BUY DATE', 'NOTES', 'ACTION']
        for col, header in zip(header_cols, headers):
            with col:
                st.markdown(f"**{header}**")
        
        st.markdown("<hr style='margin: 5px 0; border-color: #42a5f5; border-width: 2px;'>", unsafe_allow_html=True)
        
        # Display each holding as a row with inline delete button
        for i, holding in enumerate(metrics_frag['holdings_with_pnl']):
            pnl_color = get_pnl_color(holding['pnl'])
            
            # Create columns for row layout (last column smaller for compact delete button)
            cols = st.columns([0.5, 1, 0.8, 1, 1, 1.2, 1.2, 1.5, 1.2, 1.5, 0.35])
            
            with cols[0]:
                st.markdown(f"**{i+1}**")
            with cols[1]:
                # Display stock name without .NS extension
                display_symbol = holding['stock_symbol'].replace('.NS', '')
                st.markdown(f"**{display_symbol}**")
            with cols[2]:
                st.markdown(f"{int(holding['quantity'])}")
            with cols[3]:
                st.markdown(f"{format_currency(holding['buy_price'])}")
            with cols[4]:
                st.markdown(f"{format_currency(holding['current_price'])}")
            with cols[5]:
                st.markdown(f"{format_currency(holding['invested'])}")
            with cols[6]:
                st.markdown(f"{format_currency(holding['current_value'])}")
            with cols[7]:
                st.markdown(f"<span style='color: {pnl_color}; font-weight: 600;'>{format_currency(holding['pnl'])} ({format_percentage(holding['pnl_pct'])})</span>", unsafe_allow_html=True)
            with cols[8]:
                st.markdown(f"{holding['buy_date']}")
            with cols[9]:
                st.markdown(f"{holding.get('notes', '')}")
            with cols[10]:
                # Clickable delete button - small size with proper spacing
                st.markdown("<div style='padding-top: 5px;'>", unsafe_allow_html=True)
                if st.button("✕", key=f"del_{i}", help=f"Delete {display_symbol}", use_container_width=False):
                    st.session_state.portfolio_holdings.pop(i)
                    save_portfolio(st.session_state.portfolio_holdings)
                    st.session_state.portfolio_loaded = False  # Force reload
                    st.toast(f"✅ Deleted {display_symbol}", icon="🗑️")
                    st.rerun()  # Full refresh to update metrics at top
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Separator line with more top margin to prevent overlap
            st.markdown("<hr style='margin: 10px 0 5px 0; border-color: #555;'>", unsafe_allow_html=True)
    
    # Call the fragment
    render_holdings_fragment()
    
    st.markdown("---")
    
    # Export Portfolio
    if st.session_state.portfolio_holdings:
        export_df = pd.DataFrame(st.session_state.portfolio_holdings)
        csv_data = export_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Portfolio (CSV)",
            data=csv_data,
            file_name="my_portfolio.csv",
            mime="text/csv",
            use_container_width=False
        )
    
    # Top Performers - only show if at least 3 unique stocks
    unique_stocks = len(set(h['stock_symbol'] for h in st.session_state.portfolio_holdings))
    if unique_stocks >= 3:
        st.markdown("---")
        perf_col1, perf_col2 = st.columns(2)
        
        with perf_col1:
            st.subheader("🏆 Top Performers")
            top = get_top_performers(metrics['holdings_with_pnl'], 3)
            for symbol, pnl_pct in top:
                display_sym = symbol.replace('.NS', '')
                color = get_pnl_color(pnl_pct)
                st.markdown(f"**{display_sym}**: <span style='color: {color};'>{format_percentage(pnl_pct)}</span>", unsafe_allow_html=True)
        
        with perf_col2:
            st.subheader("📉 Needs Attention")
            worst = get_worst_performers(metrics['holdings_with_pnl'], 3)
            for symbol, pnl_pct in worst:
                display_sym = symbol.replace('.NS', '')
                color = get_pnl_color(pnl_pct)
                st.markdown(f"**{display_sym}**: <span style='color: {color};'>{format_percentage(pnl_pct)}</span>", unsafe_allow_html=True)

# -------------------- Main --------------------
def main():
    st.set_page_config(
        page_title="NSE Stock Tracker",
        page_icon="Chart Increasing",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    apply_screenshot_protection()

    init_session_state()
    
    # CRITICAL FIX: Check nonce FIRST to prevent race conditions
    # Move this to top before any other UI operations
    if st.session_state.trigger_rerun_nonce:
        st.session_state.trigger_rerun_nonce = None
        st.rerun()

    # Render header first (fast - uses cached data)
    render_header()

    # Load gainer/loser banner (stays visible while rest loads)
    with st.spinner("⏳ Loading market movers and FII/DII data..."):
        fii_dii_source = render_gainer_loser_banner()

    # Load ticker (stays visible while rest loads)
    with st.spinner("⏳ Loading live ticker with 50 stocks..."):
        stock_count, advances, declines = render_live_ticker()

    # Display heading with advance/decline info
    if stock_count and advances is not None and declines is not None:
        fii_dii_text = ""
        if fii_dii_source:
            fii_dii_text = f"<span style='color: #888; font-size: 0.85rem;'>FII/DII: {fii_dii_source}</span>"

        st.markdown(
            f"""<div style='display: flex; justify-content: space-between; align-items: center; margin: -10px 0 8px 0; padding: 8px;'>
                <div style='flex: 1; text-align: left;'>
                    <span style='color: #ffffff; font-size: 1.35rem; font-weight: 600;'>📈 Market Indices - Today's Performance</span>
                </div>
                <div style='flex: 1; text-align: center; font-size: 0.9rem;'>
                    <span style='color: #888; margin: 0 8px;'>•</span>
                    <span style='color: #00ff00; font-weight: 600;'>Advances: {advances}</span>
                    <span style='color: #888; margin: 0 8px;'>•</span>
                    <span style='color: #ff4444; font-weight: 600;'>Declines: {declines}</span>
                </div>
                <div style='flex: 1; text-align: right; font-size: 0.85rem;'>
                    {fii_dii_text}
                </div>
            </div>""",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """<div style='margin: -10px 0 8px 0; padding: 8px;'>
                <span style='color: #ffffff; font-size: 1.35rem; font-weight: 600;'>📈 Market Indices - Today's Performance</span>
            </div>""",
            unsafe_allow_html=True
        )

    # Render Market Indices (stays visible while rest loads)
    with st.spinner("⏳ Loading market indices data..."):
        render_market_indices()

    # CRITICAL: Render admin login FIRST so admin_mode is set
    render_admin_login()

    # Show appropriate view based on admin status
    st.markdown("---")
    
    # Admin gets portfolio section at top
    if st.session_state.admin_mode:
        with st.expander("💼 My Portfolio", expanded=False):
            render_portfolio_ui()
        st.markdown("---")
    
    # Everyone (including admin) sees market view
    market_view_content()

def market_view_content():
    """Render the main market view content (existing functionality)"""
    category = render_stock_selection_sidebar()

    if st.session_state.last_category != category:
        st.session_state.last_category = category
        st.session_state.cached_stocks_data = None
        st.session_state.cached_stocks_list_key = None
        st.session_state.search_query = ""
        st.session_state.search_version += 1

    # Get stock list
    if category == "Upload File":
        selected_stocks, _ = handle_file_upload()
    else:
        with st.spinner("Loading index list..."):
            selected_stocks, _ = cached_get_stock_list(category)

    # Sidebar controls
    st.sidebar.markdown("---")
    sort_by = st.sidebar.selectbox("Sort by", ["3 Months %", "1 Month %", "1 Week %", "Today %", "Stock Name"])
    sort_order = st.sidebar.radio("Order", ["Best to Worst", "Worst to Best"], horizontal=True)
    use_parallel = st.sidebar.checkbox("Parallel fetch (faster)", value=True)
    use_cache = st.sidebar.checkbox("Use cache", value=True)

    if st.sidebar.button("Refresh All Data", type="primary"):
        clear_cache_manager()
        st.session_state.cached_stocks_data = None
        st.session_state.cached_stocks_list_key = None
        cached_get_stock_list.clear()
        cached_load_all_saved_lists.clear()
        st.success("All caches cleared!")
        st.rerun()

    render_sidebar_info()

    if not selected_stocks:
        st.warning("Please select or upload a stock list.")
        return

    list_key = make_list_key(selected_stocks)
    if st.session_state.cached_stocks_data is None or st.session_state.cached_stocks_list_key != list_key:
        status = st.empty()
        with status:
            st.write("Fetching latest stock data...")
        stocks_data = fetch_stocks_data(selected_stocks, use_parallel, use_cache, status)
        st.session_state.cached_stocks_data = stocks_data
        st.session_state.cached_stocks_list_key = list_key
        st.session_state.last_updated_ts = time.time()
        status.empty()
    else:
        stocks_data = st.session_state.cached_stocks_data

    render_main_ui(category, selected_stocks, stocks_data, sort_by, sort_order)


if __name__ == "__main__":
    main()
