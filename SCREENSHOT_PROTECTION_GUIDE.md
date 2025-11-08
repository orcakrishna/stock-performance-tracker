# Screenshot Protection Guide

## Overview
The NSE Stock Dashboard includes built-in screenshot protection that automatically enables security measures when deployed to the cloud while allowing normal screenshots when running locally.

## How It Works

### Local Environment (Development)
- ✅ Screenshots allowed
- ✅ Right-click enabled
- ✅ DevTools accessible
- ✅ Printing enabled
- 🏠 Shows "Local Development Mode" indicator

### Cloud Environment (Production)
- ❌ Screenshots blocked/discouraged
- ❌ Right-click disabled
- ❌ DevTools blocked
- ❌ Printing disabled
- 🔒 Shows watermark overlay
- ⚠️ Blur effect on focus loss
- ☁️ Shows "Cloud Mode - Protected" indicator

## Detection Methods

The system uses multiple methods to detect the environment:

1. **Environment Variable** (Most reliable)
   - Checks `STREAMLIT_ENV` variable
   
2. **Server Address**
   - Detects if running on localhost/127.0.0.1
   
3. **Hostname Analysis**
   - Checks for keywords: local, desktop, laptop, macbook, etc.
   
4. **Port Detection**
   - Standard development ports: 8501-8504

## Configuration

### Force Local Mode (Allow Screenshots)
Set environment variable before starting the app:

```bash
# Mac/Linux
export STREAMLIT_ENV=local
streamlit run app.py --server.address 0.0.0.0 --server.port 8501

# Windows
set STREAMLIT_ENV=local
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

### Force Cloud Mode (Block Screenshots)
```bash
# Mac/Linux
export STREAMLIT_ENV=production
streamlit run app.py

# Windows
set STREAMLIT_ENV=production
streamlit run app.py
```

### Default Behavior
If no environment variable is set, the system will auto-detect based on hostname and port.

## Security Features

### Full Protection Mode (Default for Cloud)

1. **Screenshot Detection**
   - Blocks PrtScn key
   - Blocks Mac shortcuts (Cmd+Shift+3/4/5)
   - Blocks Windows Snipping Tool (Win+Shift+S)
   
2. **Right-Click Protection**
   - Disables context menu
   - Prevents "Save Image As"
   
3. **DevTools Protection**
   - Blocks F12
   - Blocks Ctrl+Shift+I
   
4. **Visual Deterrents**
   - Watermark overlay: "CONFIDENTIAL - NSE Stock Dashboard"
   - Blur effect when window loses focus
   - Console warnings
   
5. **Print Protection**
   - Blocks Ctrl+P/Cmd+P

### Lite Protection Mode (Optional)

To use lighter protection (watermark only), modify `app.py`:

```python
# Replace this line:
environment = apply_screenshot_protection()

# With this:
from screenshot_protection import apply_lite_screenshot_protection
environment = apply_lite_screenshot_protection()
```

## Deployment Scenarios

### Scenario 1: Local Development
```bash
# Your local machine
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```
**Result:** No protection, screenshots allowed

### Scenario 2: Local Testing of Cloud Mode
```bash
# Test cloud protection locally
export STREAMLIT_ENV=production
streamlit run app.py
```
**Result:** Protection active even locally

### Scenario 3: Cloud Deployment (Streamlit Cloud, Heroku, AWS)
```bash
# Deploy normally - auto-detects cloud
# On Streamlit Cloud: Already configured
# On Heroku: Set Config Var STREAMLIT_ENV=production
# On AWS: Set environment variable in deployment
```
**Result:** Full protection automatically enabled

### Scenario 4: Mobile Local Network
```bash
# Access from mobile on same network (10.0.0.230:8501)
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```
**Result:** Still detected as local, screenshots allowed

## Testing

### Test Local Mode
1. Start app: `streamlit run app.py --server.address 0.0.0.0`
2. Look for green indicator: "🏠 Local Development Mode"
3. Try taking screenshot - should work normally
4. Right-click should work

### Test Cloud Mode
1. Set env: `export STREAMLIT_ENV=production`
2. Start app: `streamlit run app.py`
3. Look for red indicator: "☁️ Cloud Mode - Protected"
4. Try taking screenshot - should show alert/watermark
5. Right-click should be disabled

## Important Notes

⚠️ **Limitations:**
- Screenshot protection is not 100% foolproof
- Users can still use external cameras
- Screen recording software may bypass some protections
- These are deterrents, not absolute security

✅ **Best Practices:**
- Use full protection for sensitive financial data
- Keep watermarks visible
- Combine with user agreements/terms of service
- Monitor for unauthorized sharing

🔧 **Customization:**
- Edit `screenshot_protection.py` to customize messages
- Adjust watermark opacity and text
- Add custom detection methods
- Modify blur timing and intensity

## Troubleshooting

### Protection Active When Not Expected
```bash
# Explicitly set local mode
export STREAMLIT_ENV=local
```

### Protection Not Active on Cloud
```bash
# Verify environment variable is not set to local
echo $STREAMLIT_ENV

# If set incorrectly, unset it
unset STREAMLIT_ENV
```

### Indicator Not Showing
- Clear browser cache
- Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
- Check browser console for errors

## Support

For issues or questions:
1. Check the indicator at bottom-right of screen
2. Review browser console (F12)
3. Verify environment variables
4. Test with explicit STREAMLIT_ENV setting
