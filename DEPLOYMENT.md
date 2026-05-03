# Deployment Guide: SparePartFinder on Render

This guide walks you through deploying the SparePartFinder application to Render's cloud platform.

## Prerequisites

- GitHub account with repository access
- Render account (free tier available at https://render.com)
- Git installed locally
- All project files committed to repository

## Architecture Overview

The deployment consists of three services:
1. **Backend Service**: Flask API with PyTorch ML model (Web Service)
2. **Frontend Service**: React SPA built with Vite (Static Site)
3. **Database Service**: PostgreSQL database (Managed Database)

## Deployment Steps

### Step 1: Prepare Repository

Ensure all required files are committed:

```bash
# Check git status
git status

# Add all deployment files
git add Procfile render.yaml requirements.txt
git add app.py frontend/src/services/api.js
git add spare_part_model.pth classes.json
git add AutoMobile_Dataset/

# Commit changes
git commit -m "Add Render deployment configuration"

# Push to GitHub
git push origin main
```

**Important Files:**
- `Procfile` - Defines how to start the backend service
- `render.yaml` - Infrastructure as code configuration
- `requirements.txt` - Python dependencies with pinned versions
- `spare_part_model.pth` - Trained PyTorch model (~14MB)
- `classes.json` - Part classification labels
- `AutoMobile_Dataset/` - Dataset for reference (optional in production)

### Step 2: Create Render Account

1. Go to https://render.com
2. Sign up with GitHub account
3. Authorize Render to access your repositories

### Step 3: Deploy Backend Service

#### Option A: Using render.yaml (Recommended)

1. In Render Dashboard, click **"New +"** → **"Blueprint"**
2. Connect your GitHub repository
3. Render will detect `render.yaml` and create all services automatically
4. Review the configuration and click **"Apply"**

#### Option B: Manual Setup

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: `sparepartfinder-backend`
   - **Region**: Oregon (or closest to you)
   - **Branch**: `main`
   - **Root Directory**: Leave empty (or `SparePartFinder` if nested)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --log-level info`

4. Add Environment Variables:
   - `FLASK_ENV` = `production`
   - `USE_POSTGRES` = `true`
   - `DATABASE_URL` = (will be added after database creation)

5. Click **"Create Web Service"**

### Step 4: Create PostgreSQL Database

1. Click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `sparepartfinder-db`
   - **Region**: Same as backend service
   - **Plan**: Free tier
3. Click **"Create Database"**
4. Wait for database to provision (~2 minutes)
5. Copy the **Internal Database URL**

### Step 5: Connect Database to Backend

1. Go to backend service settings
2. Navigate to **"Environment"** tab
3. Add/Update environment variable:
   - `DATABASE_URL` = (paste the Internal Database URL)
4. Save changes (service will auto-redeploy)

### Step 6: Initialize Database

Once backend is running:

```bash
# Get your backend URL (e.g., https://sparepartfinder-backend.onrender.com)
BACKEND_URL="https://your-backend-url.onrender.com"

# Initialize database with sample parts
curl -X POST $BACKEND_URL/api/init-database

# Verify database
curl $BACKEND_URL/api/analytics
```

Expected response:
```json
{
  "total_parts": 10,
  "parts_in_stock": 10,
  "total_price_records": 0,
  "model_accuracy": "Check evaluate_model.py for latest metrics"
}
```

### Step 7: Deploy Frontend Service

1. Click **"New +"** → **"Static Site"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `sparepartfinder-frontend`
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`

4. Add Environment Variable:
   - `VITE_API_URL` = `https://sparepartfinder-backend.onrender.com` (your backend URL)

5. Click **"Create Static Site"**

### Step 8: Configure SPA Routing

For React Router to work correctly:

1. Go to frontend service settings
2. Navigate to **"Redirects/Rewrites"** tab
3. Add rewrite rule:
   - **Source**: `/*`
   - **Destination**: `/index.html`
   - **Action**: Rewrite

### Step 9: Update CORS (if needed)

If you encounter CORS errors, update `app.py`:

```python
# Update CORS configuration
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://sparepartfinder-frontend.onrender.com",
            "http://localhost:5173"
        ]
    }
})
```

Commit and push changes to trigger redeployment.

### Step 10: Verify Deployment

1. **Backend Health Check**:
   ```bash
   curl https://sparepartfinder-backend.onrender.com/api/analytics
   ```

2. **Frontend Access**:
   - Open `https://sparepartfinder-frontend.onrender.com`
   - Upload a test image
   - Verify prediction and price comparison work

3. **Database Verification**:
   ```bash
   curl https://sparepartfinder-backend.onrender.com/api/parts
   ```

## Configuration Reference

### Backend Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `PORT` | Auto-set by Render | Dynamic port for service binding |
| `FLASK_ENV` | `production` | Disables debug mode |
| `USE_POSTGRES` | `true` | Enables PostgreSQL instead of SQLite |
| `DATABASE_URL` | Auto-set from database | PostgreSQL connection string |

### Frontend Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `VITE_API_URL` | Backend URL | Production API endpoint |

## Troubleshooting

### Backend Won't Start

**Symptom**: Service shows "Deploy failed" or crashes immediately

**Solutions**:
1. Check build logs for missing dependencies
2. Verify `requirements.txt` includes all packages
3. Ensure `spare_part_model.pth` is committed (check file size < 100MB)
4. Check that `classes.json` exists in repository

**Common Issues**:
```bash
# If torch installation fails, check Python version
# Render uses Python 3.11 by default

# If model file is too large, use Git LFS
git lfs track "*.pth"
git add .gitattributes spare_part_model.pth
git commit -m "Track model with Git LFS"
```

### Database Connection Errors

**Symptom**: `sqlalchemy.exc.OperationalError: could not connect to server`

**Solutions**:
1. Verify `DATABASE_URL` is set correctly
2. Check database service is running
3. Ensure backend and database are in same region
4. Verify `USE_POSTGRES=true` is set

### Frontend Can't Connect to Backend

**Symptom**: Network errors or 404 on API calls

**Solutions**:
1. Verify `VITE_API_URL` is set correctly (no trailing slash)
2. Check CORS configuration in `app.py`
3. Ensure backend service is running
4. Check browser console for exact error

**Test API connectivity**:
```javascript
// In browser console on frontend site
fetch('https://sparepartfinder-backend.onrender.com/api/analytics')
  .then(r => r.json())
  .then(console.log)
```

### Model Loading Fails

**Symptom**: `RuntimeError: Error loading model` or `FileNotFoundError`

**Solutions**:
1. Verify `spare_part_model.pth` is in repository root
2. Check file wasn't corrupted during git operations
3. Ensure model architecture matches in `app.py`
4. Verify `classes.json` has correct number of classes

### Slow Cold Starts

**Symptom**: First request after inactivity takes 30+ seconds

**Explanation**: Render's free tier spins down services after 15 minutes of inactivity

**Solutions**:
1. Upgrade to paid tier for always-on services
2. Implement a keep-alive ping service
3. Add loading indicator in frontend for cold starts

### Build Timeout

**Symptom**: Build exceeds time limit

**Solutions**:
1. Remove unnecessary files from repository
2. Use `.dockerignore` or `.slugignore` to exclude large files
3. Consider using pre-built Docker image

## Performance Optimization

### Backend Optimization

1. **Gunicorn Workers**:
   ```bash
   # For paid tiers with more RAM
   gunicorn app:app --workers 2 --bind 0.0.0.0:$PORT --timeout 120
   ```

2. **Model Caching**:
   - Model is loaded once at startup (already implemented)
   - Consider using Redis for prediction caching

3. **Database Connection Pooling**:
   ```python
   app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
       'pool_size': 10,
       'pool_recycle': 3600,
   }
   ```

### Frontend Optimization

1. **Build Optimization**:
   ```javascript
   // vite.config.js
   export default defineConfig({
     build: {
       rollupOptions: {
         output: {
           manualChunks: {
             vendor: ['react', 'react-dom', 'react-router-dom'],
             charts: ['chart.js', 'react-chartjs-2']
           }
         }
       }
     }
   })
   ```

2. **Image Optimization**:
   - Compress uploaded images before sending
   - Use WebP format where supported

## Monitoring and Logs

### View Logs

**Backend Logs**:
1. Go to backend service in Render dashboard
2. Click **"Logs"** tab
3. Monitor for errors and performance issues

**Frontend Logs**:
- Static sites don't have runtime logs
- Use browser console for client-side debugging

### Key Metrics to Monitor

- **Response Time**: API endpoints should respond < 2 seconds
- **Error Rate**: Should be < 1% of requests
- **Database Connections**: Monitor for connection pool exhaustion
- **Memory Usage**: PyTorch model uses ~500MB RAM

## Scaling Considerations

### Free Tier Limitations

- **Backend**: 512MB RAM, shared CPU, spins down after 15 min inactivity
- **Database**: 256MB storage, 97 connection limit
- **Frontend**: 100GB bandwidth/month

### Upgrade Path

1. **Starter Plan** ($7/month):
   - Always-on services
   - 512MB RAM
   - Better performance

2. **Standard Plan** ($25/month):
   - 2GB RAM
   - Multiple workers
   - Custom domains

## Security Best Practices

1. **Environment Variables**:
   - Never commit `.env` file
   - Use Render's environment variable management
   - Rotate database credentials periodically

2. **CORS Configuration**:
   - Restrict origins to your frontend domain
   - Don't use `origins="*"` in production

3. **File Upload Security**:
   - Already implemented: file type validation
   - Already implemented: secure_filename()
   - Consider: virus scanning for production

4. **Database Security**:
   - Use Render's internal database URL (not public)
   - Enable SSL for database connections
   - Regular backups (automatic on paid tiers)

## Backup and Recovery

### Database Backups

**Manual Backup**:
```bash
# From Render dashboard, go to database service
# Click "Backups" tab → "Create Backup"
```

**Automated Backups**:
- Available on paid database plans
- Daily backups with 7-day retention

### Model Versioning

```bash
# Tag model versions in git
git tag -a v1.0-model -m "MobileNetV2 trained on 49 classes"
git push origin v1.0-model
```

## Cost Estimation

### Free Tier (Current Setup)
- Backend Web Service: $0
- PostgreSQL Database: $0
- Frontend Static Site: $0
- **Total**: $0/month

**Limitations**:
- Services spin down after 15 minutes
- 750 hours/month free (shared across services)
- Limited resources

### Production Setup (Recommended)
- Backend Web Service (Starter): $7/month
- PostgreSQL Database (Starter): $7/month
- Frontend Static Site: $0
- **Total**: $14/month

## Continuous Deployment

Render automatically deploys when you push to the connected branch:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push origin main

# Render will automatically:
# 1. Detect the push
# 2. Run build commands
# 3. Deploy new version
# 4. Run health checks
```

### Deployment Notifications

1. Go to service settings
2. Navigate to **"Notifications"** tab
3. Add email or Slack webhook for deployment alerts

## Support and Resources

- **Render Documentation**: https://render.com/docs
- **Render Community**: https://community.render.com
- **Flask Documentation**: https://flask.palletsprojects.com
- **PyTorch Documentation**: https://pytorch.org/docs
- **React Documentation**: https://react.dev

## Next Steps

After successful deployment:

1. ✅ Set up custom domain (optional)
2. ✅ Configure SSL certificate (automatic with custom domain)
3. ✅ Set up monitoring and alerts
4. ✅ Implement CI/CD pipeline
5. ✅ Add more sample parts to database
6. ✅ Optimize model for production inference
7. ✅ Implement caching strategy
8. ✅ Add user authentication (if needed)

## Rollback Procedure

If deployment fails:

1. Go to service in Render dashboard
2. Click **"Manual Deploy"** tab
3. Select previous successful deployment
4. Click **"Deploy"**

Or via git:

```bash
# Revert to previous commit
git revert HEAD
git push origin main
```

---

**Deployment Checklist**:
- [ ] All files committed to GitHub
- [ ] Backend service created and running
- [ ] Database created and connected
- [ ] Database initialized with sample data
- [ ] Frontend service created and running
- [ ] API URL configured in frontend
- [ ] CORS configured correctly
- [ ] Health checks passing
- [ ] Test image upload and prediction
- [ ] Test price comparison feature
- [ ] Monitor logs for errors

**Congratulations!** Your SparePartFinder application is now live on Render! 🚀
