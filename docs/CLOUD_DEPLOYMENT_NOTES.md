# Cloud Deployment Notes - FII/DII Data

## Issue: FII/DII Shows "Loading..." in Cloud

### Root Cause:
NSE (National Stock Exchange) implements strict anti-bot protection that blocks requests from:
- Cloud server IPs (AWS, Heroku, Streamlit Cloud, etc.)
- Data center IPs
- Known VPN/proxy IPs

This causes the NSE API to fail with timeouts or 403 errors when deployed to cloud platforms.

### Why It Works Locally:
- Your local IP is residential (ISP-provided)
- NSE allows residential IPs
- No rate limiting for home users

### Solution Implemented:

**3-Tier Fallback System:**

1. **NSE API** (Primary - Fast but blocked on cloud)
   - Timeout: 5s homepage + 8s data
   - Works: ✅ Local, ❌ Cloud
   
2. **NSE Website Scraping** (Secondary - Also blocked on cloud)
   - Timeout: 3s homepage + 5s data
   - Works: ✅ Local, ❌ Cloud
   
3. **MoneyControl** (Fallback - Works everywhere)
   - Timeout: 15s
   - Works: ✅ Local, ✅ Cloud
   - Most reliable for cloud deployments

### Optimizations for Cloud:

**Reduced Timeouts:**
- NSE sources fail faster (5-8s instead of 10-15s)
- MoneyControl gets more time (15s) as it's the reliable fallback
- Total max wait: ~28s before showing data or "Loading..."

**Better Error Handling:**
- Catches all exceptions
- Logs which source is being tried
- Returns cached data if available
- Shows "Loading..." only if all sources fail

### Testing:

**Local (Your Computer):**
```bash
# Usually gets data from NSE API
FII/DII: Fetched from NSE API - FII Net: 96.72 Cr, DII Net: -607.01 Cr
```

**Cloud (Streamlit/Heroku):**
```bash
# NSE blocked, falls back to MoneyControl
NSE API failed: timeout
NSE Website scraping failed: 403
Trying MoneyControl for FII/DII data...
FII/DII: Fetched from MoneyControl
```

### Monitoring:

Check your cloud logs for these messages:
- `NSE API failed:` - Expected on cloud
- `Trying MoneyControl for FII/DII data...` - Fallback working
- `FII/DII: Fetched from MoneyControl` - Success!
- `FII/DII: All sources failed` - All 3 sources down (rare)

### Alternative Solutions (If MoneyControl Also Fails):

1. **Use a Proxy Service:**
   ```python
   # Add to data_fetchers.py
   proxies = {
       'http': 'http://your-proxy:port',
       'https': 'http://your-proxy:port'
   }
   response = requests.get(url, proxies=proxies)
   ```

2. **Scheduled Data Fetch:**
   - Run a local script that fetches FII/DII data
   - Upload to a simple API/database
   - Cloud app reads from your API

3. **Manual Update:**
   - Create a simple JSON file with FII/DII data
   - Update it manually/daily
   - App reads from file as fallback

4. **Use Official NSDL API:**
   - https://www.fpi.nsdl.co.in/web/Reports/Latest.aspx
   - More reliable but requires parsing

### Current Status:

✅ **Optimized for cloud deployment**
✅ **MoneyControl fallback should work**
✅ **Faster failure detection**
✅ **Better error logging**

### If Still Showing "Loading..." on Cloud:

1. Check cloud logs for error messages
2. Verify MoneyControl is accessible from cloud
3. Try increasing MoneyControl timeout to 30s
4. Consider implementing alternative solution #2 or #4

### Cache Behavior:

- FII/DII data cached for 1 hour
- If fetch fails, shows "Loading..." (not cached data)
- To show last successful data on failure, modify caching logic

### Recommended: Add Fallback to Last Known Value

```python
# In data_fetchers.py - modify get_fii_dii_data()
# Store last successful result
if fii_data or dii_data:
    st.session_state['last_fii_dii'] = result
    return result

# If all sources fail, return last known value
if 'last_fii_dii' in st.session_state:
    return st.session_state['last_fii_dii']
```

This way, users see stale data instead of "Loading..." when all sources fail.
