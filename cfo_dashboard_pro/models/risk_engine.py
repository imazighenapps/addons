# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


class CFORiskScore(models.Model):
    _name = 'cfo.risk.score'
    _description = 'Customer/Supplier Risk Scoring'
    _order = 'risk_score desc'
    
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, index=True)
    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Supplier')])
    
    risk_score = fields.Float(string='Risk Score', help='0-100, higher is riskier')
    risk_level = fields.Selection([
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
    ], compute='_compute_risk_level', store=True)
    
    # Scoring Factors
    payment_delay_avg = fields.Float(string='Avg Payment Delay (days)')
    overdue_count = fields.Integer(string='Overdue Invoices')
    overdue_amount = fields.Monetary(string='Overdue Amount', currency_field='currency_id')
    concentration_pct = fields.Float(string='Revenue Concentration %')
    
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    computation_date = fields.Datetime(default=fields.Datetime.now)
    
    @api.depends('risk_score')
    def _compute_risk_level(self):
        config = self.env['cfo.dashboard.config'].get_config()
        for rec in self:
            if rec.risk_score >= config.risk_high_threshold:
                rec.risk_level = 'high'
            elif rec.risk_score >= config.risk_medium_threshold:
                rec.risk_level = 'medium'
            else:
                rec.risk_level = 'low'
    
    @api.model
    def recompute_all_scores(self, company_id=None):
        """Recompute risk scores for all partners"""
        if not company_id:
            company_id = self.env.company.id
        
        # Clear existing scores
        self.search([('company_id', '=', company_id)]).unlink()
        
        # Compute customer scores
        self._compute_customer_scores(company_id)
        
        # Compute supplier scores
        self._compute_supplier_scores(company_id)
        
        return True
    
    def _compute_customer_scores(self, company_id):
        """Compute risk scores for customers"""
        query = """
            SELECT 
                partner_id,
                AVG(EXTRACT(DAY FROM (apr.date - am.invoice_date_due))) as avg_delay,
                COUNT(CASE WHEN am.invoice_date_due < CURRENT_DATE THEN 1 END) as overdue_count,
                SUM(CASE WHEN am.invoice_date_due < CURRENT_DATE 
                    THEN aml.amount_residual ELSE 0 END) as overdue_amount
            FROM account_move am
            JOIN account_move_line aml ON aml.move_id = am.id
            LEFT JOIN account_partial_reconcile apr ON apr.credit_move_id = aml.id
            WHERE am.move_type = 'out_invoice'
                AND am.state = 'posted'
                AND am.company_id = %s
            GROUP BY partner_id
        """
        
        self.env.cr.execute(query, (company_id,))
        
        for row in self.env.cr.dictfetchall():
            score = self._calculate_risk_score(
                row['avg_delay'] or 0,
                row['overdue_count'] or 0,
                row['overdue_amount'] or 0
            )
            
            self.create({
                'partner_id': row['partner_id'],
                'partner_type': 'customer',
                'risk_score': score,
                'payment_delay_avg': row['avg_delay'] or 0,
                'overdue_count': row['overdue_count'] or 0,
                'overdue_amount': row['overdue_amount'] or 0,
                'company_id': company_id,
            })
    
    def _compute_supplier_scores(self, company_id):
        """Compute dependency scores for suppliers"""
        # Similar logic for suppliers
        pass
    
    def _calculate_risk_score(self, avg_delay, overdue_count, overdue_amount):
        """Calculate risk score from factors"""
        score = 0.0
        
        # Delay factor (0-40 points)
        if avg_delay > 30:
            score += 40
        elif avg_delay > 15:
            score += 25
        elif avg_delay > 0:
            score += 10
        
        # Overdue count (0-30 points)
        if overdue_count > 5:
            score += 30
        elif overdue_count > 2:
            score += 20
        elif overdue_count > 0:
            score += 10
        
        # Amount factor (0-30 points)
        if overdue_amount > 50000:
            score += 30
        elif overdue_amount > 10000:
            score += 20
        elif overdue_amount > 0:
            score += 10
        
        return min(score, 100.0)
