# 📊 NSE Advances/Declines Feature

## ✅ Feature Added

### What's New:
Added **real-time Advances/Declines counter** below the rolling stock ticker, displaying the number of stocks advancing vs declining among the 50 stocks in the live ticker.

---

## 🎯 Display Layout

### Desktop View:
```
[Rolling Stock Ticker - 50 stocks scrolling]

📊 Live Ticker: 50 stocks • Updates every 60 seconds • Hover to pause  |  📈 Advances: 28 • Declines: 19  |  📊 FII/DII: NSE India
```

### Mobile View:
```
[Rolling Stock Ticker]

📊 Live Ticker: 50 stocks • Updates every 60 seconds • Hover to pause
📈 Advances: 28 • Declines: 19
📊 FII/DII: NSE India
```

---

## 🔧 Changes Made

### 1. Modified `ui_components.py` - `render_live_ticker()` function:

**Added calculations:**
- Count of advancing stocks (change > 0)
- Count of declining stocks (change < 0)
- Count of unchanged stocks (change = 0)

**Updated return value:**
- Before: `return stock_count`
- After: `return stock_count, advances, declines`

### 2. Modified `app.py` - Ticker info display:

**Added center column:**
- Created 3-column layout: Left (ticker info) | Center (advances/declines) | Right (FII/DII)
- Added color coding:
  - Green (#00ff00) for Advances
  - Red (#ff4444) for Declines
- Made it responsive for mobile devices

**CSS Styling:**
```css
.ticker-info-center {
    font-size: 0.85rem;
    color: #888;
    text-align: center;
    white-space: nowrap;
}
.adv-dec-positive { color: #00ff00; font-weight: bold; }
.adv-dec-negative { color: #ff4444; font-weight: bold; }
```

---

## 📱 Features

### Responsive Design:
✅ **Desktop**: 3-column horizontal layout  
✅ **Mobile**: Stacked vertical layout  
✅ **Auto-updates**: Refreshes with ticker data (every 60 seconds)  

### Visual Indicators:
✅ **Color-coded**: Green for advances, Red for declines  
✅ **Bold text**: Makes numbers stand out  
✅ **Icons**: 📈 chart icon for market sentiment  

### Data Accuracy:
✅ **Real-time**: Based on live ticker data  
✅ **Automatic**: Updates when ticker updates  
✅ **Accurate**: Counts from actual 50 stocks displayed  

---

## 🎨 Display Format

**Full format:**
```
📈 Advances: 28 • Declines: 19
```

**Example scenarios:**
- Bullish market: `📈 Advances: 35 • Declines: 12`
- Bearish market: `📈 Advances: 15 • Declines: 31`
- Flat market: `📈 Advances: 24 • Declines: 23`

---

## 💡 How It Works

### Calculation Logic:
1. **Ticker data** is fetched from NSE for 50 stocks
2. **For each stock:**
   - If change > 0 → Count as Advance
   - If change < 0 → Count as Decline
   - If change = 0 → Count as Unchanged
3. **Display** advances and declines in the center column

### Update Frequency:
- Updates every **60 seconds** (same as ticker)
- Real-time during market hours
- Cached data outside market hours

---

## 🧪 Testing

### Test Cases:
- [x] Displays correctly on desktop (horizontal layout)
- [x] Displays correctly on mobile (vertical stack)
- [x] Shows accurate counts (sum = 50 stocks)
- [x] Color coding works (green/red)
- [x] Updates with ticker refresh
- [x] Handles missing data gracefully

### Example Output:
```python
Stock Count: 50
Advances: 28 (56%)
Declines: 19 (38%)
Unchanged: 3 (6%)
```

---

## 📊 Benefits

✅ **Market Sentiment**: Quick view of market breadth  
✅ **Real-time**: Updates automatically with ticker  
✅ **Visual**: Color-coded for easy interpretation  
✅ **Informative**: Shows distribution of market movement  
✅ **Compact**: Fits nicely between ticker info and FII/DII data  

---

## 🚀 Usage

No additional setup required! The feature is automatically active when you run the app:

```bash
streamlit run app.py
```

The advances/declines counter will appear below the rolling ticker, centered between the ticker info and FII/DII data.

---

## 📝 Technical Details

### Files Modified:
1. **ui_components.py** (lines 122-151)
   - Added advance/decline calculation
   - Modified return statement

2. **app.py** (lines 376-452)
   - Updated to receive 3 values from render_live_ticker
   - Added center column for advances/declines
   - Added CSS styling for color coding

### Performance Impact:
- ✅ **Minimal**: Only adds simple counting logic
- ✅ **No additional API calls**: Uses existing ticker data
- ✅ **Efficient**: O(n) calculation where n = 50 stocks

---

## 🎉 Result

You now have a complete market breadth indicator showing:
- Total stocks tracked (50)
- Number advancing (green)
- Number declining (red)
- Real-time updates
- Responsive design

This gives users an instant view of market sentiment beyond just the indices!
