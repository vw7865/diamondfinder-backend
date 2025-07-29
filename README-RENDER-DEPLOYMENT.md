# DiamondFinder Backend - Render.com Deployment

This guide will help you deploy the DiamondFinder backend to Render.com for free hosting.

## 🚀 Quick Deployment

### Step 1: Prepare Your Repository

1. **Ensure all files are committed to GitHub:**
   ```bash
   git add .
   git commit -m "Deploy to Render.com"
   git push origin main
   ```

2. **Required files in your repository:**
   - ✅ `server_api.py` - Main FastAPI server
   - ✅ `server_enricher_v2.py` - LunarClient data enrichment
   - ✅ `requirements.txt` - Python dependencies
   - ✅ `render.yaml` - Render.com configuration
   - ✅ `enriched_servers.json` - Server data (optional, will be generated)

### Step 2: Deploy to Render.com

1. **Go to [Render.com Dashboard](https://dashboard.render.com)**
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repository**
4. **Configure the service:**
   - **Name:** `diamondfinder-backend`
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python server_api.py`
   - **Plan:** `Free`

5. **Click "Create Web Service"**

### Step 3: Verify Deployment

Once deployed, your API will be available at:
- **🌐 Main URL:** https://diamondfinder-backend.onrender.com
- **📊 Health Check:** https://diamondfinder-backend.onrender.com/health
- **📋 Server Data:** https://diamondfinder-backend.onrender.com/enriched_servers.json

## 📋 API Endpoints

| Endpoint | Description | Example |
|----------|-------------|---------|
| `GET /` | API information | `https://diamondfinder-backend.onrender.com/` |
| `GET /health` | Health check | `https://diamondfinder-backend.onrender.com/health` |
| `GET /enriched_servers.json` | Server data | `https://diamondfinder-backend.onrender.com/enriched_servers.json` |
| `GET /servers/count` | Server count | `https://diamondfinder-backend.onrender.com/servers/count` |

## 🔧 Configuration

### Environment Variables (Auto-configured)
- `PYTHON_VERSION=3.11.0`
- `PYTHONUNBUFFERED=1`

### Health Checks
- **Path:** `/health`
- **Interval:** 30 seconds
- **Timeout:** 10 seconds

## 📱 iOS App Integration

Update your iOS app's `EnrichedServerService.swift` to use the Render.com URL:

```swift
// Change from localhost to Render.com URL
private let baseURL = "https://diamondfinder-backend.onrender.com"
```

## 🚨 Troubleshooting

### Common Issues

1. **Build Fails**
   - Check `requirements.txt` has all dependencies
   - Verify Python version compatibility
   - Check Render.com logs for errors

2. **Service Won't Start**
   - Verify `startCommand` is correct
   - Check if port 8000 is properly configured
   - Review application logs

3. **Health Check Fails**
   - Ensure `/health` endpoint returns 200
   - Check if service is responding
   - Verify CORS settings

### Debugging

1. **Check Render.com Logs:**
   - Go to your service dashboard
   - Click "Logs" tab
   - Look for error messages

2. **Test Locally First:**
   ```bash
   pip install -r requirements.txt
   python server_api.py
   curl http://localhost:8000/health
   ```

3. **Verify API Response:**
   ```bash
   curl https://diamondfinder-backend.onrender.com/health
   ```

## 🔄 Auto-Deployment

Render.com will automatically:
- ✅ Deploy on every push to main branch
- ✅ Run health checks every 30 seconds
- ✅ Restart service on failures
- ✅ Scale based on traffic (free tier limitations)

## 💰 Free Tier Limitations

- **Build time:** 500 minutes/month
- **Runtime:** 750 hours/month
- **Sleep after inactivity:** 15 minutes
- **Cold start:** ~30 seconds after sleep

## 📞 Support

- **Render.com Docs:** https://render.com/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Service Dashboard:** https://dashboard.render.com

---

**🎯 Your API will be live at:** https://diamondfinder-backend.onrender.com 