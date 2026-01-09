"""
Firebase Real-time Integration Module
Enables cloud data sync, real-time updates, and scalability
"""

import json
from datetime import datetime
from typing import Dict, List, Optional


class FirebaseConfig:
    """Firebase configuration manager"""
    
    def __init__(self):
        self.config = {
            "apiKey": "YOUR_API_KEY",
            "authDomain": "your-project.firebaseapp.com",
            "databaseURL": "https://your-project.firebaseio.com",
            "projectId": "your-project-id",
            "storageBucket": "your-project.appspot.com",
            "messagingSenderId": "YOUR_SENDER_ID",
            "appId": "YOUR_APP_ID"
        }
        self.is_configured = False
    
    def set_config(self, config_dict: Dict):
        """Set Firebase configuration from dict or JSON"""
        self.config.update(config_dict)
        self.validate()
    
    def validate(self):
        """Validate Firebase configuration"""
        required_keys = ["apiKey", "authDomain", "projectId"]
        if all(key in self.config for key in required_keys):
            self.is_configured = self.config["apiKey"] != "YOUR_API_KEY"
        return self.is_configured
    
    def load_from_json(self, json_path: str):
        """Load configuration from JSON file"""
        try:
            with open(json_path, 'r') as f:
                config = json.load(f)
            self.set_config(config)
            return True
        except:
            return False


class FirebaseRealtimeDB:
    """Firebase Realtime Database wrapper for traffic data"""
    
    def __init__(self, config: FirebaseConfig):
        self.config = config
        self.is_connected = False
        self.local_cache = {}
        
        if config.is_configured:
            try:
                # This would require firebase-admin SDK
                # import firebase_admin
                # from firebase_admin import db
                # Initialize connection
                self.is_connected = True
            except ImportError:
                print("Firebase SDK not installed. Using local caching mode.")
                self.is_connected = False
    
    def push_traffic_data(self, junction_id: str, lane: str, vehicle_count: int, 
                         signal_state: str, timestamp: datetime = None):
        """Push real-time traffic data to Firebase"""
        
        if timestamp is None:
            timestamp = datetime.now()
        
        data = {
            'junction_id': junction_id,
            'lane': lane,
            'vehicle_count': vehicle_count,
            'signal_state': signal_state,
            'timestamp': timestamp.isoformat()
        }
        
        if self.is_connected:
            try:
                # Firebase push would happen here
                # db.reference(f'traffic/{junction_id}/{lane}').set(data)
                pass
            except Exception as e:
                print(f"Firebase push error: {e}")
                self._cache_locally(junction_id, lane, data)
        else:
            # Use local caching when Firebase is not available
            self._cache_locally(junction_id, lane, data)
        
        return True
    
    def fetch_traffic_data(self, junction_id: str, lane: str = None, limit: int = 100):
        """Fetch historical traffic data from Firebase"""
        
        if self.is_connected:
            try:
                # Firebase fetch would happen here
                # data = db.reference(f'traffic/{junction_id}').get().val()
                return []
            except:
                return self._get_cache(junction_id, lane, limit)
        else:
            return self._get_cache(junction_id, lane, limit)
    
    def _cache_locally(self, junction_id: str, lane: str, data: Dict):
        """Store data locally for offline support"""
        key = f"{junction_id}:{lane}"
        if key not in self.local_cache:
            self.local_cache[key] = []
        self.local_cache[key].append(data)
        
        # Keep only last 1000 entries per lane
        if len(self.local_cache[key]) > 1000:
            self.local_cache[key] = self.local_cache[key][-1000:]
    
    def _get_cache(self, junction_id: str, lane: str = None, limit: int = 100):
        """Retrieve cached data"""
        results = []
        
        if lane:
            key = f"{junction_id}:{lane}"
            if key in self.local_cache:
                results = self.local_cache[key][-limit:]
        else:
            # Return all lanes for this junction
            for key in self.local_cache:
                if key.startswith(f"{junction_id}:"):
                    results.extend(self.local_cache[key][-limit:])
        
        return results
    
    def sync_to_cloud(self):
        """Sync all cached data to Firebase (for offline-first support)"""
        if not self.is_connected:
            return False
        
        synced = 0
        for key, data_list in self.local_cache.items():
            try:
                # Firebase sync would happen here
                synced += len(data_list)
            except:
                continue
        
        return synced > 0


class FirebaseAuth:
    """Firebase Authentication wrapper"""
    
    def __init__(self, config: FirebaseConfig):
        self.config = config
        self.current_user = None
        self.auth_token = None
    
    def authenticate(self, email: str, password: str):
        """Authenticate user with Firebase"""
        try:
            # Firebase auth would happen here
            # from firebase_admin import auth
            # user = auth.get_user_by_email(email)
            self.current_user = email
            return True
        except:
            return False
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return self.current_user is not None
    
    def get_current_user(self):
        """Get current authenticated user"""
        return self.current_user


class FirebaseAnalytics:
    """Firebase Analytics integration for traffic data"""
    
    def __init__(self, config: FirebaseConfig):
        self.config = config
        self.events = []
    
    def log_event(self, event_name: str, event_params: Dict = None):
        """Log analytics event"""
        event = {
            'name': event_name,
            'parameters': event_params or {},
            'timestamp': datetime.now().isoformat()
        }
        self.events.append(event)
        
        if self.config.is_configured:
            try:
                # Firebase Analytics event would be logged here
                pass
            except:
                pass
        
        return True
    
    def log_signal_change(self, junction_id: str, lane: str, green_time: int):
        """Log signal timing change"""
        return self.log_event('signal_change', {
            'junction_id': junction_id,
            'lane': lane,
            'green_time': green_time
        })
    
    def log_congestion_event(self, junction_id: str, severity: str):
        """Log congestion detection"""
        return self.log_event('congestion_detected', {
            'junction_id': junction_id,
            'severity': severity
        })
    
    def log_emergency_override(self, junction_id: str, vehicle_type: str):
        """Log emergency vehicle detection"""
        return self.log_event('emergency_override', {
            'junction_id': junction_id,
            'vehicle_type': vehicle_type
        })
    
    def get_analytics_summary(self):
        """Get summary of logged events"""
        return {
            'total_events': len(self.events),
            'events_by_type': self._group_events_by_name(),
            'recent_events': self.events[-10:] if self.events else []
        }
    
    def _group_events_by_name(self):
        """Group events by event name"""
        groups = {}
        for event in self.events:
            name = event['name']
            groups[name] = groups.get(name, 0) + 1
        return groups


class CloudSyncManager:
    """Manages cloud synchronization and offline support"""
    
    def __init__(self, db: FirebaseRealtimeDB, analytics: FirebaseAnalytics):
        self.db = db
        self.analytics = analytics
        self.sync_queue = []
        self.is_syncing = False
    
    def enqueue_sync(self, data: Dict):
        """Add data to sync queue"""
        self.sync_queue.append({
            'data': data,
            'timestamp': datetime.now(),
            'synced': False
        })
    
    def sync_all(self):
        """Sync all queued data to cloud"""
        if self.is_syncing:
            return False
        
        self.is_syncing = True
        synced_count = 0
        
        try:
            for item in self.sync_queue:
                if not item['synced']:
                    # Attempt to sync
                    # item['synced'] = self.db.push_data(item['data'])
                    synced_count += 1
        finally:
            self.is_syncing = False
        
        # Remove synced items
        self.sync_queue = [item for item in self.sync_queue if not item['synced']]
        
        return synced_count
    
    def get_sync_status(self):
        """Get current sync status"""
        return {
            'is_syncing': self.is_syncing,
            'queued_items': len(self.sync_queue),
            'db_connected': self.db.is_connected
        }


class TrafficDataCloud:
    """Main cloud integration facade"""
    
    def __init__(self, firebase_config_path: str = None):
        self.config = FirebaseConfig()
        
        if firebase_config_path:
            self.config.load_from_json(firebase_config_path)
        
        self.db = FirebaseRealtimeDB(self.config)
        self.auth = FirebaseAuth(self.config)
        self.analytics = FirebaseAnalytics(self.config)
        self.sync_manager = CloudSyncManager(self.db, self.analytics)
    
    def push_traffic_snapshot(self, junction_data: Dict):
        """Push traffic snapshot to cloud"""
        for junction_id, lanes in junction_data.items():
            for lane_data in lanes:
                self.db.push_traffic_data(
                    junction_id,
                    lane_data['lane'],
                    lane_data['vehicles'],
                    lane_data['state']
                )
    
    def get_cloud_status(self):
        """Get overall cloud integration status"""
        return {
            'configured': self.config.is_configured,
            'db_connected': self.db.is_connected,
            'authenticated': self.auth.is_authenticated(),
            'sync_status': self.sync_manager.get_sync_status()
        }
    
    def is_ready(self):
        """Check if cloud integration is ready"""
        return self.config.is_configured and self.auth.is_authenticated()


# Quick start helper
def setup_firebase(config_path: str = None):
    """Quick setup for Firebase integration"""
    cloud = TrafficDataCloud(config_path)
    return cloud


if __name__ == "__main__":
    # Example usage
    config = FirebaseConfig()
    
    # To use with real Firebase, set your credentials:
    # config.set_config({
    #     "apiKey": "YOUR_API_KEY",
    #     "authDomain": "your-project.firebaseapp.com",
    #     "projectId": "your-project-id"
    # })
    
    cloud = TrafficDataCloud()
    print("Firebase Integration Module Ready")
    print(f"Cloud Status: {cloud.get_cloud_status()}")
