# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from datetime import datetime, timedelta


class TestForecasting(TransactionCase):
    
    def setUp(self):
        super().setUp()
        
        # Create test product
        self.product = self.env['product.product'].create({
            'name': 'Test Product AI Forecast',
            'type': 'product',
            'list_price': 100.0,
            'standard_price': 50.0,
        })
        
        # Create test warehouse
        self.warehouse = self.env['stock.warehouse'].search([], limit=1)
        
        # Create test configuration
        self.config = self.env['forecast.config'].create({
            'name': 'Test Configuration',
            'algorithm': 'arima',  # Use ARIMA for faster tests
            'forecast_horizon': 30,
            'confidence_level': 0.95,
            'min_history_days': 30,
            'enable_seasonality': False,
            'enable_holidays': False,
        })
    
    def test_config_creation(self):
        """Test configuration creation"""
        self.assertTrue(self.config.id)
        self.assertEqual(self.config.algorithm, 'arima')
        self.assertEqual(self.config.forecast_horizon, 30)
    
    def test_prediction_creation(self):
        """Test prediction creation"""
        prediction = self.env['forecast.prediction'].create({
            'product_id': self.product.id,
            'warehouse_id': self.warehouse.id,
            'date': datetime.now().date() + timedelta(days=1),
            'predicted_demand': 100.0,
            'confidence_lower': 80.0,
            'confidence_upper': 120.0,
            'algorithm_used': 'arima',
            'config_id': self.config.id,
        })
        
        self.assertTrue(prediction.id)
        self.assertEqual(prediction.predicted_demand, 100.0)
    
    def test_alert_creation(self):
        """Test alert creation"""
        alert = self.env['forecast.alert'].create({
            'product_id': self.product.id,
            'warehouse_id': self.warehouse.id,
            'alert_type': 'stockout',
            'severity': 'high',
            'message': 'Test alert',
            'status': 'new',
        })
        
        self.assertTrue(alert.id)
        self.assertEqual(alert.status, 'new')
    
    def test_alert_acknowledge(self):
        """Test alert acknowledgement"""
        alert = self.env['forecast.alert'].create({
            'product_id': self.product.id,
            'alert_type': 'stockout',
            'severity': 'high',
            'message': 'Test',
            'status': 'new',
        })
        
        alert.action_acknowledge()
        self.assertEqual(alert.status, 'acknowledged')
    
    def test_reorder_creation(self):
        """Test reorder rule creation"""
        reorder = self.env['forecast.reorder'].create({
            'product_id': self.product.id,
            'warehouse_id': self.warehouse.id,
            'optimal_min_qty': 50.0,
            'optimal_max_qty': 200.0,
            'optimal_order_qty': 150.0,
            'safety_stock': 20.0,
            'lead_time_days': 7,
        })
        
        self.assertTrue(reorder.id)
        self.assertEqual(reorder.optimal_min_qty, 50.0)
    
    def test_product_forecast_count(self):
        """Test product forecast count"""
        # Create some predictions
        for i in range(5):
            self.env['forecast.prediction'].create({
                'product_id': self.product.id,
                'warehouse_id': self.warehouse.id,
                'date': datetime.now().date() + timedelta(days=i+1),
                'predicted_demand': 100.0,
                'algorithm_used': 'arima',
            })
        
        # Invalidate cache and recompute
        self.product.invalidate_recordset(['forecast_count'])
        self.assertEqual(self.product.forecast_count, 5)
