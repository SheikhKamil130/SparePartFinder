# Render Deployment - Quick Reference

## 🚀 One-Command Deploy

```bash
# 1. Commit and push
git add . && git commit -m "Deploy to Render" && git push origin main

# 2. Go to Render Dashboard → New → Blueprint
# 3. Connect repository (render.yaml auto-detected)
# 4. Click "Apply"

# 5. Initialize database
curl -X POST https://your-backend.onrender.com/api/init-database
```

## 📋 Essential URLs

| Service | URL Pattern |
|---------|-------------|
| Backend | `https://sparepartfinder-backend.onrender.com` |
| Frontend | `https://sparepartfinder-frontend.onrender.com` |
| Database | Internal URL (from Render dashboard) |

## 🔧 Environment Variables

### Backend
```bash
FLASK_ENV=production
USE_POSTGRES=true
DATABASE_URL=<from Render>
PORT=<auto-set>
```

### Frontend
```bash
VITE_API_URL=https://sparepartfinder-backend.onrender.com
```

## ✅ Health Check Commands

```bash
# Set your backend URL
export BACKEND_URL="https://your-backend.onrender.com"

# Quick health check
curl $BACKEND_URL/api/analytics

# Full health check
python health_check.py $BACKEND_URL

# Initialize database
curl -X POST $BACKEND_URL/api/init-database

# Get parts list
curl $BACKEND_URL/api/parts
```

## 🐛 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Check logs for missing dependencies |
| Database connection error | Verify DATABASE_URL is set |
| Frontend can't reach backend | Check VITE_API_URL and CORS |
| Model loading fails | Verify spare_part_model.pth exists |
| Build timeout | Check .slugignore excludes large files |

## 📁 Key Files

| File | Purpose |
|------|---------|
| `Procfile` | Gunicorn start command |
| `render.yaml` | Infrastructure config |
| `requirements.txt` | Python dependencies |
| `runtime.txt` | Python version |
| `.env.example` | Environment template |

## 🔍 Verification Checklist

- [ ] Backend responds at `/api/analytics`
- [ ] Database initialized with parts
- [ ] Frontend loads in browser
- [ ] Image upload works
- [ ] Prediction returns results
- [ ] Price comparison works

## 📚 Documentation

- **Full Guide**: `DEPLOYMENT.md`
- **Checklist**: `DEPLOYMENT_CHECKLIST.md`
- **Local Dev**: `QUICKSTART.md`
- **Implementation**: `.kiro/specs/render-deployment/implementation-summary.md`

## 🆘 Emergency Rollback

```bash
# Via Render Dashboard
# Service → Manual Deploy → Select previous deployment → Deploy

# Via Git
git revert HEAD
git push origin main
```

## 💰 Cost

**Free Tier:**
- Backend: $0/month (spins down after 15 min)
- Database: $0/month (256MB)
- Frontend: $0/month

**Recommended Production:**
- Backend Starter: $7/month
- Database Starter: $7/month
- Total: $14/month

## 🎯 Success Criteria

✅ Backend health check passes
✅ Database has 10+ parts
✅ Frontend loads without errors
✅ Image prediction works
✅ Response time < 5 seconds

---

**Need Help?** See `DEPLOYMENT.md` for detailed instructions.
