#!/usr/bin/env python3
"""
Health check script for SparePartFinder deployment
Tests all critical endpoints and services
"""

import sys
import requests
import json
from urllib.parse import urljoin

def check_endpoint(base_url, endpoint, method='GET', expected_status=200):
    """Check if an endpoint is responding correctly"""
    url = urljoin(base_url, endpoint)
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, timeout=10)
        
        if response.status_code == expected_status:
            print(f"✅ {method} {endpoint} - Status {response.status_code}")
            return True, response
        else:
            print(f"❌ {method} {endpoint} - Expected {expected_status}, got {response.status_code}")
            return False, response
    except requests.exceptions.RequestException as e:
        print(f"❌ {method} {endpoint} - Connection error: {str(e)}")
        return False, None

def main():
    if len(sys.argv) < 2:
        print("Usage: python health_check.py <backend_url>")
        print("Example: python health_check.py https://sparepartfinder-backend.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1]
    if not base_url.startswith('http'):
        base_url = f"https://{base_url}"
    
    print(f"\n🔍 Health Check for: {base_url}\n")
    print("=" * 60)
    
    all_passed = True
    
    # Test 1: Analytics endpoint (health check)
    print("\n📊 Testing Analytics Endpoint...")
    success, response = check_endpoint(base_url, '/api/analytics')
    if success and response:
        try:
            data = response.json()
            print(f"   Total Parts: {data.get('total_parts', 'N/A')}")
            print(f"   Parts in Stock: {data.get('parts_in_stock', 'N/A')}")
            print(f"   Price Records: {data.get('total_price_records', 'N/A')}")
        except json.JSONDecodeError:
            print("   ⚠️  Invalid JSON response")
            all_passed = False
    else:
        all_passed = False
    
    # Test 2: Parts list endpoint
    print("\n📦 Testing Parts List Endpoint...")
    success, response = check_endpoint(base_url, '/api/parts')
    if success and response:
        try:
            parts = response.json()
            print(f"   Retrieved {len(parts)} parts")
            if len(parts) == 0:
                print("   ⚠️  No parts in database - run /api/init-database")
        except json.JSONDecodeError:
            print("   ⚠️  Invalid JSON response")
            all_passed = False
    else:
        all_passed = False
    
    # Test 3: Scraping stats endpoint
    print("\n🌐 Testing Scraping Stats Endpoint...")
    success, response = check_endpoint(base_url, '/api/scraping-stats')
    if success and response:
        try:
            stats = response.json()
            print(f"   Scraping stats available")
        except json.JSONDecodeError:
            print("   ⚠️  Invalid JSON response")
    else:
        all_passed = False
    
    # Test 4: Root endpoint
    print("\n🏠 Testing Root Endpoint...")
    success, response = check_endpoint(base_url, '/')
    if not success:
        all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All health checks passed!")
        print("\n🚀 Next steps:")
        print(f"   1. Initialize database: curl -X POST {base_url}/api/init-database")
        print(f"   2. Test prediction with image upload")
        print(f"   3. Configure frontend with API URL: {base_url}")
        sys.exit(0)
    else:
        print("❌ Some health checks failed")
        print("\n🔧 Troubleshooting:")
        print("   1. Check Render deployment logs")
        print("   2. Verify environment variables are set")
        print("   3. Ensure database is connected")
        print("   4. Check model file is present")
        sys.exit(1)

if __name__ == '__main__':
    main()
