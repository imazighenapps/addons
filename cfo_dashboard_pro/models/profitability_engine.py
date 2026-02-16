# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta


class CFOProfitabilityCube(models.Model):
    _name = 'cfo.profitability.cube'
    _description = 'Profitability Analysis Cube'
    _order = 'date desc'
    
    # Dimensions
    date = fields.Date(string='Date', required=True, index=True)
    product_id = fields.Many2one('product.product', string='Product', index=True)
    product_categ_id = fields.Many2one('product.category', string='Category', index=True)
    partner_id = fields.Many2one('res.partner', string='Customer', index=True)
    user_id = fields.Many2one('res.users', string='Salesperson', index=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Project', index=True)
    
    # Metrics
    revenue = fields.Monetary(string='Revenue', currency_field='currency_id')
    direct_cost = fields.Monetary(string='Direct Cost', currency_field='currency_id')
    indirect_cost = fields.Monetary(string='Indirect Cost', currency_field='currency_id')
    
    gross_margin = fields.Monetary(string='Gross Margin', compute='_compute_margins', store=True)
    net_margin = fields.Monetary(string='Net Margin', compute='_compute_margins', store=True)
    contribution_margin = fields.Monetary(string='Contribution Margin', compute='_compute_margins', store=True)
    
    gross_margin_pct = fields.Float(string='Gross Margin %', compute='_compute_margins', store=True)
    net_margin_pct = fields.Float(string='Net Margin %', compute='_compute_margins', store=True)
    
    quantity = fields.Float(string='Quantity')
    
    company_id = fields.Many2one('res.company', string='Company', required=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    
    @api.depends('revenue', 'direct_cost', 'indirect_cost')
    def _compute_margins(self):
        for rec in self:
            rec.gross_margin = rec.revenue - rec.direct_cost
            rec.net_margin = rec.revenue - rec.direct_cost - rec.indirect_cost
            rec.contribution_margin = rec.gross_margin  # Simplified
            
            rec.gross_margin_pct = (rec.gross_margin / rec.revenue * 100) if rec.revenue else 0.0
            rec.net_margin_pct = (rec.net_margin / rec.revenue * 100) if rec.revenue else 0.0
    
    @api.model
    def rebuild_cube(self, date_from=None, date_to=None, company_id=None):
        """Rebuild profitability cube from invoice lines"""
        if not company_id:
            company_id = self.env.company.id
        
        if not date_to:
            date_to = fields.Date.today()
        if not date_from:
            date_from = fields.Date.to_date(datetime.now() - relativedelta(months=12))
        
        # Delete existing data for period
        self.search([
            ('company_id', '=', company_id),
            ('date', '>=', date_from),
            ('date', '<=', date_to)
        ]).unlink()
        
        config = self.env['cfo.dashboard.config'].get_config()
        
        # Build cube from invoice lines
        self.env.cr.execute("""
            INSERT INTO cfo_profitability_cube
            (date, product_id, product_categ_id, partner_id, user_id, 
             analytic_account_id, revenue, direct_cost, indirect_cost,
             quantity, company_id, create_uid, create_date, write_uid, write_date)
            SELECT 
                am.date,
                sol.product_id,
                pt.categ_id,
                am.partner_id,
                so.user_id,
                aal.account_id as analytic_account_id,
                SUM(aml.credit - aml.debit) as revenue,
                0.0 as direct_cost,
                0.0 as indirect_cost,
                SUM(aml.quantity) as quantity,
                am.company_id,
                %s, NOW(), %s, NOW()
            FROM account_move_line aml
            JOIN account_move am ON am.id = aml.move_id
            JOIN account_account aa ON aa.id = aml.account_id
            LEFT JOIN sale_order_line sol ON sol.id = aml.sale_line_id
            LEFT JOIN sale_order so ON so.id = sol.order_id
            LEFT JOIN product_product pp ON pp.id = sol.product_id
            LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
            LEFT JOIN account_analytic_line aal ON aal.move_line_id = aml.id
            WHERE am.state = 'posted'
                AND am.move_type IN ('out_invoice', 'out_refund')
                AND am.company_id = %s
                AND am.date >= %s
                AND am.date <= %s
                AND aa.account_type IN ('income', 'income_other')
            GROUP BY am.date, sol.product_id, pt.categ_id, am.partner_id, 
                     so.user_id, aal.account_id, am.company_id
        """, (self.env.uid, self.env.uid, company_id, date_from, date_to))
        
        # Update costs using product costing
        self._update_costs(date_from, date_to, company_id)
        
        return True
    
    def _update_costs(self, date_from, date_to, company_id):
        """Update direct and indirect costs"""
        # Update direct costs from product standard price
        self.env.cr.execute("""
            UPDATE cfo_profitability_cube cube
            SET direct_cost = cube.quantity * COALESCE(pp.standard_price, 0)
            FROM product_product pp
            WHERE cube.product_id = pp.id
                AND cube.date >= %s
                AND cube.date <= %s
                AND cube.company_id = %s
        """, (date_from, date_to, company_id))
        
        # Apply indirect cost allocation
        config = self.env['cfo.dashboard.config'].get_config()
        
        if config.indirect_cost_allocation_method == 'revenue':
            rate = config.indirect_cost_percentage / 100.0
            self.env.cr.execute("""
                UPDATE cfo_profitability_cube
                SET indirect_cost = revenue * %s
                WHERE date >= %s
                    AND date <= %s
                    AND company_id = %s
            """, (rate, date_from, date_to, company_id))
        
    @api.model
    def get_analysis_data(self, dimension, date_from=None, date_to=None, company_id=None):
        """Get profitability analysis grouped by dimension"""
        if not company_id:
            company_id = self.env.company.id
        
        if not date_to:
            date_to = fields.Date.today()
        if not date_from:
            date_from = fields.Date.to_date(datetime.now() - relativedelta(months=12))
        
        dimension_field = f"{dimension}_id" if dimension != 'date' else 'date'
        
        query = f"""
            SELECT 
                {dimension_field},
                SUM(revenue) as total_revenue,
                SUM(direct_cost) as total_cost,
                SUM(gross_margin) as total_margin,
                AVG(gross_margin_pct) as avg_margin_pct
            FROM cfo_profitability_cube
            WHERE company_id = %s
                AND date >= %s
                AND date <= %s
            GROUP BY {dimension_field}
            ORDER BY total_revenue DESC
            LIMIT 20
        """
        
        self.env.cr.execute(query, (company_id, date_from, date_to))
        
        return self.env.cr.dictfetchall()
