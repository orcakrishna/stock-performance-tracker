"""
NSE Stock Performance Tracker - Main Application
Streamlit app for tracking Indian stock market performance
"""

import streamlit as st
import pandas as pd
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import custom modules
from config import CUSTOM_CSS, ITEMS_PER_PAGE
from data_fetchers import get_stock_list, get_stock_performance
from file_manager import load_all_saved_lists, save_list_to_csv, delete_list_csv
from ui_components import (
    render_header, render_market_indices, render_sidebar_info,
    render_top_bottom_performers, render_averages, render_pagination_controls
)
from utils import create_html_table

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="NSE Stock Performance",
    page_icon="📈",
    layout="wide"
)

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_stock_selection_sidebar():
    """Render sidebar for stock selection and options"""
    st.sidebar.header("📋 Stock Selection")
    
    # Category selection
    category = st.sidebar.selectbox(
        "Select Category",
        options=['Nifty 50', 'Nifty Next 50', 'Nifty Total Market', 'Custom Selection', 'Upload File'],
        index=0
    )
    
    return category


def handle_file_upload():
    """Handle file upload and saved lists management"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📤 Manage Stock Lists**")
    
    # Display saved lists
    if st.session_state.saved_lists:
        st.sidebar.markdown("**💾 Saved Lists:**")
        for list_name, stocks in st.session_state.saved_lists.items():
            col1, col2 = st.sidebar.columns([3, 1])
            with col1:
                if st.button(f"📋 {list_name} ({len(stocks)})", key=f"load_{list_name}"):
                    st.session_state.current_list_name = list_name
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{list_name}"):
                    del st.session_state.saved_lists[list_name]
                    delete_list_csv(list_name)
                    if st.session_state.current_list_name == list_name:
                        st.session_state.current_list_name = None
                    st.rerun()
        st.sidebar.markdown("---")
    
    # Upload new list
    st.sidebar.markdown("**📤 Upload New List**")
    
    sample_content = "RELIANCE.NS\nTCS.NS\nHDFCBANK.NS\nICICIBANK.NS\nINFY.NS"
    st.sidebar.download_button(
        label="📥 Download Sample Template",
        data=sample_content,
        file_name="sample_stocks.txt",
        mime="text/plain"
    )
    
    uploaded_file = st.sidebar.file_uploader(
        "Choose a file",
        type=['csv', 'txt'],
        help="Upload a file with stock symbols (one per line)"
    )
    
    if uploaded_file is not None:
        try:
            content = uploaded_file.read().decode('utf-8')
            uploaded_stocks = [line.strip() for line in content.split('\n') if line.strip()]
            
            valid_stocks = []
            for symbol in uploaded_stocks:
                if '.NS' in symbol or '.BO' in symbol:
                    valid_stocks.append(symbol)
                else:
                    valid_stocks.append(f"{symbol}.NS")
            
            list_name = st.sidebar.text_input(
                "Enter a name for this list:",
                value=uploaded_file.name.replace('.txt', '').replace('.csv', ''),
                key="new_list_name"
            )
            
            if st.sidebar.button("💾 Save List"):
                if list_name.strip():
                    st.session_state.saved_lists[list_name.strip()] = valid_stocks
                    st.session_state.current_list_name = list_name.strip()
                    save_list_to_csv(list_name.strip(), valid_stocks)
                    st.sidebar.success(f"✅ Saved '{list_name}' with {len(valid_stocks)} stocks")
                else:
                    st.sidebar.error("Please enter a list name")
            
            return valid_stocks, valid_stocks
            
        except Exception as e:
            st.sidebar.error(f"Error reading file: {str(e)}")
            return [], []
    
    elif st.session_state.current_list_name and st.session_state.current_list_name in st.session_state.saved_lists:
        selected_stocks = st.session_state.saved_lists[st.session_state.current_list_name]
        st.sidebar.success(f"✅ Using '{st.session_state.current_list_name}' ({len(selected_stocks)} stocks)")
        return selected_stocks, selected_stocks
    else:
        st.sidebar.info(
            "📋 **Upload a stock list:**\n\n"
            "**Format:**\n"
            "- One symbol per line\n"
            "- Add .NS for NSE stocks\n"
            "- Add .BO for BSE stocks\n\n"
            "**Example:**\n"
            "```\n"
            "RELIANCE.NS\n"
            "TCS.NS\n"
            "INFY.BO\n"
            "```"
        )
        return [], []


def fetch_stocks_data(selected_stocks, use_parallel):
    """Fetch stock data using parallel or sequential method"""
    if use_parallel:
        with st.spinner(f"⚡ Fetching {len(selected_stocks)} stocks in parallel (5 at a time to avoid rate limits)..."):
            stocks_data = []
            progress_bar = st.progress(0)
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_ticker = {executor.submit(get_stock_performance, ticker): ticker for ticker in selected_stocks}
                completed = 0
                
                for future in as_completed(future_to_ticker):
                    completed += 1
                    try:
                        data = future.result(timeout=30)
                        if data:
                            stocks_data.append(data)
                    except Exception as e:
                        ticker = future_to_ticker[future]
                        print(f"Error fetching {ticker}: {e}")
                    progress_bar.progress(completed / len(selected_stocks))
            
            progress_bar.empty()
    else:
        # Sequential method
        with st.spinner(f"Fetching data for {len(selected_stocks)} stocks..."):
            stocks_data = []
            progress_bar = st.progress(0)
            
            for idx, ticker in enumerate(selected_stocks):
                data = get_stock_performance(ticker)
                if data:
                    stocks_data.append(data)
                progress_bar.progress((idx + 1) / len(selected_stocks))
            
            progress_bar.empty()
    
    return stocks_data


def main():
    """Main application logic"""
    # Initialize session state
    if 'saved_lists' not in st.session_state:
        st.session_state.saved_lists = load_all_saved_lists()
    if 'current_list_name' not in st.session_state:
        st.session_state.current_list_name = None
    
    # Render header
    render_header()
    
    # Sidebar: Stock selection
    category = render_stock_selection_sidebar()
    
    # Determine stock list based on category
    if category in ['Nifty 50', 'Nifty Next 50', 'Nifty Total Market']:
        with st.spinner(f"Fetching {category} stock list..."):
            selected_stocks, fetch_status = get_stock_list(category)
            available_stocks = selected_stocks
        
        if "✅" in fetch_status:
            st.sidebar.success(fetch_status)
        else:
            st.sidebar.warning(fetch_status)
    
    elif category == 'Upload File':
        selected_stocks, available_stocks = handle_file_upload()
    
    else:  # Custom Selection
        all_nifty_50, _ = get_stock_list('Nifty 50')
        all_nifty_next_50, _ = get_stock_list('Nifty Next 50')
        
        available_stocks = list(set(all_nifty_50 + all_nifty_next_50))
        selected_stocks = st.sidebar.multiselect(
            "Select stocks",
            options=available_stocks,
            default=all_nifty_50[:10],
            format_func=lambda x: x.replace('.NS', '').replace('.BO', '')
        )
    
    # Sorting options
    st.sidebar.markdown("---")
    st.sidebar.header("Sorting Options")
    sort_by = st.sidebar.selectbox(
        "Sort by",
        options=['3 Months %', '2 Months %', '1 Month %', '1 Week %', 'Stock Name'],
        index=0
    )
    sort_order = st.sidebar.radio(
        "Order",
        options=['Best to Worst', 'Worst to Best'],
        index=0
    )
    
    # Performance options
    st.sidebar.markdown("---")
    st.sidebar.header("⚡ Performance")
    use_parallel = st.sidebar.checkbox(
        "Use Parallel Fetching (3x faster)",
        value=False,
        help="Fetch 5 stocks at once (rate-limit safe). Keep unchecked for sequential mode (slower but more reliable)."
    )
    
    # Sidebar info
    render_sidebar_info()
    
    # Check if stocks are selected
    if not selected_stocks:
        st.warning("⚠️ Please select at least one stock to view performance.")
        return
    
    # Display Market Indices
    render_market_indices()
    
    # Display title
    if category == 'Upload File' and st.session_state.current_list_name:
        display_title = f"📊 {st.session_state.current_list_name} - Performance Summary ({len(selected_stocks)} Stock(s))"
    else:
        display_title = f"📊 {category} - Performance Summary ({len(selected_stocks)} Stock(s))"
    
    st.subheader(display_title)
    st.caption(f"🔽 Sorted by: **{sort_by}** ({sort_order})")
    
    # Fetch stock data
    stocks_data = fetch_stocks_data(selected_stocks, use_parallel)
    
    if not stocks_data:
        st.error("❌ Failed to fetch data for the selected stocks. Please try again later.")
        return
    
    # Create DataFrame
    df = pd.DataFrame(stocks_data)
    
    # Apply sorting
    ascending = True if sort_order == 'Worst to Best' else False
    
    if sort_by == 'Stock Name':
        df = df.sort_values(by='Stock Name', ascending=True)
    else:
        df = df.sort_values(by=sort_by, ascending=ascending)
    
    # Add rank
    df.insert(0, 'Rank', range(1, len(df) + 1))
    
    # Pagination
    total_items = len(df)
    start_idx, end_idx = render_pagination_controls(total_items, ITEMS_PER_PAGE)
    df_page = df.iloc[start_idx:end_idx]
    
    # Display table
    html_table = create_html_table(df_page)
    st.markdown(html_table, unsafe_allow_html=True)
    st.caption(f"Showing {start_idx + 1} to {end_idx} of {total_items} stocks")
    
    # Top/Bottom performers
    render_top_bottom_performers(df)
    
    # Averages
    render_averages(df)


if __name__ == "__main__":
    main()
