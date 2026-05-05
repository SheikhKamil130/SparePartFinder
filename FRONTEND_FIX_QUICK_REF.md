# 🔧 Frontend Fix - Quick Reference

## Problem
Frontend deployed as Python Web Service instead of Static Site

## Solution
Delete wrong service → Create Static Site

---

## Step-by-Step Fix

### 1. Delete Wrong Service
```
Dashboard → Your Service → Settings → Delete Web Service
```

### 2. Create Static Site
```
New + → Static Site (NOT Web Service!)
```

### 3. Configure
```
Name: sparepartfinder-frontend
Branch: main
Root Directory: (empty)
Build Command: cd frontend && npm install && npm run build
Publish Directory: frontend/dist
```

### 4. Environment Variable
```
VITE_API_URL=https://sparepartfinder-1.onrender.com
```

### 5. Rewrite Rule
```
Source: /*
Destination: /index.html
Action: Rewrite
```

### 6. Deploy
```
Create Static Site → Wait 2-3 minutes
```

---

## Critical Settings

| Setting | Value | Notes |
|---------|-------|-------|
| **Service Type** | Static Site | NOT Web Service! |
| **Root Directory** | (empty) | Leave blank |
| **Build Command** | `cd frontend && npm install && npm run build` | Must start with `cd frontend` |
| **Publish Directory** | `frontend/dist` | Full path |
| **VITE_API_URL** | `https://sparepartfinder-1.onrender.com` | No trailing slash |

---

## Verification

### ✅ Correct (Static Site)
```
Build logs show:
- npm install
- vite build
- ✓ built in 15s
```

### ❌ Wrong (Web Service)
```
Build logs show:
- pip install
- requirements.txt
- Python errors
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Created Web Service | Delete and create Static Site |
| Root Directory = "frontend" | Leave empty, use `cd frontend` in build command |
| Publish Directory = "dist" | Use full path: `frontend/dist` |
| Missing VITE_API_URL | Add environment variable |
| No rewrite rule | Add `/* → /index.html` |

---

## Time to Fix
**5 minutes total**

---

## Cost
**$0** - Static Sites are free on Render

---

**Full Guide:** `FRONTEND_DEPLOYMENT_FIX.md`
