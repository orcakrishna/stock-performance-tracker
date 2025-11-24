"""
Portfolio Manager - Core logic for portfolio tracking
Handles portfolio calculations, metrics, and data management
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


def calculate_portfolio_metrics(holdings: List[Dict], current_prices: Dict[str, float]) -> Dict:
    """
    Calculate comprehensive portfolio metrics
    
    Args:
        holdings: List of dicts with keys: stock_symbol, quantity, buy_price, buy_date, notes
        current_prices: Dict mapping stock_symbol to current price
    
    Returns:
        Dict with portfolio metrics:
        - total_invested: Total money invested
        - current_value: Current portfolio value
        - total_pnl: Total profit/loss
        - total_pnl_pct: P&L percentage
        - today_change: Today's change in value
        - today_change_pct: Today's change percentage
        - holdings_with_pnl: Holdings list with P&L calculated
    """
    
    if not holdings:
        return {
            'total_invested': 0.0,
            'current_value': 0.0,
            'total_pnl': 0.0,
            'total_pnl_pct': 0.0,
            'today_change': 0.0,
            'today_change_pct': 0.0,
            'holdings_with_pnl': []
        }
    
    holdings_with_pnl = []
    total_invested = 0.0
    total_current = 0.0
    
    for holding in holdings:
        symbol = holding['stock_symbol']
        quantity = float(holding['quantity'])
        buy_price = float(holding['buy_price'])
        
        # Get current price
        current_price = current_prices.get(symbol, buy_price)
        
        # Calculate metrics for this holding
        invested = quantity * buy_price
        current_value = quantity * current_price
        pnl = current_value - invested
        pnl_pct = (pnl / invested * 100) if invested > 0 else 0.0
        
        # Add to holding dict
        holding_with_pnl = {
            **holding,
            'current_price': current_price,
            'invested': invested,
            'current_value': current_value,
            'pnl': pnl,
            'pnl_pct': pnl_pct
        }
        holdings_with_pnl.append(holding_with_pnl)
        
        # Accumulate totals
        total_invested += invested
        total_current += current_value
    
    # Calculate portfolio totals
    total_pnl = total_current - total_invested
    total_pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0.0
    
    # Today's change (will be 0 for now, can enhance later with yesterday's prices)
    today_change = 0.0
    today_change_pct = 0.0
    
    return {
        'total_invested': total_invested,
        'current_value': total_current,
        'total_pnl': total_pnl,
        'total_pnl_pct': total_pnl_pct,
        'today_change': today_change,
        'today_change_pct': today_change_pct,
        'holdings_with_pnl': holdings_with_pnl
    }


def get_sector_allocation(holdings_with_pnl: List[Dict]) -> Dict[str, float]:
    """
    Calculate sector-wise allocation (placeholder - needs sector mapping)
    
    Args:
        holdings_with_pnl: Holdings list with calculated values
    
    Returns:
        Dict mapping sector to percentage allocation
    """
    # TODO: Add sector mapping in future
    # For now, return empty dict
    return {}


def get_top_performers(holdings_with_pnl: List[Dict], top_n: int = 3) -> List[Tuple[str, float]]:
    """
    Get top N performing stocks by P&L percentage (unique stocks only)
    
    Args:
        holdings_with_pnl: Holdings list with calculated P&L
        top_n: Number of top performers to return
    
    Returns:
        List of tuples (stock_symbol, pnl_pct)
    """
    if not holdings_with_pnl:
        return []
    
    # Group by stock symbol and calculate average P&L% for duplicates
    stock_pnl = {}
    for h in holdings_with_pnl:
        symbol = h['stock_symbol']
        pnl_pct = h.get('pnl_pct', 0)
        
        if symbol in stock_pnl:
            # Average P&L% for same stock with multiple entries
            stock_pnl[symbol].append(pnl_pct)
        else:
            stock_pnl[symbol] = [pnl_pct]
    
    # Calculate average and create list
    unique_stocks = [(symbol, sum(pnls) / len(pnls)) for symbol, pnls in stock_pnl.items()]
    
    # Sort by P&L percentage descending
    sorted_stocks = sorted(unique_stocks, key=lambda x: x[1], reverse=True)
    
    return sorted_stocks[:top_n]


def get_worst_performers(holdings_with_pnl: List[Dict], bottom_n: int = 3) -> List[Tuple[str, float]]:
    """
    Get bottom N performing stocks by P&L percentage (unique stocks only)
    
    Args:
        holdings_with_pnl: Holdings list with calculated P&L
        bottom_n: Number of worst performers to return
    
    Returns:
        List of tuples (stock_symbol, pnl_pct)
    """
    if not holdings_with_pnl:
        return []
    
    # Group by stock symbol and calculate average P&L% for duplicates
    stock_pnl = {}
    for h in holdings_with_pnl:
        symbol = h['stock_symbol']
        pnl_pct = h.get('pnl_pct', 0)
        
        if symbol in stock_pnl:
            # Average P&L% for same stock with multiple entries
            stock_pnl[symbol].append(pnl_pct)
        else:
            stock_pnl[symbol] = [pnl_pct]
    
    # Calculate average and create list
    unique_stocks = [(symbol, sum(pnls) / len(pnls)) for symbol, pnls in stock_pnl.items()]
    
    # Sort by P&L percentage ascending (worst first)
    sorted_stocks = sorted(unique_stocks, key=lambda x: x[1])
    
    return sorted_stocks[:bottom_n]


def validate_holding_input(symbol: str, quantity: float, buy_price: float, buy_date: str) -> Tuple[bool, str]:
    """
    Validate portfolio holding input
    
    Args:
        symbol: Stock symbol
        quantity: Number of shares
        buy_price: Purchase price per share
        buy_date: Purchase date (YYYY-MM-DD)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate symbol
    if not symbol or len(symbol.strip()) == 0:
        return False, "Stock symbol cannot be empty"
    
    # Validate quantity
    if quantity <= 0:
        return False, "Quantity must be greater than 0"
    
    # Validate buy price
    if buy_price <= 0:
        return False, "Buy price must be greater than 0"
    
    # Validate date format
    try:
        date_obj = datetime.strptime(buy_date, "%Y-%m-%d")
        if date_obj > datetime.now():
            return False, "Buy date cannot be in the future"
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD"
    
    return True, ""


def format_currency(amount: float) -> str:
    """
    Format amount as Indian currency (₹)
    
    Args:
        amount: Amount to format
    
    Returns:
        Formatted string like "₹1,23,456.78"
    """
    if amount < 0:
        return f"-₹{abs(amount):,.2f}"
    return f"₹{amount:,.2f}"


def format_percentage(pct: float, include_sign: bool = True) -> str:
    """
    Format percentage with color indication
    
    Args:
        pct: Percentage value
        include_sign: Whether to include + or - sign
    
    Returns:
        Formatted percentage string
    """
    if include_sign:
        if pct > 0:
            return f"+{pct:.2f}%"
        elif pct < 0:
            return f"{pct:.2f}%"
        else:
            return f"{pct:.2f}%"
    return f"{abs(pct):.2f}%"


def get_pnl_color(pnl: float) -> str:
    """
    Get color code based on P&L value
    
    Args:
        pnl: Profit/Loss value
    
    Returns:
        Color hex code
    """
    if pnl > 0:
        return "#00c853"  # Green
    elif pnl < 0:
        return "#ff1744"  # Red
    else:
        return "#888888"  # Gray
