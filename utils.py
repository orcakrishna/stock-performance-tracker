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


def format_time_display(ist_time, edt_time, commodities_prices, next_holiday=None):
    """Format time and commodities display for header with arrows and colors"""
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
    oil_arrow = commodities_prices.get('oil_arrow', '')
    oil_color = commodities_prices.get('oil_color', '#ffffff')
    
    btc_price = commodities_prices.get('btc', '--')
    btc_arrow = commodities_prices.get('btc_arrow', '')
    btc_color = commodities_prices.get('btc_color', '#ffffff')
    # Add space before arrow if it exists
    btc_display = f"{btc_price} {btc_arrow}" if btc_arrow else btc_price
    
    gold_price = commodities_prices.get('gold', '--')
    gold_inr = commodities_prices.get('gold_inr', '--')
    gold_arrow = commodities_prices.get('gold_arrow', '')
    gold_color = commodities_prices.get('gold_color', '#ffffff')
    
    silver_price = commodities_prices.get('silver', '--')
    silver_inr = commodities_prices.get('silver_inr', '--')
    silver_arrow = commodities_prices.get('silver_arrow', '')
    silver_color = commodities_prices.get('silver_color', '#ffffff')
    
    usd_inr = commodities_prices.get('usd_inr', '--')
    
    # Build USD/INR and Holiday line
    holiday_text = ""
    if next_holiday:
        holiday_text = f" | <span style='color: #fff; font-weight: bold;'>🏖️ Holiday:</span> <span style='color: #ff4444; font-weight: bold;'>{next_holiday}</span>"
    
    return f"""
    <div style='text-align: right; padding-top: 20px;'>
    </br>
        <p style='margin: 0; font-size: 13px;'>
            <span style='color: #fff; font-weight: bold;'>🛢️ Oil:</span> 
            <span style='color: {oil_color}; font-weight: bold;'>{oil_price} {oil_arrow}</span> | 
            <span style='color: #fff; font-weight: bold;'>₿ BTC:</span> 
            <span style='color: {btc_color}; font-weight: bold;'>{btc_display}</span> | 
            <span style='color: #fff; font-weight: bold;'>🕐 IST:</span> 
            <span style='color: #fff; font-weight: bold;'>{ist_time.strftime('%I:%M %p')}</span>
        </p>
        <p style='margin: 0; font-size: 13px;'>
            <span style='color: #fff; font-weight: bold;'>🥇 Gold:</span> 
            <span style='color: {gold_color}; font-weight: bold;'>{gold_price} {gold_arrow}</span>
            <span style='color: #ffd700; font-weight: normal;'> ({gold_inr})</span> | 
            <span style='color: #fff; font-weight: bold;'>🕐 EDT:</span> 
            <span style='color: #fff; font-weight: bold;'>{edt_time.strftime('%I:%M %p')}</span>
        </p>
        <p style='margin: 0; font-size: 13px;'>
            <span style='color: #fff; font-weight: bold;'>🪙 Silver:</span> 
            <span style='color: {silver_color}; font-weight: bold;'>{silver_price} {silver_arrow}</span>
            <span style='color: #c0c0c0; font-weight: normal;'> ({silver_inr})</span> | 
            <span style='color: #fff; font-weight: bold;'>📅</span> 
            <span style='color: #fff; font-weight: bold;'>{ist_time.strftime('%d %b %Y')}</span>
        </p>
        <p style='margin: 0; font-size: 13px;'>
            <span style='color: #fff; font-weight: bold;'>💵 USD/INR:</span> 
            <span style='color: {usd_inr_color}; font-weight: bold;'>{usd_inr}</span>{holiday_text}
        </p>
    </div>
    """


def create_sparkline_svg(sparkline_data, today_change, width=80, height=30):
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
    
    svg = f'''<svg width="{width}" height="{height}" style="display: block;">
        <path d="{path_data}" fill="none" stroke="{color}" stroke-width="1.5" />
    </svg>'''
    
    return svg


def create_html_table(df_page):
    """Create HTML table with colored percentage values and mini charts"""
    
    # Add CSS and JavaScript for TradingView popup
    html_styles = '''
    <style>
        .sparkline-cell {
            cursor: pointer;
            position: relative;
            padding: 12px;
            border: 1px solid #555;
        }
        .sparkline-cell:hover {
            background-color: #3d3d3d;
        }
        .tradingview-popup {
            display: none;
            position: fixed !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
            width: 800px !important;
            height: 600px !important;
            background-color: #1e1e1e !important;
            border: 2px solid #00ff88 !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 20px rgba(0, 255, 136, 0.3) !important;
            z-index: 999999 !important;
            padding: 10px !important;
        }
        .tradingview-popup.active {
            display: block;
        }
        .popup-overlay {
            display: none;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: 100% !important;
            background-color: rgba(0, 0, 0, 0.7) !important;
            z-index: 999998 !important;
        }
        .popup-overlay.active {
            display: block;
        }
        .popup-close {
            position: absolute;
            top: 10px;
            right: 10px;
            background-color: #ff4444;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px 10px;
            cursor: pointer;
            font-weight: bold;
            z-index: 10001;
        }
        .popup-close:hover {
            background-color: #ff6666;
        }
    </style>
    '''
    
    html_script = '''
    <script>
        let hoverTimeout = null;
        let isPopupOpen = false;
        
        function showTradingViewPopup(symbol, event) {
            // Clear any existing timeout
            if (hoverTimeout) {
                clearTimeout(hoverTimeout);
            }
            
            // Add delay to prevent accidental triggers
            hoverTimeout = setTimeout(() => {
                // Create overlay
                let overlay = document.getElementById('tradingview-overlay');
                if (!overlay) {
                    overlay = document.createElement('div');
                    overlay.id = 'tradingview-overlay';
                    overlay.className = 'popup-overlay';
                    overlay.onclick = closeTradingViewPopup;
                    document.body.appendChild(overlay);
                }
                
                // Create popup
                let popup = document.getElementById('tradingview-popup');
                if (!popup) {
                    popup = document.createElement('div');
                    popup.id = 'tradingview-popup';
                    popup.className = 'tradingview-popup';
                    document.body.appendChild(popup);
                }
                
                // Add close button and message with link
                popup.innerHTML = \`
                    <button class="popup-close" onclick="closeTradingViewPopup()">✕ Close</button>
                    <div style="text-align: center; padding: 40px; color: white;">
                        <h2 style="color: #00ff88; margin-bottom: 20px;">📊 \${symbol}</h2>
                        <p style="font-size: 18px; margin-bottom: 30px;">Click the chart to view full TradingView analysis</p>
                        <button 
                            onclick="openTradingViewChart('\${symbol}', event); closeTradingViewPopup();"
                            style="background: linear-gradient(135deg, #00ff88 0%, #00cc70 100%); 
                                   color: #000; 
                                   border: none; 
                                   padding: 15px 40px; 
                                   font-size: 16px; 
                                   font-weight: bold; 
                                   border-radius: 8px; 
                                   cursor: pointer;
                                   box-shadow: 0 4px 15px rgba(0, 255, 136, 0.3);">
                            🚀 Open TradingView Chart
                        </button>
                        <p style="font-size: 14px; margin-top: 30px; color: #888;">
                            Or simply click anywhere on the sparkline
                        </p>
                    </div>
                \`;
                
                // Show popup and overlay
                overlay.classList.add('active');
                popup.classList.add('active');
                isPopupOpen = true;
            }, 500); // 500ms delay before showing popup
        }
        
        function hidePopupOnMouseLeave() {
            // Clear timeout if mouse leaves before popup shows
            if (hoverTimeout) {
                clearTimeout(hoverTimeout);
                hoverTimeout = null;
            }
        }
        
        function closeTradingViewPopup() {
            const overlay = document.getElementById('tradingview-overlay');
            const popup = document.getElementById('tradingview-popup');
            if (overlay) overlay.classList.remove('active');
            if (popup) popup.classList.remove('active');
            isPopupOpen = false;
            
            // Clear any pending timeout
            if (hoverTimeout) {
                clearTimeout(hoverTimeout);
                hoverTimeout = null;
            }
        }
        
        function openTradingViewChart(symbol, event) {
            console.log('Click detected on chart for symbol:', symbol);
            
            // Prevent event bubbling
            if (event) {
                event.stopPropagation();
                event.preventDefault();
            }
            
            // Close popup if open
            if (isPopupOpen) {
                console.log('Closing popup before opening new tab');
                closeTradingViewPopup();
            }
            
            // Clear any pending hover timeout
            if (hoverTimeout) {
                clearTimeout(hoverTimeout);
                hoverTimeout = null;
            }
            
            // Open in new tab
            const url = `https://www.tradingview.com/chart/?symbol=NSE:${symbol}`;
            console.log('Opening URL:', url);
            const newWindow = window.open(url, '_blank');
            
            if (!newWindow) {
                console.error('Popup blocked! Please allow popups for this site.');
                alert('Please allow popups to open TradingView charts');
            } else {
                console.log('Successfully opened new tab');
            }
        }
    </script>
    '''
    
    html_table = html_styles + html_script
    html_table += '<table style="width:100%; border-collapse: collapse; background-color: #2d2d2d;">'
    html_table += '<thead><tr style="background-color: #3d3d3d;">'
    
    # Add "Chart" column header after "Stock Name"
    for col in df_page.columns:
        if col != 'sparkline_data':  # Skip the raw data column
            html_table += f'<th style="padding: 12px; text-align: left; border: 1px solid #555; color: #ffffff; font-weight: bold;">{col}</th>'
            if col == 'Stock Name':
                html_table += '<th style="padding: 12px; text-align: center; border: 1px solid #555; color: #ffffff; font-weight: bold;">Chart</th>'
    
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
                html_table += f'<td style="padding: 12px; border: 1px solid #555; color: #ffffff;">{colored_value}</td>'
            else:
                html_table += f'<td style="padding: 12px; border: 1px solid #555; color: #ffffff;">{value}</td>'
            
            # Add sparkline cell after Stock Name
            if col == 'Stock Name':
                sparkline_svg = create_sparkline_svg(sparkline_data, today_change)
                html_table += f'''<td class="sparkline-cell" 
                    onmouseover="showTradingViewPopup('{stock_symbol}', event)" 
                    onmouseleave="hidePopupOnMouseLeave()"
                    onclick="openTradingViewChart('{stock_symbol}', event)"
                    title="Click to open TradingView chart in new tab"
                    style="text-align: center; padding: 12px; border: 1px solid #555;">
                    {sparkline_svg}
                </td>'''
        
        html_table += '</tr>'
    
    html_table += '</tbody></table>'
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
