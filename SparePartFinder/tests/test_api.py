"""Unit tests for Flask API endpoints"""
import pytest
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, Part, PriceRecord

@pytest.fixture
def client():
    """Create test client with in-memory database"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Initialize with sample data
            sample_part = Part(
                name='TEST PART',
                description='Test part for unit tests',
                category='Test Category',
                price=99.99,
                quantity=10,
                in_stock=True
            )
            db.session.add(sample_part)
            db.session.commit()
        yield client

def test_index_endpoint(client):
    """Test GET / endpoint"""
    response = client.get('/')
    assert response.status_code == 200

def test_get_parts_endpoint(client):
    """Test GET /api/parts"""
    response = client.get('/api/parts')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0
    assert 'name' in data[0]
    assert 'price' in data[0]

def test_get_specific_part(client):
    """Test GET /api/part/<id>"""
    # Get the test part ID
    parts_response = client.get('/api/parts')
    parts = json.loads(parts_response.data)
    part_id = parts[0]['id']
    
    response = client.get(f'/api/part/{part_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'part' in data
    assert 'price_history' in data
    assert data['part']['name'] == 'TEST PART'

def test_get_analytics(client):
    """Test GET /api/analytics"""
    response = client.get('/api/analytics')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'total_parts' in data
    assert 'parts_in_stock' in data
    assert 'total_price_records' in data

def test_get_scraping_stats(client):
    """Test GET /api/scraping-stats"""
    response = client.get('/api/scraping-stats')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'success' in data
    assert 'failed' in data
    assert 'fallback' in data

def test_init_database(client):
    """Test POST /api/init-database"""
    # Database already has data from fixture, should return 200
    response = client.post('/api/init-database')
    assert response.status_code in [200, 201]

def test_predict_no_file(client):
    """Test POST /predict with no file - should return 400"""
    response = client.post('/predict')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_predict_invalid_file(client):
    """Test POST /predict with invalid file type"""
    # Create a temporary text file
    with open('test_invalid.txt', 'w') as f:
        f.write('This is not an image')
    
    with open('test_invalid.txt', 'rb') as f:
        response = client.post('/predict', data={
            'file': (f, 'test.txt')
        }, content_type='multipart/form-data')
    
    assert response.status_code == 400
    
    # Cleanup
    if os.path.exists('test_invalid.txt'):
        os.remove('test_invalid.txt')

def test_database_models():
    """Test database model creation and serialization"""
    with app.app_context():
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        db.create_all()
        
        part = Part(
            name='BRAKE PAD',
            description='High-quality brake pad',
            category='Brake System',
            price=45.00,
            quantity=20,
            in_stock=True
        )
        db.session.add(part)
        db.session.commit()
        
        # Test to_dict method
        part_dict = part.to_dict()
        assert part_dict['name'] == 'BRAKE PAD'
        assert part_dict['price'] == 45.00
        assert part_dict['quantity'] == 20
        assert part_dict['in_stock'] == True
        
        # Test PriceRecord
        record = PriceRecord(
            part_name='BRAKE PAD',
            retailer='Test Retailer',
            price=50.00,
            availability='In Stock',
            url='http://test.com'
        )
        db.session.add(record)
        db.session.commit()
        
        assert record.part_name == 'BRAKE PAD'
        assert record.price == 50.00
