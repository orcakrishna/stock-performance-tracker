"""
Utility Functions for NSE Stock Performance Tracker
Helper functions for formatting, coloring, and data processing
"""

from datetime import datetime
import pytz
import streamlit as st
import pandas as pd
import yfinance as yf
from data_fetchers import get_stock_list

# Color constants for consistency
COLOR_GREEN = '#00FFA3'  # Mint green for gains
COLOR_RED = '#FF6B6B'    # Coral red for losses
COLOR_NEUTRAL = '#ffffff'
COLOR_WARNING = '#ffa500'

# Market timing constants (IST, in minutes)
PRE_OPEN_START = 9 * 60      # 9:00 AM
MARKET_OPEN = 9 * 60 + 15     # 9:15 AM
MARKET_CLOSE = 15 * 60 + 30   # 3:30 PM

def color_percentage(val):
    """Color code percentage values for HTML display"""
    try:
        num_val = float(val)
        if num_val > 0:
            return f'<span style="color: {COLOR_GREEN}; font-weight: bold;">+{num_val}%</span>'
        elif num_val < 0:
            return f'<span style="color: {COLOR_RED}; font-weight: bold;">{num_val}%</span>'
        else:
            return f'<span style="color: {COLOR_NEUTRAL};">{num_val}%</span>'
    except:
        return val


def get_current_times():
    """Get current time in IST and EDT timezones"""
    ist = pytz.timezone('Asia/Kolkata')
    edt = pytz.timezone('America/New_York')
    
    current_time_utc = datetime.now(pytz.utc)
    ist_time = current_time_utc.astimezone(ist)
    edt_time = current_time_utc.astimezone(edt)
    
    return ist_time, edt_time


def get_market_session_status():
    """Determine NSE market session status based on IST time"""
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(pytz.utc).astimezone(ist)
    
    # Check if weekend
    weekday = current_time.weekday()  # 0 = Monday, 6 = Sunday
    if weekday >= 5:  # Saturday or Sunday
        return "🔴 Market Closed (Weekend)", COLOR_RED
    
    current_hour = current_time.hour
    current_minute = current_time.minute
    current_time_mins = current_hour * 60 + current_minute
    
    # Use constants for market timings
    if current_time_mins < PRE_OPEN_START:
        return "🔴 Market Closed", COLOR_RED
    elif PRE_OPEN_START <= current_time_mins < MARKET_OPEN:
        return "🟡 Pre-Open Session", COLOR_WARNING
    elif MARKET_OPEN <= current_time_mins < MARKET_CLOSE:
        return "🟢 Market Open (Live)", COLOR_GREEN
    else:
        return "🔴 Market Closed", COLOR_RED


def format_time_display(ist_time, edt_time, commodities_prices, next_holiday=None):
    """Format time and commodities display for header with arrows and colors - no style tags"""
    # Determine USD/INR color based on change
    usd_inr_change = commodities_prices.get('usd_inr_change', 0)
    if usd_inr_change > 0:
        usd_inr_color = COLOR_RED  # Red - INR weakened
    elif usd_inr_change < 0:
        usd_inr_color = COLOR_GREEN  # Green - INR strengthened
    else:
        usd_inr_color = COLOR_NEUTRAL  # Neutral
    
    # Get commodity data with defaults
    oil_price = commodities_prices.get('oil', '--')
    oil_change = commodities_prices.get('oil_change', 0)
    oil_arrow = '▲' if oil_change >= 0 else '▼'
    oil_color = COLOR_GREEN if oil_change >= 0 else COLOR_RED
    oil_change_display = f"{oil_arrow} {abs(oil_change):.2f}%" if oil_change != 0 else '-'
    
    eth_price = commodities_prices.get('ethereum', '--')
    eth_change = commodities_prices.get('ethereum_change', 0)
    eth_arrow = '▲' if eth_change >= 0 else '▼'
    eth_color = COLOR_GREEN if eth_change >= 0 else COLOR_RED
    eth_change_display = f"{eth_arrow} {abs(eth_change):.2f}%" if eth_change != 0 else '-'
    
    btc_price = commodities_prices.get('btc', '--')
    btc_change = commodities_prices.get('btc_change', 0)
    btc_arrow = '▲' if btc_change >= 0 else '▼'
    btc_color = COLOR_GREEN if btc_change >= 0 else COLOR_RED
    btc_change_display = f"{btc_arrow} {abs(btc_change):.2f}%" if btc_change != 0 else '-'
    
    gold_price = commodities_prices.get('gold', '--')
    gold_inr = commodities_prices.get('gold_inr', '--')
    gold_change = commodities_prices.get('gold_change', 0)
    gold_arrow = '▲' if gold_change >= 0 else '▼'
    gold_color = COLOR_GREEN if gold_change >= 0 else COLOR_RED
    gold_change_display = f"{gold_arrow} {abs(gold_change):.2f}%" if gold_change != 0 else '-'
    
    silver_price = commodities_prices.get('silver', '--')
    silver_inr = commodities_prices.get('silver_inr', '--')
    silver_change = commodities_prices.get('silver_change', 0)
    silver_arrow = '▲' if silver_change >= 0 else '▼'
    silver_color = COLOR_GREEN if silver_change >= 0 else COLOR_RED
    silver_change_display = f"{silver_arrow} {abs(silver_change):.2f}%" if silver_change != 0 else '-'
    
    usd_inr = commodities_prices.get('usd_inr', '--')
    usd_inr_change_raw = commodities_prices.get('usd_inr_change', 0)
    
    # CRITICAL FIX: Calculate USD/INR today's percentage change correctly
    # usd_inr_change_raw is absolute change (e.g., +0.90)
    # Formula: (change / previous_value) * 100
    if usd_inr_change_raw != 0 and usd_inr != '--':
        try:
            current_value = float(usd_inr.replace('₹', ''))
            previous_value = current_value - usd_inr_change_raw
            
            if previous_value > 0:
                usd_inr_change_pct = (usd_inr_change_raw / previous_value) * 100
                usd_inr_arrow = '▲' if usd_inr_change_pct >= 0 else '▼'
                # Red=INR weakened (USD up), Green=INR strengthened (USD down)
                usd_inr_today_color = COLOR_RED if usd_inr_change_pct >= 0 else COLOR_GREEN
                usd_inr_today_display = f"<span style='color: {usd_inr_today_color}; font-weight: bold;'>{usd_inr_arrow} {abs(usd_inr_change_pct):.2f}%</span>"
            else:
                usd_inr_today_display = '-'
        except Exception as e:
            print(f"Error calculating USD/INR change: {e}")
            usd_inr_today_display = '-'
    else:
        usd_inr_today_display = '-'
    
    # Build USD/INR and Holiday line
    holiday_text = ""
    if next_holiday:
        holiday_text = f" | 🏖️ NSE Holiday: <span style='color: #ff4444; font-weight: bold;'>{next_holiday}</span>"
    
    # Get 1-week changes
    oil_week = commodities_prices.get('oil_week_change', 0)
    eth_week = commodities_prices.get('ethereum_week_change', 0)
    gold_week = commodities_prices.get('gold_week_change', 0)
    silver_week = commodities_prices.get('silver_week_change', 0)
    btc_week = commodities_prices.get('btc_week_change', 0)
    usd_inr_week = commodities_prices.get('usd_inr_week_change', 0)
    
    # Helper function to create triangle with percentage (matching Today column style)
    def week_change_html(week_change):
        if week_change == 0:
            return '-'
        color = COLOR_GREEN if week_change >= 0 else COLOR_RED
        triangle = '▲' if week_change >= 0 else '▼'
        return f"<span style='color: {color}; font-weight: bold;'>{triangle} {abs(week_change):.2f}%</span>"
    
    # Return as table format with INR in brackets and 1W change column
    return f"""<table style='width: 100%; font-size: 0.875rem; border-collapse: collapse;'>
        <thead>
            <tr style='border-bottom: 1px solid rgba(66, 165, 245, 0.3);'>
                <th style='text-align: left; padding: 0.2rem 0.5rem; color: #42a5f5; font-weight: 600; font-size: 0.8rem;'>Commodity</th>
                <th style='text-align: right; padding: 0.2rem 0.5rem; color: #42a5f5; font-weight: 600; font-size: 0.8rem;'>Price</th>
                <th style='text-align: right; padding: 0.2rem 0.5rem; color: #42a5f5; font-weight: 600; font-size: 0.8rem;'>Today</th>
                <th style='text-align: right; padding: 0.2rem 0.5rem; color: #42a5f5; font-weight: 600; font-size: 0.8rem;'>1W</th>
            </tr>
        </thead>
        <tbody>
            <tr style='border-bottom: 1px solid rgba(255, 255, 255, 0.1);'>
                <td style='padding: 0.4rem 0.5rem; color: #ffffff; font-weight: 600;'>🛢️ Oil</td>
                <td style='padding: 0.4rem 0.5rem; text-align: right;'>{oil_price}</td>
                <td style='padding: 0.4rem 0.5rem; text-align: right;'><span style='color: {oil_color}; font-weight: bold;'>{oil_change_display}</span></td>
                <td style='padding: 0.4rem 0.5rem; text-align: right;'>{week_change_html(oil_week)}</td>
            </tr>
            <tr style='border-bottom: 1px solid rgba(255, 255, 255, 0.1);'>
                <td style='padding: 0.4rem 0.5rem; color: #ffffff; font-weight: 600;'>🥇 Gold</td>
                <td style='padding: 0.4rem 0.5rem; text-align: right;'>{gold_price} <span style='color: #888; font-size: 0.75rem;'>({gold_inr})</span></td>
                <td style='padding: 0.4rem 0.5rem; text-align: right;'><span style='color: {gold_color}; font-weight: bold;'>{gold_change_display}</span></td>
                <td style='padding: 0.4rem 0.5rem; text-align: right;'>{week_change_html(gold_week)}</td>
            </tr>
            <tr style='border-bottom: 1px solid rgba(255, 255, 255, 0.1);'>
                <td style='padding: 0.4rem 0.5rem; color: #ffffff; font-weight: 600;'>🪙 Silver</td>
                <td style='padding: 0.4rem 0.5rem; text-align: right;'>{silver_price} <span style='color: #888; font-size: 0.75rem;'>({silver_inr})</span></td>
                <td style='padding: 0.4rem 0.5rem; text-align: right;'><span style='color: {silver_color}; font-weight: bold;'>{silver_change_display}</span></td>
                <td style='padding: 0.4rem 0.5rem; text-align: right;'>{week_change_html(silver_week)}</td>
            </tr>
            <tr style='border-bottom: 1px solid rgba(255, 255, 255, 0.1);'>
                <td style='padding: 0.4rem 0.5rem; color: #ffffff; font-weight: 600;'>🪙 Ethereum</td>
                <td style='padding: 0.4rem 0.5rem; text-align: right;'>{eth_price}</td>
                <td style='padding: 0.4rem 0.5rem; text-align: right;'><span style='color: {eth_color}; font-weight: bold;'>{eth_change_display}</span></td>
                <td style='padding: 0.4rem 0.5rem; text-align: right;'>{week_change_html(eth_week)}</td>
            </tr>
            <tr style='border-bottom: 1px solid rgba(255, 255, 255, 0.1);'>
                <td style='padding: 0.4rem 0.5rem; color: #ffffff; font-weight: 600;'>₿ BTC</td>
                <td style='padding: 0.4rem 0.5rem; text-align: right;'>{btc_price}</td>
                <td style='padding: 0.4rem 0.5rem; text-align: right;'><span style='color: {btc_color}; font-weight: bold;'>{btc_change_display}</span></td>
                <td style='padding: 0.4rem 0.5rem; text-align: right;'>{week_change_html(btc_week)}</td>
            </tr>
            <tr>
                <td style='padding: 0.4rem 0.5rem; color: #ffffff; font-weight: 600;'>💵 USD/INR</td>
                <td style='padding: 0.4rem 0.5rem; text-align: right;'>{usd_inr}</td>
                <td style='padding: 0.4rem 0.5rem; text-align: right;'>{usd_inr_today_display}</td>
                <td style='padding: 0.4rem 0.5rem; text-align: right;'>{week_change_html(usd_inr_week)}</td>
            </tr>
        </tbody>
        <tfoot>
            <tr style='border-top: 1px solid rgba(66, 165, 245, 0.3);'>
                <td colspan='4' style='padding: 0.5rem; text-align: center; color: #ffffff; font-size: 0.875rem; font-weight: 500;'>
                    🕐 IST: <span style='color: #42a5f5; font-weight: 600;'>{ist_time.strftime('%I:%M %p')}</span> | EDT: <span style='color: #42a5f5; font-weight: 600;'>{edt_time.strftime('%I:%M %p')}</span> | 📅 <span style='color: #42a5f5; font-weight: 600;'>{ist_time.strftime('%d %b %Y')}</span>{holiday_text}
                </td>
            </tr>
        </tfoot>
    </table>"""


def create_sparkline_svg(sparkline_data, today_change, stock_symbol, width=80, height=30):
    """Create an SVG sparkline from price data with auto-normalization and color based on today's performance"""
    if not sparkline_data or len(sparkline_data) < 2:
        return ""
    
    # CRITICAL FIX: Normalize data to 0-100 range
    min_val = min(sparkline_data)
    max_val = max(sparkline_data)
    range_val = max_val - min_val
    
    if range_val == 0:
        # Flat line - all values same
        normalized = [50] * len(sparkline_data)
    else:
        # Normalize to 0-100
        normalized = [(val - min_val) / range_val * 100 for val in sparkline_data]
    
    # Create SVG path
    points = []
    step = width / (len(normalized) - 1)
    
    for i, value in enumerate(normalized):
        x = i * step
        # Invert Y axis (SVG coordinates start from top)
        y = height - (value / 100 * height)
        points.append(f"{x:.2f},{y:.2f}")
    
    path_data = "M " + " L ".join(points)
    
    # Determine color based on today's performance (Today % column)
    try:
        today_pct = float(today_change)
        color = COLOR_GREEN if today_pct >= 0 else COLOR_RED
    except:
        # Fallback to trend-based color if today_change is invalid
        color = COLOR_GREEN if sparkline_data[-1] >= sparkline_data[0] else COLOR_RED
    
    # Create clickable SVG with direct link
    tradingview_url = f"https://www.tradingview.com/chart/?symbol=NSE:{stock_symbol}"
    
    svg = f'''<a href="{tradingview_url}" target="_blank" style="text-decoration: none;">
        <svg width="{width}" height="{height}" style="display: block; cursor: pointer;" 
             onmouseover="this.style.opacity='0.7'" 
             onmouseout="this.style.opacity='1'">
            <path d="{path_data}" fill="none" stroke="{color}" stroke-width="2" />
        </svg>
    </a>'''
    
    return svg


def create_html_table(df_page):
    """Create HTML table with colored percentage values and mini charts"""
    
    html_table = ''
    html_table += '''<div style="overflow-x: auto; -webkit-overflow-scrolling: touch;">
    <table style="width:100%; border-collapse: collapse; background-color: #2d2d2d; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">'''
    html_table += '<thead><tr style="background-color: #3d3d3d;">'
    
    # Add "Chart" column header after "Stock Name"
    for col in df_page.columns:
        if col != 'sparkline_data':  # Skip the raw data column
            html_table += f'<th style="padding: 12px; text-align: left; border: 1px solid #555; color: #ffffff; font-weight: bold; font-size: 14px;">{col}</th>'
            if col == 'Stock Name':
                html_table += '<th style="padding: 12px; text-align: center; border: 1px solid #555; color: #ffffff; font-weight: bold; font-size: 14px;">Chart</th>'
    
    html_table += '</tr></thead><tbody>'
    
    for _, row in df_page.iterrows():
        html_table += '<tr>'
        stock_symbol = row.get('Stock Name', '')
        sparkline_data = row.get('sparkline_data', [])
        today_change = row.get('Today %', 0)  # Get today's performance for color
        
        for col in df_page.columns:
            if col == 'sparkline_data':
                continue  # Skip the raw data column
                
            value = row[col]
            
            if col in ['Today %', '1 Week %', '1 Month %', '2 Months %', '3 Months %']:
                colored_value = color_percentage(value)
                html_table += f'<td style="padding: 12px; border: 1px solid #555; color: #ffffff; font-size: 14px;">{colored_value}</td>'
            else:
                html_table += f'<td style="padding: 12px; border: 1px solid #555; color: #ffffff; font-size: 14px;">{value}</td>'
            
            # Add sparkline cell after Stock Name
            if col == 'Stock Name':
                sparkline_svg = create_sparkline_svg(sparkline_data, today_change, stock_symbol)
                html_table += f'''<td style="text-align: center; padding: 12px; border: 1px solid #555;">
                    {sparkline_svg}
                </td>'''
        
        html_table += '</tr>'
    
    html_table += '</tbody></table></div>'
    return html_table


def _is_market_open():
    """Check if market is currently open (weekday + trading hours)"""
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(pytz.utc).astimezone(ist)
    
    # Check if weekend
    weekday = current_time.weekday()
    if weekday >= 5:  # Saturday or Sunday
        return False
    
    current_hour = current_time.hour
    current_minute = current_time.minute
    current_time_mins = current_hour * 60 + current_minute
    
    # Market timings (IST): use constants
    return MARKET_OPEN <= current_time_mins < MARKET_CLOSE


@st.cache_data(ttl=3600, show_spinner=False)  # Default 1-hour cache for closed market
def _get_ticker_data_closed():
    """Fetch ticker data when market is closed (cached for 1 hour)"""
    return _fetch_ticker_data_internal()


@st.cache_data(ttl=90, show_spinner=False)  # 90-second cache for open market (optimized)
def _get_ticker_data_open():
    """Fetch ticker data when market is open (cached for 90 seconds)"""
    return _fetch_ticker_data_internal()


def _fetch_ticker_data_internal():
    """Internal function to fetch ticker data using bulk download for speed"""
    ticker_data = []
    
    # Get Nifty 50 stocks dynamically
    nifty_50_stocks, _ = get_stock_list('Nifty 50')
    
    # If no stocks fetched, return empty list
    if not nifty_50_stocks:
        return []
    
    stocks_to_fetch = nifty_50_stocks[:50]  # Limit to 50 for ticker
    
    try:
        # Use bulk download for much faster fetching (10-50x speedup)
        data = yf.download(
            tickers=stocks_to_fetch,
            period='2d',
            interval='1d',
            group_by='ticker',
            progress=False,
            auto_adjust=True,
            threads=True
        )
        
        if data.empty:
            return []
        
        is_multi = isinstance(data.columns, pd.MultiIndex)
        
        for symbol in stocks_to_fetch:
            try:
                if is_multi and len(stocks_to_fetch) > 1:
                    close_series = data[(symbol, 'Close')].dropna()
                else:
                    close_series = data['Close'].dropna() if 'Close' in data.columns else pd.Series()
                
                if close_series.empty:
                    continue
                
                if len(close_series) >= 2:
                    current_price = float(close_series.iloc[-1])
                    prev_close = float(close_series.iloc[-2])
                    change_pct = ((current_price - prev_close) / prev_close) * 100
                elif len(close_series) == 1:
                    # Try to get open price for single-day data
                    if is_multi and len(stocks_to_fetch) > 1:
                        open_series = data[(symbol, 'Open')].dropna()
                    else:
                        open_series = data['Open'].dropna() if 'Open' in data.columns else pd.Series()
                    
                    if not open_series.empty:
                        current_price = float(close_series.iloc[-1])
                        open_price = float(open_series.iloc[-1])
                        if open_price > 0:
                            change_pct = ((current_price - open_price) / open_price) * 100
                        else:
                            continue
                    else:
                        continue
                else:
                    continue
                
                ticker_data.append({
                    'symbol': symbol.replace('.NS', '').replace('.BO', ''),
                    'price': current_price,
                    'change': change_pct
                })
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                continue
    
    except Exception as e:
        print(f"Bulk ticker fetch failed: {e}")
        # Fallback to sequential if bulk fails
        return _fetch_ticker_data_fallback(stocks_to_fetch)
    
    market_status = "open" if _is_market_open() else "closed"
    print(f"📊 Ticker: Fetched {len(ticker_data)}/{len(stocks_to_fetch)} stocks (market: {market_status})")
    return ticker_data


def _fetch_ticker_data_fallback(stocks_to_fetch):
    """Fallback method using individual calls with limited workers"""
    ticker_data = []
    
    def fetch_symbol_data(symbol):
        try:
            ticker = yf.Ticker(symbol)
            fast_info = getattr(ticker, 'fast_info', None)
            
            if fast_info:
                current_price = getattr(fast_info, 'last_price', None)
                prev_close = getattr(fast_info, 'previous_close', None)
                
                if current_price and prev_close and prev_close > 0:
                    change_pct = ((current_price - prev_close) / prev_close) * 100
                    return {
                        'symbol': symbol.replace('.NS', '').replace('.BO', ''),
                        'price': float(current_price),
                        'change': float(change_pct)
                    }
            
            # Fallback to history
            hist = ticker.history(period='2d')
            if len(hist) >= 2:
                current_price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                change_pct = ((current_price - prev_close) / prev_close) * 100
                return {
                    'symbol': symbol.replace('.NS', '').replace('.BO', ''),
                    'price': float(current_price),
                    'change': float(change_pct)
                }
        except Exception:
            pass
        return None
    
    from concurrent.futures import ThreadPoolExecutor, as_completed
    max_workers = min(4, len(stocks_to_fetch))  # Limit to 4 workers to avoid rate limits
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_symbol_data, symbol): symbol for symbol in stocks_to_fetch}
        for future in as_completed(futures):
            result = future.result()
            if result:
                ticker_data.append(result)
    
    return ticker_data


def get_ticker_data():
    """Fetch live data for ticker stocks with dynamic caching based on market status"""
    if _is_market_open():
        # Market is open: use 60-second cache for live updates
        return _get_ticker_data_open()
    else:
        # Market is closed (weekend/holiday/after-hours): use 1-hour cache
        return _get_ticker_data_closed()
