"""
Traffic Analytics and Historical Data Logging
Tracks and analyzes traffic patterns over time.
"""

import json
from datetime import datetime
from collections import defaultdict

class TrafficAnalytics:
    """
    Tracks historical traffic data and generates analytics.
    Records vehicle counts, signal states, and system performance.
    """
    
    def __init__(self):
        """Initialize analytics system."""
        self.traffic_logs = []  # List of timestamped snapshots
        self.hourly_stats = defaultdict(lambda: defaultdict(list))
        self.peak_hours = []
        self.average_wait_times = {}
        self.system_efficiency_history = []
        self.total_vehicles_processed = 0
        
    def log_snapshot(self, timestamp, junction_id, signal_state, statistics):
        """
        Log a snapshot of traffic state.
        
        Args:
            timestamp (str): ISO format timestamp
            junction_id (int): Which junction
            signal_state (dict): Current signal states for all lanes
            statistics (dict): Traffic statistics
        """
        snapshot = {
            'timestamp': timestamp,
            'datetime': datetime.fromisoformat(timestamp),
            'junction_id': junction_id,
            'signal_state': signal_state,
            'statistics': statistics,
            'congestion_level': self._calculate_congestion_level(statistics),
            'throughput': statistics['total_vehicles']
        }
        
        self.traffic_logs.append(snapshot)
        self._update_hourly_stats(snapshot)
        self.total_vehicles_processed += statistics['total_vehicles']
    
    def _calculate_congestion_level(self, statistics):
        """
        Calculate overall congestion level (0-100).
        
        Args:
            statistics (dict): Traffic statistics
            
        Returns:
            float: Congestion level percentage
        """
        total = statistics['total_vehicles']
        max_capacity = 100  # Per-junction capacity
        return min(100, (total / max_capacity) * 100)
    
    def _update_hourly_stats(self, snapshot):
        """Update hourly statistics."""
        hour = snapshot['datetime'].hour
        junction_id = snapshot['junction_id']
        
        self.hourly_stats[hour][junction_id].append(snapshot)
    
    def get_peak_hours(self):
        """
        Identify peak traffic hours.
        
        Returns:
            list: Hours with highest average traffic
        """
        hour_averages = {}
        
        for hour, junctions in self.hourly_stats.items():
            total_vehicles = sum(
                sum(s['throughput'] for s in snapshots) 
                for snapshots in junctions.values()
            )
            count = sum(len(snapshots) for snapshots in junctions.values())
            
            if count > 0:
                hour_averages[hour] = total_vehicles / count
        
        # Sort by traffic volume
        sorted_hours = sorted(hour_averages.items(), key=lambda x: x[1], reverse=True)
        self.peak_hours = [hour for hour, _ in sorted_hours[:3]]
        
        return self.peak_hours
    
    def get_average_wait_time(self, junction_id=None):
        """
        Calculate average wait time for vehicles.
        
        Args:
            junction_id (int): If None, calculate system-wide
            
        Returns:
            float: Average wait time in seconds
        """
        relevant_logs = self.traffic_logs
        
        if junction_id is not None:
            relevant_logs = [log for log in self.traffic_logs 
                           if log['junction_id'] == junction_id]
        
        if not relevant_logs:
            return 0
        
        # Average of max green times (proxy for wait time)
        total_wait = sum(
            log['statistics']['cycle_number'] * 5  # Estimate based on cycles
            for log in relevant_logs
        )
        
        return total_wait / len(relevant_logs) if relevant_logs else 0
    
    def get_system_efficiency(self):
        """
        Calculate system efficiency metrics.
        
        Returns:
            dict: Efficiency metrics
        """
        if not self.traffic_logs:
            return {'efficiency': 0, 'throughput': 0, 'congestion': 0}
        
        total_congestion = sum(log['congestion_level'] for log in self.traffic_logs)
        avg_congestion = total_congestion / len(self.traffic_logs)
        
        efficiency = max(0, 100 - avg_congestion)
        throughput = self.total_vehicles_processed
        
        return {
            'efficiency_score': round(efficiency, 1),
            'total_throughput': throughput,
            'average_congestion': round(avg_congestion, 1),
            'total_snapshots': len(self.traffic_logs)
        }
    
    def get_lane_performance(self, junction_id=None):
        """
        Get performance metrics per lane.
        
        Args:
            junction_id (int): Specific junction or None for all
            
        Returns:
            dict: Lane-specific metrics
        """
        relevant_logs = self.traffic_logs
        
        if junction_id is not None:
            relevant_logs = [log for log in self.traffic_logs 
                           if log['junction_id'] == junction_id]
        
        lane_stats = defaultdict(lambda: {
            'total_vehicles': 0,
            'times_green': 0,
            'average_wait': 0,
            'throughput': 0
        })
        
        for log in relevant_logs:
            for lane, state in log['signal_state'].items():
                lane_stats[lane]['total_vehicles'] += state['vehicles']
                if state['signal'] == 'GREEN':
                    lane_stats[lane]['times_green'] += 1
                lane_stats[lane]['throughput'] += state['vehicles']
        
        return dict(lane_stats)
    
    def export_analytics_report(self):
        """
        Generate comprehensive analytics report.
        
        Returns:
            str: JSON formatted report
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_logs': len(self.traffic_logs),
            'total_vehicles_processed': self.total_vehicles_processed,
            'efficiency': self.get_system_efficiency(),
            'peak_hours': self.get_peak_hours(),
            'average_wait_time': round(self.get_average_wait_time(), 1),
            'lane_performance': self.get_lane_performance()
        }
        
        return json.dumps(report, indent=2)
    
    def get_traffic_trend(self, last_n_logs=10):
        """
        Get traffic trend (increasing, decreasing, stable).
        
        Args:
            last_n_logs (int): Number of recent logs to analyze
            
        Returns:
            dict: Trend information
        """
        if len(self.traffic_logs) < 2:
            return {'trend': 'insufficient_data', 'direction': 'N/A'}
        
        recent = self.traffic_logs[-last_n_logs:]
        congestion_values = [log['congestion_level'] for log in recent]
        
        if congestion_values[-1] > congestion_values[0] * 1.1:
            trend = 'increasing'
        elif congestion_values[-1] < congestion_values[0] * 0.9:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'current_congestion': congestion_values[-1],
            'previous_congestion': congestion_values[0],
            'change_percent': round(
                ((congestion_values[-1] - congestion_values[0]) / 
                 congestion_values[0] * 100) if congestion_values[0] > 0 else 0, 1
            )
        }
    
    def clear_logs(self):
        """Clear all logged data and reset all counters."""
        self.traffic_logs = []
        self.hourly_stats = defaultdict(lambda: defaultdict(list))
        self.peak_hours = []
        self.average_wait_times = {}
        self.system_efficiency_history = []
        self.total_vehicles_processed = 0
