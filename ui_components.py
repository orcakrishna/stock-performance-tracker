"""
UI Components for NSE Stock Performance Tracker
Streamlit UI rendering functions
"""

import streamlit as st
import yfinance as yf
from config import INDICES_ROW1, INDICES_ROW2, METRIC_CSS, TICKER_STOCKS
from data_fetchers import get_index_performance, get_commodities_prices, get_stock_list
from utils import get_current_times, format_time_display


def render_header():
    """Render app header with title, time, and commodities"""
    col_title, col_time = st.columns([3, 1])
    
    with col_title:
        st.title("📊 Indian Stock Performance Tracker")
        st.markdown("View 1-month, 2-month, and 3-month performance of NSE/BSE stocks.")
    
    with col_time:
        ist_time, edt_time = get_current_times()
        commodities_prices = get_commodities_prices()
        
        st.markdown(
            format_time_display(ist_time, edt_time, commodities_prices),
            unsafe_allow_html=True
        )


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
            if price and change:
                st.metric(
                    label=name,
                    value=f"{price:,.2f}",
                    delta=f"{change:+.2f}%"
                )
            else:
                st.metric(label=name, value="--", delta="--")
    
    # Row 2: Sectoral Indices
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### <span style='color: #ffffff; font-weight: 600; font-family: Segoe UI, Arial, sans-serif;'>Sectoral Indices:</span>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    cols2 = st.columns(len(INDICES_ROW2))
    for idx, (name, symbol) in enumerate(INDICES_ROW2.items()):
        with cols2[idx]:
            price, change = get_index_performance(symbol)
            if price and change:
                st.metric(
                    label=name,
                    value=f"{price:,.2f}",
                    delta=f"{change:+.2f}%"
                )
            else:
                st.metric(label=name, value="--", delta="--")
    
    st.markdown("---")


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
    """Render average performance metrics"""
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_1w = df['1 Week %'].mean()
        st.metric("Average 1-Week Change", f"{avg_1w:.2f}%")
    
    with col2:
        avg_1m = df['1 Month %'].mean()
        st.metric("Average 1-Month Change", f"{avg_1m:.2f}%")
    
    with col3:
        avg_2m = df['2 Months %'].mean()
        st.metric("Average 2-Month Change", f"{avg_2m:.2f}%")
    
    with col4:
        avg_3m = df['3 Months %'].mean()
        st.metric("Average 3-Month Change", f"{avg_3m:.2f}%")


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


@st.cache_data(ttl=60)  # Cache for 60 seconds
def get_ticker_data():
    """Fetch live data for ticker stocks"""
    ticker_data = []
    
    # Get Nifty 50 stocks
    nifty_50_stocks, _ = get_stock_list('Nifty 50')
    stocks_to_fetch = nifty_50_stocks if nifty_50_stocks else TICKER_STOCKS
    
    # Fetch data for each stock
    for symbol in stocks_to_fetch:
        try:
            ticker = yf.Ticker(symbol)
            # Use 2-day history (most reliable method)
            hist = ticker.history(period='2d')
            
            if len(hist) >= 2:
                current_price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                change_pct = ((current_price - prev_close) / prev_close) * 100
                
                ticker_data.append({
                    'symbol': symbol.replace('.NS', '').replace('.BO', ''),
                    'price': float(current_price),
                    'change': float(change_pct)
                })
            elif len(hist) == 1:
                # If only 1 day, use open vs close
                current_price = hist['Close'].iloc[-1]
                open_price = hist['Open'].iloc[-1]
                if open_price > 0:
                    change_pct = ((current_price - open_price) / open_price) * 100
                    ticker_data.append({
                        'symbol': symbol.replace('.NS', '').replace('.BO', ''),
                        'price': float(current_price),
                        'change': float(change_pct)
                    })
        except Exception as e:
            # Skip stocks that fail
            continue
    
    print(f"📊 Ticker: Fetched {len(ticker_data)}/{len(stocks_to_fetch)} stocks")
    return ticker_data


def render_gainer_loser_banner():
    """Render top gainer and loser banner from market indices"""
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
    
    # Display using compact inline format
    col1, col2, col_spacer = st.columns([1.5, 1.5, 5])
    
    with col1:
        st.markdown('<div class="gainer-loser-metric">', unsafe_allow_html=True)
        st.markdown(f"**🏆 Top Gainer:** <span style='color: #00ff00; font-size: 15px;'>{top_gainer['name']} ({top_gainer['change']:+.2f}%)</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="gainer-loser-metric">', unsafe_allow_html=True)
        st.markdown(f"**⚠️ Top Loser:** <span style='color: #ff4444; font-size: 15px;'>{top_loser['name']} ({top_loser['change']:+.2f}%)</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def render_live_ticker():
    """Render a live rolling stock ticker at the top"""
    ticker_data = get_ticker_data()
    
    if not ticker_data:
        # Show loading message
        st.markdown("""
        <div class="ticker-container">
            <div style="text-align: center; padding: 10px; color: #888;">
                📊 Loading live stock data...
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Sort alphabetically by symbol
    ticker_data_sorted = sorted(ticker_data, key=lambda x: x['symbol'])
    
    # Create ticker HTML - duplicate items for seamless loop
    ticker_items = ""
    for stock in ticker_data_sorted + ticker_data_sorted:  # Duplicate for seamless scrolling
        change_class = "ticker-change-positive" if stock['change'] >= 0 else "ticker-change-negative"
        change_symbol = "▲" if stock['change'] >= 0 else "▼"
        
        ticker_items += f"""<div class="ticker-item"><span class="ticker-symbol">{stock['symbol']}</span><span class="ticker-price">₹{stock['price']:.2f}</span><span class="{change_class}">{change_symbol} {abs(stock['change']):.2f}%</span></div>"""
    
    ticker_html = f"""<div class="ticker-container"><div class="ticker-wrapper">{ticker_items}</div></div>"""
    
    st.markdown(ticker_html, unsafe_allow_html=True)
