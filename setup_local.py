#!/usr/bin/env python3
"""
Local Setup Script for Crypto Dashboard
This script helps set up the local environment for testing without API keys.
"""

import os
import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Set up environment variables for local testing"""
    print("🔧 Setting up environment for local testing...")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file for local testing...")
        env_content = """# Local Testing Configuration
# Data Source Configuration
PRIMARY_DATA_SOURCE=ccxt
CCXT_EXCHANGES=binance,coinbase,kraken
USE_MOCK_DATA=False

# Database Configuration (SQLite for local testing)
DATABASE_URL=sqlite:///crypto_dashboard.db
REDIS_URL=redis://localhost:6379

# Application Configuration
DEBUG=True
LOG_LEVEL=INFO
UPDATE_INTERVAL=30

# Optional: API Keys (leave empty for CCXT testing)
BINANCE_API_KEY=
BINANCE_SECRET_KEY=
COINGECKO_API_KEY=

# AWS Configuration (not needed for local testing)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
S3_BUCKET=crypto-dashboard-data

# Risk Configuration
VAR_CONFIDENCE_LEVEL=0.95
VAR_TIME_HORIZON=1

# Data Quality Thresholds
PRICE_DEVIATION_THRESHOLD=0.05
DATA_FRESHNESS_THRESHOLD=300
VOLUME_THRESHOLD=1000000
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created")
    else:
        print("✅ .env file already exists")

def check_redis():
    """Check if Redis is available"""
    print("🔍 Checking Redis availability...")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis is running")
        return True
    except Exception as e:
        print(f"⚠️  Redis not available: {e}")
        print("💡 You can install Redis or the app will use in-memory caching")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating necessary directories...")
    directories = ['logs', 'data']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directories created")

def main():
    """Main setup function"""
    print("🚀 Setting up Crypto Dashboard for Local Testing")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Set up environment
    setup_environment()
    
    # Check Redis
    check_redis()
    
    # Create directories
    create_directories()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start Redis (optional): redis-server")
    print("2. Run the dashboard: streamlit run app/main.py")
    print("3. Open browser: http://localhost:8501")
    print("\n💡 The app will use CCXT for price data (no API keys required)")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 