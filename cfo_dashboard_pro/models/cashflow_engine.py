# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class CFOCashflowProjection(models.Model):
    _name = 'cfo.cashflow.projection'
    _description = 'Cash Flow Projection'
    _order = 'projection_date desc'
    _rec_name = 'projection_date'

    projection_date = fields.Date(string='Projection Date', required=True, index=True)
    expected_inflows = fields.Monetary(string='Expected Inflows', currency_field='currency_id')
    expected_outflows = fields.Monetary(string='Expected Outflows', currency_field='currency_id')
    net_flow = fields.Monetary(string='Net Flow', compute='_compute_net_flow', store=True)
    projected_balance = fields.Monetary(string='Projected Balance', currency_field='currency_id')
    
    scenario = fields.Selection([
        ('realistic', 'Realistic'),
        ('optimistic', 'Optimistic'),
        ('pessimistic', 'Pessimistic'),
    ], string='Scenario', default='realistic', required=True)
    
    company_id = fields.Many2one('res.company', string='Company', required=True, 
                                  default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', 
                                   string='Currency')
    computation_date = fields.Datetime(string='Computed On', default=fields.Datetime.now)
    
    @api.depends('expected_inflows', 'expected_outflows')
    def _compute_net_flow(self):
        for rec in self:
            rec.net_flow = rec.expected_inflows - rec.expected_outflows

    @api.model
    def rebuild_projections(self, company_id=None, scenario='realistic'):
        """
        Rebuild all cash flow projections
        This is the main entry point called by cron
        """
        if not company_id:
            company_id = self.env.company.id
        
        config = self.env['cfo.dashboard.config'].get_config()
        projection_days = config.cashflow_projection_days
        
        _logger.info(f"Rebuilding cash flow projections for {projection_days} days")
        
        # Delete existing projections for this scenario
        self.search([
            ('company_id', '=', company_id),
            ('scenario', '=', scenario),
            ('projection_date', '>=', fields.Date.today())
        ]).unlink()
        
        # Get initial cash balance
        kpi_engine = self.env['cfo.kpi.engine']
        initial_balance = kpi_engine._compute_cash_available(company_id)
        
        # Generate projections for each day
        projections = []
        current_balance = initial_balance
        today = fields.Date.today()
        
        for day_offset in range(projection_days + 1):
            projection_date = today + timedelta(days=day_offset)
            
            inflows = self._compute_expected_inflows(projection_date, company_id, scenario)
            outflows = self._compute_expected_outflows(projection_date, company_id, scenario)
            
            current_balance = current_balance + inflows - outflows
            
            projections.append({
                'projection_date': projection_date,
                'expected_inflows': inflows,
                'expected_outflows': outflows,
                'projected_balance': current_balance,
                'scenario': scenario,
                'company_id': company_id,
            })
        
        # Bulk create for performance
        self.create(projections)
        
        _logger.info(f"Created {len(projections)} cash flow projection records")
        
        return True

    def _compute_expected_inflows(self, projection_date, company_id, scenario):
        """
        Calculate expected cash inflows for a specific date
        Based on open invoices and their predicted payment dates
        """
        config = self.env['cfo.dashboard.config'].get_config()
        
        # Get unpaid customer invoices
        self.env.cr.execute("""
            SELECT 
                am.id,
                am.partner_id,
                aml.amount_residual,
                am.invoice_date,
                am.invoice_date_due
            FROM account_move am
            JOIN account_move_line aml ON aml.move_id = am.id
            JOIN account_account aa ON aa.id = aml.account_id
            WHERE am.state = 'posted'
                AND am.move_type IN ('out_invoice', 'out_refund')
                AND aa.account_type = 'asset_receivable'
                AND aml.amount_residual > 0
                AND am.company_id = %s
        """, (company_id,))
        
        invoices = self.env.cr.fetchall()
        
        total_inflows = 0.0
        
        for invoice_id, partner_id, amount, invoice_date, due_date in invoices:
            # Calculate expected payment date based on partner history
            expected_date = self._predict_payment_date(
                partner_id, 
                invoice_date, 
                due_date,
                company_id
            )
            
            # If expected payment date matches projection date, add to inflows
            if expected_date == projection_date:
                # Apply scenario factor
                factor = self._get_scenario_factor(scenario, 'inflow', config)
                total_inflows += amount * factor
        
        # Add confirmed sales orders not yet invoiced
        total_inflows += self._get_uninvoiced_sales(projection_date, company_id, scenario)
        
        return total_inflows

    def _compute_expected_outflows(self, projection_date, company_id, scenario):
        """
        Calculate expected cash outflows for a specific date
        Based on unpaid bills and their predicted payment dates
        """
        config = self.env['cfo.dashboard.config'].get_config()
        
        # Get unpaid supplier bills
        self.env.cr.execute("""
            SELECT 
                am.id,
                am.partner_id,
                aml.amount_residual,
                am.invoice_date,
                am.invoice_date_due
            FROM account_move am
            JOIN account_move_line aml ON aml.move_id = am.id
            JOIN account_account aa ON aa.id = aml.account_id
            WHERE am.state = 'posted'
                AND am.move_type IN ('in_invoice', 'in_refund')
                AND aa.account_type = 'liability_payable'
                AND aml.amount_residual > 0
                AND am.company_id = %s
        """, (company_id,))
        
        bills = self.env.cr.fetchall()
        
        total_outflows = 0.0
        
        for bill_id, partner_id, amount, invoice_date, due_date in bills:
            # Calculate expected payment date
            expected_date = self._predict_payment_date(
                partner_id,
                invoice_date,
                due_date,
                company_id,
                is_supplier=True
            )
            
            if expected_date == projection_date:
                # Apply scenario factor
                factor = self._get_scenario_factor(scenario, 'outflow', config)
                total_outflows += amount * factor
        
        # Add confirmed purchase orders not yet billed
        total_outflows += self._get_unbilled_purchases(projection_date, company_id, scenario)
        
        return total_outflows

    def _predict_payment_date(self, partner_id, invoice_date, due_date, company_id, 
                                is_supplier=False):
        """
        Predict payment date based on partner payment history
        Uses weighted average of past payment delays
        """
        if not due_date:
            due_date = invoice_date + timedelta(days=30)
        
        # Get partner payment history
        move_type = ('in_invoice', 'in_refund') if is_supplier else ('out_invoice', 'out_refund')
        
        self.env.cr.execute("""
                SELECT 
                    am.invoice_date_due,
                    pay_move.date AS payment_date
                FROM account_move am
                JOIN account_move_line aml ON aml.move_id = am.id
                JOIN account_partial_reconcile apr 
                    ON apr.debit_move_id = aml.id 
                    OR apr.credit_move_id = aml.id
                JOIN account_move_line pay_aml 
                    ON pay_aml.id = CASE 
                        WHEN apr.debit_move_id = aml.id 
                        THEN apr.credit_move_id 
                        ELSE apr.debit_move_id 
                    END
                JOIN account_move pay_move ON pay_move.id = pay_aml.move_id
                WHERE am.partner_id = %s
                    AND am.move_type IN %s
                    AND am.company_id = %s
                    AND am.invoice_date_due IS NOT NULL
                    AND pay_move.date >= CURRENT_DATE - INTERVAL '6 months'
                ORDER BY pay_move.date DESC
                LIMIT 10
            """, (partner_id, move_type, company_id))
    
        
        history = self.env.cr.fetchall()
        
        if not history:
            # No history, use due date
            return due_date
        
        # Calculate weighted average delay
        total_weight = 0
        weighted_delay = 0
        
        for i, (hist_due_date, payment_date) in enumerate(history):
            delay = (payment_date - hist_due_date).days
            weight = 1.0 / (i + 1)  # More recent payments have higher weight
            weighted_delay += delay * weight
            total_weight += weight
        
        avg_delay = int(weighted_delay / total_weight) if total_weight > 0 else 0
        
        predicted_date = due_date + timedelta(days=avg_delay)
        
        # Don't predict dates in the past
        if predicted_date < fields.Date.today():
            predicted_date = fields.Date.today()
        
        return predicted_date

    def _get_scenario_factor(self, scenario, flow_type, config):
        """
        Get multiplication factor based on scenario
        """
        if scenario == 'realistic':
            return 1.0
        elif scenario == 'optimistic':
            factor = 1.0 + (config.cashflow_optimistic_factor / 100.0)
            return factor if flow_type == 'inflow' else 1.0 / factor
        else:  # pessimistic
            factor = 1.0 + (config.cashflow_pessimistic_factor / 100.0)
            return factor if flow_type == 'inflow' else 1.0 / factor

    def _get_uninvoiced_sales(self, projection_date, company_id, scenario):
        """
        Get revenue from confirmed sales orders not yet invoiced
        Distributed across projection period
        """
        # Get sales orders confirmed but not fully invoiced
        self.env.cr.execute("""
            SELECT COALESCE(SUM(amount_untaxed), 0.0)
            FROM sale_order
            WHERE state IN ('sale', 'done')
                AND invoice_status IN ('to invoice', 'invoiced')
                AND company_id = %s
                AND date_order >= CURRENT_DATE - INTERVAL '90 days'
        """, (company_id,))
        
        result = self.env.cr.fetchone()
        total = result[0] if result else 0.0
        
        # Distribute evenly over next 60 days (simplified)
        daily_amount = total / 60.0
        
        days_from_today = (projection_date - fields.Date.today()).days
        if 0 <= days_from_today <= 60:
            return daily_amount
        
        return 0.0

    def _get_unbilled_purchases(self, projection_date, company_id, scenario):
        """
        Get expenses from confirmed purchase orders not yet billed
        """
        self.env.cr.execute("""
            SELECT COALESCE(SUM(amount_untaxed), 0.0)
            FROM purchase_order
            WHERE state IN ('purchase', 'done')
                AND invoice_status IN ('to invoice', 'invoiced')
                AND company_id = %s
                AND date_order >= CURRENT_DATE - INTERVAL '90 days'
        """, (company_id,))
        
        result = self.env.cr.fetchone()
        total = result[0] if result else 0.0
        
        # Distribute evenly over next 45 days
        daily_amount = total / 45.0
        
        days_from_today = (projection_date - fields.Date.today()).days
        if 0 <= days_from_today <= 45:
            return daily_amount
        
        return 0.0

    @api.model
    def get_projection_chart_data(self, scenario='realistic', days=90, company_id=None):
        """
        Get chart data for cash flow projection
        Returns data formatted for Chart.js
        """
        if not company_id:
            company_id = self.env.company.id
        
        projections = self.search([
            ('company_id', '=', company_id),
            ('scenario', '=', scenario),
            ('projection_date', '>=', fields.Date.today()),
            ('projection_date', '<=', fields.Date.today() + timedelta(days=days))
        ], order='projection_date')
        
        labels = []
        balances = []
        inflows = []
        outflows = []
        
        for proj in projections:
            labels.append(proj.projection_date.strftime('%Y-%m-%d'))
            balances.append(proj.projected_balance)
            inflows.append(proj.expected_inflows)
            outflows.append(proj.expected_outflows)
        
        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Projected Balance',
                    'data': balances,
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'tension': 0.1,
                },
                {
                    'label': 'Inflows',
                    'data': inflows,
                    'borderColor': 'rgb(54, 162, 235)',
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'tension': 0.1,
                },
                {
                    'label': 'Outflows',
                    'data': outflows,
                    'borderColor': 'rgb(255, 99, 132)',
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'tension': 0.1,
                },
            ]
        }


class CFOCashflowDetail(models.Model):
    _name = 'cfo.cashflow.detail'
    _description = 'Cash Flow Detail Line'
    _order = 'expected_date'

    projection_id = fields.Many2one('cfo.cashflow.projection', string='Projection', 
                                     ondelete='cascade')
    expected_date = fields.Date(string='Expected Date', required=True)
    amount = fields.Monetary(string='Amount', currency_field='currency_id')
    flow_type = fields.Selection([
        ('inflow', 'Inflow'),
        ('outflow', 'Outflow'),
    ], string='Type', required=True)
    
    source_type = fields.Selection([
        ('invoice', 'Customer Invoice'),
        ('bill', 'Supplier Bill'),
        ('sale_order', 'Sales Order'),
        ('purchase_order', 'Purchase Order'),
        ('other', 'Other'),
    ], string='Source Type')
    
    source_id = fields.Integer(string='Source ID')
    source_name = fields.Char(string='Source Reference')
    partner_id = fields.Many2one('res.partner', string='Partner')
    
    company_id = fields.Many2one('res.company', string='Company', required=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    
    confidence_score = fields.Float(string='Confidence %', default=100.0,
                                     help='Prediction confidence based on historical accuracy')
