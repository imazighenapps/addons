# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Smart button counts
    forecast_count = fields.Integer(
        string='Forecasts',
        compute='_compute_forecast_count'
    )
    alert_count = fields.Integer(
        string='Alerts',
        compute='_compute_alert_count'
    )
    
    # Latest prediction
    next_predicted_demand = fields.Float(
        string='Next 7-Day Demand',
        compute='_compute_next_demand',
        help='Predicted demand for next 7 days'
    )
    
    def _compute_forecast_count(self):
        for product in self:
            product.forecast_count = self.env['forecast.prediction'].search_count([
                ('product_id', '=', product.id),
                ('date', '>=', fields.Date.today())
            ])
    
    def _compute_alert_count(self):
        for product in self:
            product.alert_count = self.env['forecast.alert'].search_count([
                ('product_id', '=', product.id),
                ('status', 'in', ['new', 'acknowledged'])
            ])
    
    def _compute_next_demand(self):
        today = fields.Date.today()
        end_date = fields.Date.add(today, days=7)
        
        for product in self:
            predictions = self.env['forecast.prediction'].search([
                ('product_id', '=', product.id),
                ('date', '>=', today),
                ('date', '<=', end_date)
            ])
            
            product.next_predicted_demand = sum(predictions.mapped('predicted_demand'))
    
    def action_view_forecasts(self):
        """Open forecast predictions for this product"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Forecasts - {self.name}',
            'res_model': 'forecast.prediction',
            'view_mode': 'list,form,graph',
            'domain': [('product_id', '=', self.id)],
            'context': {'default_product_id': self.id},
        }
    
    def action_view_alerts(self):
        """Open alerts for this product"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Alerts - {self.name}',
            'res_model': 'forecast.alert',
            'view_mode': 'list,form',
            'domain': [('product_id', '=', self.id)],
            'context': {'default_product_id': self.id},
        }
    
    def action_generate_forecast(self):
        """Quick action to generate forecast for this product"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generate Forecast',
            'res_model': 'generate.forecast.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_product_ids': [(6, 0, [self.id])]},
        }
