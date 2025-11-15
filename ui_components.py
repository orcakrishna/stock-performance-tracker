"""
UI Components for NSE Stock Performance Tracker
Streamlit UI rendering functions
"""

import streamlit as st
from config import INDICES_ROW1, INDICES_ROW2, METRIC_CSS
from data_fetchers import get_index_performance, get_commodities_prices, get_stock_list, get_next_nse_holiday, get_fii_dii_data, get_highest_volume_stocks
from utils import get_current_times, format_time_display, get_ticker_data, get_market_session_status


# =========================
# HEADER SECTION
# =========================
def render_header():
    """Render app header with title, time, and commodities"""
    # Box styling for header sections
    st.markdown("""
    <style>
        /* Beautiful box styling for header sections - Navy Blue Theme */
        .info-box {
            background: linear-gradient(135deg, rgba(26, 35, 126, 0.3) 0%, rgba(13, 27, 42, 0.5) 100%) !important;
            border: 1px solid rgba(66, 165, 245, 0.3) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4), 0 0 20px rgba(66, 165, 245, 0.1) !important;
            transition: all 0.3s ease !important;
            margin-bottom: 1rem !important;
        }
        
        .info-box:hover {
            background: linear-gradient(135deg, rgba(26, 35, 126, 0.5) 0%, rgba(13, 71, 161, 0.3) 100%) !important;
            border-color: rgba(66, 165, 245, 0.6) !important;
            transform: translateY(-3px) !important;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.5), 0 0 30px rgba(66, 165, 245, 0.2) !important;
        }
        
        .info-box-title {
            font-size: 0.875rem !important;
            font-weight: 600 !important;
            color: #42a5f5 !important;
            margin-bottom: 0.75rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            border-bottom: 1px solid rgba(66, 165, 245, 0.3) !important;
            padding-bottom: 0.5rem !important;
        }

        .market-overview-title {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
        }

        .market-overview-meta {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
            justify-content: flex-end;
        }

        .market-overview-status {
            position: relative;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 0;
            font-weight: 700;
            font-size: 0.8rem;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            white-space: nowrap;
            color: var(--status-color, #42a5f5);
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }


        .market-overview-updated {
            color: #95e1d3;
            font-size: 0.78rem;
            white-space: nowrap;
        }

        .market-overview-updated span {
            color: #42a5f5;
            font-weight: 600;
        }

        @media (max-width: 768px) {
            .header-title {
                font-size: 1.4rem !important;
            }
            .header-subtitle {
                font-size: 0.875rem !important;
            }
            /* Force single column on mobile */
            div[data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Title section
    st.markdown('<h1 class="header-title">📊 Indian Stock Performance Tracker</h1>', unsafe_allow_html=True)
    st.markdown(
        """<div style='margin-top: -10px;'>
            <span class='header-subtitle' style='color: #00ff88; font-weight: bold; font-size: 1rem;'>
                View 1-month, 2-month, and 3-month performance of NSE/BSE stocks.
            </span>
        </div>""",
        unsafe_allow_html=True
    )
    
    # Commodities section - wrapped in left-aligned container
    ist_time, edt_time = get_current_times()
    market_status, status_color = get_market_session_status()
    last_updated = ist_time.strftime('%d %b %Y, %I:%M %p IST')
    commodities_prices = get_commodities_prices()
    next_holiday = get_next_nse_holiday()

    # Create two columns: commodities on left, volume stocks on right
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Build commodities box content
        commodities_html = f"""
        <div class="info-box">
            <div class="info-box-title market-overview-title">
                <span>🌍 Market Overview</span>
                <div class="market-overview-meta">
                    <span class="market-overview-status" style="--status-color: {status_color}; color: {status_color};">
                        {market_status}
                    </span>
                    <span class="market-overview-updated">🕒 Updated: <span>{last_updated}</span></span>
                </div>
            </div>
            {format_time_display(ist_time, edt_time, commodities_prices, next_holiday)}
        </div>
        """
        st.markdown(commodities_html, unsafe_allow_html=True)
    
    with col2:
        # Render highest volume stocks from ticker (Nifty 50 - already loaded, avoids rate limits)
        try:
            from data_fetchers import get_highest_volume_stocks
            
            # Create placeholder FIRST before any computation
            volume_placeholder = st.empty()
            
            # Show loading indicator IMMEDIATELY
            base_box_html = '<div class="info-box"><div class="info-box-title">📊 Highest Volume Stocks</div>'
            loading_html = base_box_html + """
                <div style='text-align: center; padding: 20px 0;'>
                    <div class='volume-spinner'></div>
                    <p style='color: #42a5f5; margin-top: 10px; font-size: 0.875rem; font-weight: 500;'>⏳ Loading volume data...</p>
                </div>
                <style>
                    .volume-spinner {
                        border: 3px solid rgba(66, 165, 245, 0.2);
                        border-top: 3px solid #42a5f5;
                        border-radius: 50%;
                        width: 24px;
                        height: 24px;
                        animation: volume-spin 0.8s linear infinite;
                        margin: 0 auto;
                    }
                    @keyframes volume-spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                </style>
            </div>"""
            volume_placeholder.markdown(loading_html, unsafe_allow_html=True)
            
            # Cached function to fetch high volume stocks once per day
            @st.cache_data(ttl=86400, show_spinner=False)  # Cache for 24 hours
            def get_cached_volume_stocks(stock_symbols_tuple):
                """Fetch high volume stocks with daily caching"""
                print(f"📊 Fetching volume data from {len(stock_symbols_tuple)} ticker stocks (cached for 24h)")
                return get_highest_volume_stocks(list(stock_symbols_tuple), top_n=7)
            
            # Use ticker stocks (already loaded, no extra API calls)
            ticker_stocks = get_ticker_data()

            if ticker_stocks and len(ticker_stocks) >= 7:
                stock_symbols = tuple([s['symbol'] for s in ticker_stocks])  # Convert to tuple for caching
                volume_stocks = get_cached_volume_stocks(stock_symbols)

                if volume_stocks:
                    volume_stocks_html = base_box_html
                    volume_stocks_html += '<table style="width: 100%; font-size: 0.875rem; border-collapse: collapse;">'
                    volume_stocks_html += '<thead><tr style="border-bottom: 1px solid rgba(66, 165, 245, 0.3);"><th style="text-align: left; padding: 0.3rem 0.5rem; color: #42a5f5; font-weight: 600;">Symbol</th><th style="text-align: right; padding: 0.3rem 0.5rem; color: #42a5f5; font-weight: 600;">Price</th><th style="text-align: right; padding: 0.3rem 0.5rem; color: #42a5f5; font-weight: 600;">Change</th><th style="text-align: right; padding: 0.3rem 0.5rem; color: #42a5f5; font-weight: 600;">Volume</th></tr></thead>'
                    volume_stocks_html += '<tbody>'

                    for stock in volume_stocks:
                        change_pct = stock.get('change_pct', stock.get('change', 0))
                        change_icon = "▲" if change_pct >= 0 else "▼"
                        change_color = "#00ff00" if change_pct >= 0 else "#ff4444"
                        vol_display = f"{stock['volume']/1_000_000:.1f}M" if stock['volume'] >= 1_000_000 else f"{stock['volume']/1_000:.0f}K"

                        volume_stocks_html += f'<tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.1);"><td style="padding: 0.4rem 0.5rem; color: #ffffff; font-weight: 600;">{stock["symbol"]}</td><td style="padding: 0.4rem 0.5rem; text-align: right;">₹{stock["price"]:.2f}</td><td style="padding: 0.4rem 0.5rem; text-align: right;"><span style="color: {change_color}; font-weight: bold;">{change_icon} {abs(change_pct):.2f}%</span></td><td style="padding: 0.4rem 0.5rem; text-align: right;">{vol_display}</td></tr>'

                    volume_stocks_html += '</tbody></table>'
                    volume_stocks_html += '</div>'
                    volume_placeholder.markdown(volume_stocks_html, unsafe_allow_html=True)
                else:
                    volume_placeholder.markdown(base_box_html + "<span style='color: rgba(255, 255, 255, 0.5);'>No volume data available.</span></div>", unsafe_allow_html=True)
            else:
                volume_placeholder.markdown(base_box_html + "<span style='color: rgba(255, 255, 255, 0.5);'>Ticker data unavailable.</span></div>", unsafe_allow_html=True)
            
        except Exception as e:
            print(f"Error rendering volume stocks in header: {e}")
            import traceback
            traceback.print_exc()
            error_html = """
            <div class="info-box">
                <div class="info-box-title">📊 Highest Volume Stocks</div>
                <span style='color: rgba(255, 255, 255, 0.5);'>Unable to load data</span>
            </div>
            """
            st.markdown(error_html, unsafe_allow_html=True)


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
@st.cache_data(ttl=3600, show_spinner=False)
def get_index_sparkline(symbol):
    """Get sparkline data for index (7 days)"""
    import yfinance as yf
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='7d')
        if not hist.empty and len(hist) >= 2:
            prices = hist['Close'].tolist()
            # Normalize to 0-100 range
            min_price = min(prices)
            max_price = max(prices)
            if max_price > min_price:
                normalized = [(p - min_price) / (max_price - min_price) * 100 for p in prices]
                return normalized
    except:
        pass
    return None


def create_index_sparkline_svg(sparkline_data, change_pct, symbol, width=50, height=25):
    """Create a clickable mini SVG sparkline for indices"""
    if not sparkline_data or len(sparkline_data) < 2:
        return ""
    
    points = []
    step = width / (len(sparkline_data) - 1)
    
    for i, value in enumerate(sparkline_data):
        x = i * step
        y = height - (value / 100 * height)
        points.append(f"{x:.1f},{y:.1f}")
    
    path_data = "M " + " L ".join(points)
    color = "#00ff00" if change_pct >= 0 else "#ff4444"
    
    # Map NSE symbols to TradingView symbols
    tv_symbol_map = {
        '^NSEI': 'NSE:NIFTY',
        '^NSEBANK': 'NSE:BANKNIFTY',
        '^BSESN': 'BSE:SENSEX',
        '^CNXIT': 'NSE:CNXIT',
        '^CNXPHARMA': 'NSE:CNXPHARMA',
        '^CNXREALTY': 'NSE:CNXREALTY',
        '^CNXMETAL': 'NSE:CNXMETAL',
        '^CNXENERGY': 'NSE:CNXENERGY',
        '^CNXFMCG': 'NSE:CNXFMCG',
        '^CNXAUTO': 'NSE:CNXAUTO'
    }
    
    tv_symbol = tv_symbol_map.get(symbol, 'NSE:NIFTY')
    tradingview_url = f"https://www.tradingview.com/chart/?symbol={tv_symbol}"
    
    return f'''<a href="{tradingview_url}" target="_blank" style="text-decoration: none; cursor: pointer;" title="View on TradingView">
        <svg width="{width}" height="{height}" style="display: inline-block; vertical-align: middle; opacity: 0.8; transition: opacity 0.2s;" 
             onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.8'">
            <path d="{path_data}" fill="none" stroke="{color}" stroke-width="2" />
        </svg>
    </a>'''


def render_market_indices():
    """Render market indices performance section with mini charts"""
    st.markdown("### 📈 Market Indices - Today's Performance")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(METRIC_CSS, unsafe_allow_html=True)
    
    # Add CSS to position chart next to percentage delta inside metric box
    st.markdown("""
    <style>
        /* Make metric box relative for absolute positioning of chart */
        div[data-testid="stMetric"] {
            position: relative !important;
        }
        
        /* Position chart absolutely inside metric, next to delta */
        .mini-chart-inline {
            position: absolute !important;
            bottom: 10px !important;
            right: 10px !important;
            z-index: 10 !important;
        }
        
        /* Add right padding to metric delta to make space for chart when chart exists */
        .has-chart [data-testid="stMetricDelta"] {
            margin-right: 60px !important;
        }
        
        /* Loading skeleton animation */
        .indices-loading {
            background: linear-gradient(90deg, rgba(255,255,255,0.05) 25%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0.05) 75%);
            background-size: 200% 100%;
            animation: loading-shimmer 1.5s infinite;
        }
        @keyframes loading-shimmer {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
    </style>
    """, unsafe_allow_html=True)

    # Row 1: Major Indices - Wrapped for mobile targeting
    st.markdown('<div class="metric-row">', unsafe_allow_html=True)
    cols1 = st.columns(len(INDICES_ROW1))
    for idx, (name, symbol) in enumerate(INDICES_ROW1.items()):
        with cols1[idx]:
            price, change = get_index_performance(symbol)
            sparkline_data = get_index_sparkline(symbol)
            
            if price is not None and change is not None:
                has_chart = bool(sparkline_data)
                
                if has_chart:
                    st.markdown('<div class="has-chart">', unsafe_allow_html=True)
                
                st.metric(label=name, value=f"{price:,.2f}", delta=f"{change:+.2f}%")
                
                if has_chart:
                    chart_html = create_index_sparkline_svg(sparkline_data, change, symbol, width=50, height=25)
                    st.markdown(f'<div class="mini-chart-inline">{chart_html}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.metric(label=name, value="--", delta="--")
    st.markdown('</div>', unsafe_allow_html=True)

    # Row 2: Sectoral Indices
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "### <span style='color: #ffffff; font-weight: 600;'>Sectoral Indices:</span>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="metric-row">', unsafe_allow_html=True)
    cols2 = st.columns(len(INDICES_ROW2))
    for idx, (name, symbol) in enumerate(INDICES_ROW2.items()):
        with cols2[idx]:
            price, change = get_index_performance(symbol)
            sparkline_data = get_index_sparkline(symbol)
            
            if price is not None and change is not None:
                has_chart = sparkline_data
                
                if has_chart:
                    st.markdown('<div class="has-chart">', unsafe_allow_html=True)
                
                st.metric(label=name, value=f"{price:,.2f}", delta=f"{change:+.2f}%")
                
                if has_chart:
                    chart_html = create_index_sparkline_svg(sparkline_data, change, symbol, width=50, height=25)
                    st.markdown(f'<div class="mini-chart-inline">{chart_html}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.metric(label=name, value="--", delta="--")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")


# =========================
# LIVE TICKER
# =========================
def render_live_ticker(fii_dii_source=None):
    """Render a live rolling stock ticker at the top with FII/DII source at the end"""
    ticker_data = get_ticker_data()

    if not ticker_data:
        st.markdown('<div class="ticker-container"><div style="text-align: center; padding: 10px; color: #888;">📊 Loading live stock data...</div></div>', unsafe_allow_html=True)
        return None, None, None

    # Sort alphabetically and duplicate for smooth loop
    ticker_data_sorted = sorted(ticker_data, key=lambda x: x["symbol"])
    stock_count = len(ticker_data_sorted)
    
    # Calculate advances and declines
    advances = sum(1 for stock in ticker_data_sorted if stock["change"] > 0)
    declines = sum(1 for stock in ticker_data_sorted if stock["change"] < 0)
    unchanged = stock_count - advances - declines
    
    ticker_items = ""

    # Duplicate stocks for seamless infinite scroll
    for stock in ticker_data_sorted + ticker_data_sorted:
        change_class = "ticker-change-positive" if stock["change"] >= 0 else "ticker-change-negative"
        change_symbol = "▲" if stock["change"] >= 0 else "▼"
        
        ticker_items += f'<div class="ticker-item"><span class="ticker-symbol">{stock["symbol"]}</span><span class="ticker-price">₹{stock["price"]:.2f}</span><span class="{change_class}">{change_symbol} {abs(stock["change"]):.2f}%</span></div>'

    ticker_html = f'<div class="ticker-container"><div class="ticker-wrapper">{ticker_items}</div></div>'
    
    st.markdown(ticker_html, unsafe_allow_html=True)
    return stock_count, advances, declines


# Highest volume stocks rendering is now handled directly in render_header() function above


# =========================
# GAINER/LOSER BANNER
# =========================
def render_gainer_loser_banner():
    """Render top gainer and loser banner from market indices with FII/DII data and weekly sectoral"""
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
    
    # Fetch weekly sectoral data
    import yfinance as yf
    sectoral_indices = {
        'Nifty Auto': '^CNXAUTO',
        'Nifty Energy': '^CNXENERGY',
        'Nifty FMCG': '^CNXFMCG',
        'Nifty IT': '^CNXIT',
        'Nifty Metal': '^CNXMETAL',
        'Nifty Pharma': '^CNXPHARMA',
        'Nifty Realty': '^CNXREALTY'
    }
    
    weekly_sectoral_data = []
    for name, symbol in sectoral_indices.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1wk')
            if len(hist) >= 2:
                week_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                weekly_sectoral_data.append({'name': name, 'change': week_change})
        except Exception as e:
            print(f"Error fetching weekly data for {name}: {e}")
            continue
    
    # Find weekly sectoral gainer and loser
    weekly_gainer = None
    weekly_loser = None
    if weekly_sectoral_data:
        weekly_gainer = max(weekly_sectoral_data, key=lambda x: x['change'])
        weekly_loser = min(weekly_sectoral_data, key=lambda x: x['change'])
    
    # Fetch FII/DII data
    fii_dii_data = get_fii_dii_data()
    
    # Display using compact inline format with FII/DII data and weekly sectoral
    # 6 columns with equal widths
    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
    
    with col1:
        st.markdown('<div class="gainer-loser-metric">', unsafe_allow_html=True)
        st.markdown(f"**🏆 Top Gainer:** <span style='color: #00ff00; font-size: 1rem; line-height: 1.5;'>{top_gainer['name']} ({top_gainer['change']:+.2f}%)</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="gainer-loser-metric">', unsafe_allow_html=True)
        st.markdown(f"**⚠️ Top Loser:** <span style='color: #ff4444; font-size: 0.85rem; line-height: 1.5;'>{top_loser['name']} ({top_loser['change']:+.2f}%)</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="gainer-loser-metric">', unsafe_allow_html=True)
        if weekly_gainer:
            st.markdown(f"**📈 Weekly Gainer:** <span style='color: #00ff00; font-size: 0.85rem; line-height: 1.5;'>{weekly_gainer['name'].replace('Nifty ', '')} ({weekly_gainer['change']:+.2f}%)</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"**📈 Weekly Gainer:** <span style='color: #888; font-size: 0.85rem;'>N/A</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="gainer-loser-metric">', unsafe_allow_html=True)
        if weekly_loser:
            st.markdown(f"**📉 Weekly Loser:** <span style='color: #ff4444; font-size: 0.85rem; line-height: 1.5;'>{weekly_loser['name'].replace('Nifty ', '')} ({weekly_loser['change']:+.2f}%)</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"**📉 Weekly Loser:** <span style='color: #888; font-size: 0.85rem;'>N/A</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col5:
        st.markdown('<div class="gainer-loser-metric">', unsafe_allow_html=True)
        if fii_dii_data.get('status') in ['success', 'cached', 'placeholder', 'error'] and fii_dii_data.get('fii'):
            fii = fii_dii_data['fii']
            net_color = '#00ff00' if fii['net'] >= 0 else '#ff4444'
            net_abs = abs(fii['net'])
            action = 'Buy' if fii['net'] >= 0 else 'Sell'
            # Show N/A for placeholder/error (0.0 values)
            if fii_dii_data['status'] in ['placeholder', 'error']:
                st.markdown(f"**🌍 FII:** <span style='color: #888; font-size: 0.85rem; line-height: 1.5;'>N/A</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"**🌍 FII:** <span style='color: {net_color}; font-size: 0.85rem; line-height: 1.5;'>₹{net_abs:.0f} Cr ({action})</span>", unsafe_allow_html=True)
        else:
            st.markdown("**🌍 FII:** <span style='color: #888; font-size: 0.85rem;'>N/A</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col6:
        st.markdown('<div class="gainer-loser-metric">', unsafe_allow_html=True)
        if fii_dii_data.get('status') in ['success', 'cached', 'placeholder', 'error'] and fii_dii_data.get('dii'):
            dii = fii_dii_data['dii']
            net_color = '#00ff00' if dii['net'] >= 0 else '#ff4444'
            net_abs = abs(dii['net'])
            action = 'Buy' if dii['net'] >= 0 else 'Sell'
            # Show N/A for placeholder/error (0.0 values)
            if fii_dii_data['status'] in ['placeholder', 'error']:
                st.markdown(f"**🏦 DII:** <span style='color: #888; font-size: 0.85rem; line-height: 1.5;'>N/A</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"**🏦 DII:** <span style='color: {net_color}; font-size: 0.85rem; line-height: 1.5;'>₹{net_abs:.0f} Cr ({action})</span>", unsafe_allow_html=True)
        else:
            st.markdown("**🏦 DII:** <span style='color: #888; font-size: 0.85rem;'>N/A</span>", unsafe_allow_html=True)
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
        "**Smart Caching:**\n"
        "- 📈 Market Open: 5-min cache (fresh data)\n"
        "- 🌙 After Hours: 1-hour cache\n"
        "- 📅 Weekend: 24-hour cache (no market)\n"
        "- 🏖️ Holiday: 24-hour cache (no market)\n"
        "- 🔄 Auto-refresh based on market status\n\n"
        "**Features:**\n"
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
    
    # CSS for responsive layout: 2 columns on desktop, stacked on mobile
    st.markdown("""
    <style>
        .performers-section [data-testid="stHorizontalBlock"] {
            display: flex;
        }
        @media (max-width: 768px) {
            .performers-section [data-testid="stHorizontalBlock"] {
                flex-direction: column !important;
            }
            .performers-section [data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }
            /* Keep performer text on single line */
            .performers-section [data-testid="stAlert"] {
                white-space: nowrap !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
            }
            .performers-section [data-testid="stAlert"] > div {
                white-space: nowrap !important;
            }
        }
    </style>
    <div class="performers-section">
    """, unsafe_allow_html=True)
    
    # Two columns on desktop, stacked on mobile
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
    
    # Close performers section
    st.markdown("</div>", unsafe_allow_html=True)


def render_averages(df):
    """Render key index 1-year performance"""
    import yfinance as yf
    from datetime import datetime, timedelta
    
    st.markdown("---")
    st.subheader("📊 Key Index Performance (1 Year)")
    
    # Define main indices and commodities - indices first, then commodities
    # Note: Smallcap indices not available in Yahoo Finance with reliable data
    indices = {
        'Nifty 50': '^NSEI',
        'Sensex': '^BSESN',
        'Bank Nifty': '^NSEBANK',
        'Nifty Midcap 50': '^NSEMDCP50',
        'Gold': 'GC=F',
        'Silver': 'SI=F'
    }
    
    # Create 6 columns for 4 indices + 2 commodities
    cols = st.columns(6)
    
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
                    
                    # Calculate 52-week high and low
                    week_52_high = hist['High'].max()
                    week_52_low = hist['Low'].min()
                    
                    # Determine delta styling
                    arrow = "▲" if year_change >= 0 else "▼"
                    delta_class = "positive" if year_change >= 0 else "negative"
                    
                    # Add $ only for Gold and Silver (USD commodities)
                    currency_symbol = "$" if name in ["Gold", "Silver"] else ""
                    
                    # Create single unified box with all data
                    st.markdown(f"""
                        <div class="yearly-metric-box">
                            <div class="yearly-metric-label">{name}</div>
                            <div class="yearly-metric-value">{currency_symbol}{end_price:,.2f}</div>
                            <div class="yearly-metric-delta {delta_class}">{arrow} {abs(year_change):.2f}%</div>
                            <div class="yearly-52w-data">
                                <div>52W High: <span style='color: #00ff00; font-weight: 600;'>{currency_symbol}{week_52_high:,.2f}</span></div>
                                <div>52W Low: <span style='color: #ff4444; font-weight: 600;'>{currency_symbol}{week_52_low:,.2f}</span></div>
                            </div>
                        </div>
                        <style>
                            .yearly-metric-box {{
                                background: linear-gradient(135deg, rgba(26, 35, 126, 0.3) 0%, rgba(13, 27, 42, 0.5) 100%);
                                border: 1px solid rgba(66, 165, 245, 0.3);
                                border-radius: 8px;
                                padding: 0.5rem 0.75rem;
                                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3), 0 0 15px rgba(66, 165, 245, 0.08);
                                transition: all 0.3s ease;
                            }}
                            .yearly-metric-box:hover {{
                                background: linear-gradient(135deg, rgba(26, 35, 126, 0.5) 0%, rgba(13, 71, 161, 0.3) 100%);
                                border-color: rgba(66, 165, 245, 0.6);
                                transform: translateY(-2px);
                                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4), 0 0 20px rgba(66, 165, 245, 0.15);
                            }}
                            .yearly-metric-label {{
                                font-size: 0.7rem;
                                line-height: 1.3;
                                color: rgba(255, 255, 255, 0.7);
                                font-weight: 500;
                                margin-bottom: 0.25rem;
                            }}
                            .yearly-metric-value {{
                                font-size: 1rem;
                                font-weight: 600;
                                color: #ffffff;
                                line-height: 1.2;
                                margin-bottom: 0.2rem;
                                font-family: 'JetBrains Mono', monospace;
                            }}
                            .yearly-metric-delta {{
                                display: inline-flex;
                                align-items: center;
                                gap: 4px;
                                font-size: 0.7rem;
                                font-weight: 600;
                                line-height: 1.2;
                                padding: 2px 5px;
                                border-radius: 3px;
                                white-space: nowrap;
                                margin-bottom: 0.5rem;
                            }}
                            .yearly-metric-delta.positive {{
                                color: #00ff00;
                                background-color: rgba(0, 255, 0, 0.15);
                                border: 1px solid rgba(0, 255, 0, 0.3);
                            }}
                            .yearly-metric-delta.negative {{
                                color: #ff4444;
                                background-color: rgba(255, 68, 68, 0.15);
                                border: 1px solid rgba(255, 68, 68, 0.3);
                            }}
                            .yearly-52w-data {{
                                font-size: 0.7rem;
                                color: rgba(255, 255, 255, 0.6);
                                line-height: 1.5;
                                padding-top: 0.5rem;
                                border-top: 1px solid rgba(66, 165, 245, 0.2);
                            }}
                        </style>
                    """, unsafe_allow_html=True)
                else:
                    st.metric(label=name, value="--", delta="--")
            except Exception as e:
                st.metric(label=name, value="--", delta="--")


# =========================
# PAGINATION
# =========================
def render_pagination_controls(total_items, items_per_page, position="top"):
    """Render pagination controls and return current page data range"""
    total_pages = (total_items + items_per_page - 1) // items_per_page

    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    elif total_pages > 0:
        st.session_state.current_page = max(1, min(st.session_state.current_page, total_pages))
    else:
        st.session_state.current_page = 1
    
    # Wrap pagination in a container div for specific styling
    st.markdown('<div class="pagination-container">', unsafe_allow_html=True)
    
    # Use 3 columns: left arrow, centered text, right arrow
    # Increase middle width to push right button further right
    col1, col2, col3 = st.columns([0.4, 11.2, 0.4])
    
    with col1:
        st.markdown("""
            <style>
            div[data-testid="column"]:nth-of-type(1) {
                display: flex !important;
                justify-content: flex-start !important;
            }
            div[data-testid="column"]:nth-of-type(1) button {
                background-color: #00d4ff !important;
                color: white !important;
                border: none !important;
                font-size: 1.2rem !important;
                padding: 5px 10px !important;
                margin-left: 0 !important;
            }
            /* Mobile pagination - keep horizontal and stick to left */
            @media (max-width: 768px) {
                .pagination-container [data-testid="column"]:nth-of-type(1) {
                    flex: 0 0 auto !important;
                    width: auto !important;
                    min-width: 40px !important;
                }
            }
            </style>
        """, unsafe_allow_html=True)
        if st.button("◄", disabled=(st.session_state.current_page == 1), key=f"prev_page_{position}"):
            st.session_state.current_page -= 1
            st.rerun()
    
    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    with col2:
        st.markdown("""
            <style>
                .pagination-text {
                    text-align: center;
                    margin: 0 0 -15px 0 !important;
                    padding: 10px 0 5px 0 !important;
                    font-size: 0.9rem;
                    color: white;
                    font-weight: bold;
                    white-space: nowrap;
                    line-height: 1.2;
                    vertical-align: middle;
                }
                @media (max-width: 768px) {
                    .pagination-text {
                        font-size: 0.65rem !important;
                        white-space: normal !important;
                        padding: 8px 2px 3px 2px !important;
                        margin: 0 0 -10px 0 !important;
                        line-height: 1.2 !important;
                    }
                }
                @media (max-width: 480px) {
                    .pagination-text {
                        font-size: 0.6rem !important;
                        padding: 6px 2px 2px 2px !important;
                        margin: 0 0 -8px 0 !important;
                    }
                }
            </style>
        """, unsafe_allow_html=True)
        st.markdown(
            f"<p class='pagination-text'>Page {st.session_state.current_page} of {total_pages} <span style='color: #95e1d3; font-weight: normal;'>(Showing {start_idx + 1}-{end_idx} of {total_items})</span></p>",
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown("""
            <style>
            div[data-testid="column"]:nth-of-type(3) {
                display: flex !important;
                justify-content: flex-end !important;
            }
            div[data-testid="column"]:nth-of-type(3) button {
                background-color: #00ff88 !important;
                color: white !important;
                border: none !important;
                font-size: 1.2rem !important;
                padding: 5px 10px !important;
                margin-right: 0 !important;
            }
            /* Mobile pagination - keep horizontal and stick to right */
            @media (max-width: 768px) {
                .pagination-container [data-testid="column"]:nth-of-type(3) {
                    flex: 0 0 auto !important;
                    min-width: 40px !important;
                    max-width: 60px !important;
                }
                .pagination-container [data-testid="column"]:nth-of-type(3) button {
                    font-size: 1rem !important;
                    padding: 4px 8px !important;
                    width: 100% !important;
                }
            }
            </style>
        """, unsafe_allow_html=True)
        if st.button("►", disabled=(st.session_state.current_page == total_pages), key=f"next_page_{position}"):
            st.session_state.current_page += 1
            st.rerun()
    
    # Close pagination container
    st.markdown("</div>", unsafe_allow_html=True)
    
    return start_idx, end_idx


# =========================
# SECTORAL YEARLY PERFORMANCE
# =========================
@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour, hide spinner
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
                    
                    # Calculate 52-week high and low
                    week_52_high = hist['High'].max()
                    week_52_low = hist['Low'].min()
                    
                    sectoral_data.append({
                        'Sector': name,
                        'Current Price': end_price,
                        '1 Year Change %': round(year_change, 2),
                        'Start Price': start_price,
                        '52W High': week_52_high,
                        '52W Low': week_52_low
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
                        'Current Price': None,
                        '1 Year Change %': 0,
                        'Start Price': None,
                        '52W High': None,
                        '52W Low': None
                    })
        
        # Longer delay between indices to avoid rate limiting
        time.sleep(0.5)
    
    return sectoral_data


def render_sectoral_yearly_performance():
    """Render comprehensive sectoral indices 1-year performance"""
    
    st.markdown("---")
    st.subheader("📊 Sectoral Indices - 1 Year Performance")
    st.caption("Annual performance comparison across all major sectors")
    
    # Fetch data with caching (no button required - loads automatically)
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
                if data['Current Price'] is None:
                    st.metric(
                        label=data['Sector'],
                        value="--",
                        delta="--"
                    )
                else:
                    # Use same custom HTML box as key indices
                    name = data['Sector']
                    end_price = data['Current Price']
                    year_change = change_pct
                    week_52_high = data['52W High']
                    week_52_low = data['52W Low']
                    
                    # Determine delta styling
                    arrow = "▲" if year_change >= 0 else "▼"
                    delta_class = "positive" if year_change >= 0 else "negative"
                    
                    # Create single unified box with all data
                    st.markdown(f"""
                        <div class="yearly-metric-box">
                            <div class="yearly-metric-label">{name}</div>
                            <div class="yearly-metric-value">{end_price:,.2f}</div>
                            <div class="yearly-metric-delta {delta_class}">{arrow} {abs(year_change):.2f}%</div>
                            <div class="yearly-52w-data">
                                <div>52W High: <span style='color: #00ff00; font-weight: 600;'>{week_52_high:,.2f}</span></div>
                                <div>52W Low: <span style='color: #ff4444; font-weight: 600;'>{week_52_low:,.2f}</span></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Unable to fetch sectoral performance data. Yahoo Finance may be rate limiting. Please wait a few minutes and refresh.")
