"""
Utility Functions for NSE Stock Performance Tracker
Helper functions for formatting, coloring, and data processing
"""

from datetime import datetime
import pytz


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
        <p style='margin: 0; font-size: 12px; color: #888;'>{ist_time.strftime('%d %b %Y')}</p>
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
