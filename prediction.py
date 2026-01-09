"""
ML-Based Traffic Prediction Module
Predicts future traffic patterns using historical data
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.seasonal import seasonal_decompose
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class TrafficPredictor:
    """ML-based traffic forecasting system"""
    
    def __init__(self):
        self.historical_data = []
        self.prediction_models = {}
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        
    def add_historical_data(self, timestamp, lane, vehicle_count):
        """Add historical traffic data point"""
        self.historical_data.append({
            'timestamp': timestamp,
            'lane': lane,
            'vehicles': vehicle_count,
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday()
        })
        
    def get_historical_df(self):
        """Convert historical data to DataFrame"""
        if not self.historical_data:
            return None
        return pd.DataFrame(self.historical_data)
    
    def predict_next_hours(self, lane, hours_ahead=4):
        """
        Predict traffic for next N hours using multiple methods
        Returns: predictions with confidence intervals
        """
        df = self.get_historical_df()
        
        if df is None or len(df) < 5:
            return self._simple_forecast(lane, hours_ahead)
        
        lane_data = df[df['lane'] == lane].copy()
        if len(lane_data) < 5:
            return self._simple_forecast(lane, hours_ahead)
        
        predictions = {}
        
        # Method 1: Time-based averaging (always available)
        predictions['simple'] = self._simple_forecast(lane, hours_ahead)
        
        # Method 2: ARIMA (if statsmodels available)
        if STATSMODELS_AVAILABLE and len(lane_data) >= 10:
            predictions['arima'] = self._arima_forecast(lane_data, hours_ahead)
        
        # Method 3: ML-based (if sklearn available)
        if SKLEARN_AVAILABLE and len(lane_data) >= 15:
            predictions['ml'] = self._ml_forecast(lane_data, lane, hours_ahead)
        
        # Return best available prediction
        if 'ml' in predictions:
            return predictions['ml']
        elif 'arima' in predictions:
            return predictions['arima']
        else:
            return predictions['simple']
    
    def _simple_forecast(self, lane, hours_ahead):
        """
        Simple forecast based on historical hourly patterns
        Works without external ML libraries
        """
        df = self.get_historical_df()
        
        if df is None or len(df) == 0:
            # Return baseline predictions
            current_hour = datetime.now().hour
            predictions = []
            for i in range(hours_ahead):
                hour = (current_hour + i + 1) % 24
                # Simulate traffic pattern: peak at 8-9am, 5-6pm
                if hour in [8, 9, 17, 18]:
                    base = 75
                elif hour in [10, 11, 14, 15, 16]:
                    base = 50
                else:
                    base = 30
                
                predictions.append({
                    'hour': hour,
                    'predicted_vehicles': base,
                    'lower_bound': max(10, base - 15),
                    'upper_bound': base + 15,
                    'confidence': 0.65
                })
            return predictions
        
        lane_data = df[df['lane'] == lane].copy()
        hourly_avg = lane_data.groupby('hour')['vehicles'].agg(['mean', 'std']).fillna(0)
        
        current_hour = datetime.now().hour
        predictions = []
        
        for i in range(hours_ahead):
            future_hour = (current_hour + i + 1) % 24
            
            if future_hour in hourly_avg.index:
                mean = hourly_avg.loc[future_hour, 'mean']
                std = hourly_avg.loc[future_hour, 'std']
            else:
                mean = lane_data['vehicles'].mean()
                std = lane_data['vehicles'].std()
            
            std = std if std > 0 else mean * 0.2
            
            predictions.append({
                'hour': future_hour,
                'predicted_vehicles': int(mean),
                'lower_bound': max(5, int(mean - 1.96 * std)),
                'upper_bound': int(mean + 1.96 * std),
                'confidence': 0.75
            })
        
        return predictions
    
    def _arima_forecast(self, lane_data, hours_ahead):
        """ARIMA-based forecasting (requires statsmodels)"""
        try:
            if len(lane_data) < 10:
                return self._simple_forecast(lane_data['lane'].iloc[0], hours_ahead)
            
            series = lane_data['vehicles'].values
            
            # Try ARIMA(1,1,1)
            try:
                model = ARIMA(series, order=(1, 1, 1))
                fitted = model.fit()
                forecast = fitted.get_forecast(steps=hours_ahead)
                pred_mean = forecast.predicted_mean.values
                pred_ci = forecast.conf_int(alpha=0.05).values
            except:
                # Fallback to simpler ARIMA
                return self._simple_forecast(lane_data['lane'].iloc[0], hours_ahead)
            
            predictions = []
            current_hour = datetime.now().hour
            
            for i, pred in enumerate(pred_mean):
                future_hour = (current_hour + i + 1) % 24
                predictions.append({
                    'hour': future_hour,
                    'predicted_vehicles': int(max(0, pred)),
                    'lower_bound': int(max(0, pred_ci[i][0])),
                    'upper_bound': int(max(0, pred_ci[i][1])),
                    'confidence': 0.82,
                    'method': 'ARIMA'
                })
            
            return predictions
        except:
            return self._simple_forecast(lane_data['lane'].iloc[0], hours_ahead)
    
    def _ml_forecast(self, lane_data, lane, hours_ahead):
        """ML-based forecasting using RandomForest (requires sklearn)"""
        try:
            if len(lane_data) < 15:
                return self._simple_forecast(lane, hours_ahead)
            
            # Create features
            lane_data = lane_data.copy()
            lane_data['hour_sin'] = np.sin(2 * np.pi * lane_data['hour'] / 24)
            lane_data['hour_cos'] = np.cos(2 * np.pi * lane_data['hour'] / 24)
            lane_data['day_sin'] = np.sin(2 * np.pi * lane_data['day_of_week'] / 7)
            lane_data['day_cos'] = np.cos(2 * np.pi * lane_data['day_of_week'] / 7)
            
            # Rolling statistics
            lane_data['rolling_mean'] = lane_data['vehicles'].rolling(window=3, min_periods=1).mean()
            lane_data['rolling_std'] = lane_data['vehicles'].rolling(window=3, min_periods=1).std()
            
            features = ['hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'rolling_mean', 'rolling_std']
            X = lane_data[features].fillna(0)
            y = lane_data['vehicles']
            
            # Train model
            model = RandomForestRegressor(n_estimators=50, max_depth=8, random_state=42)
            model.fit(X, y)
            
            # Make predictions
            predictions = []
            current_hour = datetime.now().hour
            current_day = datetime.now().weekday()
            
            for i in range(hours_ahead):
                future_hour = (current_hour + i + 1) % 24
                future_day = (current_day + ((current_hour + i + 1) // 24)) % 7
                
                hour_sin = np.sin(2 * np.pi * future_hour / 24)
                hour_cos = np.cos(2 * np.pi * future_hour / 24)
                day_sin = np.sin(2 * np.pi * future_day / 7)
                day_cos = np.cos(2 * np.pi * future_day / 7)
                rolling_mean = y.tail(3).mean()
                rolling_std = y.tail(3).std() if y.tail(3).std() > 0 else rolling_mean * 0.2
                
                X_future = np.array([[hour_sin, hour_cos, day_sin, day_cos, rolling_mean, rolling_std]])
                pred = model.predict(X_future)[0]
                std_dev = rolling_std if rolling_std > 0 else pred * 0.15
                
                predictions.append({
                    'hour': future_hour,
                    'predicted_vehicles': int(max(0, pred)),
                    'lower_bound': int(max(0, pred - 1.96 * std_dev)),
                    'upper_bound': int(max(0, pred + 1.96 * std_dev)),
                    'confidence': 0.88,
                    'method': 'ML (Random Forest)'
                })
            
            return predictions
        except:
            return self._simple_forecast(lane, hours_ahead)
    
    def get_peak_hours_prediction(self):
        """Predict peak traffic hours for next 24 hours"""
        df = self.get_historical_df()
        
        if df is None or len(df) == 0:
            # Default patterns
            return {
                'morning_peak': (8, 9),
                'afternoon_peak': (5, 6),
                'current_trend': 'normal'
            }
        
        hourly_avg = df.groupby('hour')['vehicles'].mean()
        
        if len(hourly_avg) == 0:
            return {'morning_peak': (8, 9), 'afternoon_peak': (5, 6), 'current_trend': 'normal'}
        
        # Find peak hours
        peak_hour = hourly_avg.idxmax()
        second_peak = hourly_avg.nlargest(2).index[-1]
        
        current_vehicles = df['vehicles'].tail(1).values[0] if len(df) > 0 else 0
        avg_vehicles = df['vehicles'].mean()
        
        if current_vehicles > avg_vehicles * 1.3:
            trend = 'high'
        elif current_vehicles < avg_vehicles * 0.7:
            trend = 'low'
        else:
            trend = 'normal'
        
        return {
            'morning_peak': tuple(sorted([peak_hour, second_peak])[:2]),
            'afternoon_peak': tuple(sorted([peak_hour, second_peak])[-2:]) if len(hourly_avg) > 2 else (5, 6),
            'current_trend': trend,
            'avg_vehicles': int(avg_vehicles),
            'current_vehicles': int(current_vehicles)
        }
    
    def get_congestion_forecast(self, lanes, threshold=50):
        """Predict which lanes will be congested in next 4 hours"""
        forecasts = {}
        
        for lane in lanes:
            pred = self.predict_next_hours(lane, hours_ahead=4)
            congestion_risk = sum(1 for p in pred if p['predicted_vehicles'] > threshold) / len(pred)
            
            forecasts[lane] = {
                'congestion_risk': round(congestion_risk * 100, 1),
                'max_expected': max(p['predicted_vehicles'] for p in pred),
                'avg_expected': int(np.mean([p['predicted_vehicles'] for p in pred])),
                'predictions': pred
            }
        
        return forecasts


class SmartTrafficOptimizer:
    """Uses predictions to optimize signal timing"""
    
    def __init__(self, predictor):
        self.predictor = predictor
    
    def get_recommended_timing(self, lane, next_hour_forecast):
        """Recommend signal timing based on predictions"""
        if not next_hour_forecast:
            return 25  # Default 25 seconds
        
        predicted_vehicles = next_hour_forecast[0]['predicted_vehicles']
        
        # Adaptive timing formula
        total_vehicles = 200  # Assume standard 4-way intersection
        green_time = int((predicted_vehicles / total_vehicles) * 80)
        green_time = max(10, min(60, green_time))  # Constrain 10-60 seconds
        
        return green_time
    
    def get_optimization_recommendations(self, junction_data):
        """Get overall optimization recommendations"""
        lanes = ['North', 'East', 'South', 'West']
        recommendations = []
        
        for lane in lanes:
            forecast = self.predictor.predict_next_hours(lane, hours_ahead=2)
            if forecast and forecast[0]['predicted_vehicles'] > 60:
                recommendations.append(f"Consider extending {lane} lane green time in next hour")
        
        peak_info = self.predictor.get_peak_hours_prediction()
        if peak_info['current_trend'] == 'high':
            recommendations.append("Current traffic is high - coordinate with neighboring junctions")
        
        return recommendations
