import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import redis
import json
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from data.data_collectors import BinanceDataCollector, CoinGeckoDataCollector, CCXTDataCollector
from data.data_validators import DataValidator
from data.risk_calculators import RiskCalculator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Shared in-memory cache for when Redis is not available
class SharedMemoryCache:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SharedMemoryCache, cls).__new__(cls)
            cls._instance.cache = {}
        return cls._instance

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        self.cache[key] = value

class DataManager:
    """
    Central data management class for the crypto dashboard
    """
    
    def __init__(self, config: Dict):
        self.config = config
        
        # Initialize Redis with fallback to in-memory cache
        try:
            self.redis_client = redis.from_url(config['redis_url'])
            self.redis_client.ping()  # Test connection
            self.use_redis = True
            logger.info("✅ Redis connected successfully")
        except Exception as e:
            logger.warning(f"⚠️ Redis not available: {e}. Using in-memory cache.")
            self.redis_client = None
            self.use_redis = False
            self.memory_cache = SharedMemoryCache()  # Use shared in-memory cache
        
        self.engine = create_engine(config['database_url'])
        
        # Initialize data collectors
        self.binance_collector = BinanceDataCollector(config)
        self.coingecko_collector = CoinGeckoDataCollector(config)
        self.ccxt_collector = CCXTDataCollector(config)
        
        # Set primary data source
        self.primary_data_source = config.get('primary_data_source', 'ccxt')
        
        # Initialize validators and calculators
        self.data_validator = DataValidator(config)
        self.risk_calculator = RiskCalculator(config)
        
        # Portfolio state
        self.portfolio = self._load_portfolio()
        
    def _load_portfolio(self) -> Dict:
        """Load portfolio from database or create default"""
        try:
            # Try to load from database
            query = "SELECT * FROM portfolio WHERE active = 1"
            df = pd.read_sql(query, self.engine)
            
            if not df.empty:
                return df.to_dict('records')[0]
        except:
            pass
        
        # Default portfolio
        return {
            'id': 1,
            'name': 'Main Portfolio',
            'nav': 10000000,  # $10M starting NAV
            'currency': 'USD',
            'active': True,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
    
    def get_real_time_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Get real-time prices for given symbols with smart data source selection
        """
        try:
            # Try to get from cache first
            cached_prices = {}
            for symbol in symbols:
                if self.use_redis:
                    # Use Redis cache
                    cached = self.redis_client.get(f"price:{symbol}")
                    if cached:
                        cached_prices[symbol] = float(cached.decode())
                else:
                    # Use in-memory cache
                    cache_key = f"price:{symbol}"
                    cache_data = self.memory_cache.get(cache_key)
                    if cache_data:
                        # Check if cache is still valid (60 seconds)
                        if (datetime.now() - cache_data['timestamp']).seconds < 60:
                            cached_prices[symbol] = cache_data['price']
            
            # Get missing prices from API
            missing_symbols = [s for s in symbols if s not in cached_prices]
            if missing_symbols:
                # Use primary data source
                if self.primary_data_source == 'ccxt':
                    api_prices = self.ccxt_collector.get_best_prices(missing_symbols)
                elif self.primary_data_source == 'binance' and self.config.get('binance_api_key'):
                    api_prices = self.binance_collector.get_prices(missing_symbols)
                elif self.primary_data_source == 'coingecko' and self.config.get('coingecko_api_key'):
                    api_prices = self.coingecko_collector.get_prices(missing_symbols)
                else:
                    # Fallback to CCXT if no API keys
                    api_prices = self.ccxt_collector.get_best_prices(missing_symbols)
                
                # Cache new prices
                for symbol, price in api_prices.items():
                    if self.use_redis:
                        # Cache in Redis
                        self.redis_client.setex(f"price:{symbol}", 60, str(price))
                    else:
                        # Cache in memory
                        self.memory_cache.set(f"price:{symbol}", {
                            'price': price,
                            'timestamp': datetime.now()
                        })
                    cached_prices[symbol] = price
            
            return cached_prices
            
        except Exception as e:
            logger.error(f"Error getting real-time prices: {e}")
            # Return sample data as fallback
            return self._get_sample_prices(symbols)
    
    def _get_sample_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get sample prices for demonstration when APIs fail"""
        sample_prices = {
            'BTC': 47000.0,
            'ETH': 3400.0,
            'SOL': 140.0,
            'ADA': 0.65,
            'DOT': 8.5,
            'LINK': 18.5,
            'MATIC': 1.2,
            'AVAX': 45.0
        }
        return {symbol: sample_prices.get(symbol, 100.0) for symbol in symbols}
    
    def get_portfolio_positions(self) -> List[Dict]:
        """
        Get current portfolio positions
        """
        try:
            query = """
            SELECT p.*, c.symbol, c.name as asset_name
            FROM positions p
            JOIN crypto_assets c ON p.asset_id = c.id
            WHERE p.active = 1
            """
            df = pd.read_sql(query, self.engine)
            
            if df.empty:
                # Return sample positions for demo
                return self._get_sample_positions()
            
            return df.to_dict('records')
            
        except Exception as e:
            logger.error(f"Error getting portfolio positions: {e}")
            return self._get_sample_positions()
    
    def _get_sample_positions(self) -> List[Dict]:
        """Get sample positions for demonstration"""
        sample_positions = [
            {
                'id': 1,
                'asset_id': 1,
                'symbol': 'BTC',
                'asset_name': 'Bitcoin',
                'quantity': 150.5,
                'avg_price': 45000,
                'current_price': 47000,
                'market_value': 7073500,
                'unrealized_pnl': 301000,
                'unrealized_pnl_pct': 6.69,
                'weight': 0.35,
                'active': True
            },
            {
                'id': 2,
                'asset_id': 2,
                'symbol': 'ETH',
                'asset_name': 'Ethereum',
                'quantity': 1250.0,
                'avg_price': 3200,
                'current_price': 3400,
                'market_value': 4250000,
                'unrealized_pnl': 250000,
                'unrealized_pnl_pct': 6.25,
                'weight': 0.25,
                'active': True
            },
            {
                'id': 3,
                'asset_id': 3,
                'symbol': 'SOL',
                'asset_name': 'Solana',
                'quantity': 5000.0,
                'avg_price': 120,
                'current_price': 140,
                'market_value': 700000,
                'unrealized_pnl': 100000,
                'unrealized_pnl_pct': 16.67,
                'weight': 0.20,
                'active': True
            }
        ]
        return sample_positions
    
    def calculate_portfolio_metrics(self) -> Dict:
        """
        Calculate comprehensive portfolio metrics
        """
        try:
            positions = self.get_portfolio_positions()
            
            if not positions:
                return self._get_sample_metrics()
            
            # Calculate basic metrics
            total_market_value = sum(p['market_value'] for p in positions)
            total_unrealized_pnl = sum(p['unrealized_pnl'] for p in positions)
            total_cost = sum(p['quantity'] * p['avg_price'] for p in positions)
            
            # Calculate returns
            total_return = (total_market_value - total_cost) / total_cost if total_cost > 0 else 0
            
            # Get historical data for risk metrics
            historical_data = self._get_historical_data()
            
            # Calculate risk metrics
            risk_metrics = self.risk_calculator.calculate_portfolio_risk(
                positions, historical_data
            )
            
            return {
                'nav': total_market_value,
                'total_cost': total_cost,
                'unrealized_pnl': total_unrealized_pnl,
                'total_return': total_return,
                'total_return_pct': total_return * 100,
                'positions_count': len(positions),
                'risk_metrics': risk_metrics,
                'last_updated': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {e}")
            return self._get_sample_metrics()
    
    def _get_sample_metrics(self) -> Dict:
        """Get sample metrics for demonstration"""
        return {
            'nav': 12847392,
            'total_cost': 12542871,
            'unrealized_pnl': 294521,
            'total_return': 0.0234,
            'total_return_pct': 2.34,
            'positions_count': 3,
            'risk_metrics': {
                'sharpe_ratio': 1.87,
                'var_95': -847392,
                'var_99': -1247392,
                'max_drawdown': -0.089,
                'volatility': 0.0234,
                'beta': 0.95
            },
            'last_updated': datetime.now()
        }
    
    def _get_historical_data(self) -> pd.DataFrame:
        """
        Get historical price data for risk calculations
        """
        try:
            # Try to get from database
            query = """
            SELECT date, symbol, close_price, volume
            FROM historical_prices
            WHERE date >= NOW() - INTERVAL '90 days'
            ORDER BY date, symbol
            """
            df = pd.read_sql(query, self.engine)
            
            if df.empty:
                # Generate sample historical data
                return self._generate_sample_historical_data()
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return self._generate_sample_historical_data()
    
    def _generate_sample_historical_data(self) -> pd.DataFrame:
        """Generate sample historical data for demonstration"""
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        symbols = ['BTC', 'ETH', 'SOL']
        
        data = []
        for symbol in symbols:
            # Generate realistic price movements
            base_price = {'BTC': 45000, 'ETH': 3200, 'SOL': 120}[symbol]
            returns = np.random.normal(0.001, 0.02, len(dates))
            prices = base_price * np.cumprod(1 + returns)
            
            for date, price in zip(dates, prices):
                data.append({
                    'date': date,
                    'symbol': symbol,
                    'close_price': price,
                    'volume': np.random.uniform(1000000, 10000000)
                })
        
        return pd.DataFrame(data)
    
    def validate_data_quality(self) -> Dict:
        """
        Validate data quality across all sources
        """
        try:
            # Get current prices from multiple sources
            symbols = ['BTC', 'ETH', 'SOL']
            
            binance_prices = self.binance_collector.get_prices(symbols)
            coingecko_prices = self.coingecko_collector.get_prices(symbols)
            
            # Validate price consistency
            validation_results = {}
            for symbol in symbols:
                binance_price = binance_prices.get(symbol)
                coingecko_price = coingecko_prices.get(symbol)
                
                if binance_price and coingecko_price:
                    deviation = abs(binance_price - coingecko_price) / binance_price
                    is_valid = deviation <= self.config['price_deviation_threshold']
                    
                    validation_results[symbol] = {
                        'binance_price': binance_price,
                        'coingecko_price': coingecko_price,
                        'deviation': deviation,
                        'deviation_pct': deviation * 100,
                        'is_valid': is_valid,
                        'threshold': self.config['price_deviation_threshold']
                    }
            
            # Overall data quality score
            valid_count = sum(1 for result in validation_results.values() if result['is_valid'])
            total_count = len(validation_results)
            quality_score = valid_count / total_count if total_count > 0 else 0
            
            return {
                'quality_score': quality_score,
                'validation_results': validation_results,
                'last_updated': datetime.now(),
                'overall_status': 'GOOD' if quality_score >= 0.8 else 'WARNING' if quality_score >= 0.6 else 'CRITICAL'
            }
            
        except Exception as e:
            logger.error(f"Error validating data quality: {e}")
            return {
                'quality_score': 0,
                'validation_results': {},
                'last_updated': datetime.now(),
                'overall_status': 'ERROR'
            }
    
    def get_performance_attribution(self) -> Dict:
        """
        Calculate performance attribution analysis
        """
        try:
            positions = self.get_portfolio_positions()
            
            if not positions:
                return {}
            
            # Calculate contribution to total return
            total_nav = sum(p['market_value'] for p in positions)
            total_pnl = sum(p['unrealized_pnl'] for p in positions)
            
            attribution = []
            for position in positions:
                contribution = position['unrealized_pnl'] / total_nav if total_nav > 0 else 0
                attribution.append({
                    'symbol': position['symbol'],
                    'contribution': contribution,
                    'contribution_pct': contribution * 100,
                    'weight': position['weight'],
                    'return': position['unrealized_pnl_pct'] / 100,
                    'excess_return': (position['unrealized_pnl_pct'] / 100) - (total_pnl / total_nav if total_nav > 0 else 0)
                })
            
            return {
                'attribution': attribution,
                'total_contribution': total_pnl / total_nav if total_nav > 0 else 0,
                'last_updated': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance attribution: {e}")
            return {} 