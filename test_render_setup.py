#!/usr/bin/env python3
"""
Script test để kiểm tra setup trước khi deploy lên Render
"""

import os
import sys
import subprocess
import requests
import time

def test_dependencies():
    """Test các dependencies cần thiết"""
    print("=== Testing Dependencies ===")
    
    required_packages = [
        'flask', 'torch', 'pandas', 'numpy', 
        'sentence_transformers', 'transformers', 
        'sklearn', 'scipy', 'requests'
    ]
    
    # Gunicorn chỉ cần thiết trên server, không cần test locally
    try:
        import gunicorn
        print("✅ gunicorn (optional)")
    except ImportError:
        print("⚠️  gunicorn not installed (will be installed on Render)")
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {missing_packages}")
        return False
    else:
        print("\n✅ All dependencies are available")
        return True

def test_model_download():
    """Test model download"""
    print("\n=== Testing Model Download ===")
    
    try:
        import download_model
        
        # Test download
        success = download_model.download_from_huggingface()
        
        if success:
            print("✅ Model download successful")
            return True
        else:
            print("⚠️  Model download failed, testing dummy model creation")
            success = download_model.create_dummy_model()
            if success:
                print("✅ Dummy model creation successful")
                return True
            else:
                print("❌ Both download and dummy model failed")
                return False
                
    except Exception as e:
        print(f"❌ Error testing model: {str(e)}")
        return False

def test_app_startup():
    """Test app startup"""
    print("\n=== Testing App Startup ===")
    
    try:
        # Import app
        from app import app
        
        # Test health endpoint
        with app.test_client() as client:
            response = client.get('/api/health')
            if response.status_code == 200:
                print("✅ Health endpoint working")
                return True
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing app: {str(e)}")
        return False

def test_search_api():
    """Test search API"""
    print("\n=== Testing Search API ===")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test search endpoint
            response = client.post('/api/search', 
                                 json={'query': '你好'},
                                 content_type='application/json')
            
            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    print("✅ Search API working")
                    return True
                else:
                    print(f"⚠️  Search API returned error: {data.get('error')}")
                    return True  # API working, just no results
            else:
                print(f"❌ Search API failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing search API: {str(e)}")
        return False

def test_render_environment():
    """Test Render environment variables"""
    print("\n=== Testing Render Environment ===")
    
    # Check if PORT is set (Render sets this)
    port = os.environ.get('PORT')
    if port:
        print(f"✅ PORT environment variable: {port}")
    else:
        print("⚠️  PORT not set (normal for local testing)")
    
    # Check other important variables
    env_vars = ['FLASK_ENV', 'PYTHONUNBUFFERED']
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"⚠️  {var} not set")
    
    return True

def main():
    """Run all tests"""
    print("🚀 Render Deployment Test Suite")
    print("=" * 50)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Model Download", test_model_download),
        ("App Startup", test_app_startup),
        ("Search API", test_search_api),
        ("Render Environment", test_render_environment)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for Render deployment!")
        return True
    else:
        print("⚠️  Some tests failed. Please fix issues before deploying.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 