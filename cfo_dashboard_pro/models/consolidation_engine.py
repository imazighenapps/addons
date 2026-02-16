# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CFOConsolidation(models.Model):
    _name = 'cfo.consolidation'
    _description = 'Multi-Company Consolidation'
    
    name = fields.Char(compute='_compute_name', store=True)
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)
    
    company_ids = fields.Many2many('res.company', string='Companies to Consolidate')
    
    consolidated_revenue = fields.Monetary(currency_field='currency_id')
    consolidated_expenses = fields.Monetary(currency_field='currency_id')
    consolidated_profit = fields.Monetary(currency_field='currency_id', compute='_compute_profit')
    
    intercompany_eliminated = fields.Monetary(string='Intercompany Eliminated', currency_field='currency_id')
    
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    state = fields.Selection([('draft', 'Draft'), ('computed', 'Computed')], default='draft')
    
    @api.depends('period_start', 'period_end')
    def _compute_name(self):
        for rec in self:
            rec.name = f"Consolidation {rec.period_start} - {rec.period_end}"
    
    @api.depends('consolidated_revenue', 'consolidated_expenses')
    def _compute_profit(self):
        for rec in self:
            rec.consolidated_profit = rec.consolidated_revenue - rec.consolidated_expenses
    
    def action_compute(self):
        """Compute consolidation"""
        self.ensure_one()
        
        total_revenue = 0.0
        total_expenses = 0.0
        intercompany_amount = 0.0
        
        for company in self.company_ids:
            kpi = self.env['cfo.kpi.engine'].with_company(company).compute_executive_kpis(
                self.period_start, self.period_end, company.id
            )
            
            # Convert to consolidation currency
            revenue_converted = company.currency_id._convert(
                kpi['revenue_ytd'],
                self.currency_id,
                company,
                self.period_end
            )
            
            total_revenue += revenue_converted
        
        # Identify and eliminate intercompany transactions
        config = self.env['cfo.dashboard.config'].get_config()
        if config.intercompany_account_ids:
            intercompany_amount = self._compute_intercompany_eliminations()
        
        self.write({
            'consolidated_revenue': total_revenue,
            'consolidated_expenses': total_expenses,
            'intercompany_eliminated': intercompany_amount,
            'state': 'computed',
        })
    
    def _compute_intercompany_eliminations(self):
        """Identify intercompany transactions to eliminate"""
        # Simplified - would need more complex logic in production
        return 0.0
