"""
Enhanced Multi-Junction Traffic Management System
Manages multiple traffic intersections with coordination capabilities.
"""

from logic import TrafficSignalController
from datetime import datetime
import json

class MultiJunctionController:
    """
    Manages multiple traffic signal intersections with coordination.
    Allows controlling 2-4 junctions simultaneously with resource allocation.
    """
    
    def __init__(self, num_junctions=2):
        """
        Initialize multi-junction system.
        
        Args:
            num_junctions (int): Number of intersections (2-4, default 2)
        """
        self.num_junctions = max(2, min(num_junctions, 4))
        self.junctions = {}
        self.active_junction = 0
        self.coordination_mode = 'independent'  # 'independent' or 'coordinated'
        self.total_vehicle_capacity = 100  # Total vehicles across all junctions
        
        # Initialize junctions with unique names
        junction_names = ['Downtown', 'Midtown', 'Uptown', 'Suburb']
        for i in range(self.num_junctions):
            self.junctions[i] = {
                'name': junction_names[i],
                'controller': TrafficSignalController(),
                'total_vehicles': 0,
                'efficiency_score': 0.0,
                'active': True
            }
    
    def set_active_junction(self, junction_id):
        """Set the currently active junction for viewing/control."""
        if 0 <= junction_id < self.num_junctions:
            self.active_junction = junction_id
            return True
        return False
    
    def get_active_junction(self):
        """Get the currently active junction."""
        return self.junctions[self.active_junction]
    
    def set_coordination_mode(self, mode):
        """
        Set coordination mode.
        
        Args:
            mode (str): 'independent' (each junction separate) or 
                       'coordinated' (junctions work together)
        """
        self.coordination_mode = mode
    
    def set_vehicle_count(self, junction_id, lane, count):
        """
        Set vehicle count for a specific lane in a junction.
        
        Args:
            junction_id (int): Junction identifier
            lane (str): Lane direction ('North', 'South', 'East', 'West')
            count (int): Number of vehicles
        """
        if junction_id in self.junctions:
            self.junctions[junction_id]['controller'].set_vehicle_count(lane, count)
            self._update_junction_stats(junction_id)
    
    def _update_junction_stats(self, junction_id):
        """Calculate statistics for a junction."""
        controller = self.junctions[junction_id]['controller']
        state = controller.get_signal_state()
        total = sum(state[lane]['vehicles'] for lane in state)
        self.junctions[junction_id]['total_vehicles'] = total
    
    def advance_signal(self, junction_id=None):
        """
        Advance signal for a specific junction or all junctions.
        
        Args:
            junction_id (int): If None, advance all junctions
        """
        if junction_id is not None:
            if junction_id in self.junctions:
                self.junctions[junction_id]['controller'].advance_signal()
        else:
            for junc_id in self.junctions:
                self.junctions[junc_id]['controller'].advance_signal()
    
    def get_all_junctions_state(self):
        """
        Get state of all junctions.
        
        Returns:
            dict: State of all junctions with signals and statistics
        """
        all_state = {}
        for junc_id, junction_data in self.junctions.items():
            controller = junction_data['controller']
            all_state[junc_id] = {
                'name': junction_data['name'],
                'signal_state': controller.get_signal_state(),
                'statistics': controller.get_statistics(),
                'total_vehicles': junction_data['total_vehicles'],
                'active': junction_data['active']
            }
        return all_state
    
    def get_system_health(self):
        """
        Calculate overall system health metrics.
        
        Returns:
            dict: System-wide metrics
        """
        all_state = self.get_all_junctions_state()
        
        total_vehicles = sum(
            state['total_vehicles'] for state in all_state.values()
        )
        avg_congestion = total_vehicles / (self.num_junctions * 25)
        
        # Calculate efficiency score (0-100)
        efficiency = max(0, 100 - (avg_congestion * 50))
        
        most_congested_junc = max(
            all_state.items(),
            key=lambda x: x[1]['total_vehicles']
        )
        
        return {
            'total_vehicles': total_vehicles,
            'average_vehicles_per_junction': total_vehicles / self.num_junctions,
            'system_efficiency': round(efficiency, 1),
            'coordination_mode': self.coordination_mode,
            'most_congested_junction': most_congested_junc[0],
            'most_congested_name': most_congested_junc[1]['name'],
            'max_vehicles_any_junction': most_congested_junc[1]['total_vehicles'],
            'active_junctions': sum(1 for j in self.junctions.values() if j['active'])
        }
    
    def enable_coordinated_control(self):
        """
        Enable coordinated control between junctions.
        Junctions with lower traffic help manage higher traffic junctions.
        """
        self.coordination_mode = 'coordinated'
        all_state = self.get_all_junctions_state()
        
        # Find most and least congested junctions
        junc_by_vehicles = sorted(
            all_state.items(),
            key=lambda x: x[1]['total_vehicles'],
            reverse=True
        )
        
        # Most congested gets priority, least congested helps
        for rank, (junc_id, state) in enumerate(junc_by_vehicles):
            priority = 1 - (rank / self.num_junctions)  # 1.0 to near 0
            self.junctions[junc_id]['priority'] = priority
    
    def get_coordination_recommendations(self):
        """
        Get recommendations for traffic flow optimization.
        
        Returns:
            list: List of optimization suggestions
        """
        recommendations = []
        all_state = self.get_all_junctions_state()
        
        # Check for bottlenecks
        for junc_id, state in all_state.items():
            if state['total_vehicles'] > 80:
                recommendations.append({
                    'type': 'congestion',
                    'junction': state['name'],
                    'message': f"High congestion at {state['name']}. Consider traffic diversion.",
                    'severity': 'high'
                })
            elif state['total_vehicles'] < 20:
                recommendations.append({
                    'type': 'underutilized',
                    'junction': state['name'],
                    'message': f"{state['name']} has low traffic. Available for overflow.",
                    'severity': 'low'
                })
        
        return recommendations
    
    def export_junction_data(self, junction_id):
        """
        Export data for a junction as JSON.
        
        Args:
            junction_id (int): Junction to export
            
        Returns:
            str: JSON formatted data
        """
        junction = self.get_all_junctions_state()[junction_id]
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'junction_name': junction['name'],
            'signal_state': junction['signal_state'],
            'statistics': junction['statistics']
        }
        return json.dumps(export_data, indent=2)
    
    def reset_all(self):
        """Reset all junctions to initial state."""
        for junc_id in self.junctions:
            self.junctions[junc_id]['controller'].reset()
    
    def toggle_junction(self, junction_id):
        """
        Enable/disable a junction.
        
        Args:
            junction_id (int): Junction to toggle
        """
        if junction_id in self.junctions:
            self.junctions[junction_id]['active'] = \
                not self.junctions[junction_id]['active']
