# Quick Start Guide

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd SparePartFinder
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run backend
python app.py
```

Backend will run at: http://localhost:5000

### 3. Frontend Setup
```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Run frontend
npm run dev
```

Frontend will run at: http://localhost:5173

### 4. Test the Application

1. Open http://localhost:5173 in your browser
2. Upload a spare part image
3. View prediction and price comparison

## Deploy to Render

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions.

**Quick Deploy**:
```bash
# 1. Commit all changes
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Go to Render Dashboard
# 3. New → Blueprint
# 4. Connect repository
# 5. Render auto-deploys from render.yaml

# 6. Initialize database
curl -X POST https://your-backend.onrender.com/api/init-database
```

## Verify Installation

### Backend Health Check
```bash
curl http://localhost:5000/api/analytics
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

### Frontend Test
1. Navigate to http://localhost:5173
2. Upload test image from `AutoMobile_Dataset/test/BATTERY/1.jpg`
3. Verify prediction shows "BATTERY"
4. Check price comparison results

## Troubleshooting

### Backend Issues

**Port already in use**:
```bash
# Change port in .env
PORT=5001
```

**Model not found**:
```bash
# Verify model file exists
ls -lh spare_part_model.pth
# Should be ~14MB
```

**Database errors**:
```bash
# Delete and recreate database
rm -rf instance/
python app.py
```

### Frontend Issues

**API connection failed**:
- Verify backend is running on port 5000
- Check Vite proxy configuration in `vite.config.js`

**Build errors**:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

- [ ] Review [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- [ ] Customize sample parts in `/api/init-database` endpoint
- [ ] Train model with your own dataset
- [ ] Configure web scraping for your retailers
- [ ] Add authentication (optional)
- [ ] Set up monitoring and alerts

## Support

- Check [README.md](README.md) for project overview
- See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment guide
- Review code comments for implementation details
