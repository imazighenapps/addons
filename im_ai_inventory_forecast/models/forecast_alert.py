# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ForecastAlert(models.Model):
    _name = 'forecast.alert'
    _description = 'Forecast Alert'
    _order = 'date_detection desc, severity desc'
    _rec_name = 'message'

    product_id          = fields.Many2one('product.product', string='Product', required=True, ondelete='cascade')
    warehouse_id        = fields.Many2one('stock.warehouse',string='Warehouse',ondelete='cascade')
    alert_type          = fields.Selection([('stockout', 'Stockout Risk'),('overstock', 'Overstock'),('anomaly', 'Demand Anomaly'),('trend', 'Trend Change'),], string='Alert Type', required=True, default='stockout')
    severity            = fields.Selection([('low', 'Low'),('medium', 'Medium'),('high', 'High'),('critical', 'Critical'),], string='Severity', required=True, default='medium')
    message             = fields.Text(string='Message', required=True)
    recommended_action  = fields.Text(string='Recommended Action')
    estimated_impact    = fields.Float(string='Estimated Impact ($)',help='Estimated financial impact if not addressed')
    date_detection      = fields.Datetime(string='Detection Date', default=fields.Datetime.now, required=True)
    date_expected       = fields.Date(string='Expected Date',help='When the issue is expected to occur')
    status              = fields.Selection([('user', 'New'),('admin', 'Acknowledged'),('resolved', 'Resolved'),('ignored', 'Ignored'),], string='Status', default='new', required=True, tracking=True)
    assigned_to         = fields.Many2one('res.users', string='Assigned To', help='User responsible for handling this alert')
    
    # Actions taken
    purchase_order_id   = fields.Many2one('purchase.order', string='Purchase Order', help='PO created to address this alert')
    sale_order_id       = fields.Many2one('sale.order', string='Sale Order', help='Related sale order')
    notes               = fields.Text(string='Notes')
    company_id          = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    active              = fields.Boolean(default=True)
    
    # Computed
    days_until_event = fields.Integer(string='Days Until Event', compute='_compute_days_until')
    color            = fields.Integer(compute='_compute_color')
    

    def action_view_product(self):
        pass



    @api.depends('date_expected')
    def _compute_days_until(self):
        today = fields.Date.today()
        for record in self:
            if record.date_expected:
                delta = (record.date_expected - today).days
                record.days_until_event = delta
            else:
                record.days_until_event = 0
    
    def _compute_color(self):
        """Color for kanban view"""
        for record in self:
            if record.severity == 'critical':
                record.color = 1  # Red
            elif record.severity == 'high':
                record.color = 3  # Orange
            elif record.severity == 'medium':
                record.color = 4  # Yellow
            else:
                record.color = 10  # Gray
    
    @api.model
    def check_and_create_alerts(self):
        """
        Check predictions and create alerts (called by cron)
        """
        today = fields.Date.today()
        config = self.env['forecast.config'].search([('active', '=', True)], limit=1)
        
        if not config:
            _logger.warning("No active forecast configuration")
            return
        
        # Get upcoming predictions
        predictions = self.env['forecast.prediction'].search([
            ('date', '>=', today),
            ('date', '<=', fields.Date.add(today, days=config.stockout_threshold_days))
        ])
        
        alerts_created = 0
        
        for pred in predictions:
            # Check for stockout
            if pred.current_stock < pred.predicted_demand:
                shortage = pred.predicted_demand - pred.current_stock
                
                # Check if alert already exists
                existing = self.search([
                    ('product_id', '=', pred.product_id.id),
                    ('warehouse_id', '=', pred.warehouse_id.id if pred.warehouse_id else False),
                    ('alert_type', '=', 'stockout'),
                    ('status', 'in', ['new', 'acknowledged']),
                    ('date_expected', '=', pred.date)
                ])
                
                if not existing:
                    self.create({
                        'product_id': pred.product_id.id,
                        'warehouse_id': pred.warehouse_id.id if pred.warehouse_id else False,
                        'alert_type': 'stockout',
                        'severity': 'critical' if shortage > pred.predicted_demand * 0.5 else 'high',
                        'message': f'Stockout risk for {pred.product_id.name} on {pred.date}. '
                                  f'Current stock: {pred.current_stock:.0f}, '
                                  f'Predicted demand: {pred.predicted_demand:.0f}',
                        'recommended_action': f'Order {shortage:.0f} units immediately. '
                                            f'Lead time consideration required.',
                        'estimated_impact': shortage * pred.product_id.list_price,
                        'date_expected': pred.date,
                    })
                    alerts_created += 1
            
            # Check for overstock
            if pred.current_stock > pred.predicted_demand * config.overstock_ratio:
                excess = pred.current_stock - pred.predicted_demand
                
                existing = self.search([
                    ('product_id', '=', pred.product_id.id),
                    ('warehouse_id', '=', pred.warehouse_id.id if pred.warehouse_id else False),
                    ('alert_type', '=', 'overstock'),
                    ('status', 'in', ['new', 'acknowledged'])
                ], limit=1)
                
                if not existing:
                    self.create({
                        'product_id': pred.product_id.id,
                        'warehouse_id': pred.warehouse_id.id if pred.warehouse_id else False,
                        'alert_type': 'overstock',
                        'severity': 'medium',
                        'message': f'Overstock for {pred.product_id.name}. '
                                  f'Current: {pred.current_stock:.0f}, '
                                  f'Predicted need: {pred.predicted_demand:.0f}',
                        'recommended_action': f'Consider promotion or reduce ordering. '
                                            f'Excess: {excess:.0f} units',
                        'estimated_impact': excess * pred.product_id.standard_price * 0.1,  # 10% holding cost
                        'date_expected': pred.date,
                    })
                    alerts_created += 1
            
            # Check for anomalies
            if pred.is_anomaly:
                existing = self.search([
                    ('product_id', '=', pred.product_id.id),
                    ('alert_type', '=', 'anomaly'),
                    ('date_expected', '=', pred.date),
                    ('status', 'in', ['new', 'acknowledged'])
                ])
                
                if not existing:
                    self.create({
                        'product_id': pred.product_id.id,
                        'warehouse_id': pred.warehouse_id.id if pred.warehouse_id else False,
                        'alert_type': 'anomaly',
                        'severity': 'high',
                        'message': f'Demand anomaly detected for {pred.product_id.name}',
                        'recommended_action': 'Investigate cause: promotion, seasonality, or data error',
                        'date_expected': pred.date,
                    })
                    alerts_created += 1
        
        _logger.info(f'Created {alerts_created} new alerts')
        return alerts_created
    
    def action_acknowledge(self):
        """Mark alert as acknowledged"""
        self.write({'status': 'acknowledged'})
        return True
    
    def action_resolve(self):
        """Mark alert as resolved"""
        self.write({'status': 'resolved'})
        return True
    
    def action_ignore(self):
        """Ignore this alert"""
        self.write({'status': 'ignored'})
        return True
    
    def action_create_purchase_order(self):
        """Create purchase order to address stockout"""
        self.ensure_one()
        
        if self.alert_type != 'stockout':
            raise UserError(_('Can only create PO for stockout alerts'))
        
        # Get preferred supplier
        supplier_info = self.env['product.supplierinfo'].search([
            ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)
        ], limit=1, order='sequence')
        
        if not supplier_info:
            raise UserError(_('No supplier configured for this product'))
        
        # Calculate order quantity
        qty_needed = self.product_id.with_context(
            warehouse=self.warehouse_id.id if self.warehouse_id else False
        ).virtual_available
        
        po = self.env['purchase.order'].create({
            'partner_id': supplier_info.partner_id.id,
            'order_line': [(0, 0, {
                'product_id': self.product_id.id,
                'product_qty': abs(qty_needed) if qty_needed < 0 else supplier_info.min_qty,
                'price_unit': supplier_info.price,
                'date_planned': fields.Datetime.now(),
            })]
        })
        
        self.write({
            'purchase_order_id': po.id,
            'status': 'resolved'
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': po.id,
            'view_mode': 'form',
            'target': 'current',
        }
