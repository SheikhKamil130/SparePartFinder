# SparePartFinder Pro

AI-powered spare part identification system with price comparison and market analysis.

## Features
- 🔍 Image-based spare part recognition (49 classes)
- 💰 Real-time price comparison from multiple retailers
- 🌐 Web scraping for market prices
- 📊 Analytics dashboard with historical data
- ⚛️ React frontend with modern UI
- 🚀 Flask REST API backend with PyTorch ML model
- 🗄️ PostgreSQL database support for production

## Quick Start

### 1. Install Dependencies
```bash
pip install Flask Flask-CORS Flask-SQLAlchemy python-dotenv torch torchvision Pillow numpy requests beautifulsoup4
```

### 2. Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 3. Run Application

**Option A: Easy Start**
```bash
start_app.bat
```

**Option B: Manual Start**

Terminal 1 - Backend:
```bash
python app.py
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

Open: http://localhost:5173

## Project Structure
```
├── app.py                 # Flask backend
├── frontend/              # React frontend
├── train_model.py         # Model training (MobileNetV2)
├── train_enhanced.py      # Enhanced training (ResNet50)
├── evaluate_model.py      # Model evaluation
├── scraper.py             # Web scraping module
├── AutoMobile_Dataset/    # Training data (49 classes)
└── instance/              # SQLite database
```

## Model Training

**Train new model:**
```bash
python train_enhanced.py
```

**Evaluate model:**
```bash
python evaluate_model.py
```

## API Endpoints
- `POST /predict` - Predict part from image
- `GET /api/parts` - Get all parts
- `GET /api/analytics` - Get system analytics

## Tech Stack
- **Frontend:** React 18, Vite, Chart.js
- **Backend:** Flask, SQLAlchemy
- **AI/ML:** PyTorch, MobileNetV2/ResNet50
- **Database:** SQLite

## Deployment

### Deploy to Render (Recommended)

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guide.

**Quick Deploy**:
1. Push code to GitHub
2. Connect repository to Render
3. Render will auto-detect `render.yaml` and deploy all services
4. Initialize database: `curl -X POST https://your-backend.onrender.com/api/init-database`

**Services**:
- Backend: Flask API with PyTorch model
- Frontend: React SPA (Static Site)
- Database: PostgreSQL

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Development
USE_POSTGRES=false
FLASK_ENV=development
PORT=5000

# Production (Render)
USE_POSTGRES=true
FLASK_ENV=production
DATABASE_URL=<from Render>
VITE_API_URL=<backend URL>
```

## Production Features

- ✅ Gunicorn WSGI server for production
- ✅ PostgreSQL database with connection pooling
- ✅ CORS configuration for cross-origin requests
- ✅ File upload validation and security
- ✅ Health check endpoints
- ✅ Automatic database initialization
- ✅ CPU-optimized PyTorch inference
- ✅ Static asset serving

## License
MIT
