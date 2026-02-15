# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ForecastPrediction(models.Model):
    _name = 'forecast.prediction'
    _description = 'Forecast Prediction'
    _order = 'date desc, product_id'
    _rec_name = 'product_id'

    # Core fields
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        ondelete='cascade',
        index=True
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        ondelete='cascade',
        index=True
    )
    date = fields.Date(string='Forecast Date', required=True, index=True)
    
    # Prediction values
    predicted_demand = fields.Float(
        string='Predicted Demand',
        digits='Product Unit of Measure'
    )
    confidence_lower = fields.Float(
        string='Lower Bound',
        digits='Product Unit of Measure'
    )
    confidence_upper = fields.Float(
        string='Upper Bound',
        digits='Product Unit of Measure'
    )
    confidence_interval = fields.Float(string='Confidence %', default=95.0)
    
    # Metadata
    algorithm_used = fields.Selection([
        ('prophet', 'Prophet'),
        ('arima', 'ARIMA'),
        ('ensemble', 'Ensemble'),
    ], string='Algorithm', default='prophet')
    
    accuracy_score = fields.Float(string='Accuracy (MAPE)')
    is_anomaly = fields.Boolean(string='Anomaly Detected')
    
    trend = fields.Selection([
        ('increasing', 'Increasing'),
        ('decreasing', 'Decreasing'),
        ('stable', 'Stable'),
    ], string='Trend', compute='_compute_trend', store=True)
    
    seasonality_detected = fields.Boolean(string='Seasonality')
    model_version = fields.Char(string='Model Version')
    computation_time = fields.Float(string='Computation Time (s)')
    
    # Computed fields
    actual_demand = fields.Float(
        string='Actual Demand',
        compute='_compute_actual_demand',
        store=True
    )
    error_percentage = fields.Float(
        string='Error %',
        compute='_compute_error',
        store=True
    )
    
    # Current stock
    current_stock = fields.Float(
        string='Current Stock',
        compute='_compute_current_stock'
    )
    
    # Relations
    config_id = fields.Many2one('forecast.config', string='Configuration')
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        required=True
    )
    active = fields.Boolean(default=True)
    
    _sql_constraints = [
        ('unique_prediction',
         'UNIQUE(product_id, warehouse_id, date, company_id)',
         'Only one prediction per product/warehouse/date allowed!')
    ]
    
    @api.depends('predicted_demand')
    def _compute_trend(self):
        for record in self:
            if not record.predicted_demand:
                record.trend = 'stable'
                continue
            
            # Get recent predictions
            domain = [
                ('product_id', '=', record.product_id.id),
                ('date', '<', record.date),
                ('date', '>=', fields.Date.subtract(record.date, days=30))
            ]
            if record.warehouse_id:
                domain.append(('warehouse_id', '=', record.warehouse_id.id))
            
            previous = self.search(domain, order='date desc', limit=5)
            
            if len(previous) < 2:
                record.trend = 'stable'
                continue
            
            avg_demand = sum(previous.mapped('predicted_demand')) / len(previous)
            
            if record.predicted_demand > avg_demand * 1.2:
                record.trend = 'increasing'
            elif record.predicted_demand < avg_demand * 0.8:
                record.trend = 'decreasing'
            else:
                record.trend = 'stable'
    
    @api.depends('date', 'product_id', 'warehouse_id')
    def _compute_actual_demand(self):
        for record in self:
            if record.date > fields.Date.today():
                record.actual_demand = 0.0
                continue
            
            # Get actual sales/consumption
            domain = [
                ('product_id', '=', record.product_id.id),
                ('date', '>=', record.date),
                ('date', '<', fields.Date.add(record.date, days=1)),
                ('state', '=', 'done'),
            ]
            
            # Outgoing moves only
            moves = self.env['stock.move'].search(domain)
            outgoing = moves.filtered(
                lambda m: m.location_id.usage == 'internal' and 
                         m.location_dest_id.usage != 'internal'
            )
            
            record.actual_demand = sum(outgoing.mapped('product_qty'))
    
    @api.depends('predicted_demand', 'actual_demand')
    def _compute_error(self):
        for record in self:
            if record.actual_demand and record.predicted_demand:
                error = abs(record.predicted_demand - record.actual_demand)
                record.error_percentage = (error / (record.actual_demand + 0.001)) * 100
            else:
                record.error_percentage = 0.0
    
    def _compute_current_stock(self):
        for record in self:
            if record.warehouse_id:
                location = record.warehouse_id.lot_stock_id
                quant = self.env['stock.quant'].search([
                    ('product_id', '=', record.product_id.id),
                    ('location_id', '=', location.id)
                ], limit=1)
                record.current_stock = quant.quantity if quant else 0.0
            else:
                record.current_stock = record.product_id.qty_available
    
    @api.model
    def generate_predictions(self, product_ids=None, warehouse_ids=None, config_id=None):
        """
        Generate forecasts for products
        
        Args:
            product_ids: list of product IDs (None = all)
            warehouse_ids: list of warehouse IDs (None = all)
            config_id: configuration ID (None = default active config)
        
        Returns:
            dict with results
        """
        if not config_id:
            config = self.env['forecast.config'].search([('active', '=', True)], limit=1)
            if not config:
                raise UserError(_('No active forecast configuration found. Please create one first.'))
        else:
            config = self.env['forecast.config'].browse(config_id)
        
        if not product_ids:
            # Get all stockable products with sales history
            products = self.env['product.product'].search([
                ('type', '=', 'product'),
                ('sale_ok', '=', True)
            ], limit=100)  # Limit for safety
            product_ids = products.ids
        
        if not warehouse_ids:
            warehouses = self.env['stock.warehouse'].search([])
            warehouse_ids = warehouses.ids
        
        # Import forecasting engine
        from ..algorithms.forecast_engine import ForecastEngine
        
        engine = ForecastEngine(config)
        results = {
            'success': 0,
            'failed': 0,
            'total': len(product_ids) * len(warehouse_ids),
            'errors': []
        }
        
        for product_id in product_ids:
            for warehouse_id in warehouse_ids:
                try:
                    # Generate predictions for this product-warehouse combo
                    predictions = engine.generate_forecast(product_id, warehouse_id)
                    
                    # Save predictions
                    for pred in predictions:
                        self.create({
                            'product_id': product_id,
                            'warehouse_id': warehouse_id,
                            'date': pred['date'],
                            'predicted_demand': pred['predicted_demand'],
                            'confidence_lower': pred['lower_bound'],
                            'confidence_upper': pred['upper_bound'],
                            'confidence_interval': config.confidence_level * 100,
                            'algorithm_used': config.algorithm,
                            'accuracy_score': pred.get('accuracy', 0.0),
                            'is_anomaly': pred.get('is_anomaly', False),
                            'seasonality_detected': pred.get('seasonality', False),
                            'model_version': '1.0',
                            'computation_time': pred.get('computation_time', 0.0),
                            'config_id': config.id,
                        })
                    
                    results['success'] += 1
                    
                except Exception as e:
                    _logger.error(f"Failed to generate forecast for product {product_id}: {str(e)}")
                    results['failed'] += 1
                    results['errors'].append(str(e))
        
        return results
    
    def action_create_alert(self):
        """Create alert for this prediction"""
        self.ensure_one()
        
        # Determine alert type and severity
        if self.is_anomaly:
            alert_type = 'anomaly'
            severity = 'high'
            message = f'Anomaly detected in forecast for {self.product_id.name}'
        elif self.trend == 'increasing':
            alert_type = 'trend'
            severity = 'medium'
            message = f'Increasing demand trend for {self.product_id.name}'
        else:
            alert_type = 'trend'
            severity = 'low'
            message = f'Forecast generated for {self.product_id.name}'
        
        self.env['forecast.alert'].create({
            'product_id': self.product_id.id,
            'warehouse_id': self.warehouse_id.id if self.warehouse_id else False,
            'alert_type': alert_type,
            'severity': severity,
            'message': message,
            'date_detection': fields.Datetime.now(),
            'date_expected': self.date,
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Alert Created'),
                'message': message,
                'type': 'success',
            }
        }
    
    @api.model
    def cleanup_old_predictions(self, days=365):
        """Archive old predictions (called by cron)"""
        cutoff = fields.Date.subtract(fields.Date.today(), days=days)
        old = self.search([('date', '<', cutoff)])
        old.write({'active': False})
        _logger.info(f'Archived {len(old)} old predictions')
        return True
