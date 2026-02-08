"""
Quick fix script for Render deployment issues
Run this locally to test if everything works before deploying
"""
import subprocess
import sys

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing imports...")
    
    packages = [
        'streamlit',
        'fastapi', 
        'uvicorn',
        'psycopg2',
        'sqlalchemy',
        'groq',
        'dotenv',
        'pydantic',
        'requests'
    ]
    
    failed = []
    for package in packages:
        try:
            if package == 'dotenv':
                import dotenv
            elif package == 'psycopg2':
                import psycopg2
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed.append(package)
    
    return failed

def test_backend_server():
    """Test if backend server can start"""
    print("\n🔍 Testing backend server...")
    try:
        import uvicorn
        from backend_server import app
        print("✅ Backend server imports successfully")
        return True
    except Exception as e:
        print(f"❌ Backend server error: {e}")
        return False

def test_streamlit_app():
    """Test if streamlit app can start"""
    print("\n🔍 Testing Streamlit app...")
    try:
        import streamlit
        print("✅ Streamlit imports successfully")
        return True
    except Exception as e:
        print(f"❌ Streamlit error: {e}")
        return False

def main():
    print("🚀 Deployment Fix Script")
    print("=" * 50)
    
    # Test imports
    failed_imports = test_imports()
    
    if failed_imports:
        print(f"\n❌ Failed imports: {', '.join(failed_imports)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    # Test backend
    backend_ok = test_backend_server()
    
    # Test frontend
    frontend_ok = test_streamlit_app()
    
    if backend_ok and frontend_ok:
        print("\n🎉 All tests passed! Ready for deployment.")
        return True
    else:
        print("\n❌ Some tests failed. Fix issues before deploying.")
        return False

if __name__ == "__main__":
    main()
