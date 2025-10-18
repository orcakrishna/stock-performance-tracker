"""
File Management Functions for Stock Lists
Handles saving, loading, and deleting custom stock lists
"""

import os
import pandas as pd
from config import SAVED_LISTS_DIR


def ensure_saved_lists_dir():
    """Create saved lists directory if it doesn't exist"""
    if not os.path.exists(SAVED_LISTS_DIR):
        os.makedirs(SAVED_LISTS_DIR)
        with open(os.path.join(SAVED_LISTS_DIR, '.gitkeep'), 'w') as f:
            f.write('')


def save_list_to_csv(list_name, stocks):
    """Save a stock list to CSV file"""
    ensure_saved_lists_dir()
    filename = os.path.join(SAVED_LISTS_DIR, f"{list_name}.csv")
    df = pd.DataFrame({'Symbol': stocks})
    df.to_csv(filename, index=False)


def load_list_from_csv(list_name):
    """Load a stock list from CSV file"""
    filename = os.path.join(SAVED_LISTS_DIR, f"{list_name}.csv")
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        return df['Symbol'].tolist()
    return None


def delete_list_csv(list_name):
    """Delete a stock list CSV file"""
    filename = os.path.join(SAVED_LISTS_DIR, f"{list_name}.csv")
    if os.path.exists(filename):
        os.remove(filename)


def load_all_saved_lists():
    """Load all saved stock lists from directory"""
    ensure_saved_lists_dir()
    saved_lists = {}
    if os.path.exists(SAVED_LISTS_DIR):
        for filename in os.listdir(SAVED_LISTS_DIR):
            if filename.endswith('.csv'):
                list_name = filename[:-4]
                stocks = load_list_from_csv(list_name)
                if stocks:
                    saved_lists[list_name] = stocks
    return saved_lists
