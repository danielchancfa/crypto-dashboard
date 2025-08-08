import streamlit as st
import os
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# Import custom modules
from utils.config import load_config
from utils.data_manager import DataManager
from components.header import render_header
from components.sidebar import render_sidebar
from components.streaming_dashboard import render_streaming_dashboard, render_streaming_controls

# Page configuration
st.set_page_config(
    page_title="Crypto Hedge Fund Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f2937 0%, #374151 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #3b82f6;
    }
    .alert-card {
        background: #fef3c7;
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-card {
        background: #d1fae5;
        border: 1px solid #10b981;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f8fafc;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_data_manager():
    """Initialize data manager with caching"""
    config = load_config()
    return DataManager(config)

def main():
    """Main application function"""
    
    # Initialize session state
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = initialize_data_manager()
    
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    
    # Render header
    render_header()
    
    # Render sidebar
    selected_page = render_sidebar()
    
    # Main content area
    if selected_page == "Dashboard Overview":
        render_dashboard_overview()
    elif selected_page == "Live Streaming":
        render_streaming_dashboard(st.session_state.data_manager)
        render_streaming_controls()
    elif selected_page == "Real-Time Monitor":
        render_real_time_monitor()
    elif selected_page == "Portfolio Analytics":
        render_portfolio_analytics()
    elif selected_page == "Risk Management":
        render_risk_management()
    elif selected_page == "Data Quality":
        render_data_quality()

def render_dashboard_overview():
    """Render the main dashboard overview"""
    
    st.markdown('<div class="main-header"><h1>📊 Crypto Hedge Fund Dashboard</h1></div>', unsafe_allow_html=True)
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Portfolio NAV</h3>
            <h2>$12,847,392</h2>
            <p style="color: #10b981;">+2.34% (24h)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>Daily P&L</h3>
            <h2>$294,521</h2>
            <p style="color: #10b981;">+2.34%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>Sharpe Ratio</h3>
            <h2>1.87</h2>
            <p style="color: #6b7280;">30-day rolling</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>VaR (95%)</h3>
            <h2>-$847,392</h2>
            <p style="color: #ef4444;">-6.59%</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts row
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Portfolio Performance")
        # Create sample performance data
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        portfolio_values = 10000000 * (1 + np.cumsum(np.random.normal(0.001, 0.02, len(dates))))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=portfolio_values,
            mode='lines',
            name='Portfolio NAV',
            line=dict(color='#3b82f6', width=2)
        ))
        
        fig.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Asset Allocation")
        # Sample allocation data
        assets = ['BTC', 'ETH', 'SOL', 'ADA', 'DOT']
        allocations = [35, 25, 20, 12, 8]
        
        fig = go.Figure(data=[go.Pie(
            labels=assets,
            values=allocations,
            hole=0.4,
            marker_colors=['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
        )])
        
        fig.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Alerts and notifications
    st.subheader("🔔 Recent Alerts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="alert-card">
            <strong>⚠️ Data Quality Alert</strong><br>
            ETH price deviation detected: 2.3% from expected range<br>
            <small>Last updated: 2 minutes ago</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="success-card">
            <strong>✅ Position Reconciled</strong><br>
            All positions successfully reconciled with custodian<br>
            <small>Last updated: 5 minutes ago</small>
        </div>
        """, unsafe_allow_html=True)

def render_real_time_monitor():
    """Render real-time monitoring page"""
    st.title("📈 Real-Time Monitor")
    st.write("Live market data and portfolio monitoring")
    
    # Placeholder for real-time functionality
    st.info("Real-time monitoring features will be implemented in the next iteration")

def render_portfolio_analytics():
    """Render portfolio analytics page"""
    st.title("📊 Portfolio Analytics")
    st.write("Performance attribution and optimization analysis")
    
    # Placeholder for portfolio analytics
    st.info("Portfolio analytics features will be implemented in the next iteration")

def render_risk_management():
    """Render risk management page"""
    st.title("🛡️ Risk Management")
    st.write("Risk metrics, stress testing, and scenario analysis")
    
    # Placeholder for risk management
    st.info("Risk management features will be implemented in the next iteration")

def render_data_quality():
    """Render data quality page"""
    st.title("🔍 Data Quality")
    st.write("Data validation, reconciliation, and quality metrics")
    
    # Placeholder for data quality
    st.info("Data quality features will be implemented in the next iteration")

if __name__ == "__main__":
    main() 