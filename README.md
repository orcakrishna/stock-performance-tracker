# NSE Pulse - Indian Stock Performance Tracker

A comprehensive web application that displays 1-week, 1-month, 2-month, and 3-month performance of NSE/BSE stocks with a modern navy blue theme interface.

## 🌐 Live Demo

**Access the app:** [https://nsepulse.streamlit.app/](https://nsepulse.streamlit.app/)

> Real-time Indian stock market tracking with live market indices, commodities, and high volume stocks.

## Features

### 📊 Market Overview
- **Live Market Indices:** Nifty 50, Sensex, Bank Nifty, and sectoral indices
- **Global Commodities:** Oil, Ethereum, Gold, Silver, Bitcoin prices with change indicators
- **Currency:** USD/INR exchange rate with color-coded performance
- **High Volume Stocks:** Top 7 highest volume stocks with real-time data
- **Live Ticker:** Scrolling ticker with advances/declines
- **NSE Holiday Calendar:** Next upcoming NSE holiday

### 📈 Stock Performance Tracking
- View 1-week, 1-month, 2-month, and 3-month performance
- **Multiple Stock Categories:**
  - Nifty 50
  - Nifty Next 50
  - BSE Sensex
  - Nifty 500 (Sample)
  - Custom Selection
- 📤 **Upload Custom Stock Lists** (CSV/TXT files)
- 📈 Sortable data tables with compact metric boxes
- 🟢🔴 Color-coded returns with triangles (▲/▼)
- 🏆 Top & Bottom performers highlight
- 📉 Average performance statistics
- 🔄 Smart caching for optimal performance
- 📱 Mobile-responsive design

### 🎨 Modern UI
- Deep navy blue gradient theme
- Compact, professional layout
- Color-coded percentage changes (Green/Red)
- Matching table designs for consistency
- Modern fonts (Inter & JetBrains Mono)

### 🔒 Security
- Copy protection enabled
- Right-click disabled
- Keyboard shortcuts blocked
- Content theft prevention

## Prerequisites

- Python 3.7+
- pip (Python package manager)
- Internet connection

## Installation

1. Navigate to the project directory
2. Create a virtual environment:

```bash
python3 -m venv venv
```

3. Activate the virtual environment:

```bash
source venv/bin/activate
```

4. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

1. Activate the virtual environment (if not already activated):

```bash
source venv/bin/activate
```

2. Run the Streamlit app:

```bash
streamlit run app.py
```

3. The application will open in your default web browser at `http://localhost:8501`
4. Select stocks from the sidebar or use "Select All" for all Nifty 50 stocks
5. View the performance table with color-coded percentage changes

## Data Source

- **Primary:** NSE India official website API
- **Fallback:** Sample data for demonstration (when NSE API is unavailable)

## Performance Calculation

- **1 Week:** Last 7 days performance
- **1 Month:** Last 30 days performance
- **2 Months:** Last 60 days performance
- **3 Months:** Last 90 days performance

Data automatically updates daily to show consistent rolling performance metrics.

## How to Upload Custom Stock Lists

1. Select "Upload File" from the category dropdown
2. Download the sample template provided
3. Edit the file with your stock symbols (one per line)
4. Add `.NS` suffix for NSE stocks or `.BO` for BSE stocks
5. Upload the file and view performance

**Example file format:**
```
RELIANCE.NS
TCS.NS
INFY.BO
HDFCBANK.NS
```

## Note

- The application requires an internet connection to fetch stock data
- All prices are in Indian Rupees (₹)
- Performance percentages are color-coded for easy identification
- Data updates in real-time when you refresh the page

## License

This project is open source and available under the [MIT License](LICENSE).
