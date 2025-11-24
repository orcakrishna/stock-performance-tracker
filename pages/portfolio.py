"""
Portfolio page module - Admin portfolio management
Extracted from app.py for better modularity
"""
import streamlit as st
import pandas as pd
from portfolio_manager import (
    validate_holding_input, validate_stock_symbol,
    calculate_portfolio_metrics, format_currency, format_percentage,
    get_pnl_color, get_top_performers, get_worst_performers
)
from file_manager import load_portfolio, save_portfolio
from data_fetchers import get_stock_performance
from security_fixes import sanitize_dataframe_for_csv


@st.cache_data(ttl=86400, show_spinner=False)  # Cache for 24 hours
def get_all_nse_stocks():
    """
    Get comprehensive list of NSE stocks from all indices (display names only).
    Cached for 24 hours to avoid slow first-load when adding stocks.
    """
    from data_fetchers import get_stock_list
    all_stocks = set()
    try:
        # Get stocks from major indices
        for idx in ["Nifty 50", "Nifty 100", "Nifty 200", "Nifty 500"]:
            stocks, _ = get_stock_list(idx)
            if stocks:
                # Remove .NS extension for display
                clean_stocks = [s.replace('.NS', '') for s in stocks]
                all_stocks.update(clean_stocks)
    except Exception:
        pass
    return sorted(list(all_stocks))


@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes
def get_portfolio_current_prices(holdings_tuple):
    """
    Fetch current prices for all portfolio holdings.
    Cached to avoid duplicate fetching within same session.
    
    Args:
        holdings_tuple: Tuple of (symbol, buy_price) for cache key uniqueness
    
    Returns:
        Tuple of (current_prices dict, price_fetch_errors list)
    """
    current_prices = {}
    price_fetch_errors = []
    
    for symbol, fallback_price in holdings_tuple:
        try:
            data = get_stock_performance(symbol, use_cache=True)
            if data and 'Current Price' in data:
                # Extract numeric value from formatted string like "₹1,234.56"
                price_str = data['Current Price'].replace('₹', '').replace(',', '')
                current_prices[symbol] = float(price_str)
            else:
                # API returned data but no current price
                price_fetch_errors.append(f"{symbol}: No price data available")
                current_prices[symbol] = fallback_price
        except Exception as e:
            # API call failed
            price_fetch_errors.append(f"{symbol}: {str(e)}")
            current_prices[symbol] = fallback_price
    
    return current_prices, price_fetch_errors


def render_portfolio_page():
    """Main portfolio page render function"""
    
    # Load portfolio if not loaded
    if not st.session_state.portfolio_loaded:
        st.session_state.portfolio_holdings = load_portfolio()
        st.session_state.portfolio_loaded = True
    
    st.title("💼 My Portfolio")
    
    # Get current prices for all holdings (cached function - fetched only once)
    current_prices = {}
    price_fetch_errors = []
    if st.session_state.portfolio_holdings:
        # Create cache key from holdings
        holdings_tuple = tuple((h['stock_symbol'], h['buy_price']) for h in st.session_state.portfolio_holdings)
        
        with st.spinner("Fetching current prices..."):
            current_prices, price_fetch_errors = get_portfolio_current_prices(holdings_tuple)
        
        # Show warning if any prices failed to fetch
        if price_fetch_errors:
            with st.expander("⚠️ Price Fetch Issues", expanded=False):
                st.warning("Some stock prices could not be fetched. Using buy price as fallback:")
                for error in price_fetch_errors:
                    st.text(f"• {error}")
    
    # Calculate portfolio metrics
    metrics = calculate_portfolio_metrics(st.session_state.portfolio_holdings, current_prices)
    
    # Portfolio Summary Cards
    if metrics['total_invested'] > 0:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📊 Total Invested",
                value=format_currency(metrics['total_invested'])
            )
        
        with col2:
            st.metric(
                label="💰 Current Value",
                value=format_currency(metrics['current_value']),
                delta=format_currency(metrics['total_pnl'])
            )
        
        with col3:
            pnl_pct = metrics['total_pnl_pct']
            st.metric(
                label="📈 Total P&L",
                value=format_percentage(pnl_pct),
                delta=f"{pnl_pct:+.2f}%"
            )
        
        with col4:
            st.metric(
                label="📈 Holdings",
                value=f"{len(st.session_state.portfolio_holdings)} stocks"
            )
    
    st.markdown("---")
    
    # Add Stock Form (collapsed by default for clean UI)
    _render_add_stock_form()
    
    st.markdown("---")
    
    # Holdings Table
    _render_holdings_table(current_prices)
    
    st.markdown("---")
    
    # Export Portfolio
    _render_portfolio_export()
    
    # Top Performers
    _render_top_performers(metrics)


def _render_add_stock_form():
    """Render the add stock form"""
    with st.expander("➕ Add Stock to Portfolio", expanded=False):
        # Get all available stocks for autocomplete (cached globally, fast!)
        available_stocks = get_all_nse_stocks()
        
        with st.form("add_stock_form", clear_on_submit=True):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
            
            with col1:
                # Searchable dropdown with autocomplete (display without .NS)
                symbol_dropdown = st.selectbox(
                    "Stock Symbol",
                    options=[""] + available_stocks,
                    index=0,
                    help="Start typing to search (e.g., INFY, RELIANCE, TCS)"
                )
                
                # Use dropdown selection first
                symbol = symbol_dropdown.strip().upper() if symbol_dropdown else ""
                # Remove .NS if user somehow enters it
                if symbol:
                    symbol = symbol.replace('.NS', '')
            
            with col2:
                quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
            
            with col3:
                buy_price = st.number_input("Buy Price (₹)", min_value=0.01, value=100.0, step=0.01)
            
            with col4:
                buy_date = st.date_input("Buy Date", value=pd.Timestamp.now())
            
            # Manual entry and Notes on same line to save space
            col_manual, col_notes = st.columns(2)
            with col_manual:
                symbol_manual = st.text_input("Or enter manually", placeholder="e.g., RELIANCE")
                # Override with manual entry if provided
                if symbol_manual and symbol_manual.strip():
                    symbol = symbol_manual.strip().upper().replace('.NS', '')
            
            with col_notes:
                notes = st.text_input("Notes (optional)", placeholder="e.g., Long-term hold")
            
            submitted = st.form_submit_button("Add Stock", type="primary")
            
            if submitted:
                _handle_add_stock(symbol, quantity, buy_price, buy_date, notes)


def _handle_add_stock(symbol, quantity, buy_price, buy_date, notes):
    """Handle adding a stock to portfolio"""
    # Check if symbol is provided
    if not symbol or symbol.strip() == "":
        st.error("❌ Please select or enter a stock symbol")
    else:
        # Validate input
        is_valid, error_msg = validate_holding_input(
            symbol, quantity, buy_price, buy_date.strftime("%Y-%m-%d")
        )
        
        if not is_valid:
            st.error(f"❌ {error_msg}")
        else:
            # Add .NS extension for API validation (internally needed)
            symbol_with_ns = symbol if symbol.endswith('.NS') else f"{symbol}.NS"
            
            # Validate stock symbol with .NS extension
            if not validate_stock_symbol(symbol_with_ns):
                st.error(f"❌ Invalid stock symbol: {symbol}")
            else:
                # Check for duplicate: same stock, same date
                buy_date_str = buy_date.strftime("%Y-%m-%d")
                duplicate_found = False
                
                for i, holding in enumerate(st.session_state.portfolio_holdings):
                    if holding['stock_symbol'] == symbol_with_ns and holding['buy_date'] == buy_date_str:
                        # Duplicate found - merge quantities and average price
                        old_qty = holding['quantity']
                        old_price = holding['buy_price']
                        new_qty = old_qty + quantity
                        # Weighted average price
                        avg_price = ((old_qty * old_price) + (quantity * buy_price)) / new_qty
                        
                        st.session_state.portfolio_holdings[i]['quantity'] = new_qty
                        st.session_state.portfolio_holdings[i]['buy_price'] = round(avg_price, 2)
                        st.session_state.portfolio_holdings[i]['notes'] = notes if notes else holding['notes']
                        
                        duplicate_found = True
                        st.info(f"ℹ️ Merged with existing {symbol} entry: {old_qty} + {quantity} = {new_qty} shares @ avg ₹{avg_price:.2f}")
                        break
                
                if not duplicate_found:
                    # Add new holding
                    new_holding = {
                        'stock_symbol': symbol_with_ns,
                        'quantity': quantity,
                        'buy_price': buy_price,
                        'buy_date': buy_date_str,
                        'notes': notes
                    }
                    st.session_state.portfolio_holdings.append(new_holding)
                
                # Save to file
                if save_portfolio(st.session_state.portfolio_holdings):
                    # Force reload of portfolio
                    st.session_state.portfolio_loaded = False
                    st.toast(f"✅ Added {symbol}", icon="📈")
                    # Use experimental rerun to avoid full page flash
                    st.rerun()
                else:
                    st.error("❌ Failed to save portfolio")


def _render_holdings_table(current_prices):
    """Render the holdings table with fragment for delete functionality"""
    @st.fragment
    def render_holdings_fragment():
        if not st.session_state.portfolio_holdings:
            st.info("📭 Your portfolio is empty. Add your first stock above!")
            return
        
        # Reuse cached prices (no duplicate fetching!)
        holdings_tuple = tuple((h['stock_symbol'], h['buy_price']) for h in st.session_state.portfolio_holdings)
        current_prices_frag, _ = get_portfolio_current_prices(holdings_tuple)
        
        metrics_frag = calculate_portfolio_metrics(st.session_state.portfolio_holdings, current_prices_frag)
        
        st.subheader(f"📈 Holdings ({len(st.session_state.portfolio_holdings)} stocks)")
        
        # Column headers
        header_cols = st.columns([0.5, 1, 0.8, 1, 1, 1.2, 1.2, 1.5, 1.2, 1.5, 0.6])
        headers = ['#', 'STOCK', 'QTY', 'BUY PRICE', 'CURRENT PRICE', 'INVESTED', 'CURRENT VALUE', 'P&L', 'BUY DATE', 'NOTES', 'ACTION']
        for col, header in zip(header_cols, headers):
            with col:
                st.markdown(f"**{header}**")
        
        st.markdown("<hr style='margin: 5px 0; border-color: #42a5f5; border-width: 2px;'>", unsafe_allow_html=True)
        
        # Holdings rows
        for i, holding in enumerate(metrics_frag['holdings_with_pnl']):
            cols = st.columns([0.5, 1, 0.8, 1, 1, 1.2, 1.2, 1.5, 1.2, 1.5, 0.6])
            display_symbol = holding['stock_symbol'].replace('.NS', '')
            
            pnl_color = get_pnl_color(holding.get('pnl_pct', 0))
            
            with cols[0]:
                st.markdown(f"{i+1}")
            with cols[1]:
                st.markdown(f"**{display_symbol}**")
            with cols[2]:
                st.markdown(f"{holding['quantity']}")
            with cols[3]:
                st.markdown(f"₹{holding['buy_price']:,.2f}")
            with cols[4]:
                st.markdown(f"₹{holding['current_price']:,.2f}")
            with cols[5]:
                st.markdown(f"₹{holding['invested']:,.2f}")
            with cols[6]:
                st.markdown(f"₹{holding['current_value']:,.2f}")
            with cols[7]:
                st.markdown(f"<span style='color: {pnl_color}; font-weight: 600;'>{format_currency(holding['pnl'])} ({format_percentage(holding['pnl_pct'])})</span>", unsafe_allow_html=True)
            with cols[8]:
                st.markdown(f"{holding['buy_date']}")
            with cols[9]:
                st.markdown(f"{holding.get('notes', '')}")
            with cols[10]:
                # Clickable delete button - small size with proper spacing
                st.markdown("<div style='padding-top: 5px;'>", unsafe_allow_html=True)
                if st.button("✕", key=f"del_{i}", help=f"Delete {display_symbol}", use_container_width=False):
                    st.session_state.portfolio_holdings.pop(i)
                    save_portfolio(st.session_state.portfolio_holdings)
                    # Clear price cache so it refetches with new holdings
                    get_portfolio_current_prices.clear()
                    st.session_state.portfolio_loaded = False  # Force reload
                    st.toast(f"✅ Deleted {display_symbol}", icon="🗑️")
                    st.rerun(scope="fragment")  # Fragment rerun - no full page flash!
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Separator line with more top margin to prevent overlap
            st.markdown("<hr style='margin: 10px 0 5px 0; border-color: #555;'>", unsafe_allow_html=True)
    
    # Call the fragment
    render_holdings_fragment()


def _render_portfolio_export():
    """Render portfolio export button"""
    if st.session_state.portfolio_holdings:
        export_df = pd.DataFrame(st.session_state.portfolio_holdings)
        # Remove any bloat columns (sparkline_data, Ticker, etc.) if they exist
        export_df = export_df.drop(columns=["sparkline_data", "Ticker"], errors="ignore")
        # Security: Prevent CSV injection
        safe_df = sanitize_dataframe_for_csv(export_df)
        csv_data = safe_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Portfolio (CSV)",
            data=csv_data,
            file_name="my_portfolio.csv",
            mime="text/csv",
            use_container_width=False
        )


def _render_top_performers(metrics):
    """Render top and worst performers"""
    # Top Performers - only show if at least 3 unique stocks
    unique_stocks = len(set(h['stock_symbol'] for h in st.session_state.portfolio_holdings))
    if unique_stocks >= 3:
        st.markdown("---")
        perf_col1, perf_col2 = st.columns(2)
        
        with perf_col1:
            st.subheader("🏆 Top Performers")
            top = get_top_performers(metrics['holdings_with_pnl'], 3)
            for symbol, pnl_pct in top:
                display_sym = symbol.replace('.NS', '')
                color = get_pnl_color(pnl_pct)
                st.markdown(f"**{display_sym}**: <span style='color: {color};'>{format_percentage(pnl_pct)}</span>", unsafe_allow_html=True)
        
        with perf_col2:
            st.subheader("📉 Needs Attention")
            worst = get_worst_performers(metrics['holdings_with_pnl'], 3)
            for symbol, pnl_pct in worst:
                display_sym = symbol.replace('.NS', '')
                color = get_pnl_color(pnl_pct)
                st.markdown(f"**{display_sym}**: <span style='color: {color};'>{format_percentage(pnl_pct)}</span>", unsafe_allow_html=True)
