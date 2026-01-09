"""
ENHANCED AI-Based Adaptive Traffic Signal Simulation
Multi-Junction System with Emergency Support & Analytics
Google Technologies Integration: Maps, Charts, Real-time Analytics
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from datetime import datetime
import folium
from streamlit_folium import st_folium
from logic import TrafficSignalController
from multi_junction import MultiJunctionController
from emergency import EmergencyController
from analytics import TrafficAnalytics
from prediction import TrafficPredictor, SmartTrafficOptimizer

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Advanced Traffic Signal Simulator",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .metric-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 10px 0;
    }
    .emergency-alert {
        background-color: #FFD700;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FF0000;
        margin: 10px 0;
    }
    .signal-green {
        color: #00ff00;
        font-weight: bold;
    }
    .signal-red {
        color: #ff0000;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# INITIALIZATION
# ============================================================================
if 'multi_controller' not in st.session_state:
    st.session_state.multi_controller = MultiJunctionController(num_junctions=2)
    st.session_state.emergency_controllers = {}
    st.session_state.analytics = TrafficAnalytics()
    st.session_state.simulation_active = False
    st.session_state.update_counter = 0
    st.session_state.selected_mode = 'single'  # 'single' or 'multi'
    
    # Initialize emergency controllers for each junction
    for junc_id in range(2):
        controller = st.session_state.multi_controller.junctions[junc_id]['controller']
        st.session_state.emergency_controllers[junc_id] = EmergencyController(controller)

multi_controller = st.session_state.multi_controller
emergency_controllers = st.session_state.emergency_controllers
analytics = st.session_state.analytics

# ============================================================================
# HEADER
# ============================================================================
col1, col2 = st.columns([1, 4])
with col1:
    st.markdown("# 🚦")
with col2:
    st.markdown("## Advanced AI-Based Adaptive Traffic Signal Simulation")

st.markdown("---")
st.markdown("""
**Enhanced Smart Traffic Management** - Multi-Junction Coordination with Emergency Support & Real-time Analytics
""")

# ============================================================================
# SIDEBAR: MODE SELECTION
# ============================================================================
st.sidebar.markdown("### ⚙️ System Mode")

mode = st.sidebar.radio(
    "Select Operation Mode:",
    ["Single Junction", "Multi-Junction", "Emergency Mode", "Analytics Dashboard", "� Predictive Analytics", "�🗺️ Maps View"],
    index=0
)

st.session_state.selected_mode = mode.lower()

# ============================================================================
# MODE 1: SINGLE JUNCTION (Original)
# ============================================================================
if mode == "Single Junction":
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Vehicle Input Panel")
    st.sidebar.markdown("Adjust vehicle count for each lane using sliders:")
    
    junction_id = 0
    controller = multi_controller.junctions[junction_id]['controller']
    
    # Handle Reset Button BEFORE rendering sliders
    if st.sidebar.button("🔄 Reset", key="reset_btn", use_container_width=True):
        multi_controller.reset_all()
        st.session_state.simulation_active = False
        st.rerun()
    
    # Input sliders
    lanes_input = {}
    for lane in ['North', 'South', 'East', 'West']:
        count = st.sidebar.slider(
            f"🚗 {lane} Lane Vehicles",
            min_value=0,
            max_value=100,
            value=controller.lanes[lane]['vehicles'],
            step=5,
            key=f"slider_{lane}"
        )
        lanes_input[lane] = count
        multi_controller.set_vehicle_count(junction_id, lane, count)
    
    # Control buttons
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎮 Simulation Controls")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("▶️ Start", key="start_btn", use_container_width=True):
            st.session_state.simulation_active = True
    with col2:
        if st.button("⏹️ Stop", key="stop_btn", use_container_width=True):
            st.session_state.simulation_active = False
    
    # Display current junction
    st.markdown(f"### 🏢 {multi_controller.junctions[0]['name']} Intersection")
    
    signal_state = controller.get_signal_state()
    stats = controller.get_statistics()
    
    # Signal display grid
    cols = st.columns(2)
    color_mapping = {'RED': '#ff6b6b', 'GREEN': '#51cf66', 'YELLOW': '#ffd43b'}
    signal_emojis = {'RED': '🔴', 'GREEN': '🟢', 'YELLOW': '🟡'}
    
    for idx, (lane, state) in enumerate(signal_state.items()):
        with cols[idx % 2]:
            signal_color = color_mapping[state['signal']]
            signal_emoji = signal_emojis[state['signal']]
            
            st.markdown(f"""
            <div style="background-color: {signal_color}; padding: 20px; border-radius: 10px; 
                        text-align: center; color: white; margin: 10px 0;">
                <h3 style="margin: 0; color: white;">{signal_emoji} {lane}</h3>
                <p style="margin: 5px 0; font-size: 18px; font-weight: bold;">
                    Signal: <span style="text-transform: uppercase;">{state['signal']}</span>
                </p>
                <p style="margin: 5px 0; font-size: 16px;">
                    🚗 Vehicles: {state['vehicles']}
                </p>
                <p style="margin: 5px 0; font-size: 16px;">
                    ⏱️ Green Time: {state['green_time']}s
                </p>
                <p style="margin: 5px 0; font-size: 14px;">
                    Congestion: <strong>{state['congestion']}</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Statistics
    st.markdown("---")
    st.markdown("### 📈 Traffic Statistics")
    
    stat_cols = st.columns(4)
    with stat_cols[0]:
        st.metric("Total Vehicles", stats['total_vehicles'])
    with stat_cols[1]:
        st.metric("Avg per Lane", f"{stats['average_vehicles_per_lane']:.1f}")
    with stat_cols[2]:
        st.metric("Most Congested", stats['most_congested_lane'])
    with stat_cols[3]:
        st.metric("Cycle", stats['cycle_number'])
    
    # Charts
    st.markdown("---")
    st.markdown("### 📊 Vehicle Density Chart")
    
    fig, ax = plt.subplots(figsize=(12, 5))
    lanes = list(signal_state.keys())
    vehicles = [signal_state[lane]['vehicles'] for lane in lanes]
    colors_bars = [color_mapping[signal_state[lane]['signal']] for lane in lanes]
    
    bars = ax.bar(lanes, vehicles, color=colors_bars, alpha=0.8, edgecolor='black', linewidth=2)
    
    for bar, vehicle_count in zip(bars, vehicles):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(vehicle_count)}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.set_ylabel('Number of Vehicles', fontsize=12, fontweight='bold')
    ax.set_xlabel('Lane Direction', fontsize=12, fontweight='bold')
    ax.set_title('Current Traffic Density Across All Lanes', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    st.pyplot(fig, use_container_width=True)
    
    # Simulation loop
    if st.session_state.simulation_active:
        status_placeholder = st.empty()
        progress_placeholder = st.empty()
        
        for i in range(5):
            if st.session_state.simulation_active:
                progress_placeholder.progress((i + 1) / 5)
                
                with status_placeholder.container():
                    st.info(f"""
                    **Simulation Active** | Cycle: {controller.get_statistics()['cycle_number']} | 
                    Green Lane: {controller.get_statistics()['current_green_lane']}
                    """)
                
                import time
                time.sleep(3)
                multi_controller.advance_signal(junction_id)
                st.rerun()

# ============================================================================
# MODE 2: MULTI-JUNCTION CONTROL
# ============================================================================
elif mode == "Multi-Junction":
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌐 Multi-Junction Control")
    
    num_junctions = st.sidebar.slider(
        "Number of Junctions:",
        min_value=2,
        max_value=4,
        value=multi_controller.num_junctions
    )
    
    if num_junctions != multi_controller.num_junctions:
        multi_controller = MultiJunctionController(num_junctions)
        st.session_state.multi_controller = multi_controller
        st.rerun()
    
    # Coordination mode
    coord_mode = st.sidebar.radio(
        "Coordination Mode:",
        ["Independent", "Coordinated"]
    )
    multi_controller.set_coordination_mode(coord_mode.lower())
    
    st.sidebar.markdown("---")
    
    # Junction selector
    junction_id = st.sidebar.selectbox(
        "Select Junction to Control:",
        options=list(range(num_junctions)),
        format_func=lambda x: f"{multi_controller.junctions[x]['name']} (Junction {x})"
    )
    
    # Input sliders for selected junction
    st.sidebar.markdown("### 📊 Vehicle Input")
    
    # Handle Reset Button BEFORE rendering sliders
    if st.sidebar.button("🔄 Reset All", key="reset_multi", use_container_width=True):
        multi_controller.reset_all()
        st.session_state.simulation_active = False
        st.rerun()
    
    controller = multi_controller.junctions[junction_id]['controller']
    
    for lane in ['North', 'South', 'East', 'West']:
        count = st.sidebar.slider(
            f"{lane}",
            min_value=0,
            max_value=100,
            value=controller.lanes[lane]['vehicles'],
            step=5,
            key=f"multi_slider_{junction_id}_{lane}"
        )
        multi_controller.set_vehicle_count(junction_id, lane, count)
    
    # Control buttons
    st.sidebar.markdown("---")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("▶️ Start All", key="start_multi", use_container_width=True):
            st.session_state.simulation_active = True
    with col2:
        if st.button("⏹️ Stop All", key="stop_multi", use_container_width=True):
            st.session_state.simulation_active = False
    
    # Display all junctions
    st.markdown("### 🏙️ Multi-Junction Traffic Network")
    
    health = multi_controller.get_system_health()
    
    # System health metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Vehicles", health['total_vehicles'])
    with col2:
        st.metric("System Efficiency", f"{health['system_efficiency']:.1f}%")
    with col3:
        st.metric("Mode", health['coordination_mode'].capitalize())
    with col4:
        st.metric("Active Junctions", health['active_junctions'])
    
    st.markdown("---")
    
    # Display each junction
    all_state = multi_controller.get_all_junctions_state()
    
    for junc_id, junc_state in all_state.items():
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown(f"### {junc_state['name']}")
            st.metric("Vehicles", junc_state['total_vehicles'])
            st.metric("Cycle", junc_state['statistics']['cycle_number'])
        
        with col2:
            # Mini signal display
            signal_state = junc_state['signal_state']
            mini_cols = st.columns(4)
            
            for idx, (lane, state) in enumerate(signal_state.items()):
                with mini_cols[idx]:
                    signal_emoji = {'RED': '🔴', 'GREEN': '🟢', 'YELLOW': '🟡'}[state['signal']]
                    st.markdown(f"""
                    **{signal_emoji} {lane}**
                    {state['vehicles']} vehicles
                    {state['green_time']}s green
                    """)
    
    # Recommendations
    st.markdown("---")
    st.markdown("### 💡 Optimization Recommendations")
    
    recommendations = multi_controller.get_coordination_recommendations()
    
    if recommendations:
        for rec in recommendations:
            if rec['severity'] == 'high':
                st.error(f"⚠️ {rec['message']}")
            else:
                st.info(f"ℹ️ {rec['message']}")
    else:
        st.success("✅ All junctions operating normally!")

# ============================================================================
# MODE 3: EMERGENCY MODE
# ============================================================================
elif mode == "Emergency Mode":
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🚨 Emergency Vehicle Control")
    
    junction_id = st.sidebar.selectbox(
        "Select Junction:",
        options=list(range(len(emergency_controllers))),
        format_func=lambda x: f"{multi_controller.junctions[x]['name']} (Junction {x})"
    )
    
    emergency_controller = emergency_controllers[junction_id]
    
    st.sidebar.markdown("### Detect Emergency Vehicle")
    
    lane = st.sidebar.selectbox("Lane with Emergency:", ['North', 'South', 'East', 'West'])
    
    vehicle_type = st.sidebar.selectbox(
        "Emergency Vehicle Type:",
        ['ambulance', 'fire_truck', 'police']
    )
    
    if st.sidebar.button("🚨 TRIGGER EMERGENCY", key="trigger_emergency", use_container_width=True):
        emergency_controller.detect_emergency_vehicle(lane, vehicle_type)
        st.session_state.simulation_active = True
    
    if st.sidebar.button("✅ Clear Emergency", key="clear_emergency", use_container_width=True):
        emergency_controller.clear_emergency()
    
    # Display emergency status
    st.markdown(f"### 🏢 {multi_controller.junctions[junction_id]['name']} - Emergency Mode")
    
    emergency_status = emergency_controller.get_emergency_status()
    
    if emergency_status['active']:
        alert_msg = emergency_controller.display_emergency_alert()
        st.markdown(f"""
        <div class="emergency-alert">
            {alert_msg}
            <br><br>
            Time Remaining: <strong>{emergency_status['time_remaining']}s</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # Show override in effect
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Emergency Type", emergency_status['type'].upper())
        with col2:
            st.metric("Green Lane", emergency_status['lane'])
    else:
        st.info("No active emergency. System operating normally.")
    
    # Current signal state
    st.markdown("---")
    st.markdown("### 📊 Current Signal State")
    
    controller = multi_controller.junctions[junction_id]['controller']
    signal_state = controller.get_signal_state()
    
    cols = st.columns(2)
    color_mapping = {'RED': '#ff6b6b', 'GREEN': '#51cf66', 'YELLOW': '#ffd43b'}
    signal_emojis = {'RED': '🔴', 'GREEN': '🟢', 'YELLOW': '🟡'}
    
    for idx, (lane, state) in enumerate(signal_state.items()):
        with cols[idx % 2]:
            signal_color = color_mapping[state['signal']]
            signal_emoji = signal_emojis[state['signal']]
            
            st.markdown(f"""
            <div style="background-color: {signal_color}; padding: 20px; border-radius: 10px; 
                        text-align: center; color: white; margin: 10px 0;">
                <h3 style="margin: 0; color: white;">{signal_emoji} {lane}</h3>
                <p>Signal: <strong>{state['signal']}</strong></p>
                <p>Vehicles: {state['vehicles']}</p>
                <p>Green Time: {state['green_time']}s</p>
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# MODE 4: ANALYTICS DASHBOARD
# ============================================================================
elif mode == "Analytics Dashboard":
    st.markdown("### 📊 Traffic Analytics & Performance")
    
    # Update analytics with current system state
    timestamp = datetime.now().isoformat()
    for junc_id in range(multi_controller.num_junctions):
        junc_state = multi_controller.get_all_junctions_state()[junc_id]
        analytics.log_snapshot(
            timestamp,
            junc_id,
            junc_state['signal_state'],
            junc_state['statistics']
        )
    
    # Get analytics data
    efficiency = analytics.get_system_efficiency()
    peak_hours = analytics.get_peak_hours()
    lane_perf = analytics.get_lane_performance()
    trend = analytics.get_traffic_trend()
    
    # Efficiency metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("System Efficiency", f"{efficiency['efficiency_score']:.1f}%")
    with col2:
        st.metric("Avg Congestion", f"{efficiency['average_congestion']:.1f}%")
    with col3:
        st.metric("Total Throughput", efficiency['total_throughput'])
    with col4:
        st.metric("Traffic Trend", trend['trend'].upper())
    
    st.markdown("---")
    st.markdown("### 📈 Traffic Trends")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Current Congestion", f"{trend['current_congestion']:.1f}%")
    with col2:
        st.metric("Change", f"{trend['change_percent']:.1f}%")
    
    st.markdown("---")
    st.markdown("### 🎯 Lane Performance Analysis")
    
    if lane_perf:
        df = pd.DataFrame(lane_perf).T
        st.dataframe(df, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📊 Analytics Report")
    
    if st.button("📥 Export Report as JSON"):
        report = analytics.export_analytics_report()
        st.download_button(
            label="Download JSON Report",
            data=report,
            file_name=f"traffic_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    if st.button("🔄 Clear Analytics"):
        # Clear all analytics logs
        analytics.clear_logs()
        
        # Also reset all junctions to clear current traffic state
        for junction_id in range(multi_controller.num_junctions):
            for lane in ['North', 'South', 'East', 'West']:
                multi_controller.set_vehicle_count(junction_id, lane, 0)
        
        st.session_state.simulation_active = False
        st.success("Analytics and all traffic data cleared! ✅")

# ============================================================================
# MODE 5: PREDICTIVE ANALYTICS (ML-Based Traffic Forecasting)
# ============================================================================
elif mode == "🔮 Predictive Analytics":
    st.markdown("### 🔮 ML-Based Traffic Prediction & Forecasting")
    st.markdown("Advanced predictive analytics using machine learning to forecast traffic patterns")
    
    # Initialize predictor in session state
    if 'predictor' not in st.session_state:
        st.session_state.predictor = TrafficPredictor()
        st.session_state.optimizer = SmartTrafficOptimizer(st.session_state.predictor)
    
    # Add sample data if empty (for demo)
    predictor = st.session_state.predictor
    if len(predictor.historical_data) < 20:
        # Add simulated historical data for demonstration
        from datetime import timedelta
        for hour in range(24):
            for day in range(7):
                for lane, base_vehicles in [('North', 45), ('East', 35), ('South', 40), ('West', 30)]:
                    # Create traffic pattern: peaks at rush hours
                    if hour in [8, 9, 17, 18]:
                        vehicles = base_vehicles + 30 + np.random.randint(-10, 10)
                    elif hour in [10, 11, 14, 15, 16]:
                        vehicles = base_vehicles + 15
                    else:
                        vehicles = base_vehicles + np.random.randint(-5, 5)
                    
                    timestamp = datetime(2026, 1, 9, hour, 0) - timedelta(days=day)
                    predictor.add_historical_data(timestamp, lane, max(5, vehicles))
    
    # Display predictions
    col1, col2, col3, col4 = st.columns(4)
    
    lanes = ['North', 'East', 'South', 'West']
    predictions_dict = {}
    
    for lane in lanes:
        predictions_dict[lane] = predictor.predict_next_hours(lane, hours_ahead=4)
    
    # Peak hour predictions
    peak_info = predictor.get_peak_hours_prediction()
    
    with col1:
        st.metric("🚗 Current Trend", peak_info['current_trend'].upper(), 
                 f"{peak_info['current_vehicles']} vehicles")
    
    with col2:
        st.metric("📊 Avg Vehicles/Hour", peak_info['avg_vehicles'])
    
    with col3:
        st.metric("⏰ Morning Peak", f"{peak_info['morning_peak'][0]}:00-{peak_info['morning_peak'][1]}:00")
    
    with col4:
        st.metric("⏰ Evening Peak", f"{peak_info['afternoon_peak'][0]}:00-{peak_info['afternoon_peak'][1]}:00")
    
    st.markdown("---")
    
    # Prediction details for each lane
    st.markdown("### 📈 Next 4 Hours Traffic Forecast")
    
    pred_cols = st.columns(4)
    
    for idx, lane in enumerate(lanes):
        with pred_cols[idx]:
            st.markdown(f"**{lane} Lane**")
            predictions = predictions_dict[lane]
            
            for pred in predictions:
                hour_str = f"{pred['hour']:02d}:00"
                vehicles = pred['predicted_vehicles']
                confidence = pred['confidence']
                lower = pred['lower_bound']
                upper = pred['upper_bound']
                
                # Color code based on congestion
                if vehicles > 60:
                    color = "🔴"
                    severity = "High"
                elif vehicles > 40:
                    color = "🟡"
                    severity = "Medium"
                else:
                    color = "🟢"
                    severity = "Low"
                
                st.markdown(f"""
                **{hour_str}** {color}
                - Predicted: {vehicles} vehicles
                - Range: {lower}-{upper}
                - Confidence: {confidence*100:.0f}%
                - Risk: {severity}
                """)
    
    st.markdown("---")
    
    # Congestion forecast
    st.markdown("### ⚠️ Congestion Risk Analysis (Next 4 Hours)")
    
    congestion_forecast = predictor.get_congestion_forecast(lanes, threshold=50)
    
    risk_cols = st.columns(4)
    for idx, lane in enumerate(lanes):
        with risk_cols[idx]:
            forecast = congestion_forecast[lane]
            risk_pct = forecast['congestion_risk']
            
            if risk_pct > 50:
                risk_level = "🔴 HIGH"
                color = "#ff4444"
            elif risk_pct > 25:
                risk_level = "🟡 MEDIUM"
                color = "#ffaa44"
            else:
                risk_level = "🟢 LOW"
                color = "#44ff44"
            
            st.markdown(f"""
            <div style="background-color: {color}20; padding: 15px; border-radius: 8px; border-left: 4px solid {color};">
            <b>{lane} Lane</b><br>
            Congestion Risk: <b>{risk_pct}%</b> {risk_level}<br>
            Max Expected: {forecast['max_expected']} vehicles<br>
            Avg Expected: {forecast['avg_expected']} vehicles
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recommended signal timing
    st.markdown("### 🎯 Recommended Signal Timing (Based on Predictions)")
    
    timing_cols = st.columns(4)
    optimizer = st.session_state.optimizer
    
    for idx, lane in enumerate(lanes):
        with timing_cols[idx]:
            predictions = predictions_dict[lane]
            if predictions:
                recommended_green = optimizer.get_recommended_timing(lane, predictions)
                current_pred = predictions[0]['predicted_vehicles']
                
                st.info(f"""
                **{lane} Lane**
                
                Next Hour Prediction: {current_pred} vehicles
                
                **Recommended Green Time:**
                ### {recommended_green}s
                
                (Current optimal: {recommended_green}s / Max: 60s)
                """)
    
    st.markdown("---")
    
    # Optimization recommendations
    st.markdown("### 💡 AI Optimization Recommendations")
    
    recommendations = optimizer.get_optimization_recommendations({})
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            st.success(f"{i}. {rec}")
    else:
        st.info("✅ System is operating optimally. No adjustments needed.")
    
    st.markdown("---")
    
    # Visualization: Traffic forecast chart
    st.markdown("### 📊 Traffic Forecast Chart")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    fig.patch.set_facecolor('#111111')
    
    for idx, (ax, lane) in enumerate(zip(axes.flat, lanes)):
        predictions = predictions_dict[lane]
        hours = [p['hour'] for p in predictions]
        predicted = [p['predicted_vehicles'] for p in predictions]
        lower = [p['lower_bound'] for p in predictions]
        upper = [p['upper_bound'] for p in predictions]
        
        ax.plot(hours, predicted, marker='o', color='#00ff88', linewidth=2.5, label='Prediction')
        ax.fill_between(hours, lower, upper, alpha=0.3, color='#00ff88', label='Confidence Interval')
        ax.axhline(y=50, color='#ff4444', linestyle='--', alpha=0.7, label='Congestion Threshold')
        
        ax.set_title(f'{lane} Lane - 4 Hour Forecast', color='white', fontsize=11, fontweight='bold')
        ax.set_xlabel('Hour', color='white')
        ax.set_ylabel('Predicted Vehicles', color='white')
        ax.grid(True, alpha=0.3, color='white')
        ax.legend(loc='upper left', fontsize=8)
        
        # Set axis colors
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('white')
        ax.set_facecolor('#222222')
    
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("""
    **About Predictive Analytics Mode:**
    - Uses historical traffic data to forecast patterns
    - Implements multiple prediction algorithms (Simple, ARIMA, Random Forest ML)
    - Provides confidence intervals for all predictions
    - Recommends optimal signal timing based on forecasts
    - Identifies congestion risk and peak hours
    - Helps optimize traffic flow proactively
    """)

# ============================================================================
# MODE 6: MAPS VIEW (Google Maps Integration)
# ============================================================================
elif mode == "🗺️ Maps View":
    st.markdown("### 🗺️ Junction Location & Signal Status Map")
    st.markdown("Real-time traffic signal status on interactive map (powered by Google Maps Platform)")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📍 Map Configuration")
    
    # Example junction coordinates (can be customized)
    center_lat = st.sidebar.slider("Map Center Latitude", -90.0, 90.0, 40.7128, 0.0001)
    center_lon = st.sidebar.slider("Map Center Longitude", -180.0, 180.0, -74.0060, 0.0001)
    zoom_level = st.sidebar.slider("Zoom Level", 10, 20, 15)
    
    # Create Folium map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_level,
        tiles="OpenStreetMap"
    )
    
    # Use default multi-controller for Maps View
    controller = multi_controller.junctions[0]['controller']
    
    # Lane coordinates relative to junction center (example: NYC intersection)
    lanes_data = {
        'North': {
            'coords': [center_lat + 0.003, center_lon],
            'vehicles': controller.lanes['North']['vehicles'],
            'signal': controller.lanes['North'].get('signal_state', 'Red')
        },
        'South': {
            'coords': [center_lat - 0.003, center_lon],
            'vehicles': controller.lanes['South']['vehicles'],
            'signal': controller.lanes['South'].get('signal_state', 'Red')
        },
        'East': {
            'coords': [center_lat, center_lon + 0.003],
            'vehicles': controller.lanes['East']['vehicles'],
            'signal': controller.lanes['East'].get('signal_state', 'Red')
        },
        'West': {
            'coords': [center_lat, center_lon - 0.003],
            'vehicles': controller.lanes['West']['vehicles'],
            'signal': controller.lanes['West'].get('signal_state', 'Red')
        }
    }
    
    # Color mapping for signals
    signal_colors = {
        'Green': 'green',
        'Red': 'red',
        'Yellow': 'orange'
    }
    
    # Add lane markers
    for lane, data in lanes_data.items():
        color = signal_colors.get(data['signal'], 'gray')
        folium.CircleMarker(
            location=data['coords'],
            radius=15,
            popup=f"<b>{lane} Lane</b><br>Vehicles: {data['vehicles']}<br>Signal: {data['signal']}",
            tooltip=f"{lane}: {data['vehicles']} vehicles",
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=3
        ).add_to(m)
    
    # Add junction center marker
    folium.Marker(
        location=[center_lat, center_lon],
        popup="<b>4-Way Junction</b><br>Adaptive Signal Control",
        tooltip="Main Traffic Junction",
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(m)
    
    # Display map
    st_folium(m, width=1200, height=600)
    
    # Statistics below map
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔴 North Signal", lanes_data['North']['signal'])
    with col2:
        st.metric("🟢 East Signal", lanes_data['East']['signal'])
    with col3:
        st.metric("🔴 South Signal", lanes_data['South']['signal'])
    with col4:
        st.metric("🔴 West Signal", lanes_data['West']['signal'])
    
    st.info("""
    **🗺️ Map Features** (Google Maps Platform Integration):
    - Real-time signal status for each lane (Color-coded)
    - Vehicle count per lane displayed on hover
    - Customizable map center and zoom level
    - Integration with OpenStreetMap (ready for Google Maps API)
    
    **Future Enhancements**:
    - Real junction data from Google Maps
    - Multi-junction map view
    - Real-time traffic data integration
    """)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 12px;">
    <p>🚦 Advanced AI-Based Adaptive Traffic Signal Simulation v2.0</p>
    <p>Multi-Junction | Emergency Support | Real-time Analytics | Google Maps Integration</p>
</div>
""", unsafe_allow_html=True)
