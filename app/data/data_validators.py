import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    """
    Data validation and quality assurance module
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.price_deviation_threshold = config.get('price_deviation_threshold', 0.05)
        self.data_freshness_threshold = config.get('data_freshness_threshold', 300)
        self.volume_threshold = config.get('volume_threshold', 1000000)
    
    def validate_price_consistency(self, prices_dict: Dict[str, Dict[str, float]]) -> Dict[str, Dict]:
        """
        Validate price consistency across multiple sources
        
        Args:
            prices_dict: Dictionary with source names as keys and price dictionaries as values
            Example: {'binance': {'BTC': 47000}, 'coingecko': {'BTC': 47100}}
        
        Returns:
            Dictionary with validation results for each symbol
        """
        validation_results = {}
        
        if len(prices_dict) < 2:
            logger.warning("Need at least 2 sources for price validation")
            return validation_results
        
        # Get all unique symbols
        all_symbols = set()
        for source_prices in prices_dict.values():
            all_symbols.update(source_prices.keys())
        
        for symbol in all_symbols:
            symbol_prices = {}
            
            # Collect prices for this symbol from all sources
            for source, prices in prices_dict.items():
                if symbol in prices:
                    symbol_prices[source] = prices[symbol]
            
            if len(symbol_prices) < 2:
                continue
            
            # Calculate statistics
            prices_list = list(symbol_prices.values())
            mean_price = np.mean(prices_list)
            std_price = np.std(prices_list)
            cv = std_price / mean_price if mean_price > 0 else 0
            
            # Check for outliers
            outliers = []
            for source, price in symbol_prices.items():
                deviation = abs(price - mean_price) / mean_price
                if deviation > self.price_deviation_threshold:
                    outliers.append(source)
            
            # Determine overall validity
            is_valid = len(outliers) == 0 and cv < self.price_deviation_threshold
            
            validation_results[symbol] = {
                'prices': symbol_prices,
                'mean_price': mean_price,
                'std_price': std_price,
                'coefficient_of_variation': cv,
                'outliers': outliers,
                'is_valid': is_valid,
                'recommended_price': mean_price,
                'validation_timestamp': datetime.now()
            }
        
        return validation_results
    
    def validate_data_freshness(self, timestamps: Dict[str, datetime]) -> Dict[str, Dict]:
        """
        Validate data freshness across sources
        
        Args:
            timestamps: Dictionary with source names and their last update timestamps
        
        Returns:
            Dictionary with freshness validation results
        """
        validation_results = {}
        current_time = datetime.now()
        
        for source, timestamp in timestamps.items():
            if timestamp is None:
                validation_results[source] = {
                    'is_fresh': False,
                    'age_seconds': None,
                    'status': 'NO_TIMESTAMP'
                }
                continue
            
            age_seconds = (current_time - timestamp).total_seconds()
            is_fresh = age_seconds <= self.data_freshness_threshold
            
            validation_results[source] = {
                'is_fresh': is_fresh,
                'age_seconds': age_seconds,
                'status': 'FRESH' if is_fresh else 'STALE',
                'last_update': timestamp
            }
        
        return validation_results
    
    def validate_volume_data(self, volume_data: Dict[str, float]) -> Dict[str, Dict]:
        """
        Validate trading volume data
        
        Args:
            volume_data: Dictionary with symbol-volume pairs
        
        Returns:
            Dictionary with volume validation results
        """
        validation_results = {}
        
        for symbol, volume in volume_data.items():
            if volume is None or volume <= 0:
                validation_results[symbol] = {
                    'is_valid': False,
                    'volume': volume,
                    'status': 'INVALID_VOLUME',
                    'reason': 'Zero or negative volume'
                }
                continue
            
            # Check if volume meets minimum threshold
            meets_threshold = volume >= self.volume_threshold
            
            validation_results[symbol] = {
                'is_valid': meets_threshold,
                'volume': volume,
                'meets_threshold': meets_threshold,
                'threshold': self.volume_threshold,
                'status': 'SUFFICIENT' if meets_threshold else 'INSUFFICIENT'
            }
        
        return validation_results
    
    def detect_price_anomalies(self, historical_prices: pd.DataFrame, 
                             symbol: str, window: int = 20) -> Dict[str, List]:
        """
        Detect price anomalies using statistical methods
        
        Args:
            historical_prices: DataFrame with columns ['date', 'symbol', 'close_price']
            symbol: Symbol to analyze
            window: Rolling window size for calculations
        
        Returns:
            Dictionary with detected anomalies
        """
        try:
            # Filter data for the specific symbol
            symbol_data = historical_prices[historical_prices['symbol'] == symbol].copy()
            symbol_data = symbol_data.sort_values('date')
            
            if len(symbol_data) < window:
                return {'anomalies': [], 'reason': 'Insufficient data'}
            
            # Calculate rolling statistics
            symbol_data['rolling_mean'] = symbol_data['close_price'].rolling(window=window).mean()
            symbol_data['rolling_std'] = symbol_data['close_price'].rolling(window=window).std()
            
            # Calculate z-scores
            symbol_data['z_score'] = (
                (symbol_data['close_price'] - symbol_data['rolling_mean']) / 
                symbol_data['rolling_std']
            )
            
            # Detect anomalies (z-score > 3 or < -3)
            anomalies = symbol_data[abs(symbol_data['z_score']) > 3].copy()
            
            # Calculate percentage changes
            symbol_data['pct_change'] = symbol_data['close_price'].pct_change()
            
            # Detect large price movements (> 10% in one period)
            large_moves = symbol_data[abs(symbol_data['pct_change']) > 0.10].copy()
            
            return {
                'anomalies': anomalies.to_dict('records'),
                'large_moves': large_moves.to_dict('records'),
                'total_anomalies': len(anomalies),
                'total_large_moves': len(large_moves),
                'analysis_window': window
            }
            
        except Exception as e:
            logger.error(f"Error detecting anomalies for {symbol}: {e}")
            return {'anomalies': [], 'reason': f'Error: {str(e)}'}
    
    def validate_portfolio_data(self, portfolio_data: Dict) -> Dict[str, Dict]:
        """
        Validate portfolio data consistency
        
        Args:
            portfolio_data: Dictionary containing portfolio information
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'positions': {},
            'overall': {},
            'warnings': []
        }
        
        try:
            # Validate NAV calculation
            positions = portfolio_data.get('positions', [])
            calculated_nav = sum(pos.get('market_value', 0) for pos in positions)
            reported_nav = portfolio_data.get('nav', 0)
            
            nav_deviation = abs(calculated_nav - reported_nav) / reported_nav if reported_nav > 0 else 0
            
            if nav_deviation > 0.01:  # 1% tolerance
                validation_results['warnings'].append(
                    f"NAV mismatch: Calculated ${calculated_nav:,.0f} vs Reported ${reported_nav:,.0f}"
                )
            
            # Validate position weights sum to 100%
            total_weight = sum(pos.get('weight', 0) for pos in positions)
            if abs(total_weight - 1.0) > 0.01:  # 1% tolerance
                validation_results['warnings'].append(
                    f"Position weights don't sum to 100%: {total_weight:.2%}"
                )
            
            # Validate individual positions
            for position in positions:
                symbol = position.get('symbol', 'Unknown')
                pos_validation = {}
                
                # Check for required fields
                required_fields = ['quantity', 'avg_price', 'current_price', 'market_value']
                missing_fields = [field for field in required_fields if field not in position]
                
                if missing_fields:
                    pos_validation['status'] = 'INCOMPLETE'
                    pos_validation['missing_fields'] = missing_fields
                else:
                    # Validate calculations
                    calculated_mv = position['quantity'] * position['current_price']
                    reported_mv = position['market_value']
                    
                    mv_deviation = abs(calculated_mv - reported_mv) / reported_mv if reported_mv > 0 else 0
                    
                    if mv_deviation > 0.01:
                        pos_validation['status'] = 'CALCULATION_ERROR'
                        pos_validation['mv_deviation'] = mv_deviation
                    else:
                        pos_validation['status'] = 'VALID'
                
                validation_results['positions'][symbol] = pos_validation
            
            # Overall validation status
            has_errors = any(
                pos.get('status') in ['INCOMPLETE', 'CALCULATION_ERROR'] 
                for pos in validation_results['positions'].values()
            )
            
            validation_results['overall'] = {
                'is_valid': not has_errors and len(validation_results['warnings']) == 0,
                'nav_deviation': nav_deviation,
                'weight_sum': total_weight,
                'total_positions': len(positions)
            }
            
        except Exception as e:
            logger.error(f"Error validating portfolio data: {e}")
            validation_results['overall'] = {
                'is_valid': False,
                'error': str(e)
            }
        
        return validation_results
    
    def generate_data_quality_report(self, validation_results: Dict) -> Dict:
        """
        Generate comprehensive data quality report
        
        Args:
            validation_results: Dictionary containing all validation results
        
        Returns:
            Dictionary with quality report
        """
        report = {
            'summary': {},
            'details': validation_results,
            'recommendations': [],
            'timestamp': datetime.now()
        }
        
        # Calculate overall quality score
        total_checks = 0
        passed_checks = 0
        
        # Price consistency checks
        if 'price_consistency' in validation_results:
            price_results = validation_results['price_consistency']
            total_checks += len(price_results)
            passed_checks += sum(1 for result in price_results.values() if result.get('is_valid', False))
        
        # Data freshness checks
        if 'data_freshness' in validation_results:
            freshness_results = validation_results['data_freshness']
            total_checks += len(freshness_results)
            passed_checks += sum(1 for result in freshness_results.values() if result.get('is_fresh', False))
        
        # Volume validation checks
        if 'volume_validation' in validation_results:
            volume_results = validation_results['volume_validation']
            total_checks += len(volume_results)
            passed_checks += sum(1 for result in volume_results.values() if result.get('is_valid', False))
        
        # Calculate quality score
        quality_score = passed_checks / total_checks if total_checks > 0 else 0
        
        report['summary'] = {
            'quality_score': quality_score,
            'quality_percentage': quality_score * 100,
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': total_checks - passed_checks,
            'overall_status': self._get_quality_status(quality_score)
        }
        
        # Generate recommendations
        if quality_score < 0.8:
            report['recommendations'].append("Data quality below threshold. Review data sources and validation rules.")
        
        if 'price_consistency' in validation_results:
            outliers = sum(1 for result in validation_results['price_consistency'].values() 
                          if not result.get('is_valid', True))
            if outliers > 0:
                report['recommendations'].append(f"Found {outliers} price outliers. Consider data source reliability.")
        
        if 'data_freshness' in validation_results:
            stale_sources = sum(1 for result in validation_results['data_freshness'].values() 
                              if not result.get('is_fresh', True))
            if stale_sources > 0:
                report['recommendations'].append(f"Found {stale_sources} stale data sources. Check API connectivity.")
        
        return report
    
    def _get_quality_status(self, quality_score: float) -> str:
        """Get quality status based on score"""
        if quality_score >= 0.95:
            return "EXCELLENT"
        elif quality_score >= 0.85:
            return "GOOD"
        elif quality_score >= 0.70:
            return "FAIR"
        elif quality_score >= 0.50:
            return "POOR"
        else:
            return "CRITICAL" 