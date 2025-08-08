#!/usr/bin/env python3
"""
Test script to verify CCXT data fetching
Run this to test if CCXT can fetch crypto prices without API keys
"""

import ccxt
import time
from datetime import datetime

def test_ccxt_exchanges():
    """Test different exchanges with CCXT"""
    exchanges = ['binance', 'coinbase', 'kraken']
    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
    
    print("🔍 Testing CCXT data fetching...")
    print("=" * 50)
    
    for exchange_name in exchanges:
        try:
            print(f"\n📊 Testing {exchange_name.upper()}...")
            
            # Initialize exchange
            exchange = getattr(ccxt, exchange_name)()
            
            # Test fetching ticker
            for symbol in symbols:
                try:
                    ticker = exchange.fetch_ticker(symbol)
                    price = ticker['last']
                    print(f"  ✅ {symbol}: ${price:,.2f}")
                except Exception as e:
                    print(f"  ❌ {symbol}: Error - {e}")
            
            # Rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Failed to initialize {exchange_name}: {e}")
    
    print("\n" + "=" * 50)
    print("✅ CCXT test completed!")

def test_best_price():
    """Test getting best price across multiple exchanges"""
    print("\n🏆 Testing best price across exchanges...")
    
    exchanges = ['binance', 'coinbase', 'kraken']
    symbol = 'BTC/USDT'
    prices = {}
    
    for exchange_name in exchanges:
        try:
            exchange = getattr(ccxt, exchange_name)()
            ticker = exchange.fetch_ticker(symbol)
            prices[exchange_name] = ticker['last']
            print(f"  {exchange_name}: ${ticker['last']:,.2f}")
            time.sleep(0.5)  # Rate limiting
        except Exception as e:
            print(f"  {exchange_name}: Error - {e}")
    
    if prices:
        best_exchange = min(prices, key=prices.get)
        best_price = prices[best_exchange]
        print(f"\n🏆 Best price: {best_exchange} at ${best_price:,.2f}")

def main():
    """Main test function"""
    print("🚀 CCXT Data Fetching Test")
    print("This test verifies that CCXT can fetch crypto prices without API keys")
    print("=" * 60)
    
    # Test individual exchanges
    test_ccxt_exchanges()
    
    # Test best price
    test_best_price()
    
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print("✅ If you see prices above, CCXT is working correctly")
    print("✅ You can now run the dashboard: streamlit run app/main.py")
    print("💡 The dashboard will use CCXT for real-time price data")

if __name__ == "__main__":
    main() 