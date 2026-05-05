# 🚀 Manual Deployment - Quick Reference

## Backend (Web Service)

### Configuration
```
Name: sparepartfinder-backend
Runtime: Python 3
Branch: main
```

### Commands
```bash
Build: pip install -r requirements.txt
Start: gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120
```

### Environment Variables
```
FLASK_ENV=production
USE_POSTGRES=false
PYTHON_VERSION=3.11.0
```

### Verify
```bash
curl https://your-backend.onrender.com/api/analytics
curl -X POST https://your-backend.onrender.com/api/init-database
```

---

## Frontend (Static Site)

### Configuration
```
Name: sparepartfinder-frontend
Branch: main
```

### Commands
```bash
Build: cd frontend && npm install && npm run build
Publish: frontend/dist
```

### Environment Variables
```
VITE_API_URL=https://your-backend.onrender.com
```

### Rewrite Rule
```
Source: /*
Destination: /index.html
Action: Rewrite
```

---

## Cost

**Total: $0/month** (Free Tier)

- Backend: Free (spins down after 15 min)
- Frontend: Free (always available)
- Database: SQLite (free, internal)

---

## Quick Links

- **Render Dashboard:** https://render.com/dashboard
- **Full Guide:** `MANUAL_DEPLOYMENT_GUIDE.md`
- **Troubleshooting:** See full guide

---

## Deployment Steps

1. **Backend:** New → Web Service → Configure → Deploy
2. **Frontend:** New → Static Site → Configure → Deploy
3. **Initialize:** `curl -X POST https://your-backend.onrender.com/api/init-database`
4. **Test:** Open frontend URL in browser

**Time:** ~10-15 minutes total

✅ **No Blueprint Required**  
✅ **No PostgreSQL Required**  
✅ **100% Free Tier**
