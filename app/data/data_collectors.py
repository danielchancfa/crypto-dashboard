import requests
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import ccxt
from binance.client import Client
from binance.exceptions import BinanceAPIException

logger = logging.getLogger(__name__)

class BaseDataCollector:
    """Base class for data collectors"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CryptoHedgeFundDashboard/1.0'
        })
        self.last_request_time = 0
        self.rate_limit_delay = 1  # seconds between requests
    
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Make HTTP request with error handling"""
        try:
            self._rate_limit()
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

class BinanceDataCollector(BaseDataCollector):
    """Collector for Binance API data"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get('binance_api_key', '')
        self.secret_key = config.get('binance_secret_key', '')
        
        if self.api_key and self.secret_key:
            self.client = Client(self.api_key, self.secret_key)
        else:
            self.client = None
            logger.warning("Binance API credentials not provided")
    
    def get_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get current prices for given symbols"""
        try:
            if not self.client:
                # Fallback to public API
                return self._get_prices_public(symbols)
            
            prices = {}
            for symbol in symbols:
                try:
                    ticker = self.client.get_symbol_ticker(symbol=f"{symbol}USDT")
                    prices[symbol] = float(ticker['price'])
                except BinanceAPIException as e:
                    logger.error(f"Binance API error for {symbol}: {e}")
                    continue
            
            return prices
            
        except Exception as e:
            logger.error(f"Error getting Binance prices: {e}")
            return {}
    
    def _get_prices_public(self, symbols: List[str]) -> Dict[str, float]:
        """Get prices using public API endpoint"""
        try:
            url = "https://api.binance.com/api/v3/ticker/price"
            response = self._make_request(url)
            
            if not response:
                return {}
            
            prices = {}
            for item in response:
                symbol = item['symbol']
                # Remove USDT suffix
                if symbol.endswith('USDT'):
                    base_symbol = symbol[:-4]
                    if base_symbol in symbols:
                        prices[base_symbol] = float(item['price'])
            
            return prices
            
        except Exception as e:
            logger.error(f"Error getting public Binance prices: {e}")
            return {}
    
    def get_klines(self, symbol: str, interval: str = '1d', limit: int = 100) -> List[Dict]:
        """Get historical kline data"""
        try:
            if not self.client:
                return self._get_klines_public(symbol, interval, limit)
            
            klines = self.client.get_klines(
                symbol=f"{symbol}USDT",
                interval=interval,
                limit=limit
            )
            
            return [
                {
                    'timestamp': kline[0],
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5])
                }
                for kline in klines
            ]
            
        except Exception as e:
            logger.error(f"Error getting Binance klines: {e}")
            return []
    
    def _get_klines_public(self, symbol: str, interval: str = '1d', limit: int = 100) -> List[Dict]:
        """Get klines using public API"""
        try:
            url = "https://api.binance.com/api/v3/klines"
            params = {
                'symbol': f"{symbol}USDT",
                'interval': interval,
                'limit': limit
            }
            
            response = self._make_request(url, params)
            if not response:
                return []
            
            return [
                {
                    'timestamp': kline[0],
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5])
                }
                for kline in response
            ]
            
        except Exception as e:
            logger.error(f"Error getting public Binance klines: {e}")
            return []

class CoinGeckoDataCollector(BaseDataCollector):
    """Collector for CoinGecko API data"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get('coingecko_api_key', '')
        self.base_url = "https://api.coingecko.com/api/v3"
        self.rate_limit_delay = 1.2  # CoinGecko has stricter rate limits
    
    def get_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get current prices for given symbols"""
        try:
            # Convert symbols to CoinGecko IDs
            symbol_to_id = self._get_symbol_mapping()
            
            # Get prices for available symbols
            available_symbols = [s for s in symbols if s in symbol_to_id]
            if not available_symbols:
                return {}
            
            ids = [symbol_to_id[s] for s in available_symbols]
            url = f"{self.base_url}/simple/price"
            params = {
                'ids': ','.join(ids),
                'vs_currencies': 'usd'
            }
            
            if self.api_key:
                params['x_cg_demo_api_key'] = self.api_key
            
            response = self._make_request(url, params)
            if not response:
                return {}
            
            # Convert back to symbol format
            prices = {}
            for symbol in available_symbols:
                coin_id = symbol_to_id[symbol]
                if coin_id in response and 'usd' in response[coin_id]:
                    prices[symbol] = response[coin_id]['usd']
            
            return prices
            
        except Exception as e:
            logger.error(f"Error getting CoinGecko prices: {e}")
            return {}
    
    def _get_symbol_mapping(self) -> Dict[str, str]:
        """Get mapping from symbols to CoinGecko IDs"""
        # Common mapping for major cryptocurrencies
        return {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'SOL': 'solana',
            'ADA': 'cardano',
            'DOT': 'polkadot',
            'LINK': 'chainlink',
            'MATIC': 'matic-network',
            'AVAX': 'avalanche-2',
            'UNI': 'uniswap',
            'ATOM': 'cosmos',
            'LTC': 'litecoin',
            'BCH': 'bitcoin-cash',
            'XRP': 'ripple',
            'DOGE': 'dogecoin',
            'SHIB': 'shiba-inu'
        }
    
    def get_market_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get comprehensive market data"""
        try:
            symbol_to_id = self._get_symbol_mapping()
            available_symbols = [s for s in symbols if s in symbol_to_id]
            
            if not available_symbols:
                return {}
            
            ids = [symbol_to_id[s] for s in available_symbols]
            url = f"{self.base_url}/coins/markets"
            params = {
                'ids': ','.join(ids),
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': len(ids),
                'page': 1,
                'sparkline': False
            }
            
            if self.api_key:
                params['x_cg_demo_api_key'] = self.api_key
            
            response = self._make_request(url, params)
            if not response:
                return {}
            
            # Convert to symbol-based format
            market_data = {}
            for coin in response:
                symbol = next((s for s, coin_id in symbol_to_id.items() if coin_id == coin['id']), None)
                if symbol:
                    market_data[symbol] = {
                        'price': coin['current_price'],
                        'market_cap': coin['market_cap'],
                        'volume_24h': coin['total_volume'],
                        'price_change_24h': coin['price_change_percentage_24h'],
                        'market_cap_rank': coin['market_cap_rank']
                    }
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error getting CoinGecko market data: {e}")
            return {}

class CCXTDataCollector(BaseDataCollector):
    """Collector using CCXT library for multiple exchanges"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.exchanges = {}
        self._initialize_exchanges()
    
    def _initialize_exchanges(self):
        """Initialize exchange connections"""
        exchanges_to_use = ['binance', 'coinbase', 'kraken']
        
        for exchange_id in exchanges_to_use:
            try:
                exchange_class = getattr(ccxt, exchange_id)
                self.exchanges[exchange_id] = exchange_class({
                    'enableRateLimit': True,
                    'timeout': 30000,
                })
            except Exception as e:
                logger.error(f"Failed to initialize {exchange_id}: {e}")
    
    def get_prices_multi_exchange(self, symbols: List[str]) -> Dict[str, Dict[str, float]]:
        """Get prices from multiple exchanges"""
        results = {}
        
        for exchange_id, exchange in self.exchanges.items():
            try:
                prices = {}
                for symbol in symbols:
                    try:
                        ticker = exchange.fetch_ticker(f"{symbol}/USDT")
                        prices[symbol] = ticker['last']
                    except Exception as e:
                        logger.debug(f"Failed to get {symbol} from {exchange_id}: {e}")
                        continue
                
                if prices:
                    results[exchange_id] = prices
                    
            except Exception as e:
                logger.error(f"Error getting prices from {exchange_id}: {e}")
        
        return results
    
    def get_best_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get best available prices across exchanges"""
        multi_prices = self.get_prices_multi_exchange(symbols)
        
        best_prices = {}
        for symbol in symbols:
            prices = []
            for exchange_prices in multi_prices.values():
                if symbol in exchange_prices:
                    prices.append(exchange_prices[symbol])
            
            if prices:
                # Use median price to avoid outliers
                best_prices[symbol] = sorted(prices)[len(prices)//2]
        
        return best_prices 