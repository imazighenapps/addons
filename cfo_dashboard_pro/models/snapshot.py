# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json
from datetime import datetime


class CFOKPISnapshot(models.Model):
    _name = 'cfo.kpi.snapshot'
    _description = 'Monthly KPI Snapshot'
    _order = 'snapshot_date desc'
    
    snapshot_date = fields.Date(required=True, index=True)
    period_type = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ], default='monthly', required=True)
    
    kpi_data = fields.Text(string='KPI Data (JSON)')
    
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    
    @api.model
    def compute_monthly_snapshot(self, company_id=None):
        """Create snapshot for current month"""
        if not company_id:
            company_id = self.env.company.id
        
        snapshot_date = fields.Date.today().replace(day=1)
        
        # Check if snapshot already exists
        existing = self.search([
            ('company_id', '=', company_id),
            ('snapshot_date', '=', snapshot_date),
            ('period_type', '=', 'monthly')
        ])
        
        if existing:
            return existing
        
        # Compute KPIs
        kpis = self.env['cfo.kpi.engine'].compute_executive_kpis(company_id=company_id)
        
        # Remove non-serializable data
        kpis_clean = {k: v for k, v in kpis.items() 
                      if not isinstance(v, (datetime, models.Model))}
        
        return self.create({
            'snapshot_date': snapshot_date,
            'period_type': 'monthly',
            'kpi_data': json.dumps(kpis_clean),
            'company_id': company_id,
        })
    
    def get_kpi_data(self):
        """Get parsed KPI data"""
        self.ensure_one()
        if self.kpi_data:
            return json.loads(self.kpi_data)
        return {}
