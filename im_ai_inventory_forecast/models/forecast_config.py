# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ForecastConfig(models.Model):
    _name = 'forecast.config'
    _description = 'Forecast Configuration'
    _order = 'sequence, name'

    name = fields.Char(string='Configuration Name', required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    
    # Algorithm settings
    algorithm = fields.Selection([('prophet', 'Prophet (Facebook)'),('arima', 'ARIMA'),('ensemble', 'Ensemble Method'), ], string='Algorithm', required=True, default='ensemble', help='Machine Learning algorithm to use for forecasting')
    
    # Forecast parameters
    forecast_horizon = fields.Integer(string='Forecast Horizon (days)', default=90,required=True, help='Number of days to forecast into the future')
    confidence_level = fields.Float(string='Confidence Level', default=0.95, required=True, help='Confidence level for prediction intervals (0.90 = 90%, 0.95 = 95%)')
    min_history_days = fields.Integer(string='Minimum History (days)', default=90, required=True, help='Minimum number of historical days required to generate forecast')
    
    # Seasonality
    enable_seasonality  = fields.Boolean(string='Detect Seasonality', default=True, help='Automatically detect and model seasonal patterns')
    enable_holidays     = fields.Boolean(string='Include Holidays', default=True, help='Consider holidays and special events in forecasting')
    
    # Retraining
    retrain_frequency   = fields.Selection([('daily', 'Daily'),('weekly', 'Weekly'),('monthly', 'Monthly'),], string='Retrain Frequency', default='weekly', help='How often to retrain the ML models')
    
    # Alert thresholds
    stockout_threshold_days = fields.Integer(string='Stockout Alert (days)',default=7,help='Alert when stockout predicted within X days')
    overstock_ratio         = fields.Float(string='Overstock Ratio',default=2.0,help='Alert when stock > X times predicted demand')
    
    # Advanced settings
    parallel_processing     = fields.Boolean(string='Enable Parallel Processing',default=False, help='Use multiple cores for faster computation (for 1000+ products)')
    
    # Statistics
    total_predictions   = fields.Integer(string='Total Predictions', compute='_compute_statistics', help='Number of predictions generated with this config')
    average_accuracy    = fields.Float(string='Average Accuracy (MAPE)', compute='_compute_statistics', help='Average accuracy score across all predictions')
    
    company_id          = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)
    


    @api.constrains('confidence_level')
    def _check_confidence_level(self):
        for record in self:
            if not 0.80 <= record.confidence_level <= 0.99:
                raise ValidationError(_('Confidence level must be between 0.80 and 0.99'))
    
    @api.constrains('forecast_horizon')
    def _check_forecast_horizon(self):
        for record in self:
            if record.forecast_horizon < 7 or record.forecast_horizon > 365:
                raise ValidationError(_('Forecast horizon must be between 7 and 365 days'))
    
    @api.constrains('min_history_days')
    def _check_min_history(self):
        for record in self:
            if record.min_history_days < 30:
                raise ValidationError(_('Minimum history must be at least 30 days'))
    
    def _compute_statistics(self):
        for record in self:
            predictions = self.env['forecast.prediction'].search([
                ('config_id', '=', record.id)
            ])
            record.total_predictions = len(predictions)
            
            if predictions:
                accuracies = predictions.filtered(lambda p: p.accuracy_score > 0)
                if accuracies:
                    record.average_accuracy = sum(accuracies.mapped('accuracy_score')) / len(accuracies)
                else:
                    record.average_accuracy = 0.0
            else:
                record.average_accuracy = 0.0
    
    def action_test_configuration(self):
        """Test if ML libraries are properly installed"""
        self.ensure_one()
        
        errors = []
        
        # Test Prophet
        try:
            from prophet import Prophet
            _logger.info("Prophet library OK")
        except ImportError:
            errors.append("Prophet library not installed. Run: pip install prophet")
        
        # Test ARIMA
        try:
            import pmdarima
            _logger.info("pmdarima library OK")
        except ImportError:
            errors.append("pmdarima library not installed. Run: pip install pmdarima")
        
        # Test statsmodels
        try:
            import statsmodels
            _logger.info("statsmodels library OK")
        except ImportError:
            errors.append("statsmodels library not installed. Run: pip install statsmodels")
        
        if errors:
            raise ValidationError(_("Missing dependencies:\n\n") + "\n".join(errors))
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Configuration Test Successful'),
                'message': _('All ML libraries are properly installed and ready to use!'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def name_get(self):
        result = []
        for record in self:
            name = f"{record.name} ({record.algorithm})"
            result.append((record.id, name))
        return result
