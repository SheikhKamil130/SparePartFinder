# Deployment Checklist

Use this checklist to ensure all deployment requirements are met before and after deploying to Render.

## Pre-Deployment Checklist

### Repository Preparation ✅

- [x] `requirements.txt` with pinned versions exists
- [x] `Procfile` specifies gunicorn start command
- [x] `render.yaml` contains all service configurations
- [x] `runtime.txt` specifies Python version
- [x] `spare_part_model.pth` is committed (~14MB)
- [x] `classes.json` is committed
- [x] `AutoMobile_Dataset/` is committed (or excluded via .slugignore)
- [x] `.gitignore` prevents sensitive files from being committed
- [x] `.env.example` provides template for environment variables
- [x] `static/uploads/.gitkeep` ensures directory exists

### Backend Configuration ✅

- [x] `app.py` reads PORT from environment variable
- [x] `app.py` binds to 0.0.0.0 for external connections
- [x] `app.py` handles DATABASE_URL with postgres:// → postgresql:// conversion
- [x] `app.py` supports USE_POSTGRES environment variable
- [x] `app.py` has CORS configuration
- [x] `app.py` validates file uploads (extensions, size)
- [x] `app.py` uses secure_filename() for uploads
- [x] `app.py` loads model with CPU map_location
- [x] `app.py` has error handling and logging
- [x] `app.py` creates database tables on startup
- [x] Health check endpoint exists (`/api/analytics`)

### Frontend Configuration ✅

- [x] `package.json` has build script
- [x] `vite.config.js` configured for development proxy
- [x] `api.js` uses VITE_API_URL environment variable
- [x] `api.js` falls back to empty string for development
- [x] Frontend builds to `dist/` directory

### Documentation ✅

- [x] `README.md` updated with deployment info
- [x] `DEPLOYMENT.md` comprehensive deployment guide
- [x] `QUICKSTART.md` for local development
- [x] `DEPLOYMENT_CHECKLIST.md` (this file)

## Git Preparation

```bash
# Check status
git status

# Add all deployment files
git add .

# Commit
git commit -m "Add Render deployment configuration"

# Push to GitHub
git push origin main
```

## Render Deployment Steps

### 1. Backend Service Setup

- [ ] Create Web Service in Render
- [ ] Connect GitHub repository
- [ ] Configure build command: `pip install -r requirements.txt`
- [ ] Configure start command: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --log-level info`
- [ ] Set environment variables:
  - [ ] `FLASK_ENV=production`
  - [ ] `USE_POSTGRES=true`
  - [ ] `PYTHON_VERSION=3.11.0`
- [ ] Set health check path: `/api/analytics`
- [ ] Deploy and wait for completion

### 2. Database Service Setup

- [ ] Create PostgreSQL database in Render
- [ ] Use same region as backend
- [ ] Select free tier plan
- [ ] Wait for database provisioning
- [ ] Copy Internal Database URL

### 3. Connect Database to Backend

- [ ] Go to backend service environment variables
- [ ] Add `DATABASE_URL` with Internal Database URL
- [ ] Save (triggers automatic redeployment)
- [ ] Wait for redeployment to complete

### 4. Initialize Database

```bash
# Replace with your actual backend URL
BACKEND_URL="https://sparepartfinder-backend.onrender.com"

# Initialize database with sample parts
curl -X POST $BACKEND_URL/api/init-database

# Verify initialization
curl $BACKEND_URL/api/analytics
```

Expected output:
```json
{
  "total_parts": 10,
  "parts_in_stock": 10,
  "total_price_records": 0,
  "model_accuracy": "Check evaluate_model.py for latest metrics"
}
```

### 5. Frontend Service Setup

- [ ] Create Static Site in Render
- [ ] Connect GitHub repository
- [ ] Configure build command: `cd frontend && npm install && npm run build`
- [ ] Configure publish directory: `frontend/dist`
- [ ] Set environment variable:
  - [ ] `VITE_API_URL=https://sparepartfinder-backend.onrender.com` (your backend URL)
- [ ] Configure rewrite rule: `/*` → `/index.html`
- [ ] Deploy and wait for completion

## Post-Deployment Verification

### Backend Health Checks

```bash
# Set your backend URL
BACKEND_URL="https://sparepartfinder-backend.onrender.com"

# Test analytics endpoint
curl $BACKEND_URL/api/analytics

# Test parts list
curl $BACKEND_URL/api/parts

# Test scraping stats
curl $BACKEND_URL/api/scraping-stats

# Or use the health check script
python health_check.py $BACKEND_URL
```

- [ ] Analytics endpoint returns 200 OK
- [ ] Parts list returns array of parts
- [ ] Scraping stats endpoint responds
- [ ] Response time < 5 seconds

### Frontend Verification

- [ ] Open frontend URL in browser
- [ ] Page loads without errors
- [ ] No console errors in browser DevTools
- [ ] Upload test image from `AutoMobile_Dataset/test/BATTERY/1.jpg`
- [ ] Prediction returns "BATTERY"
- [ ] Confidence score displayed
- [ ] Price comparison shows results
- [ ] Navigation works (if multi-page)

### Integration Testing

- [ ] Frontend can communicate with backend
- [ ] Image upload works end-to-end
- [ ] Predictions are accurate
- [ ] Price scraping returns results
- [ ] Database operations work (create, read)
- [ ] Analytics dashboard displays data

### Performance Checks

- [ ] Backend responds within 2 seconds (warm)
- [ ] Frontend loads within 3 seconds
- [ ] Image prediction completes within 5 seconds
- [ ] No memory leaks or crashes
- [ ] Cold start completes within 60 seconds

## Monitoring Setup

- [ ] Enable email notifications for deployment failures
- [ ] Set up Slack webhook for alerts (optional)
- [ ] Monitor logs for errors
- [ ] Check resource usage (RAM, CPU)
- [ ] Set up uptime monitoring (optional)

## Security Verification

- [ ] `FLASK_ENV=production` (debug mode disabled)
- [ ] No sensitive data in logs
- [ ] CORS configured for specific origins
- [ ] File upload validation working
- [ ] Database uses internal URL (not public)
- [ ] `.env` file not committed to git

## Troubleshooting Checklist

If deployment fails, check:

### Backend Issues

- [ ] Build logs for dependency errors
- [ ] Model file size < 100MB (use Git LFS if larger)
- [ ] `classes.json` exists and is valid JSON
- [ ] Python version matches `runtime.txt`
- [ ] All imports are in `requirements.txt`
- [ ] Database connection string is correct
- [ ] Environment variables are set correctly

### Frontend Issues

- [ ] Build logs for npm errors
- [ ] `VITE_API_URL` is set correctly (no trailing slash)
- [ ] Backend URL is accessible from frontend
- [ ] CORS headers are present in API responses
- [ ] Rewrite rule is configured for SPA routing

### Database Issues

- [ ] Database service is running
- [ ] `DATABASE_URL` is set in backend
- [ ] Backend and database in same region
- [ ] Connection string format is correct
- [ ] Tables were created successfully

## Rollback Procedure

If deployment has critical issues:

1. [ ] Go to Render dashboard
2. [ ] Select the service
3. [ ] Click "Manual Deploy" tab
4. [ ] Select previous successful deployment
5. [ ] Click "Deploy"

Or via git:

```bash
git revert HEAD
git push origin main
```

## Post-Deployment Tasks

- [ ] Update DNS records (if using custom domain)
- [ ] Configure SSL certificate (automatic with custom domain)
- [ ] Set up monitoring and alerts
- [ ] Document any configuration changes
- [ ] Update team on new URLs
- [ ] Test from different networks/devices
- [ ] Monitor logs for first 24 hours

## Optimization Tasks (Optional)

- [ ] Enable CDN for static assets
- [ ] Implement Redis caching for predictions
- [ ] Add database connection pooling
- [ ] Optimize model for faster inference
- [ ] Compress images before upload
- [ ] Add rate limiting
- [ ] Implement user authentication
- [ ] Set up automated backups

## Success Criteria

Deployment is successful when:

- ✅ Backend service is running and healthy
- ✅ Database is connected and initialized
- ✅ Frontend is accessible and functional
- ✅ Image upload and prediction work end-to-end
- ✅ Price comparison returns results
- ✅ No errors in logs
- ✅ Response times are acceptable
- ✅ All health checks pass

## Support Resources

- **Render Docs**: https://render.com/docs
- **Flask Docs**: https://flask.palletsprojects.com
- **PyTorch Docs**: https://pytorch.org/docs
- **React Docs**: https://react.dev
- **Project Docs**: See `DEPLOYMENT.md` and `QUICKSTART.md`

---

**Deployment Date**: _________________

**Deployed By**: _________________

**Backend URL**: _________________

**Frontend URL**: _________________

**Database**: _________________

**Notes**: _________________
