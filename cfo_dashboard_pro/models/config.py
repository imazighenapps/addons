# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CFODashboardConfig(models.Model):
    _name = 'cfo.dashboard.config'
    _description = 'CFO Dashboard Configuration'
    _rec_name = 'name'

    name = fields.Char(string='Configuration Name', required=True, default='Default')
    
    # Cash Flow Settings
    cashflow_projection_days = fields.Integer(
        string='Cash Flow Projection Days',
        default=180,
        help='Number of days to project cash flow'
    )
    payment_delay_calculation_method = fields.Selection([
        ('average', 'Moving Average'),
        ('weighted', 'Weighted Average'),
        ('median', 'Median'),
    ], string='Payment Delay Method', default='weighted')
    
    cashflow_optimistic_factor = fields.Float(
        string='Optimistic Factor (%)',
        default=10.0,
        help='Percentage adjustment for optimistic scenario'
    )
    cashflow_pessimistic_factor = fields.Float(
        string='Pessimistic Factor (%)',
        default=-15.0,
        help='Percentage adjustment for pessimistic scenario'
    )
    
    # DSO/DPO Settings
    dso_rolling_months = fields.Integer(
        string='DSO Rolling Period (Months)',
        default=12,
        help='Number of months for rolling DSO calculation'
    )
    
    # Risk Settings
    risk_high_threshold = fields.Float(
        string='High Risk Threshold',
        default=80.0,
        help='Score above this is considered high risk'
    )
    risk_medium_threshold = fields.Float(
        string='Medium Risk Threshold',
        default=50.0,
        help='Score above this is considered medium risk'
    )
    
    # Alert Thresholds
    burn_rate_alert_threshold = fields.Monetary(
        string='Burn Rate Alert Threshold',
        currency_field='company_currency_id',
        default=-10000.0,
        help='Alert when burn rate exceeds this (negative value)'
    )
    margin_alert_threshold = fields.Float(
        string='Margin Alert Threshold (%)',
        default=20.0,
        help='Alert when margin falls below this percentage'
    )
    dso_alert_threshold = fields.Float(
        string='DSO Alert Threshold (Days)',
        default=45.0,
        help='Alert when DSO exceeds this number of days'
    )
    customer_concentration_threshold = fields.Float(
        string='Customer Concentration Threshold (%)',
        default=30.0,
        help='Alert when single customer exceeds this % of revenue'
    )
    
    # Profitability Settings
    indirect_cost_allocation_method = fields.Selection([
        ('revenue', '% of Revenue'),
        ('cost', '% of Direct Cost'),
        ('fixed', 'Fixed Monthly Amount'),
        ('analytic', 'Analytic Distribution'),
    ], string='Indirect Cost Allocation', default='revenue')
    
    indirect_cost_percentage = fields.Float(
        string='Indirect Cost %',
        default=15.0,
        help='Percentage for indirect cost allocation'
    )
    
    # Multi-Company Settings
    enable_consolidation = fields.Boolean(
        string='Enable Multi-Company Consolidation',
        default=False
    )
    intercompany_account_ids = fields.Many2many(
        'account.account',
        string='Intercompany Accounts',
        help='Accounts to eliminate in consolidation'
    )
    
    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    company_currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string='Currency'
    )
    
    # Snapshot Settings
    auto_snapshot = fields.Boolean(
        string='Auto Monthly Snapshot',
        default=True,
        help='Automatically create monthly KPI snapshots'
    )
    
    _sql_constraints = [
        ('name_company_unique', 'unique(name, company_id)', 
         'Configuration name must be unique per company!')
    ]
    
    @api.model
    def get_config(self):
        """Get configuration for current company"""
        config = self.search([
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        if not config:
            config = self.create({
                'name': 'Default Configuration',
                'company_id': self.env.company.id,
            })
        return config
