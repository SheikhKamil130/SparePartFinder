"""Performance tests for system responsiveness and load handling"""
import pytest
import time
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, Part

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Add sample data
            for i in range(10):
                part = Part(
                    name=f'PART {i}',
                    description=f'Test part {i}',
                    category='Test',
                    price=50.0 + i,
                    quantity=10,
                    in_stock=True
                )
                db.session.add(part)
            db.session.commit()
        yield client

def test_analytics_endpoint_latency(client):
    """Test that analytics endpoint responds quickly"""
    start_time = time.time()
    
    response = client.get('/api/analytics')
    
    latency = time.time() - start_time
    
    assert response.status_code == 200
    assert latency < 1.0, f"Analytics endpoint too slow: {latency:.2f}s"
    
    print(f"Analytics endpoint latency: {latency:.3f}s")

def test_parts_list_latency(client):
    """Test that parts list endpoint responds quickly"""
    start_time = time.time()
    
    response = client.get('/api/parts')
    
    latency = time.time() - start_time
    
    assert response.status_code == 200
    assert latency < 1.0, f"Parts list endpoint too slow: {latency:.2f}s"
    
    print(f"Parts list endpoint latency: {latency:.3f}s")

def test_concurrent_requests(client):
    """Test handling multiple simultaneous requests"""
    def make_request():
        return client.get('/api/parts')
    
    # Test with 10 concurrent requests
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        responses = [f.result() for f in futures]
    
    total_time = time.time() - start_time
    
    # All requests should succeed
    assert all(r.status_code == 200 for r in responses)
    
    # Should handle concurrent load reasonably
    assert total_time < 5.0, f"Concurrent requests too slow: {total_time:.2f}s"
    
    print(f"10 concurrent requests completed in {total_time:.3f}s")

def test_database_query_performance(client):
    """Test database query performance with larger dataset"""
    with app.app_context():
        # Add more data
        for i in range(100):
            part = Part(
                name=f'PERF TEST PART {i}',
                description=f'Performance test part {i}',
                category='Performance Test',
                price=100.0 + (i * 0.5),
                quantity=i,
                in_stock=(i % 2 == 0)
            )
            db.session.add(part)
        db.session.commit()
        
        # Measure query time
        start_time = time.time()
        
        parts = Part.query.all()
        
        query_time = time.time() - start_time
        
        assert len(parts) >= 100
        assert query_time < 0.5, f"Database query too slow: {query_time:.3f}s"
        
        print(f"Query 100+ parts in {query_time:.3f}s")

def test_scraping_stats_latency(client):
    """Test scraping stats endpoint latency"""
    start_time = time.time()
    
    response = client.get('/api/scraping-stats')
    
    latency = time.time() - start_time
    
    assert response.status_code == 200
    assert latency < 0.5, f"Scraping stats endpoint too slow: {latency:.3f}s"
    
    print(f"Scraping stats latency: {latency:.3f}s")

def test_memory_usage_basic(client):
    """Basic test to ensure no memory leaks in simple operations"""
    import tracemalloc
    
    tracemalloc.start()
    
    # Perform multiple requests
    for _ in range(20):
        client.get('/api/parts')
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Peak memory should be reasonable (less than 100MB for this test)
    assert peak < 100 * 1024 * 1024, f"Peak memory usage too high: {peak / 1024 / 1024:.2f}MB"
    
    print(f"Peak memory usage: {peak / 1024 / 1024:.2f}MB")
