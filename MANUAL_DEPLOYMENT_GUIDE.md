# 🚀 Manual Deployment Guide - Render Free Tier

## Overview

This guide shows you how to deploy SparePartFinder on Render's **FREE TIER** without using Blueprint or PostgreSQL.

**Strategy:**
- ✅ Manual service creation (no Blueprint)
- ✅ SQLite database (no PostgreSQL needed)
- ✅ Free tier compatible
- ✅ No payment required

---

## ✅ Pre-Deployment Checklist

All files are already configured:

- ✅ `app.py` - Port binding configured
- ✅ `requirements.txt` - Clean and complete
- ✅ `Procfile` - Gunicorn configuration
- ✅ `frontend/` - React app with Vite
- ✅ SQLite fallback - Works without PostgreSQL

---

## 📋 Part 1: Deploy Backend (Flask API)

### Step 1: Create Web Service

1. Go to https://render.com/dashboard
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `SheikhKamil130/SparePartFinder`
4. Click **"Connect"**

### Step 2: Configure Backend Service

Fill in the following settings:

| Setting | Value |
|---------|-------|
| **Name** | `sparepartfinder-backend` (or your choice) |
| **Region** | Oregon (or closest to you) |
| **Branch** | `main` |
| **Root Directory** | Leave empty |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120` |
| **Instance Type** | Free |

### Step 3: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these variables:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `USE_POSTGRES` | `false` |
| `PYTHON_VERSION` | `3.11.0` |

**Important:** Set `USE_POSTGRES=false` to use SQLite (free tier)

### Step 4: Deploy Backend

1. Click **"Create Web Service"**
2. Wait for deployment (~5-10 minutes)
3. Watch the logs for any errors
4. Once deployed, note your backend URL: `https://your-backend-name.onrender.com`

### Step 5: Verify Backend

Test the backend:

```bash
# Replace with your actual backend URL
curl https://your-backend-name.onrender.com/api/analytics
```

**Expected Response:**
```json
{
  "total_parts": 0,
  "parts_in_stock": 0,
  "total_price_records": 0,
  "model_accuracy": "Check evaluate_model.py for latest metrics"
}
```

### Step 6: Initialize Database

```bash
curl -X POST https://your-backend-name.onrender.com/api/init-database
```

**Expected Response:**
```json
{
  "message": "Database initialized with 10 parts"
}
```

---

## 📋 Part 2: Deploy Frontend (React Static Site)

### Step 1: Create Static Site

1. Go to https://render.com/dashboard
2. Click **"New +"** → **"Static Site"**
3. Connect the same GitHub repository
4. Click **"Connect"**

### Step 2: Configure Frontend Service

Fill in the following settings:

| Setting | Value |
|---------|-------|
| **Name** | `sparepartfinder-frontend` (or your choice) |
| **Branch** | `main` |
| **Root Directory** | Leave empty |
| **Build Command** | `cd frontend && npm install && npm run build` |
| **Publish Directory** | `frontend/dist` |

### Step 3: Add Environment Variable

Click **"Advanced"** → **"Add Environment Variable"**

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://your-backend-name.onrender.com` |

**Important:** Replace with your actual backend URL (no trailing slash)

### Step 4: Configure SPA Routing

Scroll down to **"Redirects/Rewrites"**

Add a rewrite rule:

| Field | Value |
|-------|-------|
| **Source** | `/*` |
| **Destination** | `/index.html` |
| **Action** | Rewrite |

### Step 5: Deploy Frontend

1. Click **"Create Static Site"**
2. Wait for deployment (~3-5 minutes)
3. Watch the logs for any errors
4. Once deployed, note your frontend URL: `https://your-frontend-name.onrender.com`

### Step 6: Verify Frontend

1. Open `https://your-frontend-name.onrender.com` in browser
2. Upload a test image
3. Verify prediction works
4. Check price comparison displays

---

## 🎯 Complete Deployment Summary

### Backend Configuration

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120
```

**Environment Variables:**
```
FLASK_ENV=production
USE_POSTGRES=false
PYTHON_VERSION=3.11.0
```

**Health Check Endpoint:**
```
/api/analytics
```

### Frontend Configuration

**Build Command:**
```bash
cd frontend && npm install && npm run build
```

**Publish Directory:**
```
frontend/dist
```

**Environment Variables:**
```
VITE_API_URL=https://your-backend-name.onrender.com
```

**Rewrite Rule:**
```
/* → /index.html (Rewrite)
```

---

## 🔍 Verification Steps

### 1. Backend Health Check
```bash
curl https://your-backend-name.onrender.com/api/analytics
```

### 2. Initialize Database
```bash
curl -X POST https://your-backend-name.onrender.com/api/init-database
```

### 3. Get Parts List
```bash
curl https://your-backend-name.onrender.com/api/parts
```

### 4. Test Frontend
- Open frontend URL in browser
- Upload image from `AutoMobile_Dataset/test/BATTERY/1.jpg`
- Verify prediction shows "BATTERY"
- Check price comparison works

### 5. Automated Health Check
```bash
python health_check.py https://your-backend-name.onrender.com
```

---

## 💰 Cost Breakdown

### Free Tier (This Deployment)

| Service | Cost | Notes |
|---------|------|-------|
| Backend Web Service | $0/month | Spins down after 15 min inactivity |
| Frontend Static Site | $0/month | Always available |
| Database (SQLite) | $0/month | Stored in backend service |
| **Total** | **$0/month** | ✅ Completely free! |

**Limitations:**
- Backend spins down after 15 minutes of inactivity
- Cold start takes 30-60 seconds
- 750 hours/month free (shared across services)
- SQLite data persists but may be lost on redeploy

---

## 🐛 Troubleshooting

### Backend Won't Start

**Issue:** Build fails or service crashes

**Solutions:**
1. Check build logs for missing dependencies
2. Verify `requirements.txt` is correct
3. Ensure `spare_part_model.pth` is committed (~14MB)
4. Check `classes.json` exists

**Common Errors:**
```bash
# If torch installation fails
# Check Python version is 3.11.0

# If model file not found
# Verify file is in repository root
ls -lh spare_part_model.pth
```

### Frontend Can't Reach Backend

**Issue:** Network errors or CORS issues

**Solutions:**
1. Verify `VITE_API_URL` is set correctly (no trailing slash)
2. Check backend is running and healthy
3. Test backend URL directly in browser
4. Verify CORS is enabled in `app.py`

**Test API connectivity:**
```javascript
// In browser console on frontend site
fetch('https://your-backend-name.onrender.com/api/analytics')
  .then(r => r.json())
  .then(console.log)
```

### Model Loading Fails

**Issue:** Predictions return 503 error

**Solutions:**
1. Check backend logs for model loading errors
2. Verify `spare_part_model.pth` is committed
3. Ensure `classes.json` has 49 classes
4. Check file wasn't corrupted during git operations

### Database Errors

**Issue:** SQLite errors or data not persisting

**Solutions:**
1. Verify `USE_POSTGRES=false` is set
2. Check `instance/` directory is created
3. Re-initialize database with `/api/init-database`
4. Note: SQLite data may be lost on redeploy (use PostgreSQL for persistence)

### Slow Cold Starts

**Issue:** First request after inactivity takes 30+ seconds

**Explanation:** Free tier spins down after 15 minutes

**Solutions:**
1. This is normal for free tier
2. Upgrade to paid tier for always-on service ($7/month)
3. Add loading indicator in frontend
4. Use a keep-alive service (external ping)

---

## 🔄 Continuous Deployment

Render automatically redeploys when you push to GitHub:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push origin main

# Render automatically:
# 1. Detects push
# 2. Runs build
# 3. Deploys new version
# 4. Runs health checks
```

---

## 📊 Service URLs

After deployment, you'll have:

- **Backend API:** `https://your-backend-name.onrender.com`
- **Frontend:** `https://your-frontend-name.onrender.com`
- **Database:** SQLite (internal, not accessible externally)

---

## 🎯 Success Criteria

Deployment is successful when:

- ✅ Backend responds to `/api/analytics`
- ✅ Database initialized with 10 parts
- ✅ Frontend loads without errors
- ✅ Image upload works
- ✅ Prediction returns results
- ✅ Price comparison displays
- ✅ No errors in Render logs

---

## 🔧 Optional: Upgrade to PostgreSQL

If you need persistent data:

### Step 1: Create PostgreSQL Database

1. In Render dashboard, click **"New +"** → **"PostgreSQL"**
2. Name: `sparepartfinder-db`
3. Plan: Free (256MB)
4. Region: Same as backend
5. Click **"Create Database"**

### Step 2: Update Backend Environment

1. Go to backend service → **"Environment"**
2. Update `USE_POSTGRES` to `true`
3. Add `DATABASE_URL` with Internal Database URL from PostgreSQL service
4. Save (triggers redeployment)

### Step 3: Re-initialize Database

```bash
curl -X POST https://your-backend-name.onrender.com/api/init-database
```

---

## 📝 Important Notes

1. **Free tier services spin down** after 15 minutes of inactivity
2. **Cold starts take 30-60 seconds** on free tier
3. **SQLite data may be lost** on redeploy (use PostgreSQL for persistence)
4. **Model file must be < 100MB** (current: ~14MB ✅)
5. **Build time is ~5-10 minutes** for first deployment (PyTorch installation)

---

## 🆘 Getting Help

If you encounter issues:

1. Check Render deployment logs
2. Review error messages carefully
3. Test backend endpoints directly
4. Check browser console for frontend errors
5. Run `health_check.py` for diagnostics

---

## 📚 Additional Resources

- **Render Docs:** https://render.com/docs
- **Flask Docs:** https://flask.palletsprojects.com
- **PyTorch Docs:** https://pytorch.org/docs
- **React Docs:** https://react.dev

---

## ✅ Deployment Checklist

### Backend
- [ ] Web Service created
- [ ] Build command set
- [ ] Start command set
- [ ] Environment variables added
- [ ] Service deployed successfully
- [ ] Health check passes
- [ ] Database initialized

### Frontend
- [ ] Static Site created
- [ ] Build command set
- [ ] Publish directory set
- [ ] API URL environment variable set
- [ ] Rewrite rule configured
- [ ] Service deployed successfully
- [ ] Frontend loads in browser
- [ ] Can connect to backend

---

## 🎊 Congratulations!

Your SparePartFinder application is now deployed on Render's free tier!

**Next Steps:**
1. Test all features thoroughly
2. Monitor logs for errors
3. Consider upgrading to paid tier for better performance
4. Add custom domain (optional)
5. Set up monitoring and alerts

---

**Deployment Type:** Manual (No Blueprint)  
**Database:** SQLite (Free Tier)  
**Cost:** $0/month  
**Status:** 🟢 READY TO USE

🚀 **Enjoy your deployed application!**
