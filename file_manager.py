"""
File Management for Stock Lists and Portfolio
Handles saving, loading, listing, and deleting custom stock lists and portfolio data.
"""

import os
from typing import List, Optional, Dict
import pandas as pd
from config import SAVED_LISTS_DIR

# Portfolio file path
PORTFOLIO_FILE = os.path.join(SAVED_LISTS_DIR, "portfolio.csv")


def ensure_saved_lists_dir() -> None:
    """Ensure the saved lists directory exists."""
    os.makedirs(SAVED_LISTS_DIR, exist_ok=True)
    gitkeep_path = os.path.join(SAVED_LISTS_DIR, ".gitkeep")
    if not os.path.exists(gitkeep_path):
        with open(gitkeep_path, "w", encoding="utf-8") as f:
            f.write("")


def save_list_to_csv(list_name: str, stocks: List[str]) -> bool:
    """Save a stock list to CSV. Returns True if successful."""
    try:
        ensure_saved_lists_dir()
        filename = os.path.join(SAVED_LISTS_DIR, f"{list_name}.csv")
        pd.DataFrame({"Symbol": stocks}).to_csv(filename, index=False)
        return True
    except Exception as e:
        print(f"⚠️ Error saving list '{list_name}': {e}")
        return False


def load_list_from_csv(list_name: str) -> Optional[List[str]]:
    """Load a stock list from CSV. Returns list of symbols or None."""
    filename = os.path.join(SAVED_LISTS_DIR, f"{list_name}.csv")
    if not os.path.exists(filename):
        return None

    try:
        df = pd.read_csv(filename)
        return df["Symbol"].dropna().astype(str).tolist()
    except Exception as e:
        print(f"⚠️ Error loading list '{list_name}': {e}")
        return None


def delete_list_csv(list_name: str) -> bool:
    """Delete a stock list CSV file."""
    filename = os.path.join(SAVED_LISTS_DIR, f"{list_name}.csv")
    if os.path.exists(filename):
        try:
            os.remove(filename)
            return True
        except Exception as e:
            print(f"⚠️ Error deleting list '{list_name}': {e}")
            return False
    return False


def load_all_saved_lists() -> Dict[str, List[str]]:
    """Load all saved stock lists from directory."""
    ensure_saved_lists_dir()
    saved_lists = {}

    for file in os.listdir(SAVED_LISTS_DIR):
        if file.endswith(".csv") and file != "portfolio.csv":  # Exclude portfolio file
            list_name = os.path.splitext(file)[0]
            stocks = load_list_from_csv(list_name)
            if stocks:
                saved_lists[list_name] = stocks

    return saved_lists


# ==================== Portfolio Management ====================

def save_portfolio(holdings: List[Dict]) -> bool:
    """
    Save portfolio holdings to CSV
    
    Args:
        holdings: List of dicts with keys: stock_symbol, quantity, buy_price, buy_date, notes
    
    Returns:
        True if successful, False otherwise
    """
    try:
        ensure_saved_lists_dir()
        
        if not holdings:
            # If empty, create empty file
            df = pd.DataFrame(columns=['stock_symbol', 'quantity', 'buy_price', 'buy_date', 'notes'])
        else:
            df = pd.DataFrame(holdings)
        
        df.to_csv(PORTFOLIO_FILE, index=False)
        return True
    except Exception as e:
        print(f"⚠️ Error saving portfolio: {e}")
        return False


def load_portfolio() -> List[Dict]:
    """
    Load portfolio holdings from CSV
    
    Returns:
        List of dicts with portfolio holdings, empty list if file doesn't exist
    """
    if not os.path.exists(PORTFOLIO_FILE):
        return []
    
    try:
        df = pd.read_csv(PORTFOLIO_FILE)
        if df.empty:
            return []
        
        # Convert to list of dicts
        holdings = df.to_dict('records')
        return holdings
    except Exception as e:
        print(f"⚠️ Error loading portfolio: {e}")
        return []


def delete_holding(holdings: List[Dict], index: int) -> List[Dict]:
    """
    Delete a holding from portfolio by index
    
    Args:
        holdings: Current holdings list
        index: Index of holding to delete
    
    Returns:
        Updated holdings list
    """
    if 0 <= index < len(holdings):
        holdings.pop(index)
    return holdings


def clear_portfolio() -> bool:
    """
    Clear entire portfolio (delete file)
    
    Returns:
        True if successful, False otherwise
    """
    if os.path.exists(PORTFOLIO_FILE):
        try:
            os.remove(PORTFOLIO_FILE)
            return True
        except Exception as e:
            print(f"⚠️ Error clearing portfolio: {e}")
            return False
    return True
