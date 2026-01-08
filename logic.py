"""
Traffic Signal Timing Logic Module
Handles dynamic signal duration calculation based on vehicle density.
"""

class TrafficSignalController:
    """
    Manages traffic signal timing for a 4-way junction.
    Implements adaptive logic based on vehicle density.
    """
    
    def __init__(self):
        """Initialize signal controller with default parameters."""
        self.lanes = {
            'North': {'vehicles': 0, 'green_time': 20},
            'South': {'vehicles': 0, 'green_time': 20},
            'East': {'vehicles': 0, 'green_time': 20},
            'West': {'vehicles': 0, 'green_time': 20}
        }
        
        # Configuration parameters
        self.min_green_time = 10  # Minimum green light duration (seconds)
        self.max_green_time = 60  # Maximum green light duration (seconds)
        self.base_green_time = 20  # Base green time for calculation
        
        # Simulation state
        self.current_lane = 'North'  # Which lane currently has green light
        self.cycle_counter = 0  # Track cycle iterations
        self.simulation_running = False
        
    def set_vehicle_count(self, lane, count):
        """
        Update vehicle count for a specific lane.
        
        Args:
            lane (str): Lane name ('North', 'South', 'East', 'West')
            count (int): Number of vehicles in the lane
        """
        if lane in self.lanes:
            self.lanes[lane]['vehicles'] = max(0, count)
    
    def calculate_congestion_level(self, vehicle_count):
        """
        Categorize congestion based on vehicle count.
        
        Args:
            vehicle_count (int): Number of vehicles
            
        Returns:
            str: Congestion level ('Low', 'Medium', 'High')
        """
        if vehicle_count < 10:
            return 'Low'
        elif vehicle_count <= 30:
            return 'Medium'
        else:
            return 'High'
    
    def calculate_green_time(self, vehicle_count, total_vehicles):
        """
        Calculate adaptive green light duration based on vehicle density.
        Uses proportional allocation with minimum and maximum constraints.
        
        Args:
            vehicle_count (int): Vehicles in current lane
            total_vehicles (int): Total vehicles across all lanes
            
        Returns:
            int: Green light duration in seconds
        """
        # Prevent division by zero
        if total_vehicles == 0:
            return self.base_green_time
        
        # Calculate proportional green time
        # Formula: (vehicles_in_lane / total_vehicles) * total_cycle_time
        # With a base cycle of 80 seconds (20 per lane average)
        total_cycle_time = self.base_green_time * 4
        
        if total_vehicles > 0:
            proportional_time = (vehicle_count / total_vehicles) * total_cycle_time
        else:
            proportional_time = self.base_green_time
        
        # Apply constraints
        green_time = max(self.min_green_time, min(proportional_time, self.max_green_time))
        
        return int(green_time)
    
    def get_next_lane(self):
        """
        Rotate to next lane in sequence (Fair queuing).
        Order: North → East → South → West
        
        Returns:
            str: Next lane name
        """
        lane_order = ['North', 'East', 'South', 'West']
        current_index = lane_order.index(self.current_lane)
        next_index = (current_index + 1) % len(lane_order)
        return lane_order[next_index]
    
    def get_most_congested_lane(self):
        """
        Find the lane with highest vehicle density.
        
        Returns:
            tuple: (lane_name, vehicle_count)
        """
        most_congested = max(
            self.lanes.items(),
            key=lambda x: x[1]['vehicles']
        )
        return most_congested[0], most_congested[1]['vehicles']
    
    def advance_signal(self):
        """
        Move to next lane in signal cycle.
        Called after current lane's green time expires.
        
        Returns:
            dict: Updated signal state
        """
        self.current_lane = self.get_next_lane()
        self.cycle_counter += 1
        return self.get_signal_state()
    
    def get_signal_state(self):
        """
        Get current state of all traffic signals.
        
        Returns:
            dict: Signal state with green time calculations for each lane
        """
        total_vehicles = sum(lane['vehicles'] for lane in self.lanes.values())
        
        signal_state = {}
        for lane_name, lane_data in self.lanes.items():
            # Calculate green time for this lane
            green_time = self.calculate_green_time(
                lane_data['vehicles'],
                total_vehicles
            )
            
            # Determine signal state
            if lane_name == self.current_lane:
                signal = 'GREEN'
            else:
                signal = 'RED'
            
            # Calculate congestion level
            congestion = self.calculate_congestion_level(lane_data['vehicles'])
            
            signal_state[lane_name] = {
                'vehicles': lane_data['vehicles'],
                'signal': signal,
                'green_time': green_time,
                'congestion': congestion
            }
        
        return signal_state
    
    def get_statistics(self):
        """
        Get overall traffic statistics.
        
        Returns:
            dict: Traffic statistics
        """
        total_vehicles = sum(lane['vehicles'] for lane in self.lanes.values())
        congested_lane, max_vehicles = self.get_most_congested_lane()
        avg_vehicles = total_vehicles / 4
        
        return {
            'total_vehicles': total_vehicles,
            'average_vehicles_per_lane': round(avg_vehicles, 1),
            'most_congested_lane': congested_lane,
            'max_vehicles': max_vehicles,
            'current_green_lane': self.current_lane,
            'cycle_number': self.cycle_counter
        }
    
    def reset(self):
        """Reset simulation to initial state."""
        self.current_lane = 'North'
        self.cycle_counter = 0
        self.simulation_running = False
        for lane in self.lanes:
            self.lanes[lane]['vehicles'] = 0
