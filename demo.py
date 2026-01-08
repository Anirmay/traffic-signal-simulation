"""
Demo & Test Script for Traffic Signal Controller
Run this to validate the logic before launching the Streamlit app.
"""

from logic import TrafficSignalController

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_signal_state(state, title="Signal State"):
    """Pretty print signal state."""
    print(f"\n{title}:")
    print("-" * 60)
    for lane, data in state.items():
        signal_emoji = "🟢" if data['signal'] == 'GREEN' else "🔴"
        print(f"{signal_emoji} {lane:6} | Vehicles: {data['vehicles']:3} | "
              f"Green Time: {data['green_time']:2}s | {data['congestion']}")

def demo_1_initial_state():
    """Test 1: Initial state with no vehicles."""
    print_section("TEST 1: Initial State (No Vehicles)")
    
    controller = TrafficSignalController()
    state = controller.get_signal_state()
    stats = controller.get_statistics()
    
    print_signal_state(state)
    
    print(f"\nStatistics:")
    print(f"  Total Vehicles: {stats['total_vehicles']}")
    print(f"  Current Green Lane: {stats['current_green_lane']}")
    print(f"  Cycle Number: {stats['cycle_number']}")
    
    assert state['North']['signal'] == 'GREEN', "North should be green initially"
    assert all(state[l]['green_time'] == 20 for l in state), "All should have base 20s"
    print("\n✓ TEST 1 PASSED")

def demo_2_simple_scenario():
    """Test 2: Simple scenario with balanced traffic."""
    print_section("TEST 2: Simple Scenario (Balanced Traffic)")
    
    controller = TrafficSignalController()
    
    # Set equal vehicles in all lanes
    for lane in ['North', 'South', 'East', 'West']:
        controller.set_vehicle_count(lane, 25)
    
    state = controller.get_signal_state()
    stats = controller.get_statistics()
    
    print_signal_state(state)
    
    print(f"\nStatistics:")
    print(f"  Total Vehicles: {stats['total_vehicles']}")
    print(f"  Average per Lane: {stats['average_vehicles_per_lane']}")
    print(f"  Most Congested: {stats['most_congested_lane']}")
    
    # All should have same green time when balanced
    green_times = [state[l]['green_time'] for l in state]
    assert len(set(green_times)) == 1, "All lanes should have same green time when balanced"
    assert stats['total_vehicles'] == 100
    print("\n✓ TEST 2 PASSED")

def demo_3_unbalanced_traffic():
    """Test 3: Unbalanced traffic scenario."""
    print_section("TEST 3: Unbalanced Traffic Scenario")
    
    controller = TrafficSignalController()
    
    # Set unequal vehicles
    controller.set_vehicle_count('North', 60)   # Highest
    controller.set_vehicle_count('South', 30)
    controller.set_vehicle_count('East', 10)    # Lowest
    controller.set_vehicle_count('West', 50)
    
    state = controller.get_signal_state()
    stats = controller.get_statistics()
    
    print_signal_state(state)
    
    print(f"\nStatistics:")
    print(f"  Total Vehicles: {stats['total_vehicles']}")
    print(f"  Average per Lane: {stats['average_vehicles_per_lane']}")
    print(f"  Most Congested: {stats['most_congested_lane']} ({stats['max_vehicles']} vehicles)")
    
    # Verify proportional allocation
    assert state['North']['green_time'] > state['East']['green_time'], \
        "North (60) should have more green time than East (10)"
    assert stats['most_congested_lane'] == 'North'
    
    # Verify constraints (10s minimum, 60s maximum)
    assert all(10 <= state[l]['green_time'] <= 60 for l in state), \
        "All green times should be within [10, 60] seconds"
    
    print("\n✓ TEST 3 PASSED")

def demo_4_congestion_levels():
    """Test 4: Congestion level classification."""
    print_section("TEST 4: Congestion Level Classification")
    
    controller = TrafficSignalController()
    
    test_cases = [
        (5, 'Low'),
        (10, 'Medium'),
        (25, 'Medium'),
        (30, 'Medium'),
        (31, 'High'),
        (100, 'High')
    ]
    
    print("Vehicle Count → Congestion Level:")
    print("-" * 40)
    for vehicles, expected_level in test_cases:
        level = controller.calculate_congestion_level(vehicles)
        status = "✓" if level == expected_level else "✗"
        print(f"{status} {vehicles:3} vehicles → {level:8} (expected: {expected_level})")
        assert level == expected_level, f"Failed for {vehicles} vehicles"
    
    print("\n✓ TEST 4 PASSED")

def demo_5_lane_rotation():
    """Test 5: Fair lane rotation."""
    print_section("TEST 5: Fair Lane Rotation")
    
    controller = TrafficSignalController()
    
    # Set some vehicles
    for lane in ['North', 'South', 'East', 'West']:
        controller.set_vehicle_count(lane, 20)
    
    print("Lane Rotation Sequence:")
    print("-" * 40)
    
    rotation_sequence = []
    for i in range(8):  # Run 2 complete cycles (4 lanes × 2)
        rotation_sequence.append(controller.current_lane)
        print(f"Cycle {i+1}: {controller.current_lane} has GREEN")
        controller.advance_signal()
    
    # Verify pattern repeats every 4 steps
    expected_pattern = ['North', 'East', 'South', 'West']
    
    print("\nPattern Verification:")
    for cycle in range(2):
        cycle_sequence = rotation_sequence[cycle*4:(cycle+1)*4]
        print(f"  Cycle {cycle+1}: {' → '.join(cycle_sequence)}")
        assert cycle_sequence == expected_pattern, \
            f"Cycle {cycle+1} doesn't match expected pattern"
    
    print("\n✓ TEST 5 PASSED")

def demo_6_extreme_scenario():
    """Test 6: Extreme traffic scenario."""
    print_section("TEST 6: Extreme Scenario (One Lane Congestion)")
    
    controller = TrafficSignalController()
    
    # One lane heavily congested
    controller.set_vehicle_count('North', 95)
    controller.set_vehicle_count('South', 2)
    controller.set_vehicle_count('East', 1)
    controller.set_vehicle_count('West', 2)
    
    state = controller.get_signal_state()
    stats = controller.get_statistics()
    
    print_signal_state(state)
    
    print(f"\nStatistics:")
    print(f"  Total Vehicles: {stats['total_vehicles']}")
    print(f"  Most Congested: {stats['most_congested_lane']} ({stats['max_vehicles']} vehicles)")
    
    # North should get maximum green time
    assert state['North']['green_time'] == 60, "North should be clamped at max 60s"
    
    # Others should get minimum but not zero
    for lane in ['South', 'East', 'West']:
        assert state[lane]['green_time'] >= 10, f"{lane} should have minimum 10s"
    
    print("\n✓ TEST 6 PASSED")

def demo_7_statistics():
    """Test 7: Statistics calculation."""
    print_section("TEST 7: Statistics Calculation")
    
    controller = TrafficSignalController()
    
    controller.set_vehicle_count('North', 40)
    controller.set_vehicle_count('South', 30)
    controller.set_vehicle_count('East', 20)
    controller.set_vehicle_count('West', 10)
    
    stats = controller.get_statistics()
    
    print("Traffic Statistics:")
    print("-" * 40)
    print(f"  Total Vehicles: {stats['total_vehicles']}")
    print(f"  Average per Lane: {stats['average_vehicles_per_lane']:.1f}")
    print(f"  Most Congested: {stats['most_congested_lane']}")
    print(f"  Max Vehicles: {stats['max_vehicles']}")
    print(f"  Current Green: {stats['current_green_lane']}")
    print(f"  Cycle Number: {stats['cycle_number']}")
    
    assert stats['total_vehicles'] == 100
    assert stats['average_vehicles_per_lane'] == 25.0
    assert stats['most_congested_lane'] == 'North'
    assert stats['max_vehicles'] == 40
    
    print("\n✓ TEST 7 PASSED")

def run_all_demos():
    """Run all demonstration tests."""
    print("\n" + "█"*60)
    print("█  TRAFFIC SIGNAL CONTROLLER - DEMO & TEST SUITE")
    print("█"*60)
    
    try:
        demo_1_initial_state()
        demo_2_simple_scenario()
        demo_3_unbalanced_traffic()
        demo_4_congestion_levels()
        demo_5_lane_rotation()
        demo_6_extreme_scenario()
        demo_7_statistics()
        
        print("\n" + "█"*60)
        print("█  ALL TESTS PASSED! ✓")
        print("█  System is ready for deployment.")
        print("█"*60)
        print("\nNext Steps:")
        print("  1. Run: streamlit run app.py")
        print("  2. Open browser to: http://localhost:8501")
        print("  3. Adjust sliders and click 'Start Simulation'")
        print("  4. Deploy to Streamlit Cloud when ready")
        print("\n")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False
    
    return True

if __name__ == "__main__":
    run_all_demos()
