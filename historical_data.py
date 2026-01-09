"""
Historical Traffic Data Storage and Management
Stores, retrieves, and analyzes historical traffic patterns
for predictive traffic control.
"""

import json
import csv
import os
from datetime import datetime, timedelta
from pathlib import Path
import requests

class HistoricalDataManager:
    """
    Manages persistent storage of historical traffic data.
    Supports local file storage and Firebase cloud sync.
    """
    
    def __init__(self, local_dir='traffic_data', firebase_config=None):
        """
        Initialize historical data manager.
        
        Args:
            local_dir (str): Local directory for storing data
            firebase_config (dict): Firebase configuration for cloud storage
        """
        self.local_dir = local_dir
        self.firebase_config = firebase_config
        self.db_url = None
        
        # Create local directory if it doesn't exist
        Path(self.local_dir).mkdir(parents=True, exist_ok=True)
        
        # Load Firebase config if provided
        if firebase_config:
            self.db_url = firebase_config.get('databaseURL', '').rstrip('/')
    
    def save_snapshot(self, snapshot_data):
        """
        Save a single traffic snapshot to historical storage.
        
        Args:
            snapshot_data (dict): Traffic snapshot containing:
                - timestamp (str): ISO format timestamp
                - junction_id (int): Junction identifier
                - signal_state (dict): Signal states for all lanes
                - statistics (dict): Traffic statistics
                - congestion_level (float): Current congestion %
        """
        try:
            # Ensure required fields exist
            if 'timestamp' not in snapshot_data:
                snapshot_data['timestamp'] = datetime.now().isoformat()
            
            if 'junction_id' not in snapshot_data:
                snapshot_data['junction_id'] = 0
            
            if 'signal_state' not in snapshot_data:
                snapshot_data['signal_state'] = {}
            
            if 'statistics' not in snapshot_data:
                snapshot_data['statistics'] = {'total_vehicles': 0}
            
            if 'congestion_level' not in snapshot_data:
                snapshot_data['congestion_level'] = 0
            
            # Add metadata
            snapshot_data['recorded_at'] = datetime.now().isoformat()
            
            # Save to local file (JSON Lines format)
            self._save_local(snapshot_data)
            
            # Sync to Firebase if configured
            if self.db_url:
                try:
                    self._save_to_firebase(snapshot_data)
                except Exception as e:
                    # Firebase is optional, don't fail if it's not available
                    pass
                
            return True
        except Exception as e:
            print(f"Error saving snapshot: {e}")
            return False
    
    def _save_local(self, snapshot_data):
        """
        Save snapshot to local file system.
        Uses date-based directory structure for organization.
        """
        try:
            date = datetime.fromisoformat(snapshot_data['timestamp']).date()
            junction_id = snapshot_data['junction_id']
            
            # Directory: traffic_data/2024-01-15/junction_0/
            dir_path = Path(self.local_dir) / str(date) / f"junction_{junction_id}"
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # File: traffic_data/2024-01-15/junction_0/data.jsonl
            file_path = dir_path / 'data.jsonl'
            
            # Append as JSON Lines (one JSON object per line)
            with open(file_path, 'a') as f:
                json.dump(snapshot_data, f)
                f.write('\n')
        except Exception as e:
            print(f"Error in _save_local: {e}")
            raise
    
    def _save_to_firebase(self, snapshot_data):
        """
        Save snapshot to Firebase Realtime Database.
        """
        try:
            timestamp = snapshot_data['timestamp']
            junction_id = snapshot_data['junction_id']
            
            # Create unique key based on timestamp
            timestamp_key = timestamp.replace(':', '-').replace('.', '-')
            
            # Path: historical_data/junction_0/2024-01-15T10-30-45-123456/data
            path = f"historical_data/junction_{junction_id}/{timestamp_key}/data.json"
            url = f"{self.db_url}/{path}"
            
            response = requests.put(url, json=snapshot_data, timeout=5)
            
            if response.status_code not in [200, 201]:
                print(f"Firebase save warning: {response.status_code}")
                
        except Exception as e:
            print(f"Firebase sync error: {e}")
    
    def get_data_by_date(self, date, junction_id=None):
        """
        Retrieve all historical data for a specific date.
        
        Args:
            date (str or datetime): Date in YYYY-MM-DD format
            junction_id (int): Specific junction or None for all
            
        Returns:
            list: Historical snapshots
        """
        # Convert date to string format YYYY-MM-DD
        if isinstance(date, datetime):
            date_str = date.strftime('%Y-%m-%d')
        elif hasattr(date, 'strftime'):  # datetime.date object
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = str(date)
        
        data = []
        date_dir = Path(self.local_dir) / date_str
        
        if not date_dir.exists():
            return data
        
        # Iterate through all junction directories
        for junction_dir in date_dir.iterdir():
            if not junction_dir.is_dir():
                continue
            
            # Filter by junction_id if specified
            if junction_id is not None:
                if not junction_dir.name.endswith(f"_{junction_id}"):
                    continue
            
            # Read JSONL file
            data_file = junction_dir / 'data.jsonl'
            if data_file.exists():
                with open(data_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            data.append(json.loads(line))
        
        return data
    
    def get_data_by_hour(self, hour, date=None):
        """
        Retrieve data for a specific hour.
        
        Args:
            hour (int): Hour (0-23)
            date (str or datetime): Specific date or today
            
        Returns:
            list: Snapshots from that hour
        """
        if date is None:
            date = datetime.now()
        
        data = self.get_data_by_date(date)
        hour_data = []
        
        for snapshot in data:
            snapshot_hour = datetime.fromisoformat(snapshot['timestamp']).hour
            if snapshot_hour == hour:
                hour_data.append(snapshot)
        
        return hour_data
    
    def get_data_range(self, start_date, end_date, junction_id=None):
        """
        Retrieve data for a date range.
        
        Args:
            start_date (str or datetime): Start date
            end_date (str or datetime): End date
            junction_id (int): Specific junction or None
            
        Returns:
            list: All snapshots in range
        """
        # Normalize start_date to date object
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date).date()
        elif isinstance(start_date, datetime):
            start_date = start_date.date()
        
        # Normalize end_date to date object
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date).date()
        elif isinstance(end_date, datetime):
            end_date = end_date.date()
        
        data = []
        current_date = start_date
        
        while current_date <= end_date:
            data.extend(self.get_data_by_date(current_date, junction_id))
            current_date += timedelta(days=1)
        
        return data
    
    def get_peak_hours_history(self, days=7, junction_id=None):
        """
        Analyze peak traffic hours from historical data.
        
        Args:
            days (int): Number of days to analyze
            junction_id (int): Specific junction or None
            
        Returns:
            dict: Peak hours with statistics
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        hourly_vehicles = {}
        
        data = self.get_data_range(start_date, end_date, junction_id)
        
        for snapshot in data:
            hour = datetime.fromisoformat(snapshot['timestamp']).hour
            vehicles = snapshot['statistics'].get('total_vehicles', 0)
            
            if hour not in hourly_vehicles:
                hourly_vehicles[hour] = []
            hourly_vehicles[hour].append(vehicles)
        
        # Calculate averages and patterns
        peak_analysis = {}
        for hour, vehicle_list in hourly_vehicles.items():
            peak_analysis[hour] = {
                'average_vehicles': sum(vehicle_list) / len(vehicle_list),
                'peak_vehicles': max(vehicle_list),
                'min_vehicles': min(vehicle_list),
                'occurrences': len(vehicle_list)
            }
        
        return peak_analysis
    
    def get_congestion_patterns(self, days=7, junction_id=None):
        """
        Get congestion patterns for predictive analysis.
        
        Args:
            days (int): Number of days to analyze
            junction_id (int): Specific junction
            
        Returns:
            dict: Hourly congestion patterns
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        hourly_congestion = {}
        
        data = self.get_data_range(start_date, end_date, junction_id)
        
        for snapshot in data:
            hour = datetime.fromisoformat(snapshot['timestamp']).hour
            congestion = snapshot.get('congestion_level', 0)
            
            if hour not in hourly_congestion:
                hourly_congestion[hour] = []
            hourly_congestion[hour].append(congestion)
        
        # Calculate statistics
        patterns = {}
        for hour, congestion_list in hourly_congestion.items():
            patterns[hour] = {
                'average_congestion': sum(congestion_list) / len(congestion_list),
                'peak_congestion': max(congestion_list),
                'min_congestion': min(congestion_list)
            }
        
        return patterns
    
    def export_to_csv(self, output_file, start_date, end_date, junction_id=None):
        """
        Export historical data to CSV for analysis.
        
        Args:
            output_file (str): Output CSV file path
            start_date (str or datetime): Start date
            end_date (str or datetime): End date
            junction_id (int): Specific junction or None
            
        Returns:
            bool: Success status
        """
        try:
            data = self.get_data_range(start_date, end_date, junction_id)
            
            if not data:
                return False
            
            # Flatten data for CSV
            rows = []
            for snapshot in data:
                row = {
                    'timestamp': snapshot['timestamp'],
                    'junction_id': snapshot['junction_id'],
                    'total_vehicles': snapshot['statistics'].get('total_vehicles', 0),
                    'congestion_level': snapshot.get('congestion_level', 0),
                    'recorded_at': snapshot.get('recorded_at', '')
                }
                
                # Add per-lane data
                vehicles = snapshot.get('statistics', {}).get('vehicles_per_lane', {})
                for lane, count in vehicles.items():
                    row[f"vehicles_{lane}"] = count
                
                rows.append(row)
            
            # Write CSV
            if rows:
                keys = rows[0].keys()
                with open(output_file, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(rows)
                return True
            
            return False
            
        except Exception as e:
            print(f"CSV export error: {e}")
            return False
    
    def get_statistics_summary(self, days=7, junction_id=None):
        """
        Get comprehensive statistics from historical data.
        
        Args:
            days (int): Number of days to analyze
            junction_id (int): Specific junction or None
            
        Returns:
            dict: Comprehensive statistics
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        data = self.get_data_range(start_date, end_date, junction_id)
        
        if not data:
            return {'status': 'No data available'}
        
        all_vehicles = [s['statistics'].get('total_vehicles', 0) for s in data]
        all_congestion = [s.get('congestion_level', 0) for s in data]
        
        return {
            'days_analyzed': days,
            'total_snapshots': len(data),
            'total_vehicles': sum(all_vehicles),
            'average_vehicles_per_snapshot': sum(all_vehicles) / len(all_vehicles) if all_vehicles else 0,
            'peak_vehicles': max(all_vehicles) if all_vehicles else 0,
            'average_congestion': sum(all_congestion) / len(all_congestion) if all_congestion else 0,
            'peak_congestion': max(all_congestion) if all_congestion else 0,
            'date_range': f"{start_date} to {end_date}"
        }
    
    def clear_old_data(self, days_to_keep=30):
        """
        Clean up historical data older than specified days.
        
        Args:
            days_to_keep (int): Number of days to retain
            
        Returns:
            int: Number of directories deleted
        """
        cutoff_date = datetime.now().date() - timedelta(days=days_to_keep)
        deleted_count = 0
        
        for date_dir in Path(self.local_dir).iterdir():
            if not date_dir.is_dir():
                continue
            
            try:
                dir_date = datetime.strptime(date_dir.name, '%Y-%m-%d').date()
                if dir_date < cutoff_date:
                    import shutil
                    shutil.rmtree(date_dir)
                    deleted_count += 1
            except ValueError:
                continue
        
        return deleted_count


class PredictiveTrafficAnalyzer:
    """
    Uses historical data to predict traffic patterns and optimize signal timing.
    """
    
    def __init__(self, historical_manager):
        """
        Initialize analyzer with historical data manager.
        
        Args:
            historical_manager (HistoricalDataManager): Data manager instance
        """
        self.manager = historical_manager
    
    def predict_peak_traffic(self, hour, days_history=14):
        """
        Predict traffic volume for a specific hour based on history.
        
        Args:
            hour (int): Hour to predict (0-23)
            days_history (int): Days of history to use
            
        Returns:
            dict: Prediction with confidence metrics
        """
        peak_hours = self.manager.get_peak_hours_history(days_history)
        
        if hour not in peak_hours:
            return {'prediction': 'No data', 'confidence': 0}
        
        data = peak_hours[hour]
        
        return {
            'hour': hour,
            'predicted_vehicles': int(data['average_vehicles']),
            'peak_possible': int(data['peak_vehicles']),
            'confidence': min(100, data['occurrences'] * 10),  # Higher with more samples
            'samples': data['occurrences']
        }
    
    def suggest_signal_timing(self, hour, days_history=14):
        """
        Suggest optimal signal timing for an hour based on historical patterns.
        
        Args:
            hour (int): Hour to suggest timing for
            days_history (int): Days of history to use
            
        Returns:
            dict: Suggested signal timing
        """
        prediction = self.predict_peak_traffic(hour, days_history)
        
        if prediction['confidence'] == 0:
            return {'suggestion': 'Insufficient data', 'confidence': 0}
        
        vehicles = prediction['predicted_vehicles']
        
        # Simple heuristic: adjust cycle time based on predicted traffic
        base_cycle = 80
        if vehicles > 80:
            suggested_cycle = 100
        elif vehicles > 50:
            suggested_cycle = 90
        else:
            suggested_cycle = 80
        
        return {
            'hour': hour,
            'suggested_cycle_time': suggested_cycle,
            'suggested_min_green': 15,
            'suggested_max_green': 70,
            'based_on_vehicles': vehicles,
            'confidence': prediction['confidence']
        }
    
    def detect_anomalies(self, days=7):
        """
        Detect unusual traffic patterns (anomalies).
        
        Args:
            days (int): Days to analyze
            
        Returns:
            list: Detected anomalies
        """
        peak_hours = self.manager.get_peak_hours_history(days)
        
        anomalies = []
        
        for hour, data in peak_hours.items():
            avg = data['average_vehicles']
            peak = data['peak_vehicles']
            
            # If peak is significantly higher than average, it's an anomaly
            if peak > avg * 1.5:
                anomalies.append({
                    'hour': hour,
                    'type': 'traffic_spike',
                    'normal_avg': int(avg),
                    'observed_peak': int(peak),
                    'deviation': int(peak - avg)
                })
        
        return anomalies
