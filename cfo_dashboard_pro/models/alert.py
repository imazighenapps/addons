# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CFOAlert(models.Model):
    _name = 'cfo.alert'
    _description = 'CFO Financial Alerts'
    _order = 'alert_date desc'
    
    name = fields.Char(required=True)
    alert_type = fields.Selection([
        ('cash_negative', 'Negative Cash Projected'),
        ('dso_high', 'High DSO'),
        ('margin_low', 'Low Margin'),
        ('burn_rate', 'Critical Burn Rate'),
        ('customer_risk', 'Customer Risk'),
        ('concentration', 'Customer Concentration'),
    ], required=True)
    
    severity = fields.Selection([
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ], required=True, default='warning')
    
    alert_date = fields.Datetime(required=True, default=fields.Datetime.now)
    message = fields.Text(required=True)
    
    value_current = fields.Float(string='Current Value')
    value_threshold = fields.Float(string='Threshold')
    
    state = fields.Selection([
        ('new', 'New'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ], default='new')
    
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    
    @api.model
    def check_all_alerts(self, company_id=None):
        """Check all alert conditions and create alerts"""
        if not company_id:
            company_id = self.env.company.id
        
        config = self.env['cfo.dashboard.config'].get_config()
        kpis = self.env['cfo.kpi.engine'].compute_executive_kpis(company_id=company_id)
        
        alerts_to_create = []
        
        # Check DSO
        if kpis['dso'] > config.dso_alert_threshold:
            alerts_to_create.append({
                'name': 'High DSO Alert',
                'alert_type': 'dso_high',
                'severity': 'warning',
                'message': f"DSO is {kpis['dso']:.1f} days, exceeding threshold of {config.dso_alert_threshold} days",
                'value_current': kpis['dso'],
                'value_threshold': config.dso_alert_threshold,
                'company_id': company_id,
            })
        
        # Check burn rate
        if kpis['burn_rate'] < config.burn_rate_alert_threshold:
            alerts_to_create.append({
                'name': 'Critical Burn Rate',
                'alert_type': 'burn_rate',
                'severity': 'critical',
                'message': f"Monthly burn rate is {kpis['burn_rate']:,.2f}, runway is {kpis['runway_months']:.1f} months",
                'value_current': kpis['burn_rate'],
                'value_threshold': config.burn_rate_alert_threshold,
                'company_id': company_id,
            })
        
        # Check customer concentration
        if kpis['customer_concentration_risk'] > config.customer_concentration_threshold:
            alerts_to_create.append({
                'name': 'High Customer Concentration',
                'alert_type': 'concentration',
                'severity': 'warning',
                'message': f"Top customer represents {kpis['customer_concentration_risk']:.1f}% of revenue",
                'value_current': kpis['customer_concentration_risk'],
                'value_threshold': config.customer_concentration_threshold,
                'company_id': company_id,
            })
        
        # Create alerts
        for alert_data in alerts_to_create:
            # Check if similar alert already exists
            existing = self.search([
                ('alert_type', '=', alert_data['alert_type']),
                ('state', '=', 'new'),
                ('company_id', '=', company_id),
            ], limit=1)
            
            if not existing:
                self.create(alert_data)
        
        return len(alerts_to_create)
