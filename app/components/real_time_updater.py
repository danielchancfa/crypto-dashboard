import streamlit as st
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Callable
import logging

logger = logging.getLogger(__name__)

class RealTimeUpdater:
    """
    Handles real-time data updates in Streamlit
    """
    
    def __init__(self, data_manager, update_interval: int = 30):
        self.data_manager = data_manager
        self.update_interval = update_interval
        self.last_update = datetime.now()
        self.is_running = False
        self.update_callbacks = []
        
    def add_update_callback(self, callback: Callable):
        """Add a callback function to be called on data updates"""
        self.update_callbacks.append(callback)
    
    def start_background_updates(self):
        """Start background thread for data updates"""
        if not self.is_running:
            self.is_running = True
            thread = threading.Thread(target=self._background_update_loop, daemon=True)
            thread.start()
    
    def _background_update_loop(self):
        """Background loop for updating data"""
        while self.is_running:
            try:
                # Update data
                self._update_data()
                
                # Call registered callbacks
                for callback in self.update_callbacks:
                    try:
                        callback()
                    except Exception as e:
                        logger.error(f"Callback error: {e}")
                
                # Wait for next update
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Background update error: {e}")
                time.sleep(5)  # Short delay on error
    
    def _update_data(self):
        """Update all real-time data"""
        try:
            # Update prices
            symbols = ['BTC', 'ETH', 'SOL', 'ADA', 'DOT']
            prices = self.data_manager.get_real_time_prices(symbols)
            
            # Update portfolio metrics
            portfolio_metrics = self.data_manager.calculate_portfolio_metrics()
            
            # Update data quality
            data_quality = self.data_manager.validate_data_quality()
            
            # Store in session state
            st.session_state['real_time_prices'] = prices
            st.session_state['portfolio_metrics'] = portfolio_metrics
            st.session_state['data_quality'] = data_quality
            st.session_state['last_update'] = datetime.now()
            
        except Exception as e:
            logger.error(f"Data update error: {e}")
    
    def stop_updates(self):
        """Stop background updates"""
        self.is_running = False

def render_real_time_monitor(data_manager):
    """
    Render the real-time monitoring page
    """
    st.title("📈 Real-Time Monitor")
    
    # Initialize real-time updater
    if 'real_time_updater' not in st.session_state:
        st.session_state.real_time_updater = RealTimeUpdater(data_manager)
    
    # Start background updates if not already running
    if not st.session_state.real_time_updater.is_running:
        st.session_state.real_time_updater.start_background_updates()
    
    # Real-time data display
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Live Price Feeds")
        
        # Price table with real-time updates
        if 'real_time_prices' in st.session_state:
            prices = st.session_state.real_time_prices
            
            # Create price table
            price_data = []
            for symbol, price in prices.items():
                # Calculate 24h change (simulated)
                change_24h = (price * 0.02) * (1 if hash(symbol) % 2 == 0 else -1)
                change_pct = (change_24h / price) * 100
                
                price_data.append({
                    'Symbol': symbol,
                    'Price': f"${price:,.2f}",
                    '24h Change': f"${change_24h:+,.2f}",
                    '24h %': f"{change_pct:+.2f}%"
                })
            
            # Display as table with styling
            import pandas as pd
            df = pd.DataFrame(price_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Loading real-time prices...")
    
    with col2:
        st.subheader("Portfolio Status")
        
        if 'portfolio_metrics' in st.session_state:
            metrics = st.session_state.portfolio_metrics
            
            # Key metrics cards
            st.metric(
                label="Portfolio NAV",
                value=f"${metrics['nav']:,.0f}",
                delta=f"{metrics['total_return_pct']:+.2f}%"
            )
            
            st.metric(
                label="Daily P&L",
                value=f"${metrics['unrealized_pnl']:,.0f}",
                delta=f"{metrics['total_return_pct']:+.2f}%"
            )
            
            st.metric(
                label="Sharpe Ratio",
                value=f"{metrics['risk_metrics']['sharpe_ratio']:.2f}",
                delta=None
            )
        else:
            st.info("Loading portfolio metrics...")
    
    # Data quality section
    st.subheader("🔍 Data Quality Monitor")
    
    if 'data_quality' in st.session_state:
        quality = st.session_state.data_quality
        
        # Quality score gauge
        quality_score = quality.get('quality_score', 0)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Data Quality Score",
                value=f"{quality_score:.1%}",
                delta=None
            )
        
        with col2:
            status = quality.get('overall_status', 'UNKNOWN')
            status_color = {
                'GOOD': '🟢',
                'WARNING': '🟡',
                'CRITICAL': '🔴',
                'ERROR': '🔴'
            }.get(status, '⚪')
            
            st.metric(
                label="Overall Status",
                value=f"{status_color} {status}",
                delta=None
            )
        
        with col3:
            if 'last_update' in st.session_state:
                last_update = st.session_state.last_update
                time_diff = datetime.now() - last_update
                st.metric(
                    label="Last Update",
                    value=f"{time_diff.seconds}s ago",
                    delta=None
                )
        
        # Validation results table
        if 'validation_results' in quality:
            st.subheader("Price Validation Results")
            
            validation_data = []
            for symbol, result in quality['validation_results'].items():
                validation_data.append({
                    'Symbol': symbol,
                    'Binance': f"${result['binance_price']:,.2f}",
                    'CoinGecko': f"${result['coingecko_price']:,.2f}",
                    'Deviation': f"{result['deviation_pct']:.3f}%",
                    'Status': '✅' if result['is_valid'] else '❌'
                })
            
            df = pd.DataFrame(validation_data)
            st.dataframe(df, use_container_width=True)
    
    # Auto-refresh functionality
    st.subheader("⚙️ Update Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        update_interval = st.slider(
            "Update Interval (seconds)",
            min_value=10,
            max_value=300,
            value=30,
            step=10
        )
        
        if st.button("Update Settings"):
            st.session_state.real_time_updater.update_interval = update_interval
            st.success("Update interval changed!")
    
    with col2:
        if st.button("Manual Refresh"):
            st.session_state.real_time_updater._update_data()
            st.success("Data refreshed!")
        
        if st.button("Stop Updates"):
            st.session_state.real_time_updater.stop_updates()
            st.warning("Updates stopped!")

def render_live_charts(data_manager):
    """
    Render live updating charts
    """
    st.subheader("📊 Live Charts")
    
    # Portfolio performance chart
    if 'portfolio_metrics' in st.session_state:
        metrics = st.session_state.portfolio_metrics
        
        # Create sample time series data
        import numpy as np
        import plotly.graph_objects as go
        from datetime import datetime, timedelta
        
        # Generate time series data
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        times = []
        nav_values = []
        current_time = start_time
        
        while current_time <= end_time:
            times.append(current_time)
            # Simulate NAV changes
            base_nav = 12000000
            nav_change = np.sin((current_time - start_time).total_seconds() / 3600) * 500000
            nav_values.append(base_nav + nav_change)
            current_time += timedelta(minutes=15)
        
        # Create chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=times,
            y=nav_values,
            mode='lines',
            name='Portfolio NAV',
            line=dict(color='#3b82f6', width=2)
        ))
        
        fig.update_layout(
            title="Portfolio NAV - Last 24 Hours",
            xaxis_title="Time",
            yaxis_title="NAV ($)",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Price correlation heatmap
    if 'real_time_prices' in st.session_state:
        st.subheader("Asset Correlation Matrix")
        
        # Simulate correlation data
        symbols = ['BTC', 'ETH', 'SOL', 'ADA', 'DOT']
        correlation_matrix = np.random.rand(len(symbols), len(symbols))
        correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
        np.fill_diagonal(correlation_matrix, 1)
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix,
            x=symbols,
            y=symbols,
            colorscale='RdBu',
            zmid=0
        ))
        
        fig.update_layout(
            title="Asset Correlation Matrix",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

def render_alerts_panel(data_manager):
    """
    Render real-time alerts and notifications
    """
    st.subheader("🚨 Live Alerts")
    
    # Simulate alerts
    alerts = [
        {
            'type': 'warning',
            'message': 'ETH price deviation detected: 2.3% from expected range',
            'time': datetime.now() - timedelta(minutes=2),
            'symbol': 'ETH'
        },
        {
            'type': 'info',
            'message': 'Portfolio rebalancing recommended based on current weights',
            'time': datetime.now() - timedelta(minutes=5),
            'symbol': 'PORTFOLIO'
        },
        {
            'type': 'success',
            'message': 'All data sources validated successfully',
            'time': datetime.now() - timedelta(minutes=1),
            'symbol': 'SYSTEM'
        }
    ]
    
    for alert in alerts:
        alert_type = alert['type']
        message = alert['message']
        time_ago = datetime.now() - alert['time']
        
        if alert_type == 'warning':
            st.warning(f"⚠️ {message} ({time_ago.seconds//60}m ago)")
        elif alert_type == 'info':
            st.info(f"ℹ️ {message} ({time_ago.seconds//60}m ago)")
        elif alert_type == 'success':
            st.success(f"✅ {message} ({time_ago.seconds//60}m ago)") 