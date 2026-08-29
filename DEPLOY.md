# YYYClips Online Deployment Guide

## Deploy to Railway (Recommended - Easiest)

Railway automatically deploys from GitHub with zero configuration needed.

### Steps:

1. **Go to [railway.app](https://railway.app)**
   - Sign up with GitHub (connect your account)

2. **Create New Project**
   - Click "Create New Project"
   - Select "Deploy from GitHub repo"
   - Choose `yushus0706/Social-Media-Downloader-by-YYY`

3. **Add Variables**
   - Railway will automatically detect the Python project
   - No additional environment variables needed

4. **Deploy**
   - Click "Deploy"
   - Railway builds and deploys automatically
   - You'll get a public URL in ~2-5 minutes

5. **Your App is Live!**
   - Share the URL with anyone
   - No local installation needed

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
