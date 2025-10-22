# FII/DII Data Automation Setup

## ✅ Solution: JSON File + Daily Updates

Your cloud app will now **ALWAYS show FII/DII data** even when your machine is off!

## How It Works:

```
┌─────────────────────────────────────────────────────┐
│  GitHub Actions (Runs on GitHub servers - always on)│
│  ↓ Runs daily at 6:30 PM IST                        │
│  ↓ Fetches FII/DII from NSE/MoneyControl            │
│  ↓ Saves to fii_dii_data.json                       │
│  ↓ Commits to your repo automatically               │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Your Cloud App (Streamlit/Heroku)                  │
│  ↓ Reads fii_dii_data.json from repo                │
│  ↓ Shows data instantly (no API calls needed)       │
│  ↓ Falls back to live APIs if file missing          │
└─────────────────────────────────────────────────────┘
```

## Current Status:

✅ **JSON file created** with today's data
✅ **Fetch script ready** (`fetch_fii_dii_daily.py`)
✅ **Cloud app updated** to read from JSON first
✅ **Initial data**: FII ₹96.72 Cr, DII -₹607.01 Cr

## Setup Options:

### Option 1: GitHub Actions (Recommended - Fully Automatic)

**Status:** Workflow file created but needs manual upload

**Steps:**
1. Go to your GitHub repo
2. Click "Add file" → "Create new file"
3. Name it: `.github/workflows/fetch_fii_dii.yml`
4. Copy content from the local file: `.github/workflows/fetch_fii_dii.yml`
5. Commit the file
6. GitHub Actions will run automatically daily at 6:30 PM IST

**Benefits:**
- ✅ Completely automatic
- ✅ Runs even when your PC is off
- ✅ Free on GitHub
- ✅ Can trigger manually anytime

### Option 2: Manual Daily Update

**Run this command daily:**
```bash
cd /Users/krishnashukla/Desktop/NSE/CascadeProjects/windsurf-project
python fetch_fii_dii_daily.py
git add fii_dii_data.json
git commit -m "Update FII/DII data - $(date +'%Y-%m-%d')"
git push origin main
```

**Benefits:**
- ✅ Simple
- ✅ Full control
- ❌ Requires your machine to be on

### Option 3: Cron Job (Mac/Linux)

**Setup once:**
```bash
crontab -e
```

**Add this line:**
```
0 18 * * * cd /Users/krishnashukla/Desktop/NSE/CascadeProjects/windsurf-project && /usr/bin/python3 fetch_fii_dii_daily.py && /usr/bin/git add fii_dii_data.json && /usr/bin/git commit -m "Update FII/DII $(date +'%Y-%m-%d')" && /usr/bin/git push origin main
```

**Benefits:**
- ✅ Automatic on your machine
- ❌ Requires your machine to be on at 6 PM

## Testing:

### Test the fetch script:
```bash
python fetch_fii_dii_daily.py
```

### Check the JSON file:
```bash
cat fii_dii_data.json
```

### Test in your app:
1. Deploy to cloud
2. Check logs for: `FII/DII: Loaded from JSON file`
3. Should show data immediately!

## Data Flow:

**Priority Order:**
1. **JSON File** (fii_dii_data.json) ← **FASTEST, ALWAYS WORKS**
2. NSE API (blocked on cloud)
3. NSE Website (blocked on cloud)
4. MoneyControl (may work on cloud)
5. Session cache (if previously fetched)
6. Placeholder (shows N/A)

## Monitoring:

**Check if GitHub Actions is running:**
1. Go to your repo on GitHub
2. Click "Actions" tab
3. Should see "Fetch FII/DII Data Daily" workflow
4. Check run history and logs

**Check last update:**
Look at `fii_dii_data.json` in your repo:
- `fetched_at`: When data was last fetched
- `date`: Trading date of the data
- `source`: Where data came from (NSE API or MoneyControl)

## Current Data (as of commit):

```json
{
  "fii": {
    "buy": 622.39,
    "sell": 525.67,
    "net": 96.72
  },
  "dii": {
    "buy": 324.13,
    "sell": 931.14,
    "net": -607.01
  },
  "status": "success",
  "source": "NSE API",
  "fetched_at": "2025-10-21 23:09:XX UTC",
  "date": "21-Oct-2025"
}
```

## Troubleshooting:

**If data shows N/A on cloud:**
1. Check if `fii_dii_data.json` exists in repo
2. Check file content is valid JSON
3. Check cloud logs for "JSON file read failed"
4. Verify file is committed and pushed

**If GitHub Actions not running:**
1. Check if workflow file is in `.github/workflows/`
2. Check Actions tab for error messages
3. Manually trigger: Actions → Fetch FII/DII Data Daily → Run workflow

**If fetch script fails:**
1. Check internet connection
2. NSE might be down (try MoneyControl)
3. Check error messages in output
4. Try running at different time

## Next Steps:

1. **Deploy to cloud** - Data will show immediately from JSON file
2. **Set up GitHub Actions** (Option 1) - Upload workflow file manually
3. **Or run manually** once daily (Option 2)
4. **Monitor** - Check Actions tab to ensure it runs daily

Your FII/DII data will now work on cloud even when your machine is off! 🎉
