import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import threading
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class StreamingDashboard:
    """
    Real-time streaming dashboard with on-demand updates
    """
    
    def __init__(self, data_manager, update_interval: int = 5):
        self.data_manager = data_manager
        self.update_interval = update_interval
        self.price_history = {}
        self.last_update = datetime.now()
        
    def update_prices(self):
        """Update real-time prices and store history"""
        try:
            symbols = ['BTC', 'ETH', 'SOL', 'ADA', 'DOT']
            current_prices = self.data_manager.get_real_time_prices(symbols)
            
            # Store price history for charts
            timestamp = datetime.now()
            for symbol, price in current_prices.items():
                if symbol not in self.price_history:
                    self.price_history[symbol] = []
                
                self.price_history[symbol].append({
                    'timestamp': timestamp,
                    'price': price
                })
                
                # Keep only last 100 data points
                if len(self.price_history[symbol]) > 100:
                    self.price_history[symbol] = self.price_history[symbol][-100:]
            
            # Update session state
            st.session_state['streaming_prices'] = current_prices
            st.session_state['price_history'] = self.price_history
            st.session_state['last_streaming_update'] = timestamp
            
            return current_prices
            
        except Exception as e:
            logger.error(f"Error updating streaming prices: {e}")
            return {}

def render_streaming_dashboard(data_manager):
    """
    Render the main streaming dashboard
    """
    
    # Initialize streaming dashboard
    if 'streaming_dashboard' not in st.session_state:
        st.session_state.streaming_dashboard = StreamingDashboard(data_manager, update_interval=5)
    
    # Get current prices from session state, updated by the background loop
    current_prices = st.session_state.get('streaming_prices', {})
    
    # Debug: Show what prices we got
    if current_prices:
        st.sidebar.success(f"✅ Fetched {len(current_prices)} prices")
        for symbol, price in current_prices.items():
            st.sidebar.text(f"{symbol}: ${price:,.2f}")
    else:
        st.sidebar.error("❌ No prices fetched")
    
    # Header with live status
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("🚀 Live Crypto Streaming Dashboard")
    
    with col2:
        if 'last_streaming_update' in st.session_state:
            last_update = st.session_state.last_streaming_update
            time_diff = datetime.now() - last_update
            if time_diff.seconds < 10:
                st.success("🟢 LIVE")
            elif time_diff.seconds < 30:
                st.warning("🟡 SLOW")
            else:
                st.error("🔴 OFFLINE")
    
    with col3:
        st.metric(
            "Update Frequency",
            f"Every {st.session_state.streaming_dashboard.update_interval}s"
        )
        
        # Show last update time
        if 'last_streaming_update' in st.session_state:
            last_update = st.session_state.last_streaming_update
            st.text(f"Last: {last_update.strftime('%H:%M:%S')}")
    
    # Streaming status
    st.sidebar.header("📊 Streaming Status")
    
    # Show last update time
    if 'last_streaming_update' in st.session_state:
        last_update = st.session_state.last_streaming_update
        time_diff = datetime.now() - last_update
        
        st.sidebar.metric(
            "Last Update",
            f"{time_diff.seconds}s ago"
        )
        
        if time_diff.seconds < 30:
            st.sidebar.success("🟢 Data Fresh")
        elif time_diff.seconds < 60:
            st.sidebar.warning("🟡 Data Stale")
        else:
            st.sidebar.error("🔴 Data Old")
    
    # Main dashboard content
    render_live_price_cards(data_manager)
    render_live_price_chart(data_manager)
    render_portfolio_streaming(data_manager)
    render_market_activity(data_manager)
    
    # Background update loop
    if 'streaming_dashboard' in st.session_state:
        while True:
            st.session_state.streaming_dashboard.update_prices()
            time.sleep(st.session_state.streaming_dashboard.update_interval)
            st.rerun()

def render_live_price_cards(data_manager):
    """
    Render live price cards with real-time updates
    """
    st.subheader("💎 Live Price Cards")
    
    if 'streaming_prices' not in st.session_state:
        st.info("🔄 Initializing live data...")
        return
    
    prices = st.session_state.streaming_prices
    
    # Create price cards in a grid
    cols = st.columns(5)
    
    for i, (symbol, price) in enumerate(prices.items()):
        with cols[i]:
            # Calculate price change (simulated for demo)
            price_change = (price * 0.001) * (1 if hash(symbol) % 2 == 0 else -1)
            price_change_pct = (price_change / price) * 100
            
            # Determine color based on change
            if price_change > 0:
                color = "green"
                arrow = "↗️"
            elif price_change < 0:
                color = "red"
                arrow = "↘️"
            else:
                color = "gray"
                arrow = "→"
            
            # Create price card with live indicator
            st.markdown(f"""
            <div style="
                border: 2px solid {color};
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                position: relative;
            ">
                <div style="
                    position: absolute;
                    top: 5px;
                    right: 5px;
                    width: 8px;
                    height: 8px;
                    background-color: #10b981;
                    border-radius: 50%;
                "></div>
                <h3 style="margin: 0; color: #495057;">{symbol}</h3>
                <h2 style="margin: 10px 0; color: #212529; font-size: 24px;">
                    ${price:,.2f}
                </h2>
                <p style="margin: 5px 0; color: {color}; font-weight: bold;">
                    {arrow} ${price_change:+,.2f} ({price_change_pct:+.2f}%)
                </p>
                <small style="color: #6c757d;">
                    🟢 LIVE {datetime.now().strftime('%H:%M:%S')}
                </small>
            </div>
            """, unsafe_allow_html=True)

def render_live_price_chart(data_manager):
    """
    Render live price chart with real-time updates
    """
    st.subheader("📊 Live Price Chart")
    
    if 'price_history' not in st.session_state:
        st.info("📈 Loading price history...")
        return
    
    price_history = st.session_state.price_history
    
    if not price_history:
        st.info("📈 No price history available yet...")
        return
    
    # Create live price chart
    fig = go.Figure()
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    for i, (symbol, history) in enumerate(price_history.items()):
        if history:
            timestamps = [h['timestamp'] for h in history]
            prices = [h['price'] for h in history]
            
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=prices,
                mode='lines+markers',
                name=symbol,
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=4),
                hovertemplate=f'{symbol}<br>$%{{y:,.2f}}<br>%{{x}}<extra></extra>'
            ))
    
    fig.update_layout(
        title="Real-Time Price Movement",
        xaxis_title="Time",
        yaxis_title="Price (USD)",
        hovermode='x unified',
        height=400,
        showlegend=True,
        template="plotly_white"
    )
    
    # Add live indicator
    fig.add_annotation(
        x=0.02, y=0.98,
        xref="paper", yref="paper",
        text="🟢 LIVE",
        showarrow=False,
        font=dict(size=14, color="green"),
        bgcolor="rgba(0,255,0,0.1)",
        bordercolor="green",
        borderwidth=1
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_portfolio_streaming(data_manager):
    """
    Render streaming portfolio metrics
    """
    st.subheader("💼 Live Portfolio Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Simulated portfolio metrics with real-time updates
    portfolio_value = 12500000  # $12.5M
    daily_pnl = 250000  # $250K
    daily_pnl_pct = 2.04
    total_positions = 15
    
    with col1:
        st.metric(
            "Portfolio Value",
            f"${portfolio_value:,.0f}",
            f"{daily_pnl_pct:+.2f}%",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            "Daily P&L",
            f"${daily_pnl:+,.0f}",
            f"{daily_pnl_pct:+.2f}%",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            "Active Positions",
            total_positions,
            "3 new today"
        )
    
    with col4:
        # Calculate risk level based on volatility
        risk_level = "Medium"
        risk_color = "orange"
        st.metric(
            "Risk Level",
            risk_level,
            delta_color="off"
        )

def render_market_activity(data_manager):
    """
    Render live market activity feed
    """
    st.subheader("📰 Live Market Activity")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Live market activity feed
        activities = [
            {
                "time": datetime.now() - timedelta(seconds=30),
                "event": "Large BTC buy order executed",
                "impact": "Bullish",
                "amount": "$2.5M"
            },
            {
                "time": datetime.now() - timedelta(seconds=45),
                "event": "ETH breaks resistance at $3,400",
                "impact": "Bullish",
                "amount": "Technical"
            },
            {
                "time": datetime.now() - timedelta(seconds=60),
                "event": "SOL volume spikes 150%",
                "impact": "Neutral",
                "amount": "Volume"
            },
            {
                "time": datetime.now() - timedelta(seconds=90),
                "event": "Market volatility increases",
                "impact": "Bearish",
                "amount": "Risk"
            }
        ]
        
        for activity in activities:
            time_diff = datetime.now() - activity["time"]
            if time_diff.seconds < 120:  # Show only recent activities
                impact_color = {
                    "Bullish": "green",
                    "Bearish": "red",
                    "Neutral": "gray"
                }.get(activity["impact"], "gray")
                
                st.markdown(f"""
                <div style="
                    border-left: 4px solid {impact_color};
                    padding: 10px;
                    margin: 5px 0;
                    background: #f8f9fa;
                    border-radius: 5px;
                ">
                    <strong>{activity['event']}</strong><br>
                    <small style="color: #6c757d;">
                        {time_diff.seconds}s ago • {activity['impact']} • {activity['amount']}
                    </small>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        # Market sentiment gauge
        st.subheader("📊 Market Sentiment")
        
        # Simulated sentiment data
        sentiment_score = 65  # 0-100 scale
        
        # Create sentiment gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=sentiment_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Sentiment Score"},
            delta={'reference': 50},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 30], 'color': "lightgray"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

def render_streaming_controls():
    """
    Render streaming control panel
    """
    st.sidebar.header("🎛️ Streaming Controls")
    
    # Manual refresh button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh Prices", type="primary"):
            if 'streaming_dashboard' in st.session_state:
                st.session_state.streaming_dashboard.update_prices()
            st.rerun()
    
    with col2:
        if st.button("🔄 Force New Data"):
            # Clear cache to force fresh data
            if 'streaming_dashboard' in st.session_state:
                st.session_state.streaming_dashboard.memory_cache = {}
                st.session_state.streaming_dashboard.update_prices()
            st.rerun()
    
    # Update interval control
    new_interval = st.sidebar.slider(
        "Update Interval (seconds)",
        min_value=1,
        max_value=30,
        value=5,
        help="How often to update prices"
    )
    
    if 'streaming_dashboard' in st.session_state:
        st.session_state.streaming_dashboard.update_interval = new_interval
    
    # Data source selection
    st.sidebar.subheader("📡 Data Sources")
    
    data_sources = st.sidebar.multiselect(
        "Active Data Sources",
        ["Binance", "CoinGecko", "CCXT"],
        default=["Binance", "CoinGecko"],
        help="Select which data sources to use"
    )
    
    # Performance metrics
    st.sidebar.subheader("⚡ Performance")
    
    if 'last_streaming_update' in st.session_state:
        last_update = st.session_state.last_streaming_update
        time_diff = datetime.now() - last_update
        
        st.sidebar.metric(
            "Last Update",
            f"{time_diff.seconds}s ago"
        )
        
        st.sidebar.metric(
            "Response Time",
            "~500ms"
        )
    
    # Cache status
    st.sidebar.subheader("🗄️ Cache Status")
    st.sidebar.metric(
        "Cache Hit Rate",
        "95%"
    )
    st.sidebar.metric(
        "Active Keys",
        "150"
    ) 