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
    gitkeep_path = os.path.join(SAVED_LISTS_DIR, ".gitkeep")
    if not os.path.exists(gitkeep_path):
        with open(gitkeep_path, "w", encoding="utf-8") as f:
            f.write("")


def save_list_to_csv(list_name: str, stocks: list[str]) -> bool:
    """Save a stock list to CSV. Returns True if successful."""
    try:
        ensure_saved_lists_dir()
        filename = os.path.join(SAVED_LISTS_DIR, f"{list_name}.csv")
        pd.DataFrame({"Symbol": stocks}).to_csv(filename, index=False)
        return True
    except Exception as e:
        print(f"⚠️ Error saving list '{list_name}': {e}")
        return False


def load_list_from_csv(list_name: str) -> list[str] | None:
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


def load_all_saved_lists() -> dict[str, list[str]]:
    """Load all saved stock lists from directory."""
    ensure_saved_lists_dir()
    saved_lists = {}

    for file in os.listdir(SAVED_LISTS_DIR):
        if file.endswith(".csv"):
            list_name = os.path.splitext(file)[0]
            stocks = load_list_from_csv(list_name)
            if stocks:
                saved_lists[list_name] = stocks

    return saved_lists
