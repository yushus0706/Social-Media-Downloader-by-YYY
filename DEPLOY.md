# YYYClips Online Deployment Guide

## 🚀 Live Deployment

**YYYClips is already live at: [https://yyyclips.up.railway.app](https://yyyclips.up.railway.app)**

The app is deployed on Railway with automatic updates from GitHub. Any push to the `main` branch will trigger an automatic deployment.

## Deploy to Railway (Already Done!)

Railway automatically deploys from GitHub with zero configuration. This repo is already configured and deployed.

### How It's Deployed:

1. Repository is connected to Railway
2. Every commit to `main` triggers an automatic build
3. FFmpeg is pre-installed on Railway
4. Your app scales automatically

### If You Want to Deploy Your Own Fork:

1. **Go to [railway.app](https://railway.app)**
   - Sign up with GitHub (connect your account)

2. **Create New Project**
   - Click "Create New Project"
   - Select "Deploy from GitHub repo"
   - Choose your fork of `SocialMedia-Downloader-by-YYY`

3. **Deploy**
   - Railway auto-detects the Python project
   - Click "Deploy"
   - Your app will be live in ~2-5 minutes

---

## Deploy to Render (Alternative)

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repo
5. Set Build Command: `pip install -r requirements.txt`
6. Set Start Command: `python -m uvicorn main:app --host 0.0.0.0 --port 8080`
7. Deploy

---

## Important Notes

- **FFmpeg:** These cloud platforms have FFmpeg pre-installed, so audio/video conversion will work
- **Storage:** Downloaded files are temporary and automatically cleaned up
- **No Database:** The app is stateless, so it scales easily
- **Free Tier:** Both Railway and Render offer free monthly credits

---

## Local Development Still Works

```powershell
.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Then open `http://127.0.0.1:8000`
