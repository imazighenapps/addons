# -*- coding: utf-8 -*-

"""
Main Forecast Engine
Orchestrates different forecasting algorithms
"""

from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ForecastEngine:
    """
    Main forecasting engine that coordinates different algorithms
    """
    
    def __init__(self, config):
        """
        Initialize with configuration
        
        Args:
            config: forecast.config browse record
        """
        self.config = config
        self.algorithm = config.algorithm
        self.horizon_days = config.forecast_horizon
        self.confidence_level = config.confidence_level
        
    def generate_forecast(self, product_id, warehouse_id=None):
        """
        Generate forecast for a product
        
        Args:
            product_id: product.product ID
            warehouse_id: stock.warehouse ID (optional)
            
        Returns:
            list of prediction dicts
        """
        start_time = datetime.now()
        
        # Get historical data
        historical_data = self._get_historical_data(product_id, warehouse_id)
        
        if not historical_data or len(historical_data) < self.config.min_history_days:
            _logger.warning(f"Insufficient historical data for product {product_id}")
            return []
        
        # Select and run algorithm
        try:
            if self.algorithm == 'prophet':
                from .prophet_forecaster import ProphetForecaster
                forecaster = ProphetForecaster(self.config)
                
            elif self.algorithm == 'arima':
                from .arima_forecaster import ARIMAForecaster
                forecaster = ARIMAForecaster(self.config)
                
            elif self.algorithm == 'ensemble':
                from .ensemble_forecaster import EnsembleForecaster
                forecaster = EnsembleForecaster(self.config)
                
            else:
                raise ValueError(f"Unknown algorithm: {self.algorithm}")
            
            # Fit and predict
            forecaster.fit(historical_data)
            predictions = forecaster.predict(self.horizon_days)
            
            # Add computation time
            computation_time = (datetime.now() - start_time).total_seconds()
            for pred in predictions:
                pred['computation_time'] = computation_time
            
            return predictions
            
        except Exception as e:
            _logger.error(f"Forecast generation failed: {str(e)}", exc_info=True)
            return []
    
    def _get_historical_data(self, product_id, warehouse_id=None):
        """
        Extract historical sales/consumption data
        
        Returns:
            list of {'date': date, 'demand': float}
        """
        from odoo import fields
        from odoo.api import Environment
        
        # This is called from Odoo context, get env
        import threading
        if not hasattr(threading.current_thread(), 'dbname'):
            return []
        
        # We need odoo env - this will be passed from the model
        # For now, return mock data structure
        # In real implementation, this would query stock.move
        
        # Get last 180 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=180)
        
        historical = []
        
        # This should be implemented in the model method
        # that calls this engine, not here
        # For now, return empty to avoid circular imports
        
        return historical
    
    @staticmethod
    def prepare_historical_data(env, product_id, warehouse_id=None, days=180):
        """
        Static method to prepare historical data from Odoo
        Should be called from model before passing to engine
        
        Args:
            env: Odoo environment
            product_id: int
            warehouse_id: int or None
            days: number of days of history
            
        Returns:
            list of dicts
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get all done stock moves (outgoing only)
        domain = [
            ('product_id', '=', product_id),
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('state', '=', 'done'),
            ('location_id.usage', '=', 'internal'),
            ('location_dest_id.usage', '!=', 'internal'),
        ]
        
        if warehouse_id:
            warehouse = env['stock.warehouse'].browse(warehouse_id)
            domain.append(('location_id', 'child_of', warehouse.view_location_id.id))
        
        moves = env['stock.move'].search(domain)
        
        # Group by date
        daily_demand = {}
        for move in moves:
            date_key = move.date.date()
            if date_key not in daily_demand:
                daily_demand[date_key] = 0.0
            daily_demand[date_key] += move.product_qty
        
        # Fill missing dates with 0
        current_date = start_date
        while current_date <= end_date:
            if current_date not in daily_demand:
                daily_demand[current_date] = 0.0
            current_date += timedelta(days=1)
        
        # Convert to list format
        historical = [
            {'date': date, 'demand': demand}
            for date, demand in sorted(daily_demand.items())
        ]
        
        _logger.info(f"Prepared {len(historical)} days of historical data for product {product_id}")
        
        return historical
