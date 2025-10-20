"""
Utility Functions for NSE Stock Performance Tracker
Helper functions for formatting, coloring, and data processing
"""

from datetime import datetime
import pytz
import streamlit as st
import yfinance as yf
from config import TICKER_STOCKS
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


def format_time_display(ist_time, edt_time, commodities_prices):
    """Format time and commodities display for header"""
    return f"""
    <div style='text-align: right; padding-top: 20px;'>
    </br>
        <p style='margin: 0; font-size: 13px;'><span style='color: #888;'>🛢️ Oil: <strong>{commodities_prices['oil']}</strong></span> | <span style='color: #888;'>₿ BTC: <strong>{commodities_prices['btc']}</strong></span> | <span style='color: #fff;'>🕐 IST: <strong>{ist_time.strftime('%I:%M %p')}</strong></span></p>
        <p style='margin: 0; font-size: 13px;'><span style='color: #888;'>🥇 Gold: <strong>{commodities_prices['gold']}</strong></span> | <span style='color: #888;'>🪙 Silver: <strong>{commodities_prices['silver']}</strong></span> | <span style='color: #fff;'>🕐 EDT: <strong>{edt_time.strftime('%I:%M %p')}</strong></span></p>
        <p style='margin: 0; font-size: 13px;'><span style='color: #888;'>💵 USD/INR: <strong>{commodities_prices['usd_inr']}</strong></span> | <span style='color: #888;'>📅 {ist_time.strftime('%d %b %Y')}</span></p>
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
            if col in ['1 Week %', '1 Month %', '2 Months %', '3 Months %']:
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
