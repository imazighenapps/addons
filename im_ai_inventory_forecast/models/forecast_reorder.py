# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import math
import logging

_logger = logging.getLogger(__name__)


class ForecastReorder(models.Model):
    _name = 'forecast.reorder'
    _description = 'AI-Optimized Reorder Rules'
    _order = 'product_id, warehouse_id'

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        ondelete='cascade'
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        required=True,
        ondelete='cascade'
    )
    
    # Optimized quantities
    optimal_min_qty = fields.Float(
        string='Optimal Min Quantity',
        digits='Product Unit of Measure',
        help='AI-calculated minimum stock level'
    )
    optimal_max_qty = fields.Float(
        string='Optimal Max Quantity',
        digits='Product Unit of Measure',
        help='AI-calculated maximum stock level'
    )
    optimal_order_qty = fields.Float(
        string='Optimal Order Quantity',
        digits='Product Unit of Measure',
        help='Economic Order Quantity (EOQ)'
    )
    safety_stock = fields.Float(
        string='Safety Stock',
        digits='Product Unit of Measure',
        help='Buffer stock for demand variability'
    )
    
    # Parameters used
    lead_time_days = fields.Integer(
        string='Lead Time (days)',
        default=7,
        help='Supplier lead time in days'
    )
    service_level = fields.Float(
        string='Service Level (%)',
        default=95.0,
        help='Target service level percentage'
    )
    
    # Statistics
    avg_daily_demand = fields.Float(
        string='Avg Daily Demand',
        compute='_compute_statistics',
        store=True
    )
    demand_std_dev = fields.Float(
        string='Demand Std Dev',
        compute='_compute_statistics',
        store=True
    )
    
    last_computation = fields.Datetime(
        string='Last Computation',
        default=fields.Datetime.now
    )
    
    # Control
    auto_apply = fields.Boolean(
        string='Auto-Apply',
        default=False,
        help='Automatically apply these rules to Odoo reorder rules'
    )
    manual_override = fields.Boolean(
        string='Manual Override',
        help='User has manually adjusted these values'
    )
    
    # Current vs Optimal comparison
    current_min = fields.Float(
        string='Current Min',
        compute='_compute_current_rules'
    )
    current_max = fields.Float(
        string='Current Max',
        compute='_compute_current_rules'
    )
    improvement_potential = fields.Float(
        string='Improvement %',
        compute='_compute_improvement'
    )
    
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        required=True
    )
    active = fields.Boolean(default=True)
    
    _sql_constraints = [
        ('unique_reorder',
         'UNIQUE(product_id, warehouse_id, company_id)',
         'Only one reorder rule per product/warehouse!')
    ]
    
    @api.depends('product_id', 'warehouse_id')
    def _compute_statistics(self):
        """Calculate demand statistics from historical data"""
        for record in self:
            # Get last 90 days of sales
            date_from = fields.Date.subtract(fields.Date.today(), days=90)
            
            moves = self.env['stock.move'].search([
                ('product_id', '=', record.product_id.id),
                ('date', '>=', date_from),
                ('state', '=', 'done'),
                ('location_id.usage', '=', 'internal'),
                ('location_dest_id.usage', '!=', 'internal')
            ])
            
            if moves:
                # Group by date
                daily_demands = {}
                for move in moves:
                    date_key = move.date.date()
                    if date_key not in daily_demands:
                        daily_demands[date_key] = 0
                    daily_demands[date_key] += move.product_qty
                
                # Calculate statistics
                demands = list(daily_demands.values())
                if demands:
                    record.avg_daily_demand = sum(demands) / len(demands)
                    
                    # Standard deviation
                    if len(demands) > 1:
                        mean = record.avg_daily_demand
                        variance = sum((x - mean) ** 2 for x in demands) / len(demands)
                        record.demand_std_dev = math.sqrt(variance)
                    else:
                        record.demand_std_dev = 0
                else:
                    record.avg_daily_demand = 0
                    record.demand_std_dev = 0
            else:
                record.avg_daily_demand = 0
                record.demand_std_dev = 0
    
    def _compute_current_rules(self):
        """Get current Odoo reorder rules"""
        for record in self:
            rule = self.env['stock.warehouse.orderpoint'].search([
                ('product_id', '=', record.product_id.id),
                ('warehouse_id', '=', record.warehouse_id.id)
            ], limit=1)
            
            if rule:
                record.current_min = rule.product_min_qty
                record.current_max = rule.product_max_qty
            else:
                record.current_min = 0
                record.current_max = 0
    
    @api.depends('optimal_min_qty', 'current_min')
    def _compute_improvement(self):
        """Calculate improvement potential"""
        for record in self:
            if record.current_min and record.optimal_min_qty:
                improvement = abs(record.current_min - record.optimal_min_qty) / record.current_min * 100
                record.improvement_potential = improvement
            else:
                record.improvement_potential = 0
    
    @api.model
    def compute_optimal_rules(self, product_ids=None, warehouse_ids=None):
        """
        Calculate optimal reorder rules using AI predictions
        
        Formula:
        - Safety Stock = Z-score(service_level) × σ × √(Lead Time)
        - Min Qty = Avg Demand × Lead Time + Safety Stock
        - EOQ = √((2 × Annual Demand × Order Cost) / Holding Cost)
        - Max Qty = Min Qty + EOQ
        """
        if not product_ids:
            products = self.env['product.product'].search([
                ('type', '=', 'product'),
                ('sale_ok', '=', True)
            ], limit=100)
            product_ids = products.ids
        
        if not warehouse_ids:
            warehouses = self.env['stock.warehouse'].search([])
            warehouse_ids = warehouses.ids
        
        # Z-scores for service levels
        z_scores = {
            90.0: 1.28,
            95.0: 1.65,
            97.5: 1.96,
            99.0: 2.33,
            99.9: 3.09
        }
        
        created = 0
        
        for product_id in product_ids:
            product = self.env['product.product'].browse(product_id)
            
            for warehouse_id in warehouse_ids:
                # Check if rule exists
                existing = self.search([
                    ('product_id', '=', product_id),
                    ('warehouse_id', '=', warehouse_id)
                ])
                
                if existing:
                    rule = existing
                else:
                    rule = self.create({
                        'product_id': product_id,
                        'warehouse_id': warehouse_id,
                    })
                    created += 1
                
                # Get predictions for this product
                predictions = self.env['forecast.prediction'].search([
                    ('product_id', '=', product_id),
                    ('warehouse_id', '=', warehouse_id),
                    ('date', '>=', fields.Date.today())
                ], order='date', limit=30)
                
                if not predictions:
                    _logger.warning(f"No predictions for product {product_id}, using historical data only")
                    continue
                
                # Calculate average demand and std dev from predictions
                avg_demand = sum(predictions.mapped('predicted_demand')) / len(predictions)
                demands = predictions.mapped('predicted_demand')
                
                if len(demands) > 1:
                    variance = sum((x - avg_demand) ** 2 for x in demands) / len(demands)
                    std_dev = math.sqrt(variance)
                else:
                    std_dev = avg_demand * 0.2  # Assume 20% variability
                
                # Get lead time (from supplier or default)
                supplier = self.env['product.supplierinfo'].search([
                    ('product_tmpl_id', '=', product.product_tmpl_id.id)
                ], limit=1, order='sequence')
                
                lead_time = supplier.delay if supplier else 7  # Default 7 days
                
                # Calculate safety stock
                z_score = z_scores.get(rule.service_level, 1.65)  # Default 95%
                safety_stock = z_score * std_dev * math.sqrt(lead_time)
                
                # Calculate min quantity
                min_qty = (avg_demand * lead_time) + safety_stock
                
                # Calculate EOQ (Economic Order Quantity)
                annual_demand = avg_demand * 365
                order_cost = 50  # Estimated order cost in €
                holding_cost = product.standard_price * 0.2  # 20% annual holding cost
                
                if holding_cost > 0:
                    eoq = math.sqrt((2 * annual_demand * order_cost) / holding_cost)
                else:
                    eoq = avg_demand * 30  # Default: 1 month supply
                
                # Calculate max quantity
                max_qty = min_qty + eoq
                
                # Update rule
                rule.write({
                    'optimal_min_qty': max(0, min_qty),
                    'optimal_max_qty': max(0, max_qty),
                    'optimal_order_qty': max(0, eoq),
                    'safety_stock': max(0, safety_stock),
                    'lead_time_days': lead_time,
                    'last_computation': fields.Datetime.now(),
                })
        
        _logger.info(f'Computed optimal rules for {len(product_ids)} products, {created} new rules created')
        return created
    
    def action_apply_to_odoo(self):
        """Apply AI-optimized rules to Odoo's reorder rules"""
        for record in self:
            # Find existing Odoo reorder rule
            orderpoint = self.env['stock.warehouse.orderpoint'].search([
                ('product_id', '=', record.product_id.id),
                ('warehouse_id', '=', record.warehouse_id.id)
            ], limit=1)
            
            if orderpoint:
                # Update existing
                orderpoint.write({
                    'product_min_qty': record.optimal_min_qty,
                    'product_max_qty': record.optimal_max_qty,
                })
            else:
                # Create new
                self.env['stock.warehouse.orderpoint'].create({
                    'product_id': record.product_id.id,
                    'warehouse_id': record.warehouse_id.id,
                    'location_id': record.warehouse_id.lot_stock_id.id,
                    'product_min_qty': record.optimal_min_qty,
                    'product_max_qty': record.optimal_max_qty,
                })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Rules Applied'),
                'message': _('AI-optimized reorder rules have been applied successfully!'),
                'type': 'success',
            }
        }
