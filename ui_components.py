"""
UI Components for NSE Stock Performance Tracker
Streamlit UI rendering functions
"""

import streamlit as st
from config import INDICES_ROW1, INDICES_ROW2, METRIC_CSS
from data_fetchers import get_index_performance, get_commodities_prices
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
    st.markdown("**Sectoral Indices:**")
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
        "- ⚡ Parallel: 3x faster (5 stocks at once, rate-limit safe)\n"
        "- 🐢 Sequential: Original mode (default, slower but reliable)\n\n"
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
