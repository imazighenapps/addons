# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GenerateForecastWizard(models.TransientModel):
    _name = 'generate.forecast.wizard'
    _description = 'Generate Forecast Wizard'

    product_ids = fields.Many2many('product.product', string='Products')
    warehouse_ids = fields.Many2many('stock.warehouse', string='Warehouses')
    config_id = fields.Many2one('forecast.config', string='Configuration', required=True)
    all_products = fields.Boolean(string='All Products', default=False)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        config = self.env['forecast.config'].search([('active', '=', True)], limit=1)
        if config:
            res['config_id'] = config.id
        warehouses = self.env['stock.warehouse'].search([])
        res['warehouse_ids'] = [(6, 0, warehouses.ids)]
        return res

    def action_generate(self):
        self.ensure_one()
        
        product_ids = self.product_ids.ids if not self.all_products else None
        warehouse_ids = self.warehouse_ids.ids
        
        # Call generate method
        from ..algorithms.forecast_engine import ForecastEngine
        
        # Prepare data and generate
        total = 0
        for product in (self.product_ids if not self.all_products else self.env['product.product'].search([('type', '=', 'product')], limit=50)):
            for warehouse in self.warehouse_ids:
                historical = ForecastEngine.prepare_historical_data(
                    self.env, product.id, warehouse.id
                )
                
                if len(historical) >= self.config_id.min_history_days:
                    engine = ForecastEngine(self.config_id)
                    predictions = engine.generate_forecast(product.id, warehouse.id)
                    
                    for pred in predictions:
                        self.env['forecast.prediction'].create({
                            'product_id': product.id,
                            'warehouse_id': warehouse.id,
                            'date': pred['date'],
                            'predicted_demand': pred['predicted_demand'],
                            'confidence_lower': pred['lower_bound'],
                            'confidence_upper': pred['upper_bound'],
                            'algorithm_used': self.config_id.algorithm,
                            'config_id': self.config_id.id,
                        })
                    total += len(predictions)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Forecasts Generated'),
                'message': _('%d predictions created successfully!') % total,
                'type': 'success',
            }
        }
