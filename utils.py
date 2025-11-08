"""
Utility Functions for NSE Stock Performance Tracker
Helper functions for formatting, coloring, and data processing
"""

from datetime import datetime
import pytz
import streamlit as st
import yfinance as yf
from data_fetchers import get_stock_list


def color_percentage(val):
    """Color code percentage values for HTML display"""
    try:
        num_val = float(val)
        if num_val > 0:
            return f'<span style="color: #00ff00; font-weight: bold;">+{num_val}%</span>'
        elif num_val < 0:
            return f'<span style="color: #ff4444; font-weight: bold;">{num_val}%</span>'
        else:
            return f'<span style="color: #ffffff;">{num_val}%</span>'
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
        return "🔴 Market Closed (Weekend)", "#ff4444"
    
    current_hour = current_time.hour
    current_minute = current_time.minute
    current_time_mins = current_hour * 60 + current_minute
    
    # Market timings (IST)
    pre_open_start = 9 * 60 + 0  # 9:00 AM
    market_open = 9 * 60 + 15    # 9:15 AM
    market_close = 15 * 60 + 30  # 3:30 PM
    
    if current_time_mins < pre_open_start:
        return "🔴 Market Closed", "#ff4444"
    elif pre_open_start <= current_time_mins < market_open:
        return "🟡 Pre-Open Session", "#ffa500"
    elif market_open <= current_time_mins < market_close:
        return "🟢 Market Open (Live)", "#00ff00"
    else:
        return "🔴 Market Closed", "#ff4444"


def format_time_display(ist_time, edt_time, commodities_prices, next_holiday=None):
    """Format time and commodities display for header with arrows and colors - no style tags"""
    # Determine USD/INR color based on change
    usd_inr_change = commodities_prices.get('usd_inr_change', 0)
    if usd_inr_change > 0:
        usd_inr_color = '#ff4444'  # Red - INR weakened
    elif usd_inr_change < 0:
        usd_inr_color = '#00ff00'  # Green - INR strengthened
    else:
        usd_inr_color = '#95e1d3'  # Neutral
    
    # Get commodity data with defaults
    oil_price = commodities_prices.get('oil', '--')
    oil_change = commodities_prices.get('oil_change', 0)
    oil_arrow = '▲' if oil_change >= 0 else '▼'
    oil_color = '#00ff00' if oil_change >= 0 else '#ff4444'
    oil_change_display = f"{oil_arrow} {abs(oil_change):.2f}%" if oil_change != 0 else '-'
    
    eth_price = commodities_prices.get('ethereum', '--')
    eth_change = commodities_prices.get('ethereum_change', 0)
    eth_arrow = '▲' if eth_change >= 0 else '▼'
    eth_color = '#00ff00' if eth_change >= 0 else '#ff4444'
    eth_change_display = f"{eth_arrow} {abs(eth_change):.2f}%" if eth_change != 0 else '-'
    
    btc_price = commodities_prices.get('btc', '--')
    btc_change = commodities_prices.get('btc_change', 0)
    btc_arrow = '▲' if btc_change >= 0 else '▼'
    btc_color = '#00ff00' if btc_change >= 0 else '#ff4444'
    btc_change_display = f"{btc_arrow} {abs(btc_change):.2f}%" if btc_change != 0 else '-'
    
    gold_price = commodities_prices.get('gold', '--')
    gold_inr = commodities_prices.get('gold_inr', '--')
    gold_change = commodities_prices.get('gold_change', 0)
    gold_arrow = '▲' if gold_change >= 0 else '▼'
    gold_color = '#00ff00' if gold_change >= 0 else '#ff4444'
    gold_change_display = f"{gold_arrow} {abs(gold_change):.2f}%" if gold_change != 0 else '-'
    
    silver_price = commodities_prices.get('silver', '--')
    silver_inr = commodities_prices.get('silver_inr', '--')
    silver_change = commodities_prices.get('silver_change', 0)
    silver_arrow = '▲' if silver_change >= 0 else '▼'
    silver_color = '#00ff00' if silver_change >= 0 else '#ff4444'
    silver_change_display = f"{silver_arrow} {abs(silver_change):.2f}%" if silver_change != 0 else '-'
    
    usd_inr = commodities_prices.get('usd_inr', '--')
    usd_inr_change_raw = commodities_prices.get('usd_inr_change', 0)
    
    # Calculate USD/INR today's percentage change
    if usd_inr_change_raw != 0 and usd_inr != '--':
        try:
            current_value = float(usd_inr.replace('₹', ''))
            usd_inr_change_pct = (usd_inr_change_raw / (current_value - usd_inr_change_raw)) * 100
            usd_inr_arrow = '▲' if usd_inr_change_pct >= 0 else '▼'
            usd_inr_today_color = '#ff4444' if usd_inr_change_pct >= 0 else '#00ff00'  # Red=INR weakened, Green=INR strengthened
            usd_inr_today_display = f"<span style='color: {usd_inr_today_color}; font-weight: bold;'>{usd_inr_arrow} {abs(usd_inr_change_pct):.2f}%</span>"
        except:
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
        color = '#00ff00' if week_change >= 0 else '#ff4444'
        triangle = '▲' if week_change >= 0 else '▼'
        return f"<span style='color: {color}; font-weight: bold;'>{triangle} {abs(week_change):.2f}%</span>"
    
    # Return as table format with INR in brackets and 1W change column
    return f"""<table style='width: 100%; font-size: 0.875rem; border-collapse: collapse;'>
        <thead>
            <tr style='border-bottom: 1px solid rgba(66, 165, 245, 0.3);'>
                <th style='text-align: left; padding: 0.3rem 0.5rem; color: #42a5f5; font-weight: 600;'>Commodity</th>
                <th style='text-align: right; padding: 0.3rem 0.5rem; color: #42a5f5; font-weight: 600;'>Price</th>
                <th style='text-align: right; padding: 0.3rem 0.5rem; color: #42a5f5; font-weight: 600;'>Today</th>
                <th style='text-align: right; padding: 0.3rem 0.5rem; color: #42a5f5; font-weight: 600;'>1W</th>
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
    """Create an SVG sparkline from normalized data with color based on today's performance"""
    if not sparkline_data or len(sparkline_data) < 2:
        return ""
    
    # Create SVG path
    points = []
    step = width / (len(sparkline_data) - 1)
    
    for i, value in enumerate(sparkline_data):
        x = i * step
        # Invert Y axis (SVG coordinates start from top)
        y = height - (value / 100 * height)
        points.append(f"{x:.2f},{y:.2f}")
    
    path_data = "M " + " L ".join(points)
    
    # Determine color based on today's performance (Today % column)
    try:
        today_pct = float(today_change)
        color = "#00ff00" if today_pct >= 0 else "#ff4444"
    except:
        # Fallback to trend-based color if today_change is invalid
        color = "#00ff00" if sparkline_data[-1] >= sparkline_data[0] else "#ff4444"
    
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


@st.cache_data(ttl=60)  # Cache for 60 seconds
def get_ticker_data():
    """Fetch live data for ticker stocks"""
    ticker_data = []
    
    # Get Nifty 50 stocks dynamically
    nifty_50_stocks, _ = get_stock_list('Nifty 50')
    
    # If no stocks fetched, return empty list
    if not nifty_50_stocks:
        return []
    
    stocks_to_fetch = nifty_50_stocks
    
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
