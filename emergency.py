"""
Emergency Vehicle Priority System
Allows emergency vehicles (ambulances, fire trucks) to override normal signals.
"""

class EmergencyController:
    """
    Manages emergency vehicle detection and signal override.
    Gives priority to ambulances, fire trucks, and police vehicles.
    """
    
    def __init__(self, traffic_controller):
        """
        Initialize emergency controller.
        
        Args:
            traffic_controller: Reference to TrafficSignalController instance
        """
        self.controller = traffic_controller
        self.emergency_active = False
        self.emergency_lane = None
        self.emergency_type = None
        self.emergency_start_time = None
        self.override_duration = 30  # seconds
        
        # Emergency vehicle types
        self.EMERGENCY_TYPES = {
            'ambulance': {'priority': 1, 'color': '#FF6B6B', 'duration': 30},
            'fire_truck': {'priority': 2, 'color': '#FF0000', 'duration': 40},
            'police': {'priority': 3, 'color': '#0066FF', 'duration': 25}
        }
    
    def detect_emergency_vehicle(self, lane, vehicle_type):
        """
        Detect an emergency vehicle approaching.
        
        Args:
            lane (str): Lane with emergency vehicle ('North', 'South', 'East', 'West')
            vehicle_type (str): Type of vehicle ('ambulance', 'fire_truck', 'police')
            
        Returns:
            bool: Success status
        """
        if vehicle_type not in self.EMERGENCY_TYPES:
            return False
        
        self.emergency_active = True
        self.emergency_lane = lane
        self.emergency_type = vehicle_type
        self.emergency_start_time = 0  # Start counting seconds
        
        # Get override duration for this vehicle type
        self.override_duration = self.EMERGENCY_TYPES[vehicle_type]['duration']
        
        return True
    
    def override_signal_for_emergency(self):
        """
        Override current signal to give green to emergency vehicle.
        
        Returns:
            dict: Updated signal state with emergency overridden
        """
        if not self.emergency_active or not self.emergency_lane:
            return None
        
        # Force the emergency lane to have green signal
        original_lane = self.controller.current_lane
        self.controller.current_lane = self.emergency_lane
        
        return self.controller.get_signal_state()
    
    def update_emergency_timer(self, elapsed_seconds):
        """
        Update emergency override timer.
        
        Args:
            elapsed_seconds (int): Seconds elapsed since emergency started
        """
        if self.emergency_active:
            self.emergency_start_time = elapsed_seconds
            
            # Check if override duration has expired
            if elapsed_seconds >= self.override_duration:
                self.clear_emergency()
    
    def clear_emergency(self):
        """Clear emergency state and return to normal operation."""
        self.emergency_active = False
        self.emergency_lane = None
        self.emergency_type = None
        self.emergency_start_time = None
    
    def get_emergency_status(self):
        """
        Get current emergency status.
        
        Returns:
            dict: Emergency status information
        """
        return {
            'active': self.emergency_active,
            'lane': self.emergency_lane,
            'type': self.emergency_type,
            'elapsed_time': self.emergency_start_time,
            'override_duration': self.override_duration,
            'time_remaining': max(0, self.override_duration - self.emergency_start_time) 
                             if self.emergency_active else 0
        }
    
    def get_emergency_color(self):
        """
        Get color code for current emergency type.
        
        Returns:
            str: Hex color code
        """
        if self.emergency_active and self.emergency_type:
            return self.EMERGENCY_TYPES[self.emergency_type]['color']
        return None
    
    def display_emergency_alert(self):
        """
        Generate emergency alert message for display.
        
        Returns:
            str: Alert message
        """
        if not self.emergency_active:
            return None
        
        messages = {
            'ambulance': f"🚑 AMBULANCE DETECTED on {self.emergency_lane} lane - Override active",
            'fire_truck': f"🚒 FIRE TRUCK DETECTED on {self.emergency_lane} lane - Override active",
            'police': f"🚓 POLICE VEHICLE DETECTED on {self.emergency_lane} lane - Override active"
        }
        
        return messages.get(self.emergency_type, "Emergency vehicle override active")
    
    def get_all_emergency_types(self):
        """
        Get all supported emergency vehicle types.
        
        Returns:
            dict: All emergency vehicle types with properties
        """
        return self.EMERGENCY_TYPES
