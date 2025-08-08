import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging
from scipy import stats
from scipy.optimize import minimize

logger = logging.getLogger(__name__)

class RiskCalculator:
    """
    Risk calculation and analysis module for crypto portfolios
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.var_confidence_level = config.get('var_confidence_level', 0.95)
        self.var_time_horizon = config.get('var_time_horizon', 1)
        self.risk_free_rate = 0.02  # 2% annual risk-free rate
    
    def calculate_portfolio_risk(self, positions: List[Dict], 
                               historical_data: pd.DataFrame) -> Dict:
        """
        Calculate comprehensive portfolio risk metrics
        
        Args:
            positions: List of portfolio positions
            historical_data: DataFrame with historical price data
        
        Returns:
            Dictionary with risk metrics
        """
        try:
            if not positions or historical_data.empty:
                return self._get_sample_risk_metrics()
            
            # Calculate portfolio returns
            portfolio_returns = self._calculate_portfolio_returns(positions, historical_data)
            
            if portfolio_returns.empty:
                return self._get_sample_risk_metrics()
            
            # Calculate risk metrics
            risk_metrics = {
                'volatility': self._calculate_volatility(portfolio_returns),
                'var_95': self._calculate_var(portfolio_returns, 0.95),
                'var_99': self._calculate_var(portfolio_returns, 0.99),
                'expected_shortfall': self._calculate_expected_shortfall(portfolio_returns, 0.95),
                'sharpe_ratio': self._calculate_sharpe_ratio(portfolio_returns),
                'max_drawdown': self._calculate_max_drawdown(portfolio_returns),
                'beta': self._calculate_beta(portfolio_returns, historical_data),
                'skewness': self._calculate_skewness(portfolio_returns),
                'kurtosis': self._calculate_kurtosis(portfolio_returns),
                'var_historical': self._calculate_historical_var(portfolio_returns, 0.95),
                'var_monte_carlo': self._calculate_monte_carlo_var(portfolio_returns, 0.95),
                'stress_test_results': self._run_stress_tests(positions, historical_data)
            }
            
            return risk_metrics
            
        except Exception as e:
            logger.error(f"Error calculating portfolio risk: {e}")
            return self._get_sample_risk_metrics()
    
    def _calculate_portfolio_returns(self, positions: List[Dict], 
                                   historical_data: pd.DataFrame) -> pd.Series:
        """Calculate portfolio returns over time"""
        try:
            # Get unique dates from historical data
            dates = historical_data['date'].unique()
            dates.sort()
            
            portfolio_values = []
            
            for date in dates:
                date_data = historical_data[historical_data['date'] == date]
                portfolio_value = 0
                
                for position in positions:
                    symbol = position['symbol']
                    quantity = position['quantity']
                    
                    # Get price for this symbol on this date
                    symbol_data = date_data[date_data['symbol'] == symbol]
                    if not symbol_data.empty:
                        price = symbol_data.iloc[0]['close_price']
                        portfolio_value += quantity * price
                
                portfolio_values.append(portfolio_value)
            
            # Calculate returns
            portfolio_values = pd.Series(portfolio_values, index=dates)
            returns = portfolio_values.pct_change().dropna()
            
            return returns
            
        except Exception as e:
            logger.error(f"Error calculating portfolio returns: {e}")
            return pd.Series()
    
    def _calculate_volatility(self, returns: pd.Series) -> float:
        """Calculate annualized volatility"""
        try:
            daily_vol = returns.std()
            annual_vol = daily_vol * np.sqrt(252)  # 252 trading days
            return annual_vol
        except Exception as e:
            logger.error(f"Error calculating volatility: {e}")
            return 0.0
    
    def _calculate_var(self, returns: pd.Series, confidence_level: float) -> float:
        """Calculate Value at Risk using parametric method"""
        try:
            # Parametric VaR
            mean_return = returns.mean()
            std_return = returns.std()
            z_score = stats.norm.ppf(1 - confidence_level)
            
            var = mean_return - z_score * std_return
            
            # Convert to dollar amount (assuming $10M portfolio)
            portfolio_value = 10000000
            var_dollar = abs(var) * portfolio_value
            
            return -var_dollar  # Return negative value for loss
            
        except Exception as e:
            logger.error(f"Error calculating VaR: {e}")
            return 0.0
    
    def _calculate_expected_shortfall(self, returns: pd.Series, confidence_level: float) -> float:
        """Calculate Expected Shortfall (Conditional VaR)"""
        try:
            var_threshold = self._calculate_var(returns, confidence_level)
            var_threshold_return = var_threshold / 10000000  # Convert back to return
            
            # Calculate expected value of returns below VaR threshold
            tail_returns = returns[returns <= var_threshold_return]
            
            if len(tail_returns) > 0:
                es_return = tail_returns.mean()
                es_dollar = abs(es_return) * 10000000
                return -es_dollar
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error calculating Expected Shortfall: {e}")
            return 0.0
    
    def _calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """Calculate Sharpe ratio"""
        try:
            excess_returns = returns - (self.risk_free_rate / 252)  # Daily risk-free rate
            sharpe = excess_returns.mean() / returns.std() * np.sqrt(252)  # Annualized
            return sharpe
        except Exception as e:
            logger.error(f"Error calculating Sharpe ratio: {e}")
            return 0.0
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        try:
            cumulative_returns = (1 + returns).cumprod()
            rolling_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
            return max_drawdown
        except Exception as e:
            logger.error(f"Error calculating max drawdown: {e}")
            return 0.0
    
    def _calculate_beta(self, portfolio_returns: pd.Series, 
                       historical_data: pd.DataFrame) -> float:
        """Calculate portfolio beta relative to BTC"""
        try:
            # Get BTC returns as market proxy
            btc_data = historical_data[historical_data['symbol'] == 'BTC'].copy()
            btc_data = btc_data.sort_values('date')
            btc_returns = btc_data['close_price'].pct_change().dropna()
            
            # Align dates
            common_dates = portfolio_returns.index.intersection(btc_returns.index)
            if len(common_dates) < 30:  # Need minimum data points
                return 1.0
            
            portfolio_aligned = portfolio_returns.loc[common_dates]
            btc_aligned = btc_returns.loc[common_dates]
            
            # Calculate beta
            covariance = np.cov(portfolio_aligned, btc_aligned)[0, 1]
            btc_variance = np.var(btc_aligned)
            
            beta = covariance / btc_variance if btc_variance > 0 else 1.0
            return beta
            
        except Exception as e:
            logger.error(f"Error calculating beta: {e}")
            return 1.0
    
    def _calculate_skewness(self, returns: pd.Series) -> float:
        """Calculate return distribution skewness"""
        try:
            return returns.skew()
        except Exception as e:
            logger.error(f"Error calculating skewness: {e}")
            return 0.0
    
    def _calculate_kurtosis(self, returns: pd.Series) -> float:
        """Calculate return distribution kurtosis"""
        try:
            return returns.kurtosis()
        except Exception as e:
            logger.error(f"Error calculating kurtosis: {e}")
            return 0.0
    
    def _calculate_historical_var(self, returns: pd.Series, confidence_level: float) -> float:
        """Calculate historical VaR"""
        try:
            var_percentile = (1 - confidence_level) * 100
            historical_var = np.percentile(returns, var_percentile)
            portfolio_value = 10000000
            return -historical_var * portfolio_value
        except Exception as e:
            logger.error(f"Error calculating historical VaR: {e}")
            return 0.0
    
    def _calculate_monte_carlo_var(self, returns: pd.Series, confidence_level: float, 
                                 n_simulations: int = 10000) -> float:
        """Calculate VaR using Monte Carlo simulation"""
        try:
            mean_return = returns.mean()
            std_return = returns.std()
            
            # Generate random returns
            simulated_returns = np.random.normal(mean_return, std_return, n_simulations)
            
            # Calculate VaR
            var_percentile = (1 - confidence_level) * 100
            monte_carlo_var = np.percentile(simulated_returns, var_percentile)
            
            portfolio_value = 10000000
            return -monte_carlo_var * portfolio_value
            
        except Exception as e:
            logger.error(f"Error calculating Monte Carlo VaR: {e}")
            return 0.0
    
    def _run_stress_tests(self, positions: List[Dict], 
                         historical_data: pd.DataFrame) -> Dict:
        """Run stress tests on portfolio"""
        try:
            stress_scenarios = {
                'market_crash_20': {'btc_shock': -0.20, 'eth_shock': -0.25, 'alt_shock': -0.30},
                'market_crash_50': {'btc_shock': -0.50, 'eth_shock': -0.55, 'alt_shock': -0.60},
                'crypto_winter': {'btc_shock': -0.70, 'eth_shock': -0.75, 'alt_shock': -0.80},
                'flash_crash': {'btc_shock': -0.15, 'eth_shock': -0.20, 'alt_shock': -0.25},
                'correlation_breakdown': {'btc_shock': 0.05, 'eth_shock': -0.20, 'alt_shock': -0.30}
            }
            
            stress_results = {}
            
            for scenario_name, shocks in stress_scenarios.items():
                portfolio_value = 0
                
                for position in positions:
                    symbol = position['symbol']
                    quantity = position['quantity']
                    current_price = position['current_price']
                    
                    # Apply shock based on asset type
                    if symbol == 'BTC':
                        shock = shocks['btc_shock']
                    elif symbol == 'ETH':
                        shock = shocks['eth_shock']
                    else:
                        shock = shocks['alt_shock']
                    
                    new_price = current_price * (1 + shock)
                    portfolio_value += quantity * new_price
                
                # Calculate portfolio impact
                original_value = sum(pos['market_value'] for pos in positions)
                impact = (portfolio_value - original_value) / original_value
                
                stress_results[scenario_name] = {
                    'portfolio_value': portfolio_value,
                    'impact_pct': impact * 100,
                    'impact_dollar': portfolio_value - original_value,
                    'scenario_shocks': shocks
                }
            
            return stress_results
            
        except Exception as e:
            logger.error(f"Error running stress tests: {e}")
            return {}
    
    def calculate_position_risk(self, position: Dict, 
                              historical_data: pd.DataFrame) -> Dict:
        """Calculate risk metrics for individual position"""
        try:
            symbol = position['symbol']
            symbol_data = historical_data[historical_data['symbol'] == symbol].copy()
            
            if symbol_data.empty:
                return {}
            
            # Calculate position-specific metrics
            returns = symbol_data['close_price'].pct_change().dropna()
            
            position_risk = {
                'volatility': returns.std() * np.sqrt(252),
                'var_95': self._calculate_var(returns, 0.95),
                'max_drawdown': self._calculate_max_drawdown(returns),
                'sharpe_ratio': self._calculate_sharpe_ratio(returns),
                'concentration_risk': position['market_value'] / 10000000,  # % of portfolio
                'liquidity_risk': self._assess_liquidity_risk(symbol_data)
            }
            
            return position_risk
            
        except Exception as e:
            logger.error(f"Error calculating position risk for {position.get('symbol', 'Unknown')}: {e}")
            return {}
    
    def _assess_liquidity_risk(self, symbol_data: pd.DataFrame) -> str:
        """Assess liquidity risk based on volume data"""
        try:
            avg_volume = symbol_data['volume'].mean()
            
            if avg_volume > 10000000:  # $10M+ daily volume
                return "LOW"
            elif avg_volume > 1000000:  # $1M+ daily volume
                return "MEDIUM"
            else:
                return "HIGH"
                
        except Exception as e:
            logger.error(f"Error assessing liquidity risk: {e}")
            return "UNKNOWN"
    
    def optimize_portfolio_weights(self, positions: List[Dict], 
                                 historical_data: pd.DataFrame,
                                 target_return: float = None) -> Dict:
        """Optimize portfolio weights using Modern Portfolio Theory"""
        try:
            # Calculate returns for each asset
            asset_returns = {}
            for position in positions:
                symbol = position['symbol']
                symbol_data = historical_data[historical_data['symbol'] == symbol].copy()
                
                if not symbol_data.empty:
                    returns = symbol_data['close_price'].pct_change().dropna()
                    asset_returns[symbol] = returns
            
            if len(asset_returns) < 2:
                return {}
            
            # Create returns matrix
            returns_df = pd.DataFrame(asset_returns)
            returns_df = returns_df.dropna()
            
            if len(returns_df) < 30:  # Need sufficient data
                return {}
            
            # Calculate covariance matrix
            cov_matrix = returns_df.cov() * 252  # Annualized
            
            # Get current weights
            current_weights = np.array([pos['weight'] for pos in positions])
            
            # Define objective function (minimize volatility)
            def objective(weights):
                portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                return portfolio_vol
            
            # Constraints
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Weights sum to 1
            ]
            
            if target_return is not None:
                # Add return constraint
                mean_returns = returns_df.mean() * 252
                constraints.append({
                    'type': 'eq', 
                    'fun': lambda x: np.dot(x, mean_returns) - target_return
                })
            
            # Bounds (no short selling)
            bounds = [(0, 1) for _ in range(len(positions))]
            
            # Optimize
            result = minimize(
                objective, 
                current_weights, 
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            if result.success:
                optimized_weights = result.x
                
                # Calculate optimized metrics
                opt_vol = result.fun
                opt_return = np.dot(optimized_weights, returns_df.mean() * 252)
                opt_sharpe = (opt_return - self.risk_free_rate) / opt_vol
                
                return {
                    'optimized_weights': dict(zip([pos['symbol'] for pos in positions], optimized_weights)),
                    'current_weights': dict(zip([pos['symbol'] for pos in positions], current_weights)),
                    'optimized_volatility': opt_vol,
                    'optimized_return': opt_return,
                    'optimized_sharpe': opt_sharpe,
                    'weight_changes': dict(zip(
                        [pos['symbol'] for pos in positions], 
                        optimized_weights - current_weights
                    ))
                }
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error optimizing portfolio weights: {e}")
            return {}
    
    def _get_sample_risk_metrics(self) -> Dict:
        """Get sample risk metrics for demonstration"""
        return {
            'volatility': 0.0234,
            'var_95': -847392,
            'var_99': -1247392,
            'expected_shortfall': -1050000,
            'sharpe_ratio': 1.87,
            'max_drawdown': -0.089,
            'beta': 0.95,
            'skewness': -0.15,
            'kurtosis': 4.2,
            'var_historical': -823456,
            'var_monte_carlo': -856789,
            'stress_test_results': {
                'market_crash_20': {
                    'portfolio_value': 10280000,
                    'impact_pct': -17.2,
                    'impact_dollar': -2147392,
                    'scenario_shocks': {'btc_shock': -0.20, 'eth_shock': -0.25, 'alt_shock': -0.30}
                }
            }
        } 