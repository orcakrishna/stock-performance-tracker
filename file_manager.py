"""
File Management for Stock Lists
Handles saving, loading, listing, and deleting custom stock lists.
"""

import os
import pandas as pd
from config import SAVED_LISTS_DIR


def ensure_saved_lists_dir() -> None:
    """Ensure the saved lists directory exists."""
    os.makedirs(SAVED_LISTS_DIR, exist_ok=True)
    gitkeep_path = os.path.join(SAVED_LISTS_DIR, '.gitkeep')
    if not os.path.exists(gitkeep_path):
        with open(gitkeep_path, 'w') as f:
            f.write('')


def save_list_to_csv(list_name: str, stocks: list[str]) -> bool:
    """
    Save a stock list to a CSV file.
    Returns True if successful, False otherwise.
    """
    try:
        ensure_saved_lists_dir()
        filename = os.path.join(SAVED_LISTS_DIR, f"{list_name}.csv")
        pd.DataFrame({'Symbol': stocks}).to_csv(filename, index=False)
        return True
    except Exception as e:
        print(f"Error saving list '{list_name}': {e}")
        return False


def load_list_from_csv(list_name: str) -> list[str] | None:
    """
    Load a stock list from a CSV file.
    Returns a list of symbols or None if file not found.
    """
    filename = os.path.join(SAVED_LISTS_DIR, f"{list_name}.csv")
    if not os.path.exists(filename):
        return None

    try:
        df = pd.read_csv(filename)
        return df['Symbol'].dropna().astype(str).tolist()
    except Exception as e:
        print(f"Error loading list '{list_name}': {e}")
        return None


def delete_list_csv(list_name: str) -> bool:
    """
    Delete a stock list CSV file.
    Returns True if deleted, False if not found.
    """
    filename = os.path.join(SAVED_LISTS_DIR, f"{list_name}.csv")
    if os.path.exists(filename):
        try:
            os.remove(filename)
            return True
        except Exception as e:
            print(f"Error deleting list '{list_name}': {e}")
            return False
    return False


def load_all_saved_lists() -> dict[str, list[str]]:
    """
    Load all saved stock lists from directory.
    Returns a dictionary: {list_name: [symbols]}.
    """
    ensure_saved_lists_dir()
    saved_lists: dict[str, list[str]] = {}

    try:
        for filename in os.listdir(SAVED_LISTS_DIR):
            if filename.endswith('.csv'):
                list_name = filename[:-4]
                stocks = load_list_from_csv(list_name)
                if stocks:
                    saved_lists[list_name] = stocks
    except Exception as e:
        print(f"Error loading saved lists: {e}")

    return saved_lists
