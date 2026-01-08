"""
AI-Based Adaptive Traffic Signal Simulation
A Streamlit-based dashboard for simulating intelligent traffic signal control.
"""

import streamlit as st
import matplotlib.pyplot as plt
import time
from logic import TrafficSignalController

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Traffic Signal Simulator",
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
    .signal-red {
        color: #ff0000;
        font-weight: bold;
    }
    .signal-yellow {
        color: #ffaa00;
        font-weight: bold;
    }
    .signal-green {
        color: #00ff00;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# INITIALIZATION
# ============================================================================
if 'controller' not in st.session_state:
    st.session_state.controller = TrafficSignalController()
    st.session_state.simulation_active = False
    st.session_state.update_counter = 0

controller = st.session_state.controller

# ============================================================================
# HEADER
# ============================================================================
col1, col2 = st.columns([1, 4])
with col1:
    st.markdown("# 🚦")
with col2:
    st.markdown("## AI-Based Adaptive Traffic Signal Simulation")

st.markdown("---")
st.markdown("""
**Smart Traffic Management System** - Dynamically adjust signal timings based on real-time vehicle density
""")

# ============================================================================
# SIDEBAR: INPUT CONTROLS
# ============================================================================
st.sidebar.markdown("### 📊 Vehicle Input Panel")
st.sidebar.markdown("Adjust vehicle count for each lane using sliders:")

# Handle Reset Button BEFORE rendering sliders
if st.sidebar.button("🔄 Reset", key="reset_btn", use_container_width=True):
    controller.reset()
    st.session_state.simulation_active = False
    st.session_state.update_counter = 0
    st.rerun()

# Input sliders for each lane
lanes_input = {}
for lane in ['North', 'South', 'East', 'West']:
    count = st.sidebar.slider(
        f"🚗 {lane} Lane Vehicles",
        min_value=0,
        max_value=100,
        value=st.session_state.controller.lanes[lane]['vehicles'],
        step=5,
        key=f"slider_{lane}"
    )
    lanes_input[lane] = count
    controller.set_vehicle_count(lane, count)

# Control buttons
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Simulation Controls")

col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("▶️ Start Simulation", key="start_btn", use_container_width=True):
        st.session_state.simulation_active = True
        st.session_state.update_counter = 0

with col2:
    if st.button("⏹️ Stop Simulation", key="stop_btn", use_container_width=True):
        st.session_state.simulation_active = False

# ============================================================================
# MAIN CONTENT: SIGNAL STATE DISPLAY
# ============================================================================
st.markdown("### 🚨 Current Signal State")

# Get signal state
signal_state = controller.get_signal_state()
stats = controller.get_statistics()

# Display signals in 2x2 grid
cols = st.columns(2)
signal_colors = {'RED': '🔴', 'GREEN': '🟢', 'YELLOW': '🟡'}
color_mapping = {'RED': '#ff6b6b', 'GREEN': '#51cf66', 'YELLOW': '#ffd43b'}

for idx, (lane, state) in enumerate(signal_state.items()):
    with cols[idx % 2]:
        signal_color = color_mapping[state['signal']]
        signal_emoji = signal_colors[state['signal']]
        
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

# ============================================================================
# STATISTICS SECTION
# ============================================================================
st.markdown("---")
st.markdown("### 📈 Traffic Statistics")

stat_cols = st.columns(4)
with stat_cols[0]:
    st.metric(
        "Total Vehicles",
        stats['total_vehicles'],
        delta=None
    )

with stat_cols[1]:
    st.metric(
        "Avg per Lane",
        f"{stats['average_vehicles_per_lane']:.1f}",
        delta=None
    )

with stat_cols[2]:
    st.metric(
        "Most Congested",
        stats['most_congested_lane'],
        delta=f"{stats['max_vehicles']} vehicles"
    )

with stat_cols[3]:
    st.metric(
        "Cycle",
        stats['cycle_number'],
        delta="Current cycle"
    )

# ============================================================================
# VISUALIZATION: TRAFFIC DENSITY CHART
# ============================================================================
st.markdown("---")
st.markdown("### 📊 Vehicle Density Per Lane")

fig, ax = plt.subplots(figsize=(12, 5))

lanes = list(signal_state.keys())
vehicles = [signal_state[lane]['vehicles'] for lane in lanes]
colors_bars = [color_mapping[signal_state[lane]['signal']] for lane in lanes]
congestion_levels = [signal_state[lane]['congestion'] for lane in lanes]

# Create bar chart
bars = ax.bar(lanes, vehicles, color=colors_bars, alpha=0.8, edgecolor='black', linewidth=2)

# Add value labels on bars
for bar, vehicle_count, congestion in zip(bars, vehicles, congestion_levels):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(vehicle_count)}\n({congestion})',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_ylabel('Number of Vehicles', fontsize=12, fontweight='bold')
ax.set_xlabel('Lane Direction', fontsize=12, fontweight='bold')
ax.set_title('Current Traffic Density Across All Lanes', fontsize=14, fontweight='bold')
ax.set_ylim(0, max(vehicles) + 20 if vehicles else 100)
ax.grid(axis='y', alpha=0.3, linestyle='--')

st.pyplot(fig, use_container_width=True)

# ============================================================================
# TRAFFIC FLOW ANIMATION
# ============================================================================
st.markdown("---")
st.markdown("### 🎬 Traffic Flow Animation")

# Create animated traffic flow representation
flow_cols = st.columns(4)
lane_names = ['North', 'East', 'South', 'West']

for idx, (col, lane) in enumerate(zip(flow_cols, lane_names)):
    with col:
        state = signal_state[lane]
        signal = state['signal']
        vehicles = state['vehicles']
        
        # Create visual representation
        vehicle_count_display = min(vehicles // 5, 10)  # Scale vehicles for display
        car_emoji = "🚗" * vehicle_count_display
        
        if signal == 'GREEN':
            flow_visual = "→ " + car_emoji + " →"
        elif signal == 'RED':
            flow_visual = "⏸ " + car_emoji + " ⏸"
        else:
            flow_visual = "⚠ " + car_emoji + " ⚠"
        
        st.markdown(f"""
        <div style="background-color: {color_mapping[signal]}; padding: 15px; 
                    border-radius: 8px; text-align: center; color: white;">
            <p style="margin: 0; font-size: 14px; font-weight: bold;">{lane}</p>
            <p style="margin: 10px 0; font-size: 20px; font-family: monospace;">
                {flow_visual}
            </p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# SIMULATION LOOP
# ============================================================================
st.markdown("---")
st.markdown("### 💡 How It Works")

with st.expander("Algorithm Explanation", expanded=False):
    st.markdown("""
    **Adaptive Signal Control Logic:**
    
    1. **Vehicle Density Measurement**: Count vehicles in each lane (0-100)
    2. **Congestion Classification**: 
       - Low: < 10 vehicles
       - Medium: 10-30 vehicles
       - High: > 30 vehicles
    
    3. **Green Time Calculation**:
       - Proportional allocation based on vehicle density
       - Formula: `(vehicles_in_lane / total_vehicles) × 80 seconds`
       - Min green time: 10 seconds
       - Max green time: 60 seconds
    
    4. **Fair Rotation**: 
       - Cycles through lanes in order: North → East → South → West
       - Prevents starvation of any lane
    
    5. **Signal Transitions**:
       - When green time expires, automatically advances to next lane
       - Signal colors: 🟢 Green (moving), 🔴 Red (waiting), 🟡 Yellow (transitioning)
    """)

# ============================================================================
# CONTINUOUS UPDATE (Simulation Mode)
# ============================================================================
if st.session_state.simulation_active:
    # Create a placeholder for status updates
    status_placeholder = st.empty()
    progress_placeholder = st.empty()
    
    # Simulation loop
    for i in range(10):  # Run for 10 cycles before refreshing
        if st.session_state.simulation_active:
            # Update progress
            progress_placeholder.progress((i + 1) / 10)
            
            # Display current state
            with status_placeholder.container():
                st.info(f"""
                **Simulation Active** | Cycle: {controller.get_statistics()['cycle_number']} | 
                Green Lane: {controller.get_statistics()['current_green_lane']}
                """)
            
            # Advance to next signal after 3 seconds
            time.sleep(3)
            controller.advance_signal()
            st.session_state.update_counter += 1
            st.rerun()
    
    # Restart loop
    if st.session_state.simulation_active:
        st.rerun()

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 12px;">
    <p>🏗️ AI-Based Adaptive Traffic Signal Simulation v1.0</p>
    <p>Built with Python, Streamlit & Intelligent Logic</p>
    <p>Suitable for Smart City Applications & Hackathons</p>
</div>
""", unsafe_allow_html=True)
