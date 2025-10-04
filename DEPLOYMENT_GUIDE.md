# Deployment Guide - Keep App Running Always

## Option 1: Run on Startup (Mac) - Simplest

### Method A: Using LaunchAgent (Recommended)

1. Create a launch agent file:

```bash
nano ~/Library/LaunchAgents/com.stocktracker.plist
```

2. Paste this content (replace YOUR_USERNAME with your actual username):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.stocktracker</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/YOUR_USERNAME/Desktop/nse/CascadeProjects/windsurf-project/venv/bin/streamlit</string>
        <string>run</string>
        <string>/Users/YOUR_USERNAME/Desktop/nse/CascadeProjects/windsurf-project/app.py</string>
        <string>--server.port</string>
        <string>8501</string>
        <string>--server.headless</string>
        <string>true</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/YOUR_USERNAME/Desktop/nse/CascadeProjects/windsurf-project/logs/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/YOUR_USERNAME/Desktop/nse/CascadeProjects/windsurf-project/logs/stderr.log</string>
</dict>
</plist>
```

3. Create logs directory:
```bash
mkdir -p ~/Desktop/test/CascadeProjects/windsurf-project/logs
```

4. Load the launch agent:
```bash
launchctl load ~/Library/LaunchAgents/com.stocktracker.plist
```

5. Start it immediately:
```bash
launchctl start com.stocktracker
```

**To stop:**
```bash
launchctl stop com.stocktracker
launchctl unload ~/Library/LaunchAgents/com.stocktracker.plist
```

### Method B: Using a Startup Script

1. I'll create a startup script for you (see `start_app.sh`)
2. Make it executable: `chmod +x start_app.sh`
3. Add to System Preferences → Users & Groups → Login Items

---

## Option 2: Deploy to Cloud (Always Running) - Best for 24/7

### Streamlit Cloud (FREE & Easiest)

1. **Create GitHub Account** (if you don't have one)
   - Go to https://github.com
   - Sign up for free

2. **Push Your Code to GitHub:**
```bash
cd /Users/krishnashukla/Desktop/nse/CascadeProjects/windsurf-project
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/stock-tracker.git
git push -u origin main
```

3. **Deploy to Streamlit Cloud:**
   - Go to https://streamlit.io/cloud
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Click "Deploy"
   - Your app will be live at: `https://YOUR_APP_NAME.streamlit.app`

**Pros:**
- ✅ FREE
- ✅ Always running (24/7)
- ✅ Accessible from anywhere
- ✅ Auto-updates when you push to GitHub
- ✅ No laptop needed

---

## Option 3: Deploy to Heroku (FREE Tier Available)

1. Install Heroku CLI:
```bash
brew install heroku/brew/heroku
```

2. I'll create the necessary files (Procfile, setup.sh)

3. Deploy:
```bash
heroku login
heroku create your-stock-tracker
git push heroku main
heroku open
```

---

## Option 4: Run as Background Service (Mac)

Use the startup script I'll create below. It will:
- Run in background
- Auto-restart if crashes
- Keep logs
- Survive reboots

---

## Option 5: Docker Container (Advanced)

I can create a Dockerfile if you want to run it in Docker.

---

## Recommended Approach:

**For Personal Use (Your Laptop):**
→ Use **Option 1 (LaunchAgent)** - Runs on startup, always available on your laptop

**For 24/7 Access from Anywhere:**
→ Use **Option 2 (Streamlit Cloud)** - FREE, always running, accessible from any device

**Which option would you like me to set up for you?**
