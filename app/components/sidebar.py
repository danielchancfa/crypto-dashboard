import streamlit as st
from datetime import datetime

def render_sidebar():
    """
    Render the sidebar with navigation and portfolio information
    """
    
    # Sidebar styling - Light theme for better readability
    st.markdown("""
    <style>
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Ensure all sidebar text is readable with dark text */
    .sidebar .sidebar-content .stSelectbox label,
    .sidebar .sidebar-content .stSelectbox .stSelectbox > div > div,
    .sidebar .sidebar-content .stSelectbox .stSelectbox > div > div > div,
    .sidebar .sidebar-content .stSelectbox .stSelectbox > div > div > div > div {
        color: #1f2937 !important;
    }
    
    /* Style the selectbox dropdown */
    .sidebar .sidebar-content .stSelectbox select {
        background-color: white !important;
        color: #1f2937 !important;
        border: 1px solid #d1d5db !important;
    }
    
    /* Style the selectbox options */
    .sidebar .sidebar-content .stSelectbox option {
        background-color: white !important;
        color: #1f2937 !important;
    }
    
    /* Ensure all markdown text in sidebar is dark */
    .sidebar .sidebar-content .stMarkdown {
        color: #1f2937 !important;
    }
    
    /* Style the selectbox container */
    .sidebar .sidebar-content .stSelectbox > div {
        background-color: transparent !important;
    }
    
    /* Style sidebar headers */
    .sidebar .sidebar-content h3 {
        color: #1f2937 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Portfolio summary in sidebar
    st.sidebar.markdown("""
    <div style="
        background: rgba(59, 130, 246, 0.1);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        color: #1f2937;
        border: 1px solid rgba(59, 130, 246, 0.2);
    ">
        <h3 style="margin: 0 0 1rem 0; font-size: 1.1rem; color: #1f2937;">📈 Portfolio Summary</h3>
        <div style="margin-bottom: 0.5rem;">
            <span style="opacity: 0.7; color: #374151;">NAV:</span>
            <span style="float: right; font-weight: bold; color: #1f2937;">$12.8M</span>
        </div>
        <div style="margin-bottom: 0.5rem;">
            <span style="opacity: 0.7; color: #374151;">Daily P&L:</span>
            <span style="float: right; font-weight: bold; color: #10b981;">+$294K</span>
        </div>
        <div style="margin-bottom: 0.5rem;">
            <span style="opacity: 0.7; color: #374151;">Sharpe Ratio:</span>
            <span style="float: right; font-weight: bold; color: #1f2937;">1.87</span>
        </div>
        <div style="margin-bottom: 0.5rem;">
            <span style="opacity: 0.7; color: #374151;">Risk Level:</span>
            <span style="float: right; font-weight: bold; color: #f59e0b;">Medium</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    st.sidebar.markdown("### 🧭 Navigation")
    
    # Page selection
    pages = [
        "Dashboard Overview",
        "Live Streaming",
        "Real-Time Monitor", 
        "Portfolio Analytics",
        "Risk Management",
        "Data Quality"
    ]
    
    selected_page = st.sidebar.selectbox(
        "Select Page",
        pages,
        index=0,
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    
    # Market overview
    st.sidebar.markdown("### 📊 Market Overview")
    
    # Sample market data
    market_data = {
        "BTC": {"price": 47000, "change": 2.1},
        "ETH": {"price": 3400, "change": 1.8},
        "SOL": {"price": 140, "change": 5.2},
        "ADA": {"price": 0.65, "change": -0.8},
        "DOT": {"price": 8.5, "change": 3.1}
    }
    
    for symbol, data in market_data.items():
        change_color = "#10b981" if data["change"] >= 0 else "#ef4444"
        change_symbol = "+" if data["change"] >= 0 else ""
        
        st.sidebar.markdown(f"""
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
        ">
            <span style="color: #1f2937; font-weight: bold;">{symbol}</span>
            <div style="text-align: right;">
                <div style="color: #1f2937; font-size: 0.9rem;">${data['price']:,.0f}</div>
                <div style="color: {change_color}; font-size: 0.8rem;">{change_symbol}{data['change']}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # Quick filters
    st.sidebar.markdown("### 🔍 Quick Filters")
    
    # Time period filter
    time_period = st.sidebar.selectbox(
        "Time Period",
        ["1D", "1W", "1M", "3M", "6M", "1Y"],
        index=2
    )
    
    # Risk level filter
    risk_level = st.sidebar.selectbox(
        "Risk Level",
        ["All", "Low", "Medium", "High"],
        index=0
    )
    
    # Asset class filter
    asset_class = st.sidebar.selectbox(
        "Asset Class",
        ["All", "Large Cap", "Mid Cap", "Small Cap", "DeFi", "Layer 1"],
        index=0
    )
    
    st.sidebar.markdown("---")
    
    # System status
    st.sidebar.markdown("### ⚙️ System Status")
    
    status_items = [
        ("Data Feed", "🟢 Online"),
        ("Database", "🟢 Connected"),
        ("API Limits", "🟡 85% Used"),
        ("Cache", "🟢 92% Hit Rate"),
        ("Alerts", "🔴 2 Active")
    ]
    
    for item, status in status_items:
        st.sidebar.markdown(f"""
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.25rem 0;
        ">
            <span style="color: white; font-size: 0.9rem;">{item}</span>
            <span style="color: white; font-size: 0.9rem;">{status}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # Last update
    st.sidebar.markdown(f"""
    <div style="
        text-align: center;
        padding: 1rem;
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.8rem;
    ">
        Last Updated<br>
        {datetime.now().strftime("%H:%M:%S")}
    </div>
    """, unsafe_allow_html=True)
    
    return selected_page 