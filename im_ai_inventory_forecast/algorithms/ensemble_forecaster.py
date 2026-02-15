# -*- coding: utf-8 -*-

"""Ensemble forecaster combining multiple algorithms"""

from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class EnsembleForecaster:
    def __init__(self, config):
        self.config = config
        self.forecasters = []
        self.weights = [0.6, 0.4]  # Prophet 60%, ARIMA 40%
    
    def fit(self, historical_data):
        """Train all models"""
        try:
            from .prophet_forecaster import ProphetForecaster
            prophet = ProphetForecaster(self.config)
            prophet.fit(historical_data)
            self.forecasters.append(prophet)
        except Exception as e:
            _logger.warning(f"Prophet failed: {e}")
        
        try:
            from .arima_forecaster import ARIMAForecaster
            arima = ARIMAForecaster(self.config)
            arima.fit(historical_data)
            self.forecasters.append(arima)
        except Exception as e:
            _logger.warning(f"ARIMA failed: {e}")
        
        if not self.forecasters:
            raise ValueError("No forecasters available")
        
        return self
    
    def predict(self, horizon_days):
        """Combine predictions from all models"""
        all_predictions = []
        
        for forecaster in self.forecasters:
            try:
                preds = forecaster.predict(horizon_days)
                all_predictions.append(preds)
            except Exception as e:
                _logger.warning(f"Prediction failed: {e}")
        
        if not all_predictions:
            return []
        
        # Combine with weights
        combined = []
        for i in range(horizon_days):
            weighted_demand = 0
            weighted_lower = 0
            weighted_upper = 0
            
            for j, preds in enumerate(all_predictions):
                if i < len(preds):
                    weight = self.weights[j] if j < len(self.weights) else 1.0 / len(all_predictions)
                    weighted_demand += preds[i]['predicted_demand'] * weight
                    weighted_lower += preds[i]['lower_bound'] * weight
                    weighted_upper += preds[i]['upper_bound'] * weight
            
            combined.append({
                'date': all_predictions[0][i]['date'],
                'predicted_demand': weighted_demand,
                'lower_bound': weighted_lower,
                'upper_bound': weighted_upper,
                'seasonality': True,
                'is_anomaly': False,
                'accuracy': 0.0,
            })
        
        return combined
