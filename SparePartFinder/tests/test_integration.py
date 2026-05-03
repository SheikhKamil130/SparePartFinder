"""Integration tests for complete system workflows"""
import pytest
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, Part
from scraper import PartScraper

def test_scraping_functionality():
    """Test that scraper can attempt to scrape (may use fallback)"""
    scraper = PartScraper()
    
    # Test with a common part
    results = scraper.get_market_prices("BRAKE PAD")
    
    # Should return results (either scraped or fallback)
    assert len(results) > 0
    assert all('price' in r for r in results)
    assert all('name' in r for r in results)
    
    # Check scraping stats are tracked
    stats = scraper.scraping_stats
    assert 'success' in stats
    assert 'failed' in stats
    assert 'fallback' in stats
    
    print(f"Scraping test completed. Stats: {stats}")

def test_price_extraction():
    """Test price extraction from various formats"""
    scraper = PartScraper()
    
    # Test different price formats
    assert scraper._extract_price("$123.45") == 123.45
    assert scraper._extract_price("123.45") == 123.45
    assert scraper._extract_price("$1,234.56") == 1234.56
    assert scraper._extract_price("Price: $99.99") == 99.99

def test_fallback_price_generation():
    """Test fallback price generation is realistic"""
    scraper = PartScraper()
    
    price_data = scraper._get_fallback_price("Test Retailer", "BRAKE PAD", 1.5)
    
    assert 'name' in price_data
    assert 'price' in price_data
    assert price_data['price'] > 0
    assert price_data['name'] == "Test Retailer"
    assert isinstance(price_data['price'], float)

def test_full_prediction_workflow(client):
    """Test complete prediction workflow (without actual image)"""
    # This tests the API structure, not the ML model
    # First ensure database is initialized
    client.post('/api/init-database')
    
    # Test that analytics endpoint works (proves system is functional)
    response = client.get('/api/analytics')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'total_parts' in data
    assert data['total_parts'] > 0

def test_database_integration(client):
    """Test database CRUD operations"""
    # Create
    with app.app_context():
        new_part = Part(
            name='INTEGRATION TEST PART',
            description='Test part for integration testing',
            category='Test',
            price=75.00,
            quantity=5,
            in_stock=True
        )
        db.session.add(new_part)
        db.session.commit()
        
        part_id = new_part.id
        
        # Read
        response = client.get(f'/api/part/{part_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['part']['name'] == 'INTEGRATION TEST PART'
        
        # Update
        new_part.price = 80.00
        db.session.commit()
        
        response = client.get(f'/api/part/{part_id}')
        data = json.loads(response.data)
        assert data['part']['price'] == 80.00
        
        # Delete
        db.session.delete(new_part)
        db.session.commit()
        
        response = client.get(f'/api/part/{part_id}')
        assert response.status_code == 404

def test_multiple_parts_retrieval(client):
    """Test retrieving multiple parts from database"""
    # Initialize database with sample data
    client.post('/api/init-database')
    
    response = client.get('/api/parts')
    assert response.status_code == 200
    
    parts = json.loads(response.data)
    assert len(parts) > 0
    
    # Verify structure of each part
    for part in parts:
        assert 'id' in part
        assert 'name' in part
        assert 'price' in part
        assert 'quantity' in part
        assert 'in_stock' in part
