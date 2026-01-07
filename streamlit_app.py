"""
Streamlit Dashboard for Weather Agent API
Interactive UI for AI-powered weather analysis
"""

import streamlit as st
import requests
import json
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd

# =============================================================================
# Configuration
# =============================================================================

# Set page config (must be first Streamlit command)
st.set_page_config(
    page_title="AI Weather Agent",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
# Change this to your Cloud Run URL, or use localhost for testing
USE_CLOUD = False  # Set to True when using Cloud Run

if USE_CLOUD:
    API_URL = "https://weather-agent-api-620429941346.asia-east1.run.app"  # Replace with your actual URL
else:
    API_URL = "http://localhost:8000"  # Local development


# =============================================================================
# Helper Functions
# =============================================================================

def check_api_health():
    """Check if API is available"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, str(e)


def get_weather_analysis(days: int, custom_question: str = None):
    """Call the weather analysis endpoint"""
    try:
        payload = {"days": days}
        if custom_question and custom_question.strip():
            payload["custom_question"] = custom_question.strip()
        
        response = requests.post(
            f"{API_URL}/analyze",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        return False, str(e)


def create_temperature_gauge(current_temp, mean_temp, min_temp, max_temp):
    """Create a temperature gauge chart"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=current_temp,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Current Temperature (°C)"},
        delta={'reference': mean_temp, 'valueformat': ".1f"},
        gauge={
            'axis': {'range': [min_temp - 5, max_temp + 5]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_temp - 5, mean_temp], 'color': "lightblue"},
                {'range': [mean_temp, max_temp + 5], 'color': "lightcoral"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': mean_temp
            }
        }
    ))
    
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def create_stats_chart(stats):
    """Create a bar chart of key statistics"""
    categories = ['Current', 'Mean', 'Min', 'Max']
    values = [
        stats['current_temp'],
        stats['mean_temp'],
        stats['min_temp'],
        stats['max_temp']
    ]
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=values,
            text=[f"{v:.1f}°C" for v in values],
            textposition='auto',
            marker_color=colors
        )
    ])
    
    fig.update_layout(
        title="Temperature Overview",
        yaxis_title="Temperature (°C)",
        height=350,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


# =============================================================================
# Main App
# =============================================================================

def main():
    # Header
    st.title("🌦️ AI Weather Agent Dashboard")
    st.markdown("### Intelligent Weather Analysis powered by LLM + BigQuery")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Status
        st.subheader("📡 API Status")
        is_healthy, health_data = check_api_health()
        
        if is_healthy:
            st.success("✅ API Online")
            with st.expander("API Details"):
                st.json(health_data)
        else:
            st.error("❌ API Offline")
            st.warning(f"Error: {health_data}")
            st.info("Make sure your API is running:\n```\npython src/app.py\n```")
        
        st.divider()
        
        # Analysis Settings
        st.subheader("🔧 Analysis Settings")
        days = st.slider(
            "Days to Analyze",
            min_value=7,
            max_value=90,
            value=30,
            help="Number of recent days to analyze"
        )
        
        custom_question = st.text_area(
            "Custom Question (Optional)",
            placeholder="e.g., Has there been unusual weather recently?",
            help="Ask a specific question about the weather"
        )
        
        analyze_button = st.button("🔍 Analyze Weather", type="primary", use_container_width=True)
    
    # Main Content Area
    if not is_healthy:
        st.error("⚠️ Cannot connect to Weather Agent API. Please start the API first.")
        st.info("""
        **To start the API:**
        1. Open a terminal
        2. Navigate to project folder
        3. Activate virtual environment: `venv\\Scripts\\activate`
        4. Run: `python src/app.py`
        5. Refresh this page
        """)
        return
    
    # Analysis Section
    if analyze_button:
        with st.spinner(f"🤖 Analyzing {days} days of weather data..."):
            success, result = get_weather_analysis(days, custom_question)
        
        if success:
            st.success("✅ Analysis Complete!")
            
            # Store in session state for persistence
            st.session_state['last_result'] = result
        else:
            st.error(f"❌ Analysis Failed: {result}")
            return
    
    # Display Results (if available)
    if 'last_result' in st.session_state:
        result = st.session_state['last_result']
        
        # Header Info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Station ID", result['station_id'])
        with col2:
            st.metric("Days Analyzed", result['days_analyzed'])
        with col3:
            st.metric("Model", "Llama 3.2")
        
        st.divider()
        
        # Statistics Section
        st.header("📊 Statistical Analysis")
        
        stats = result['statistics']
        
        # Row 1: Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            delta_color = "normal" if abs(stats['z_score']) < 1 else "inverse"
            st.metric(
                "Current Temp",
                f"{stats['current_temp']}°C",
                f"{stats['current_temp'] - stats['mean_temp']:.1f}°C"
            )
        
        with col2:
            st.metric("Mean Temp", f"{stats['mean_temp']}°C")
        
        with col3:
            st.metric("Std Dev", f"{stats['std_dev']}°C")
        
        with col4:
            anomaly_emoji = "🚨" if stats['anomaly_detected'] else "✅"
            st.metric("Anomaly Status", anomaly_emoji)
        
        # Row 2: Charts
        col1, col2 = st.columns(2)
        
        with col1:
            gauge_fig = create_temperature_gauge(
                stats['current_temp'],
                stats['mean_temp'],
                stats['min_temp'],
                stats['max_temp']
            )
            st.plotly_chart(gauge_fig, use_container_width=True)
        
        with col2:
            stats_fig = create_stats_chart(stats)
            st.plotly_chart(stats_fig, use_container_width=True)
        
        # Row 3: Detailed Stats
        st.subheader("📈 Detailed Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Z-Score:** {stats['z_score']}")
            z_interpretation = "Normal" if abs(stats['z_score']) < 1 else "Unusual" if abs(stats['z_score']) < 2 else "Anomaly"
            st.caption(f"Interpretation: {z_interpretation}")
        
        with col2:
            st.info(f"**Day-over-Day:** {stats['day_over_day_change']:+.1f}°C")
            st.caption("24-hour temperature change")
        
        with col3:
            st.info(f"**Week-over-Week:** {stats['week_over_week_change']:+.1f}°C")
            st.caption("7-day average change")
        
        # Temperature Range
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Min Temperature", f"{stats['min_temp']}°C", f"{stats['min_temp'] - stats['mean_temp']:.1f}°C")
        with col2:
            st.metric("Max Temperature", f"{stats['max_temp']}°C", f"{stats['max_temp'] - stats['mean_temp']:.1f}°C")
        
        # Flags
        st.subheader("🚩 Detection Flags")
        flag_col1, flag_col2 = st.columns(2)
        
        with flag_col1:
            if stats['anomaly_detected']:
                st.error("🚨 **Anomaly Detected** (|z-score| > 2)")
            else:
                st.success("✅ No anomaly detected")
        
        with flag_col2:
            if stats['significant_spike']:
                st.warning("⚠️ **Significant Spike** (|Δ| > 5°C)")
            else:
                st.success("✅ No significant spike")
        
        st.divider()
        
        # AI Analysis Section
        st.header("🤖 AI-Generated Analysis")
        
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #1f77b4;">
            <p style="font-size: 16px; line-height: 1.6; color: #333;">
                {result['llm_analysis']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.caption(f"Generated by {result['model_used']} at {result['timestamp']}")
        
        st.divider()
        
        # Raw Data Section (Expandable)
        with st.expander("🔍 View Raw JSON Response"):
            st.json(result)
    
    else:
        # Welcome Screen
        st.info("👈 Configure your analysis settings in the sidebar and click **Analyze Weather** to get started!")
        
        st.markdown("""
        ### How It Works
        
        1. **Select Days**: Choose how many recent days to analyze (7-90)
        2. **Custom Question**: Optionally ask a specific question about weather patterns
        3. **Analyze**: Click the button to fetch data and generate insights
        
        ### What You'll Get
        
        - 📊 **Statistical Analysis**: Mean, standard deviation, z-scores, temperature trends
        - 🚨 **Anomaly Detection**: Automatic flagging of unusual weather patterns
        - 🤖 **AI Insights**: Natural language explanations powered by Llama 3.2
        - 📈 **Visualizations**: Interactive charts and gauges
        
        ### Data Source
        
        Weather data comes from **NOAA Global Summary of the Day (GSOD)** dataset via Google BigQuery.
        """)
    
    # Footer
    st.divider()
    st.caption("Built with Streamlit • Powered by FastAPI, BigQuery, and Llama 3.2 LLM")


# =============================================================================
# Run App
# =============================================================================

if __name__ == "__main__":
    main()

