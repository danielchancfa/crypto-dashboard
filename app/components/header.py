import streamlit as st
from datetime import datetime

def render_header():
    """
    Render the dashboard header with status indicators and navigation
    """
    
    # Header with gradient background
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
    ">
        <div>
            <h1 style="margin: 0; font-size: 2rem; font-weight: bold;">
                🏦 Crypto Hedge Fund Analytics
            </h1>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1rem;">
                Real-time Portfolio Monitoring & Risk Management
            </p>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 0.9rem; opacity: 0.8;">
                Last Updated: <span id="last-update">""" + datetime.now().strftime("%H:%M:%S") + """</span>
            </div>
            <div style="
                display: inline-block;
                background: #10b981;
                color: white;
                padding: 0.25rem 0.75rem;
                border-radius: 20px;
                font-size: 0.8rem;
                margin-top: 0.5rem;
            ">
                ● LIVE
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Status bar with key indicators
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
        <div style="
            background: white;
            padding: 0.75rem;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 0.8rem; color: #6b7280; margin-bottom: 0.25rem;">Data Quality</div>
            <div style="font-size: 1.2rem; font-weight: bold; color: #10b981;">98.5%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="
            background: white;
            padding: 0.75rem;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 0.8rem; color: #6b7280; margin-bottom: 0.25rem;">API Status</div>
            <div style="font-size: 1.2rem; font-weight: bold; color: #10b981;">● Online</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="
            background: white;
            padding: 0.75rem;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 0.8rem; color: #6b7280; margin-bottom: 0.25rem;">Positions</div>
            <div style="font-size: 1.2rem; font-weight: bold; color: #3b82f6;">3 Active</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="
            background: white;
            padding: 0.75rem;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 0.8rem; color: #6b7280; margin-bottom: 0.25rem;">Risk Level</div>
            <div style="font-size: 1.2rem; font-weight: bold; color: #f59e0b;">Medium</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div style="
            background: white;
            padding: 0.75rem;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 0.8rem; color: #6b7280; margin-bottom: 0.25rem;">Alerts</div>
            <div style="font-size: 1.2rem; font-weight: bold; color: #ef4444;">2 Active</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick action buttons
    st.markdown("""
    <div style="
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        display: flex;
        gap: 1rem;
        align-items: center;
    ">
        <span style="font-weight: bold; color: #374151;">Quick Actions:</span>
        <button style="
            background: #3b82f6;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
        ">🔄 Refresh Data</button>
        <button style="
            background: #10b981;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
        ">📊 Export Report</button>
        <button style="
            background: #f59e0b;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
        ">⚙️ Settings</button>
    </div>
    """, unsafe_allow_html=True) 