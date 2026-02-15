# -*- coding: utf-8 -*-

"""Prophet-based forecasting"""

from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

try:
    from prophet import Prophet
    import pandas as pd
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    _logger.warning("Prophet not installed")


class ProphetForecaster:
    def __init__(self, config):
        if not PROPHET_AVAILABLE:
            raise ImportError("Prophet library required")
        self.config = config
        self.model = None
        self.forecast = None
    
    def fit(self, historical_data):
        """Train model on historical data"""
        df = pd.DataFrame(historical_data)
        df = df.rename(columns={'date': 'ds', 'demand': 'y'})
        df['ds'] = pd.to_datetime(df['ds'])
        
        self.model = Prophet(
            yearly_seasonality=self.config.enable_seasonality,
            weekly_seasonality=self.config.enable_seasonality,
            daily_seasonality=False,
            interval_width=self.config.confidence_level
        )
        
        self.model.fit(df)
        return self
    
    def predict(self, horizon_days):
        """Generate predictions"""
        if not self.model:
            raise ValueError("Model not trained")
        
        future = self.model.make_future_dataframe(periods=horizon_days)
        self.forecast = self.model.predict(future)
        
        # Extract future predictions only
        today = datetime.now().date()
        predictions = []
        
        for _, row in self.forecast.iterrows():
            pred_date = row['ds'].date()
            if pred_date > today:
                predictions.append({
                    'date': pred_date,
                    'predicted_demand': max(0, row['yhat']),
                    'lower_bound': max(0, row['yhat_lower']),
                    'upper_bound': max(0, row['yhat_upper']),
                    'seasonality': self.config.enable_seasonality,
                    'is_anomaly': False,
                    'accuracy': 0.0,
                })
        
        return predictions[:horizon_days]
