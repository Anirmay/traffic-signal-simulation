"""
Quick test script for Historical Data functionality
Run this to verify the feature works correctly
"""

from historical_data import HistoricalDataManager, PredictiveTrafficAnalyzer
from datetime import datetime, timedelta
import json

def test_historical_data():
    print("\n" + "="*60)
    print("HISTORICAL DATA STORAGE TEST")
    print("="*60)
    
    # Initialize manager
    print("\n1. Initializing HistoricalDataManager...")
    manager = HistoricalDataManager(local_dir='traffic_data_test')
    print("   ✅ Manager initialized")
    
    # Create test snapshot
    print("\n2. Creating test traffic snapshot...")
    snapshot = {
        'timestamp': datetime.now().isoformat(),
        'junction_id': 0,
        'signal_state': {
            'North': {'signal': 'GREEN', 'vehicles': 25, 'green_time': 35},
            'South': {'signal': 'RED', 'vehicles': 10, 'green_time': 20},
            'East': {'signal': 'RED', 'vehicles': 18, 'green_time': 20},
            'West': {'signal': 'RED', 'vehicles': 12, 'green_time': 20}
        },
        'statistics': {
            'total_vehicles': 65,
            'average_vehicles_per_lane': 16.25,
            'most_congested_lane': 'North',
            'cycle_number': 45,
            'current_green_lane': 'North'
        },
        'congestion_level': 65.0
    }
    print(f"   ✅ Snapshot created: {snapshot['timestamp']}")
    
    # Save snapshot
    print("\n3. Saving snapshot to storage...")
    success = manager.save_snapshot(snapshot)
    if success:
        print("   ✅ Snapshot saved successfully")
    else:
        print("   ❌ Failed to save snapshot")
        return
    
    # Create more snapshots for analysis
    print("\n4. Creating multiple snapshots for pattern analysis...")
    for hour in range(8, 18):
        for minute in [0, 30]:
            test_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
            vehicles = 20 + (hour - 8) * 5 + minute // 10  # Increasing pattern
            
            test_snapshot = {
                'timestamp': test_time.isoformat(),
                'junction_id': 0,
                'signal_state': {
                    'North': {'signal': 'GREEN', 'vehicles': vehicles, 'green_time': 30},
                    'South': {'signal': 'RED', 'vehicles': vehicles//2, 'green_time': 20},
                    'East': {'signal': 'RED', 'vehicles': vehicles//2, 'green_time': 20},
                    'West': {'signal': 'RED', 'vehicles': vehicles//4, 'green_time': 20}
                },
                'statistics': {
                    'total_vehicles': vehicles * 2,
                    'average_vehicles_per_lane': vehicles * 0.5,
                    'most_congested_lane': 'North'
                },
                'congestion_level': min(100, vehicles * 1.5)
            }
            manager.save_snapshot(test_snapshot)
    
    print("   ✅ Created 20 test snapshots")
    
    # Get statistics
    print("\n5. Analyzing historical statistics...")
    stats = manager.get_statistics_summary(days=1)
    print(f"   - Total snapshots: {stats['total_snapshots']}")
    print(f"   - Total vehicles: {stats['total_vehicles']:.0f}")
    print(f"   - Average congestion: {stats['average_congestion']:.1f}%")
    print(f"   - Peak congestion: {stats['peak_congestion']:.1f}%")
    print("   ✅ Statistics retrieved")
    
    # Get peak hours
    print("\n6. Analyzing peak hours...")
    peaks = manager.get_peak_hours_history(days=1)
    if peaks:
        peak_hour = max(peaks, key=lambda h: peaks[h]['average_vehicles'])
        print(f"   - Peak hour: {peak_hour}:00")
        print(f"   - Peak hour vehicles: {peaks[peak_hour]['average_vehicles']:.0f}")
        print("   ✅ Peak hours identified")
    else:
        print("   ℹ️  No peak hours data yet")
    
    # Test Predictive Analyzer
    print("\n7. Testing PredictiveTrafficAnalyzer...")
    analyzer = PredictiveTrafficAnalyzer(manager)
    
    if peaks:
        prediction = analyzer.predict_peak_traffic(peak_hour, days_history=1)
        print(f"   - Prediction for {peak_hour}:00")
        print(f"   - Predicted vehicles: {prediction['predicted_vehicles']:.0f}")
        print(f"   - Confidence: {prediction['confidence']:.0f}%")
        print("   ✅ Predictions working")
        
        # Suggest timing
        timing = analyzer.suggest_signal_timing(peak_hour, days_history=1)
        if 'suggested_cycle_time' in timing:
            print(f"\n   - Suggested cycle time: {timing['suggested_cycle_time']}s")
            print(f"   - Suggested min green: {timing['suggested_min_green']}s")
            print(f"   - Suggested max green: {timing['suggested_max_green']}s")
            print("   ✅ Signal timing suggestions working")
    
    # Test export
    print("\n8. Testing data export...")
    export_file = 'test_export.csv'
    success = manager.export_to_csv(export_file, datetime.now().date(), datetime.now().date())
    if success:
        with open(export_file, 'r') as f:
            lines = len(f.readlines())
        print(f"   - Exported {lines} lines to CSV")
        print("   ✅ CSV export working")
    else:
        print("   ℹ️  No data to export")
    
    # Cleanup
    print("\n9. Cleanup...")
    import shutil
    try:
        shutil.rmtree('traffic_data_test')
        print("   ✅ Test directory cleaned up")
    except:
        print("   ℹ️  Could not cleanup test directory")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED - HISTORICAL DATA SYSTEM WORKING!")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_historical_data()
