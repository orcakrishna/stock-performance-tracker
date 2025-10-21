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
    """Format time and commodities display for header"""
    holiday_line = ""
    if next_holiday:
        holiday_line = f"<p style='margin: 0; font-size: 13px;'><span style='color: #fff; font-weight: bold;'>🏖️ Nifty Holiday:</span> <span style='color: #ff4444; font-weight: bold;'>{next_holiday}</span></p>"
    
    # Determine USD/INR color based on change
    # Positive change = INR weakened (bad) = Red
    # Negative change = INR strengthened (good) = Green
    usd_inr_change = commodities_prices.get('usd_inr_change', 0)
    if usd_inr_change > 0:
        usd_inr_color = '#ff4444'  # Red - INR weakened
    elif usd_inr_change < 0:
        usd_inr_color = '#00ff00'  # Green - INR strengthened
    else:
        usd_inr_color = '#95e1d3'  # Neutral - Mint green
    
    return f"""
    <div style='text-align: right; padding-top: 20px;'>
    </br>
        <p style='margin: 0; font-size: 13px;'><span style='color: #fff; font-weight: bold;'>🛢️ Oil:</span> <span style='color: #ff6b6b; font-weight: bold;'>{commodities_prices['oil']}</span> | <span style='color: #fff; font-weight: bold;'>₿ BTC:</span> <span style='color: #ffa500; font-weight: bold;'>{commodities_prices['btc']}</span> | <span style='color: #fff; font-weight: bold;'>🕐 IST:</span> <span style='color: #fff; font-weight: bold;'>{ist_time.strftime('%I:%M %p')}</span></p>
        <p style='margin: 0; font-size: 13px;'><span style='color: #fff; font-weight: bold;'>🥇 Gold:</span> <span style='color: #ffd700; font-weight: bold;'>{commodities_prices['gold']}</span> | <span style='color: #fff; font-weight: bold;'>🪙 Silver:</span> <span style='color: #c0c0c0; font-weight: bold;'>{commodities_prices['silver']}</span> | <span style='color: #fff; font-weight: bold;'>🕐 EDT:</span> <span style='color: #fff; font-weight: bold;'>{edt_time.strftime('%I:%M %p')}</span></p>
        <p style='margin: 0; font-size: 13px;'><span style='color: #fff; font-weight: bold;'>💵 USD/INR:</span> <span style='color: {usd_inr_color}; font-weight: bold;'>{commodities_prices['usd_inr']}</span> | <span style='color: #fff; font-weight: bold;'>📅</span> <span style='color: #fff; font-weight: bold;'>{ist_time.strftime('%d %b %Y')}</span></p>
        {holiday_line}
    </div>
    """


def create_html_table(df_page):
    """Create HTML table with colored percentage values"""
    html_table = '<table style="width:100%; border-collapse: collapse; background-color: #2d2d2d;">'
    html_table += '<thead><tr style="background-color: #3d3d3d;">'
    
    for col in df_page.columns:
        html_table += f'<th style="padding: 12px; text-align: left; border: 1px solid #555; color: #ffffff; font-weight: bold;">{col}</th>'
    html_table += '</tr></thead><tbody>'
    
    for _, row in df_page.iterrows():
        html_table += '<tr>'
        for col in df_page.columns:
            value = row[col]
            if col in ['Today %', '1 Week %', '1 Month %', '2 Months %', '3 Months %']:
                colored_value = color_percentage(value)
                html_table += f'<td style="padding: 12px; border: 1px solid #555; color: #ffffff;">{colored_value}</td>'
            else:
                html_table += f'<td style="padding: 12px; border: 1px solid #555; color: #ffffff;">{value}</td>'
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
