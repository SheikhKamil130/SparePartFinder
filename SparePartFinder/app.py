import os
import json
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Database configuration - supports both SQLite and PostgreSQL
use_postgres = os.environ.get('USE_POSTGRES', 'false').lower() == 'true'
if use_postgres:
    database_url = os.environ.get('DATABASE_URL', 'postgresql://localhost/spareparts')
    # Fix Render's postgres:// URL to postgresql:// for SQLAlchemy compatibility
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.logger.info("Using PostgreSQL database")
else:
    # Use absolute path for SQLite database
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'spareparts.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.logger.info(f"Using SQLite database at {db_path}")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
CORS(app)
db = SQLAlchemy(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Models
class Part(db.Model):
    """Internal inventory parts database"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer, default=0)
    in_stock = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'price': self.price,
            'quantity': self.quantity,
            'in_stock': self.in_stock
        }

class PriceRecord(db.Model):
    """Historical price records from external retailers"""
    id = db.Column(db.Integer, primary_key=True)
    part_name = db.Column(db.String(100), nullable=False, index=True)
    retailer = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    availability = db.Column(db.String(100))
    url = db.Column(db.String(500))
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create database tables
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        # Continue anyway - tables might already exist

# Load class names
with open('classes.json', 'r') as f:
    class_names = json.load(f)

# Load the model safely
def load_model():
    try:
        model = models.mobilenet_v2(weights=None)  # Updated: use weights=None
        num_ftrs = model.classifier[1].in_features
        
        # Match architecture - try Sequential first (new format with dropout)
        try:
            model.classifier = nn.Sequential(
                nn.Dropout(0.3),
                nn.Linear(num_ftrs, len(class_names))
            )
            model.load_state_dict(torch.load('spare_part_model.pth', map_location=torch.device('cpu')))
            logger.info("Model loaded successfully (Sequential format)")
        except RuntimeError:
            # Fallback to old format (Linear only)
            model.classifier[1] = nn.Linear(num_ftrs, len(class_names))
            model.load_state_dict(torch.load('spare_part_model.pth', map_location=torch.device('cpu')))
            logger.info("Model loaded successfully (Linear format)")
        
        model.eval()
        return model
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        return None

# Try to load model, but don't crash if it fails
try:
    model = load_model()
    if model is None:
        logger.warning("Model is None - predictions will not be available")
except Exception as e:
    logger.error(f"Exception during model loading: {str(e)}")
    model = None

from scraper import PartScraper

scraper = PartScraper()

# Image transformation
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_prediction(image_path):
    # Check if model is available
    if model is None:
        raise RuntimeError("ML model is not available. Please check server logs.")
    
    img = Image.open(image_path).convert('RGB')
    img_t = preprocess(img)
    batch_t = torch.unsqueeze(img_t, 0)

    with torch.no_grad():
        outputs = model(batch_t)
        _, preds = torch.max(outputs, 1)
        confidence = torch.nn.functional.softmax(outputs, dim=1)[0][preds[0]].item()
    
    return class_names[preds[0]], confidence

def get_aggregated_prices(part_name):
    """Get prices from internal stock and external retailers (Aim 4)"""
    results = []
    
    try:
        # Check internal stock database
        internal_part = Part.query.filter_by(name=part_name).first()
        if internal_part and internal_part.in_stock:
            results.append({
                "name": f"Internal Stock - {internal_part.name}",
                "price": internal_part.price,
                "availability": f"{internal_part.quantity} units available",
                "url": "#",
                "retailer": "Internal Inventory"
            })
        
        # Fetch from external sources using Scraper
        try:
            market_prices = scraper.get_market_prices(part_name)
            results.extend(market_prices)
            
            # Save to database for historical tracking
            for price_info in market_prices:
                try:
                    record = PriceRecord(
                        part_name=part_name,
                        retailer=price_info['name'],
                        price=price_info['price'],
                        availability=price_info.get('availability', 'Unknown'),
                        url=price_info.get('url', '#')
                    )
                    db.session.add(record)
                except Exception as e:
                    logger.warning(f"Failed to save price record: {str(e)}")
            
            db.session.commit()
        except Exception as e:
            logger.error(f"Web scraping error: {str(e)}")
            # Continue with internal results even if scraping fails
        
        # Sort by price (cheapest to most expensive as per Aim 4)
        return sorted(results, key=lambda x: x['price']) if results else []
    
    except Exception as e:
        logger.error(f"Price aggregation error: {str(e)}", exc_info=True)
        return []

def get_mock_details(part_name):
    # Mock technical specifications based on part name
    details = {
        "Weight": f"{round(2 + (len(part_name) % 5), 1)} kg",
        "Material": "Cast Iron / Aluminum Alloy" if len(part_name) > 8 else "High-Grade Polymer",
        "Manufacturer": "OEM Standard",
        "Warranty": "12 Months / 20,000 km",
        "Compatibility": "Universal / Model Specific"
    }
    return details

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    # Handle file upload prediction
    try:
        # Check if model is available
        if model is None:
            return jsonify({'error': 'ML model is not available. Please contact administrator.'}), 503
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            logger.info(f"Processing image: {filename}")
            
            part_name, confidence = get_prediction(filepath)
            prices = get_aggregated_prices(part_name)
            details = get_mock_details(part_name)
            
            logger.info(f"Prediction: {part_name} (confidence: {confidence*100:.2f}%)")
            
            return jsonify({
                'part_name': part_name,
                'confidence': f"{confidence*100:.2f}%",
                'image_url': f"/static/uploads/{filename}",
                'prices': prices,
                'details': details
            })
        
        return jsonify({'error': 'File type not allowed'}), 400
    
    except RuntimeError as e:
        logger.error(f"Model error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 503
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error during prediction'}), 500

@app.route('/api/parts', methods=['GET'])
def get_parts():
    """Get all parts from internal inventory database"""
    parts = Part.query.all()
    return jsonify([part.to_dict() for part in parts])

@app.route('/api/part/<int:part_id>', methods=['GET'])
def get_part(part_id):
    """Get specific part details"""
    part = Part.query.get_or_404(part_id)
    
    # Get price history
    price_history = PriceRecord.query.filter_by(part_name=part.name)\
                                    .order_by(PriceRecord.scraped_at.desc())\
                                    .limit(10).all()
    
    return jsonify({
        'part': part.to_dict(),
        'price_history': [
            {
                'retailer': r.retailer,
                'price': r.price,
                'availability': r.availability,
                'scraped_at': r.scraped_at.isoformat()
            } for r in price_history
        ]
    })

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get system analytics and statistics"""
    total_parts = Part.query.count()
    parts_in_stock = Part.query.filter_by(in_stock=True).count()
    total_price_records = PriceRecord.query.count()
    
    return jsonify({
        'total_parts': total_parts,
        'parts_in_stock': parts_in_stock,
        'total_price_records': total_price_records,
        'model_accuracy': 'Check evaluate_model.py for latest metrics'
    })

@app.route('/api/init-database', methods=['POST'])
def init_database():
    """Initialize database with sample parts data"""
    if Part.query.count() > 0:
        return jsonify({'message': 'Database already initialized'}), 200
    
    # Sample parts data based on your 49 classes
    sample_parts = [
        {'name': 'AIR COMPRESSOR', 'category': 'Engine Systems', 'price': 250.00, 'quantity': 5},
        {'name': 'ALTERNATOR', 'category': 'Electrical System', 'price': 180.00, 'quantity': 10},
        {'name': 'BATTERY', 'category': 'Electrical System', 'price': 120.00, 'quantity': 15},
        {'name': 'BRAKE CALIPER', 'category': 'Brake System', 'price': 95.00, 'quantity': 8},
        {'name': 'BRAKE PAD', 'category': 'Brake System', 'price': 45.00, 'quantity': 20},
        {'name': 'BRAKE ROTOR', 'category': 'Brake System', 'price': 65.00, 'quantity': 12},
        {'name': 'WATER PUMP', 'category': 'Cooling System', 'price': 85.00, 'quantity': 7},
        {'name': 'RADIATOR', 'category': 'Cooling System', 'price': 220.00, 'quantity': 4},
        {'name': 'SPARK PLUG', 'category': 'Ignition System', 'price': 12.00, 'quantity': 50},
        {'name': 'FUEL INJECTOR', 'category': 'Fuel System', 'price': 125.00, 'quantity': 6},
    ]
    
    for part_data in sample_parts:
        part = Part(
            name=part_data['name'],
            description=f"Automotive {part_data['name'].lower()}",
            category=part_data['category'],
            price=part_data['price'],
            quantity=part_data['quantity'],
            in_stock=part_data['quantity'] > 0
        )
        db.session.add(part)
    
    db.session.commit()
    logger.info(f"Database initialized with {len(sample_parts)} parts")
    
    return jsonify({'message': f'Database initialized with {len(sample_parts)} parts'}), 201

@app.route('/api/scraping-stats', methods=['GET'])
def get_scraping_stats():
    """Get scraping success/failure rates"""
    return jsonify(scraper.scraping_stats)

if __name__ == '__main__':
    # Get port from environment variable (Render uses PORT, default to 10000)
    port = int(os.environ.get("PORT", 10000))
    # Bind to 0.0.0.0 to accept external connections
    app.run(host="0.0.0.0", port=port, debug=os.environ.get('FLASK_ENV') != 'production')
