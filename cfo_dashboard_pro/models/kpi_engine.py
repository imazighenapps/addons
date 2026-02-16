# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import date_utils
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class CFOKPIEngine(models.Model):
    _name = 'cfo.kpi.engine'
    _description = 'CFO KPI Calculation Engine'
    _auto = False  # This is a transient computation model


    @api.model
    def get_currency(self):
        _logger.warning('\n ok ok //****************************')
        _logger.warning('\n ok ok self.env.user=>%s',self.sudo().env.user.company_id.currency_id.name)
        return self.sudo().env.user.company_id.currency_id.name
   
    @api.model
    def get_lang(self):
        _logger.warning('\n ok ok //****************************')
        _logger.warning('\n ok ok self.env.user=>%s',self.sudo().env.user.lang.replace('_','-'))
        return self.sudo().env.user.lang.replace('_','-')
   

    @api.model
    def compute_executive_kpis(self, date_from=None, date_to=None, company_id=None):
        """
        Compute all executive KPIs for dashboard
        Returns a dictionary with all calculated metrics
        """
        if not company_id:
            company_id = self.env.company.id
        
        if not date_to:
            date_to = fields.Date.today()
        if not date_from:
            date_from = fields.Date.to_date(
                datetime.strptime(str(date_to), '%Y-%m-%d') - relativedelta(months=12)
            )
        
        company = self.env['res.company'].browse(company_id)
        currency = company.currency_id
        
        # Get fiscal year dates
        today = fields.Date.today()
        ytd_start = date_utils.start_of(today, 'year')
        mtd_start = date_utils.start_of(today, 'month')
        
        kpis = {
            # Rentability Metrics
            'revenue_ytd': self._compute_revenue(ytd_start, today, company_id),
            'revenue_mtd': self._compute_revenue(mtd_start, today, company_id),
            'revenue_forecast': self._compute_revenue_forecast(company_id),
            'gross_margin': self._compute_gross_margin(ytd_start, today, company_id),
            'contribution_margin': self._compute_contribution_margin(ytd_start, today, company_id),
            'ebitda': self._compute_ebitda(ytd_start, today, company_id),
            'net_profit': self._compute_net_profit(ytd_start, today, company_id),
            'operating_margin_pct': 0.0,  # Will be calculated below
            
            # Liquidity Metrics
            'cash_available': self._compute_cash_available(company_id),
            'cash_forecast_90d': self._compute_cash_forecast_90d(company_id),
            'burn_rate': self._compute_burn_rate(company_id),
            'runway_months': 0.0,  # Will be calculated below
            'working_capital': self._compute_working_capital(company_id),
            'current_ratio': self._compute_current_ratio(company_id),
            'quick_ratio': self._compute_quick_ratio(company_id),
            
            # Risk Metrics
            'dso': self._compute_dso(company_id),
            'dpo': self._compute_dpo(company_id),
            'overdue_rate': self._compute_overdue_rate(company_id),
            'customer_concentration_risk': self._compute_customer_concentration(company_id),
            'supplier_dependency': self._compute_supplier_dependency(company_id),
            
            # Meta
            'currency_symbol': currency.symbol,
            'currency_position': currency.position,
            'computation_date': fields.Datetime.now(),
        }
        
        # Calculate derived metrics
        if kpis['revenue_ytd'] > 0:
            kpis['operating_margin_pct'] = (kpis['ebitda'] / kpis['revenue_ytd']) * 100
        
        if kpis['burn_rate'] < 0:
            kpis['runway_months'] = kpis['cash_available'] / abs(kpis['burn_rate'])
        else:
            kpis['runway_months'] = 999  # Infinite runway
        
        return kpis

    def _compute_revenue(self, date_from, date_to, company_id):
        """Compute total revenue from posted invoices"""
        self.env.cr.execute("""
            SELECT COALESCE(SUM(aml.credit - aml.debit), 0.0)
            FROM account_move_line aml
            JOIN account_move am ON am.id = aml.move_id
            JOIN account_account aa ON aa.id = aml.account_id
            WHERE am.state = 'posted'
                AND am.move_type IN ('out_invoice', 'out_refund')
                AND am.company_id = %s
                AND am.date >= %s
                AND am.date <= %s
                AND aa.account_type IN ('income', 'income_other')
        """, (company_id, date_from, date_to))
        
        result = self.env.cr.fetchone()
        return result[0] if result else 0.0

    def _compute_revenue_forecast(self, company_id):
        """Forecast revenue based on confirmed sales orders"""
        self.env.cr.execute("""
            SELECT COALESCE(SUM(amount_untaxed), 0.0)
            FROM sale_order
            WHERE state IN ('sale', 'done')
                AND invoice_status IN ('to invoice', 'invoiced')
                AND company_id = %s
                AND date_order >= CURRENT_DATE - INTERVAL '90 days'
        """, (company_id,))
        
        result = self.env.cr.fetchone()
        return result[0] if result else 0.0

    def _compute_gross_margin(self, date_from, date_to, company_id):
        """Compute gross margin (Revenue - COGS)"""
        revenue = self._compute_revenue(date_from, date_to, company_id)
        
        self.env.cr.execute("""
            SELECT COALESCE(SUM(aml.debit - aml.credit), 0.0)
            FROM account_move_line aml
            JOIN account_move am ON am.id = aml.move_id
            JOIN account_account aa ON aa.id = aml.account_id
            WHERE am.state = 'posted'
                AND am.company_id = %s
                AND am.date >= %s
                AND am.date <= %s
                AND aa.account_type = 'expense_direct_cost'
        """, (company_id, date_from, date_to))
        
        result = self.env.cr.fetchone()
        cogs = result[0] if result else 0.0
        
        return revenue - cogs

    def _compute_contribution_margin(self, date_from, date_to, company_id):
        """Compute contribution margin (GM - Variable Costs)"""
        gross_margin = self._compute_gross_margin(date_from, date_to, company_id)
        
        # Simplified: use a portion of operating expenses as variable costs
        self.env.cr.execute("""
            SELECT COALESCE(SUM(aml.debit - aml.credit), 0.0) * 0.3
            FROM account_move_line aml
            JOIN account_move am ON am.id = aml.move_id
            JOIN account_account aa ON aa.id = aml.account_id
            WHERE am.state = 'posted'
                AND am.company_id = %s
                AND am.date >= %s
                AND am.date <= %s
                AND aa.account_type = 'expense'
        """, (company_id, date_from, date_to))
        
        result = self.env.cr.fetchone()
        variable_costs = result[0] if result else 0.0
        
        return gross_margin - variable_costs

    def _compute_ebitda(self, date_from, date_to, company_id):
        """Compute EBITDA (simplified: Revenue - Operating Expenses)"""
        revenue = self._compute_revenue(date_from, date_to, company_id)
        
        self.env.cr.execute("""
            SELECT COALESCE(SUM(aml.debit - aml.credit), 0.0)
            FROM account_move_line aml
            JOIN account_move am ON am.id = aml.move_id
            JOIN account_account aa ON aa.id = aml.account_id
            WHERE am.state = 'posted'
                AND am.company_id = %s
                AND am.date >= %s
                AND am.date <= %s
                AND aa.account_type IN ('expense', 'expense_direct_cost')
        """, (company_id, date_from, date_to))
        
        result = self.env.cr.fetchone()
        operating_expenses = result[0] if result else 0.0
        
        return revenue - operating_expenses

    def _compute_net_profit(self, date_from, date_to, company_id):
        """Compute net profit (simplified EBITDA for now)"""
        return self._compute_ebitda(date_from, date_to, company_id)

    def _compute_cash_available(self, company_id):
        """Compute available cash from bank and cash accounts"""
        self.env.cr.execute("""
            SELECT COALESCE(SUM(aml.debit - aml.credit), 0.0)
            FROM account_move_line aml
            JOIN account_account aa ON aa.id = aml.account_id
            JOIN account_move am ON am.id = aml.move_id
            WHERE aa.account_type IN ('asset_cash', 'asset_current')
                AND am.state = 'posted'
                AND aml.company_id = %s
        """, (company_id,))
        
        result = self.env.cr.fetchone()
        return result[0] if result else 0.0

    def _compute_cash_forecast_90d(self, company_id):
        """Get cash forecast for 90 days from projection engine"""
        target_date = fields.Date.today() + timedelta(days=90)
        
        projection = self.env['cfo.cashflow.projection'].search([
            ('company_id', '=', company_id),
            ('projection_date', '=', target_date),
        ], limit=1)
        
        if projection:
            return projection.projected_balance
        
        # If no projection, return current cash
        return self._compute_cash_available(company_id)

    def _compute_burn_rate(self, company_id):
        """Compute monthly burn rate (average monthly cash outflow)"""
        date_from = fields.Date.today() - timedelta(days=90)
        date_to = fields.Date.today()
        
        self.env.cr.execute("""
            SELECT COALESCE(SUM(aml.credit - aml.debit), 0.0) / 3.0
            FROM account_move_line aml
            JOIN account_move am ON am.id = aml.move_id
            JOIN account_account aa ON aa.id = aml.account_id
            WHERE am.state = 'posted'
                AND am.company_id = %s
                AND am.date >= %s
                AND am.date <= %s
                AND aa.account_type IN ('expense', 'expense_direct_cost')
        """, (company_id, date_from, date_to))
        
        result = self.env.cr.fetchone()
        return -(result[0] if result else 0.0)

    def _compute_working_capital(self, company_id):
        """Compute working capital (Current Assets - Current Liabilities)"""
        self.env.cr.execute("""
            SELECT 
                COALESCE(SUM(CASE 
                    WHEN aa.account_type LIKE 'asset_current%%' 
                    THEN aml.balance ELSE 0 END), 0.0)
                -
                COALESCE(SUM(CASE 
                    WHEN aa.account_type LIKE 'liability_current%%' 
                    THEN aml.balance ELSE 0 END), 0.0)
            FROM account_move_line aml
            JOIN account_account aa ON aa.id = aml.account_id
            JOIN account_move am ON am.id = aml.move_id
            WHERE am.state = 'posted'
                AND aml.company_id = %s
        """, (company_id,))
        
        result = self.env.cr.fetchone()
        return result[0] if result else 0.0

    def _compute_current_ratio(self, company_id):
        """Compute current ratio (Current Assets / Current Liabilities)"""
        self.env.cr.execute("""
            SELECT
                COALESCE(SUM(CASE 
                    WHEN aa.account_type = 'asset_current'
                    THEN aml.balance ELSE 0 END), 0.0) AS current_assets,
                COALESCE(SUM(CASE 
                    WHEN aa.account_type = 'liability_current'
                    THEN aml.balance ELSE 0 END), 0.0) AS current_liabilities
            FROM account_move_line aml
            JOIN account_account aa ON aa.id = aml.account_id
            WHERE aml.parent_state = 'posted'
                AND aml.company_id = %s
        """, (company_id,))
        
        result = self.env.cr.fetchone()
        
        if result and result[1] != 0:
            # liabilities are negative → invert sign
            return result[0] / abs(result[1])
        
        return 0.0

    def _compute_quick_ratio(self, company_id):
        """Compute quick ratio ((Current Assets - Inventory) / Current Liabilities)"""
        # Simplified version without inventory deduction
        return self._compute_current_ratio(company_id)

    def _compute_dso(self, company_id):
        """Compute Days Sales Outstanding"""
        config = self.env['cfo.dashboard.config'].get_config()
        months = config.dso_rolling_months

        date_from = fields.Date.today() - relativedelta(months=months)
        date_to = fields.Date.today()
        days = (date_to - date_from).days

        # Revenue over rolling period
        revenue = self._compute_revenue(date_from, date_to, company_id)

        # Total receivables balance
        self.env.cr.execute("""
            SELECT COALESCE(SUM(aml.balance), 0.0)
            FROM account_move_line aml
            JOIN account_account aa ON aa.id = aml.account_id
            WHERE aml.parent_state = 'posted'
                AND aml.company_id = %s
                AND aa.account_type = 'asset_receivable'
        """, (company_id,))

        result = self.env.cr.fetchone()
        receivables = result[0] if result else 0.0

        if revenue > 0:
            return (receivables / revenue) * days

        return 0.0


    def _compute_dpo(self, company_id):
        """Compute Days Payable Outstanding"""
        config = self.env['cfo.dashboard.config'].get_config()
        months = config.dso_rolling_months

        date_from = fields.Date.today() - relativedelta(months=months)
        date_to = fields.Date.today()
        days = (date_to - date_from).days

        # ---- COGS over rolling period ----
        self.env.cr.execute("""
            SELECT COALESCE(SUM(aml.balance), 0.0)
            FROM account_move_line aml
            JOIN account_account aa ON aa.id = aml.account_id
            WHERE aml.parent_state = 'posted'
                AND aml.company_id = %s
                AND aml.date >= %s
                AND aml.date <= %s
                AND aa.account_type = 'expense_direct_cost'
        """, (company_id, date_from, date_to))

        result = self.env.cr.fetchone()
        cogs = result[0] if result else 0.0

        # ---- Total Payables balance ----
        self.env.cr.execute("""
            SELECT COALESCE(SUM(aml.balance), 0.0)
            FROM account_move_line aml
            JOIN account_account aa ON aa.id = aml.account_id
            WHERE aml.parent_state = 'posted'
                AND aml.company_id = %s
                AND aa.account_type = 'liability_payable'
        """, (company_id,))

        result = self.env.cr.fetchone()
        payables = result[0] if result else 0.0

        if cogs > 0:
            return (abs(payables) / cogs) * days

        return 0.0

    def _compute_overdue_rate(self, company_id):
        """Compute percentage of overdue invoices"""
        today = fields.Date.today()
        
        self.env.cr.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN am.invoice_date_due < %s 
                    THEN aml.debit - aml.credit ELSE 0 END), 0.0) as overdue,
                COALESCE(SUM(aml.debit - aml.credit), 0.0) as total
            FROM account_move_line aml
            JOIN account_move am ON am.id = aml.move_id
            JOIN account_account aa ON aa.id = aml.account_id
            WHERE am.state = 'posted'
                AND am.move_type IN ('out_invoice', 'out_refund')
                AND aa.account_type = 'asset_receivable'
                AND aml.reconciled = false
                AND am.company_id = %s
        """, (today, company_id))
        
        result = self.env.cr.fetchone()
        if result and result[1] > 0:
            return (result[0] / result[1]) * 100
        return 0.0

    def _compute_customer_concentration(self, company_id):
        """Compute customer concentration risk (% of revenue from top customer)"""
        date_from = fields.Date.today() - relativedelta(months=12)
        date_to = fields.Date.today()
        
        # Get total revenue
        total_revenue = self._compute_revenue(date_from, date_to, company_id)
        
        if total_revenue == 0:
            return 0.0
        
        # Get top customer revenue
        self.env.cr.execute("""
            SELECT COALESCE(MAX(partner_revenue), 0.0)
            FROM (
                SELECT SUM(aml.credit - aml.debit) as partner_revenue
                FROM account_move_line aml
                JOIN account_move am ON am.id = aml.move_id
                JOIN account_account aa ON aa.id = aml.account_id
                WHERE am.state = 'posted'
                    AND am.move_type IN ('out_invoice', 'out_refund')
                    AND am.company_id = %s
                    AND am.date >= %s
                    AND am.date <= %s
                    AND aa.account_type IN ('income', 'income_other')
                GROUP BY am.partner_id
            ) as customer_revenues
        """, (company_id, date_from, date_to))
        
        result = self.env.cr.fetchone()
        top_customer_revenue = result[0] if result else 0.0
        
        return (top_customer_revenue / total_revenue) * 100

    def _compute_supplier_dependency(self, company_id):
        """Compute supplier dependency index (% of purchases from top supplier)"""
        date_from = fields.Date.today() - relativedelta(months=12)
        date_to = fields.Date.today()
        
        # Get total purchases
        self.env.cr.execute("""
            SELECT COALESCE(SUM(aml.debit - aml.credit), 0.0)
            FROM account_move_line aml
            JOIN account_move am ON am.id = aml.move_id
            JOIN account_account aa ON aa.id = aml.account_id
            WHERE am.state = 'posted'
                AND am.move_type IN ('in_invoice', 'in_refund')
                AND am.company_id = %s
                AND am.date >= %s
                AND am.date <= %s
                AND aa.account_type = 'expense_direct_cost'
        """, (company_id, date_from, date_to))
        
        result = self.env.cr.fetchone()
        total_purchases = result[0] if result else 0.0
        
        if total_purchases == 0:
            return 0.0
        
        # Get top supplier purchases
        self.env.cr.execute("""
            SELECT COALESCE(MAX(supplier_purchases), 0.0)
            FROM (
                SELECT SUM(aml.debit - aml.credit) as supplier_purchases
                FROM account_move_line aml
                JOIN account_move am ON am.id = aml.move_id
                JOIN account_account aa ON aa.id = aml.account_id
                WHERE am.state = 'posted'
                    AND am.move_type IN ('in_invoice', 'in_refund')
                    AND am.company_id = %s
                    AND am.date >= %s
                    AND am.date <= %s
                    AND aa.account_type = 'expense_direct_cost'
                GROUP BY am.partner_id
            ) as supplier_purchases
        """, (company_id, date_from, date_to))
        
        result = self.env.cr.fetchone()
        top_supplier_purchases = result[0] if result else 0.0
        
        return (top_supplier_purchases / total_purchases) * 100
