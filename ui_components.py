"""
UI Components for NSE Stock Performance Tracker
Streamlit UI rendering functions
"""

import streamlit as st
from config import INDICES_ROW1, INDICES_ROW2, METRIC_CSS
from data_fetchers import get_index_performance, get_commodities_prices, get_stock_list, get_next_nse_holiday, get_fii_dii_data
from utils import get_current_times, format_time_display, get_ticker_data


# =========================
# HEADER SECTION
# =========================
def render_header():
    """Render app header with title, time, and commodities"""
    col_title, col_time = st.columns([3, 1])

    with col_title:
        st.title("📊 Indian Stock Performance Tracker")
        st.markdown("View 1-month, 2-month, and 3-month performance of NSE/BSE stocks.")

    with col_time:
        ist_time, edt_time = get_current_times()
        commodities_prices = get_commodities_prices()
        next_holiday = get_next_nse_holiday()

        st.markdown(
            format_time_display(ist_time, edt_time, commodities_prices, next_holiday),
            unsafe_allow_html=True,
        )


def render_holiday_and_pe_info():
    """Render next NSE holiday date below today's date on the right side"""
    from datetime import datetime
    
    # Get next holiday date
    next_holiday_date = get_next_nse_holiday()
    
    # Build the display
    holiday_text = f"🏖️ Nifty Holiday: {next_holiday_date}" if next_holiday_date else "🏖️ Nifty Holiday: N/A"
    
    # Display on the right side, below the date
    st.markdown(
        f"""<div style='text-align: right; margin-top: 5px; margin-bottom: 15px; padding-right: 10px;'>
            <span style='color: #888; font-size: 0.85rem;'>{holiday_text}</span>
        </div>""",
        unsafe_allow_html=True
    )


# =========================
# MARKET INDICES
# =========================
def render_market_indices():
    """Render market indices performance section"""
    st.markdown("### 📈 Market Indices - Today's Performance")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(METRIC_CSS, unsafe_allow_html=True)

    # Row 1: Major Indices
    cols1 = st.columns(len(INDICES_ROW1))
    for idx, (name, symbol) in enumerate(INDICES_ROW1.items()):
        with cols1[idx]:
            price, change = get_index_performance(symbol)
            if price is not None and change is not None:
                st.metric(label=name, value=f"{price:,.2f}", delta=f"{change:+.2f}%")
            else:
                st.metric(label=name, value="--", delta="--")

    # Row 2: Sectoral Indices
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "### <span style='color: #ffffff; font-weight: 600;'>Sectoral Indices:</span>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    cols2 = st.columns(len(INDICES_ROW2))
    for idx, (name, symbol) in enumerate(INDICES_ROW2.items()):
        with cols2[idx]:
            price, change = get_index_performance(symbol)
            if price is not None and change is not None:
                st.metric(label=name, value=f"{price:,.2f}", delta=f"{change:+.2f}%")
            else:
                st.metric(label=name, value="--", delta="--")
    
    st.markdown("---")


# =========================
# LIVE TICKER
# =========================
def render_live_ticker(fii_dii_source=None):
    """Render a live rolling stock ticker at the top with FII/DII source at the end"""
    ticker_data = get_ticker_data()

    if not ticker_data:
        st.markdown('<div class="ticker-container"><div style="text-align: center; padding: 10px; color: #888;">📊 Loading live stock data...</div></div>', unsafe_allow_html=True)
        return

    # Sort alphabetically and duplicate for smooth loop
    ticker_data_sorted = sorted(ticker_data, key=lambda x: x["symbol"])
    stock_count = len(ticker_data_sorted)
    ticker_items = ""

    # Duplicate stocks for seamless infinite scroll
    for stock in ticker_data_sorted + ticker_data_sorted:
        change_class = "ticker-change-positive" if stock["change"] >= 0 else "ticker-change-negative"
        change_symbol = "▲" if stock["change"] >= 0 else "▼"
        
        ticker_items += f'<div class="ticker-item"><span class="ticker-symbol">{stock["symbol"]}</span><span class="ticker-price">₹{stock["price"]:.2f}</span><span class="{change_class}">{change_symbol} {abs(stock["change"]):.2f}%</span></div>'

    ticker_html = f'<div class="ticker-container"><div class="ticker-wrapper">{ticker_items}</div></div>'
    
    st.markdown(ticker_html, unsafe_allow_html=True)
    return stock_count


# =========================
# GAINER/LOSER BANNER
# =========================
def render_gainer_loser_banner():
    """Render top gainer and loser banner from market indices with FII/DII data"""
    indices_data = []
    
    # Combine all indices but exclude VIX and international indices
    all_indices = {**INDICES_ROW1, **INDICES_ROW2}
    exclude_list = ['India VIX', 'Dow Jones', 'NASDAQ']
    
    for name, symbol in all_indices.items():
        if name not in exclude_list:
            price, change = get_index_performance(symbol)
            if price and change:
                indices_data.append({
                    'name': name,
                    'change': change
                })
    
    if not indices_data:
        return
    
    # Find top gainer and loser
    top_gainer = max(indices_data, key=lambda x: x['change'])
    top_loser = min(indices_data, key=lambda x: x['change'])
    
    # Fetch FII/DII data
    fii_dii_data = get_fii_dii_data()
    
    # Display using compact inline format with FII/DII data
    # Adjust column widths: move DII left by making col3 smaller and col4 larger
    col1, col2, col3, col4 = st.columns([1.5, 1.5, 1.3, 1.7])
    
    with col1:
        st.markdown('<div class="gainer-loser-metric">', unsafe_allow_html=True)
        st.markdown(f"**🏆 Top Gainer:** <span style='color: #00ff00; font-size: 1rem; line-height: 1.5;'>{top_gainer['name']} ({top_gainer['change']:+.2f}%)</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="gainer-loser-metric">', unsafe_allow_html=True)
        st.markdown(f"**⚠️ Top Loser:** <span style='color: #ff4444; font-size: 1rem; line-height: 1.5;'>{top_loser['name']} ({top_loser['change']:+.2f}%)</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="gainer-loser-metric">', unsafe_allow_html=True)
        if fii_dii_data['status'] in ['success', 'cached', 'placeholder'] and fii_dii_data['fii']:
            fii = fii_dii_data['fii']
            net_color = '#00ff00' if fii['net'] >= 0 else '#ff4444'
            net_abs = abs(fii['net'])
            action = 'Buy' if fii['net'] >= 0 else 'Sell'
            # Show N/A for placeholder (0.0 values)
            if fii_dii_data['status'] == 'placeholder':
                st.markdown(f"**🌍 FII:** <span style='color: #888; font-size: 1rem; line-height: 1.5;'>N/A</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"**🌍 FII:** <span style='color: {net_color}; font-size: 1rem; line-height: 1.5;'>₹{net_abs:.0f} Cr ({action})</span>", unsafe_allow_html=True)
        else:
            st.markdown("**🌍 FII:** <span style='color: #888; font-size: 1rem;'>N/A</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="gainer-loser-metric">', unsafe_allow_html=True)
        if fii_dii_data['status'] in ['success', 'cached', 'placeholder'] and fii_dii_data['dii']:
            dii = fii_dii_data['dii']
            net_color = '#00ff00' if dii['net'] >= 0 else '#ff4444'
            net_abs = abs(dii['net'])
            action = 'Buy' if dii['net'] >= 0 else 'Sell'
            # Show N/A for placeholder (0.0 values)
            if fii_dii_data['status'] == 'placeholder':
                st.markdown(f"**🏦 DII:** <span style='color: #888; font-size: 1rem; line-height: 1.5;'>N/A</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"**🏦 DII:** <span style='color: {net_color}; font-size: 1rem; line-height: 1.5;'>₹{net_abs:.0f} Cr ({action})</span>", unsafe_allow_html=True)
        else:
            st.markdown("**🏦 DII:** <span style='color: #888; font-size: 1rem;'>N/A</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Return FII/DII data source for combined caption
    return fii_dii_data.get('source')


# =========================
# SIDEBAR INFO
# =========================
def render_sidebar_info():
    """Render sidebar information section"""
    st.sidebar.markdown("---")
    st.sidebar.info(
        "ℹ️ **Data Sources:**\n"
        "- Stock Lists: NSE CSV (dynamic, no API blocks)\n"
        "- Prices: yfinance (semi-live, ~15min delay)\n\n"
        "**Performance Modes:**\n"
        "- 🚀 Bulk Mode: Auto-enabled for 100+ stocks (20 workers)\n"
        "- ⚡ Parallel: 10x faster (10 workers, 50-100 stocks)\n"
        "- 🐢 Sequential: Small datasets (<50 stocks)\n\n"
        "**Optimization:**\n"
        "- 💾 6-hour persistent cache (instant load)\n"
        "- 🔄 Smart refresh (only fetch missing/expired)\n"
        "- ⚡ 20 parallel workers for 1000+ stocks\n\n"
        "**Features:**\n"
        "- Nifty Total Market (~750 stocks)\n"
        "- Upload custom stock lists\n"
        "- Real-time commodities & indices\n"
        "- Auto-retry with rate limit protection"
    )


# =========================
# PERFORMERS & AVERAGES
# =========================
def render_top_bottom_performers(df):
    """Render top and bottom performers section"""
    st.markdown("---")
    st.subheader("🏆 Top & Bottom Performers (3 Months)")
    col_top, col_bottom = st.columns(2)
    
    with col_top:
        st.markdown("**🔝 Top 3 Performers**")
        top_3 = df.nlargest(3, '3 Months %')[['Stock Name', '3 Months %']]
        for idx, row in top_3.iterrows():
            st.success(f"**{row['Stock Name']}**: +{row['3 Months %']}%")
    
    with col_bottom:
        st.markdown("**🔻 Bottom 3 Performers**")
        bottom_3 = df.nsmallest(3, '3 Months %')[['Stock Name', '3 Months %']]
        for idx, row in bottom_3.iterrows():
            st.error(f"**{row['Stock Name']}**: {row['3 Months %']}%")


def render_averages(df):
    """Render key index 1-year performance"""
    import yfinance as yf
    from datetime import datetime, timedelta
    
    st.markdown("---")
    st.subheader("📊 Key Index Performance (1 Year)")
    
    # Define main indices only (not sectoral) - alphabetically ordered
    # Note: Smallcap indices not available in Yahoo Finance with reliable data
    indices = {
        'Bank Nifty': '^NSEBANK',
        'Nifty 50': '^NSEI',
        'Nifty Midcap 50': '^NSEMDCP50',
        'Sensex': '^BSESN'
    }
    
    # Create 4 columns for 4 indices
    cols = st.columns(4)
    
    for idx, (name, symbol) in enumerate(indices.items()):
        with cols[idx]:
            try:
                ticker = yf.Ticker(symbol)
                end_date = datetime.now()
                start_date = end_date - timedelta(days=365)
                
                hist = ticker.history(start=start_date, end=end_date)
                
                if not hist.empty and len(hist) > 1:
                    start_price = hist['Close'].iloc[0]
                    end_price = hist['Close'].iloc[-1]
                    year_change = ((end_price - start_price) / start_price) * 100
                    
                    st.metric(
                        label=name,
                        value=f"{end_price:,.2f}",
                        delta=f"{year_change:+.2f}%"
                    )
                else:
                    st.metric(label=name, value="--", delta="--")
            except Exception as e:
                st.metric(label=name, value="--", delta="--")


# =========================
# PAGINATION
# =========================
def render_pagination_controls(total_items, items_per_page):
    """Render pagination controls and return current page data range"""
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    
    col1, col2, col3 = st.columns([1, 6, 1])
    
    with col1:
        if st.button("⬅️ Previous", disabled=(st.session_state.current_page == 1)):
            st.session_state.current_page -= 1
            st.rerun()
    
    with col2:
        st.markdown(
            f"<h4 style='text-align: center; margin-top: 5px;'>Page {st.session_state.current_page} of {total_pages}</h4>",
            unsafe_allow_html=True
        )
    
    with col3:
        if st.button("Next ➡️", disabled=(st.session_state.current_page == total_pages)):
            st.session_state.current_page += 1
            st.rerun()
    
    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    return start_idx, end_idx


# =========================
# SECTORAL YEARLY PERFORMANCE
# =========================
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_sectoral_yearly_data():
    """Fetch 1-year data for sectoral indices only (not main indices)"""
    import yfinance as yf
    from datetime import datetime, timedelta
    import time
    
    # Only sectoral indices (excluding main indices) - alphabetically ordered
    all_sectoral_indices = {
        'Nifty Auto': '^CNXAUTO',
        'Nifty Energy': '^CNXENERGY',
        'Nifty FMCG': '^CNXFMCG',
        'Nifty IT': '^CNXIT',
        'Nifty Metal': '^CNXMETAL',
        'Nifty Pharma': '^CNXPHARMA',
        'Nifty Realty': '^CNXREALTY'
    }
    
    sectoral_data = []
    
    for name, symbol in all_sectoral_indices.items():
        # Retry logic with longer delays
        max_retries = 2
        for attempt in range(max_retries):
            try:
                ticker = yf.Ticker(symbol)
                
                # Use period instead of start/end for better reliability
                hist = ticker.history(period='1y')
                
                if not hist.empty and len(hist) > 20:  # Ensure sufficient data
                    start_price = hist['Close'].iloc[0]
                    end_price = hist['Close'].iloc[-1]
                    year_change = ((end_price - start_price) / start_price) * 100
                    
                    sectoral_data.append({
                        'Sector': name,
                        'Current Price': f"{end_price:,.2f}",
                        '1 Year Change %': round(year_change, 2),
                        'Start Price': f"{start_price:,.2f}"
                    })
                    break  # Success, exit retry loop
                
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait 2 seconds before retry
                    continue
                else:
                    print(f"Error fetching {name} after {max_retries} attempts: {e}")
                    # Add placeholder data so section still shows
                    sectoral_data.append({
                        'Sector': name,
                        'Current Price': '--',
                        '1 Year Change %': 0,
                        'Start Price': '--'
                    })
        
        # Longer delay between indices to avoid rate limiting
        time.sleep(0.5)
    
    return sectoral_data


def render_sectoral_yearly_performance():
    """Render comprehensive sectoral indices 1-year performance"""
    
    st.markdown("---")
    st.subheader("📊 Sectoral Indices - 1 Year Performance")
    st.caption("Annual performance comparison across all major sectors")
    
    # Add button to load on demand
    if 'show_sectoral' not in st.session_state:
        st.session_state.show_sectoral = False
    
    if not st.session_state.show_sectoral:
        if st.button("📊 Load Sectoral Performance Data"):
            st.session_state.show_sectoral = True
            st.rerun()
        return
    
    # Fetch data with caching
    with st.spinner("Loading sectoral performance data..."):
        sectoral_data = fetch_sectoral_yearly_data()
    
    if sectoral_data and len(sectoral_data) > 0:
        # Data is already in alphabetical order from the dictionary
        # Display all sectors in a single row with equal columns
        num_sectors = len(sectoral_data)
        cols = st.columns(num_sectors)
        
        for idx, data in enumerate(sectoral_data):
            with cols[idx]:
                change_pct = data['1 Year Change %']
                # Handle placeholder data
                if data['Current Price'] == '--':
                    st.metric(
                        label=data['Sector'],
                        value="--",
                        delta="--"
                    )
                else:
                    st.metric(
                        label=data['Sector'],
                        value=data['Current Price'],
                        delta=f"{change_pct:+.2f}%"
                    )
    else:
        st.warning("⚠️ Unable to fetch sectoral performance data. Yahoo Finance may be rate limiting. Please wait a few minutes and refresh.")
