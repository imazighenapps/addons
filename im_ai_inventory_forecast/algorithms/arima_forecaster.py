# -*- coding: utf-8 -*-

"""ARIMA-based forecasting"""

from datetime import datetime, timedelta
import logging
import numpy as np

_logger = logging.getLogger(__name__)

try:
    from pmdarima import auto_arima
    import pandas as pd
    ARIMA_AVAILABLE = True
except ImportError:
    ARIMA_AVAILABLE = False
    _logger.warning("pmdarima not installed")


class ARIMAForecaster:
    def __init__(self, config):
        if not ARIMA_AVAILABLE:
            raise ImportError("pmdarima library required")
        self.config = config
        self.model = None
    
    def fit(self, historical_data):
        """Train ARIMA model"""
        df = pd.DataFrame(historical_data)
        y = df['demand'].values
        
        self.model = auto_arima(
            y,
            seasonal=self.config.enable_seasonality,
            m=7 if self.config.enable_seasonality else 1,
            suppress_warnings=True,
            error_action='ignore'
        )
        
        return self
    
    def predict(self, horizon_days):
        """Generate predictions"""
        if not self.model:
            raise ValueError("Model not trained")
        
        forecast, conf_int = self.model.predict(
            n_periods=horizon_days,
            return_conf_int=True,
            alpha=1 - self.config.confidence_level
        )
        
        today = datetime.now().date()
        predictions = []
        
        for i in range(horizon_days):
            predictions.append({
                'date': today + timedelta(days=i+1),
                'predicted_demand': max(0, forecast[i]),
                'lower_bound': max(0, conf_int[i, 0]),
                'upper_bound': max(0, conf_int[i, 1]),
                'seasonality': False,
                'is_anomaly': False,
                'accuracy': 0.0,
            })
        
        return predictions
