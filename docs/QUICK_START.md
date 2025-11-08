# Quick Start Guide - Keep App Running Always

## 🚀 Option 1: Run on Your Mac (Simplest - 5 minutes)

### Step 1: Make scripts executable
```bash
cd /Users/krishnashukla/Desktop/test/CascadeProjects/windsurf-project
chmod +x start_app.sh stop_app.sh
```

### Step 2: Start the app
```bash
./start_app.sh
```

The app will now:
- ✅ Run in the background
- ✅ Auto-restart if it crashes
- ✅ Keep running even if you close Terminal
- ✅ Access at: http://localhost:8501

### Step 3: To stop the app
```bash
./stop_app.sh
```

### Step 4: Make it start on Mac boot (Optional)

1. Open **System Preferences** → **Users & Groups**
2. Click your username
3. Click **Login Items** tab
4. Click the **+** button
5. Navigate to and select `start_app.sh`
6. Done! App will start automatically when you login

---

## 🌐 Option 2: Deploy to Cloud (FREE - Always Running 24/7)

### Using Streamlit Cloud (Recommended - Easiest)

**Step 1: Create GitHub account** (if you don't have one)
- Go to https://github.com and sign up

**Step 2: Install Git** (if not installed)
```bash
brew install git
```

**Step 3: Push code to GitHub**
```bash
cd /Users/krishnashukla/Desktop/test/CascadeProjects/windsurf-project

# Initialize git
git init
git add .
git commit -m "Initial commit - Stock Tracker"

# Create a new repository on GitHub (via website)
# Then connect it:
git remote add origin https://github.com/YOUR_USERNAME/stock-tracker.git
git branch -M main
git push -u origin main
```

**Step 4: Deploy to Streamlit Cloud**
1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repository: `stock-tracker`
5. Main file path: `app.py`
6. Click **"Deploy"**

**Done!** Your app will be live at:
```
https://YOUR_USERNAME-stock-tracker.streamlit.app
```

**Benefits:**
- ✅ FREE forever
- ✅ Runs 24/7 (no laptop needed)
- ✅ Accessible from anywhere (phone, tablet, any computer)
- ✅ Auto-updates when you push changes
- ✅ HTTPS secure
- ✅ No maintenance needed

---

## 📊 Option 3: Check if App is Running

```bash
# Check if running
ps aux | grep streamlit

# View logs
tail -f logs/app.log

# View startup logs
tail -f logs/startup.log
```

---

## 🔧 Troubleshooting

### App won't start?
```bash
# Check if port 8501 is already in use
lsof -i :8501

# Kill any process using that port
kill -9 $(lsof -t -i:8501)

# Try starting again
./start_app.sh
```

### Can't access the app?
- Make sure you're using: http://localhost:8501
- Check firewall settings
- Check logs: `cat logs/app.log`

### Want to change the port?
Edit `start_app.sh` and change `8501` to your desired port

---

## 📝 Summary

**For Local Use (Your Mac):**
```bash
./start_app.sh    # Start
./stop_app.sh     # Stop
```

**For 24/7 Cloud Access:**
→ Deploy to Streamlit Cloud (see Option 2 above)

**Access:**
- Local: http://localhost:8501
- Cloud: https://your-app-name.streamlit.app

---

## 🎯 Recommended Setup

1. **Development**: Use local setup (Option 1)
2. **Production**: Deploy to Streamlit Cloud (Option 2)
3. **Both**: Run locally for testing, cloud for 24/7 access

Need help? Check the logs in the `logs/` directory!
