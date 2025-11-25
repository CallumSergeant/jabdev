#!/usr/bin/env python3
"""
Simple API test script
"""

import requests
import json

BASE_URL = 'http://localhost:3001/api'

def test_endpoint(method, endpoint, data=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, json=data)
        else:
            return False, f"Unsupported method: {method}"
        
        if response.status_code in [200, 201]:
            return True, response.json()
        else:
            return False, f"Status {response.status_code}: {response.text}"
    
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server. Is it running?"
    except Exception as e:
        return False, str(e)

def main():
    print("JABchem CMS - API Test")
    print("="*50)
    
    tests = [
        ('GET', '/health', None, 'Health check'),
        ('GET', '/subjects', None, 'Get subjects'),
        ('GET', '/structure', None, 'Get structure'),
        ('GET', '/publish/history', None, 'Get publish history'),
    ]
    
    passed = 0
    failed = 0
    
    for method, endpoint, data, description in tests:
        print(f"\nTesting: {description}")
        print(f"  {method} {endpoint}")
        
        success, result = test_endpoint(method, endpoint, data)
        
        if success:
            print(f"  ✓ PASSED")
            if isinstance(result, dict) and 'message' in result:
                print(f"    {result['message']}")
            elif isinstance(result, list):
                print(f"    Returned {len(result)} items")
            passed += 1
        else:
            print(f"  ✗ FAILED")
            print(f"    {result}")
            failed += 1
    
    print("\n" + "="*50)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*50)
    
    return failed == 0

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
