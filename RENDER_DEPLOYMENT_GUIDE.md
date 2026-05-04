# 🚀 Render Deployment Guide - SparePartFinder

## ✅ Pre-Deployment Checklist

All files have been configured and are ready for deployment:

- ✅ `app.py` - Fixed with safe model loading and correct port binding
- ✅ `requirements.txt` - Clean, production-ready dependencies
- ✅ `Procfile` - Gunicorn configuration
- ✅ `render.yaml` - Complete infrastructure setup
- ✅ `runtime.txt` - Python 3.11.0 specified

## 📋 Render Configuration

### Build Command
```bash
pip install -r requirements.txt
```

### Start Command
```bash
gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --log-level info
```

### Environment Variables (Required)
```
FLASK_ENV=production
USE_POSTGRES=true
DATABASE_URL=<from Render PostgreSQL>
PORT=<auto-set by Render>
```

## 🔧 Deployment Steps

### Option 1: Automatic Deployment (Blueprint)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Render deployment setup"
   git push origin main
   ```

2. **Deploy on Render:**
   - Go to https://render.com/dashboard
   - Click **"New +"** → **"Blueprint"**
   - Connect your GitHub repository
   - Render will detect `render.yaml` and create all services automatically
   - Click **"Apply"**

3. **Wait for deployment** (~5-10 minutes)

4. **Initialize database:**
   ```bash
   curl -X POST https://your-backend-url.onrender.com/api/init-database
   ```

### Option 2: Manual Deployment

1. **Push to GitHub** (same as above)

2. **Create Backend Service:**
   - Go to Render Dashboard
   - Click **"New +"** → **"Web Service"**
   - Connect repository
   - Configure:
     - **Name:** `sparepartfinder-backend`
     - **Region:** Oregon (or closest)
     - **Branch:** `main`
     - **Root Directory:** Leave empty
     - **Runtime:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --log-level info`
   
3. **Add Environment Variables:**
   - `FLASK_ENV` = `production`
   - `USE_POSTGRES` = `true`
   - `DATABASE_URL` = (add after creating database)

4. **Create PostgreSQL Database:**
   - Click **"New +"** → **"PostgreSQL"**
   - Name: `sparepartfinder-db`
   - Region: Same as backend
   - Plan: Free
   - Copy the **Internal Database URL**

5. **Update Backend Environment:**
   - Go to backend service → Environment
   - Add/Update `DATABASE_URL` with the Internal Database URL
   - Save (triggers redeployment)

6. **Create Frontend Service:**
   - Click **"New +"** → **"Static Site"**
   - Connect repository
   - Configure:
     - **Name:** `sparepartfinder-frontend`
     - **Branch:** `main`
     - **Build Command:** `cd frontend && npm install && npm run build`
     - **Publish Directory:** `frontend/dist`
   - Add Environment Variable:
     - `VITE_API_URL` = `https://your-backend-url.onrender.com`
   - Add Rewrite Rule:
     - Source: `/*`
     - Destination: `/index.html`
     - Action: Rewrite

## 🧪 Verification

### 1. Backend Health Check
```bash
curl https://your-backend-url.onrender.com/api/analytics
```

**Expected Response:**
```json
{
  "total_parts": 10,
  "parts_in_stock": 10,
  "total_price_records": 0,
  "model_accuracy": "Check evaluate_model.py for latest metrics"
}
```

### 2. Initialize Database
```bash
curl -X POST https://your-backend-url.onrender.com/api/init-database
```

**Expected Response:**
```json
{
  "message": "Database initialized with 10 parts"
}
```

### 3. Test Frontend
- Open `https://your-frontend-url.onrender.com`
- Upload a test image
- Verify prediction works
- Check price comparison displays

### 4. Automated Health Check
```bash
python health_check.py https://your-backend-url.onrender.com
```

## 📊 Service URLs

After deployment, you'll have:

- **Backend API:** `https://sparepartfinder-backend.onrender.com`
- **Frontend:** `https://sparepartfinder-frontend.onrender.com`
- **Database:** Internal URL (not publicly accessible)

## 🔍 Troubleshooting

### Build Fails

**Issue:** Dependencies fail to install

**Solution:**
```bash
# Check requirements.txt has no syntax errors
cat requirements.txt

# Verify Python version
cat runtime.txt
```

### Model Loading Fails

**Issue:** Model file not found or corrupted

**Solution:**
- Verify `spare_part_model.pth` is committed to git
- Check file size is ~14MB
- Ensure `classes.json` exists

### Database Connection Error

**Issue:** Can't connect to PostgreSQL

**Solution:**
- Verify `DATABASE_URL` environment variable is set
- Check `USE_POSTGRES=true` is set
- Ensure database service is running
- Verify backend and database are in same region

### Frontend Can't Reach Backend

**Issue:** CORS or network errors

**Solution:**
- Verify `VITE_API_URL` is set correctly (no trailing slash)
- Check backend is running and healthy
- Test backend URL directly in browser

### Port Binding Error

**Issue:** App fails to start with port error

**Solution:**
- Verify app.py has: `port = int(os.environ.get("PORT", 10000))`
- Ensure `app.run(host="0.0.0.0", port=port)`
- Check Procfile uses `$PORT` variable

## 💰 Cost

### Free Tier
- Backend: $0/month (spins down after 15 min)
- Database: $0/month (256MB)
- Frontend: $0/month
- **Total: $0/month**

### Production Tier (Recommended)
- Backend Starter: $7/month
- Database Starter: $7/month
- Frontend: $0/month
- **Total: $14/month**

## 🔄 Continuous Deployment

Render automatically deploys when you push to GitHub:

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

## 📝 Important Notes

1. **First deployment takes 5-10 minutes** (installing PyTorch)
2. **Free tier services spin down after 15 minutes** of inactivity
3. **Cold starts take 30-60 seconds** on free tier
4. **Model file must be < 100MB** (current: ~14MB ✅)
5. **Database is automatically backed up** on paid plans

## 🆘 Support

If you encounter issues:

1. Check Render deployment logs
2. Review `DEPLOYMENT.md` for detailed troubleshooting
3. Run `health_check.py` for automated diagnostics
4. Check Render community forums

## ✨ Success Criteria

Deployment is successful when:

- ✅ Backend responds to `/api/analytics`
- ✅ Database has 10 sample parts
- ✅ Frontend loads without errors
- ✅ Image upload and prediction work
- ✅ Price comparison displays results
- ✅ No errors in Render logs

---

**Ready to deploy!** Follow the steps above and your app will be live in ~10 minutes. 🚀
