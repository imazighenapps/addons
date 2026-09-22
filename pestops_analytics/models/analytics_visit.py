from odoo import fields, models, tools


class PestAnalyticsVisitReport(models.Model):
    _name = 'pest.analytics.visit.report'
    _description = 'PestOps Visit Analytics'
    _auto = False
    _rec_name = 'visit_id'
    _order = 'scheduled_start desc, visit_id desc'

    visit_id = fields.Many2one('pest.visit', readonly=True)
    company_id = fields.Many2one('res.company', readonly=True)
    site_id = fields.Many2one('pest.site', readonly=True)
    partner_id = fields.Many2one('res.partner', readonly=True)
    contract_id = fields.Many2one('pest.contract', readonly=True)
    technician_id = fields.Many2one('res.users', readonly=True)
    scheduled_start = fields.Datetime(readonly=True)
    actual_start = fields.Datetime(readonly=True)
    actual_end = fields.Datetime(readonly=True)
    period_date = fields.Date(readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'), ('scheduled', 'Scheduled'), ('in_progress', 'In Progress'),
        ('done', 'Done'), ('cancelled', 'Cancelled')
    ], readonly=True)
    priority = fields.Selection([('0', 'Normal'), ('1', 'High')], readonly=True)
    completion_outcome = fields.Selection([
        ('normal', 'Completed'), ('follow_up', 'Follow-up Required'), ('critical', 'Critical Findings')
    ], readonly=True)
    duration_hours = fields.Float(readonly=True)
    inspection_count = fields.Integer(readonly=True)
    treatment_count = fields.Integer(readonly=True)
    anomaly_count = fields.Integer(readonly=True)
    open_anomaly_count = fields.Integer(readonly=True)
    reservice_count = fields.Integer(readonly=True)
    quality_check_count = fields.Integer(readonly=True)
    open_quality_nc_count = fields.Integer(readonly=True)
    stock_consumption_qty = fields.Float(readonly=True)
    billable_amount = fields.Monetary(readonly=True)
    currency_id = fields.Many2one('res.currency', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f'''\
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    v.id AS id,
                    v.id AS visit_id,
                    v.company_id AS company_id,
                    v.site_id AS site_id,
                    s.partner_id AS partner_id,
                    v.contract_id AS contract_id,
                    v.technician_id AS technician_id,
                    v.scheduled_start AS scheduled_start,
                    v.actual_start AS actual_start,
                    v.actual_end AS actual_end,
                    COALESCE(v.scheduled_start, v.actual_start, v.create_date)::date AS period_date,
                    v.state AS state,
                    v.priority AS priority,
                    v.completion_outcome AS completion_outcome,
                    CASE
                        WHEN v.actual_start IS NOT NULL AND v.actual_end IS NOT NULL
                        THEN EXTRACT(EPOCH FROM (v.actual_end - v.actual_start)) / 3600.0
                        ELSE 0.0
                    END AS duration_hours,
                    COALESCE(i.inspection_count, 0) AS inspection_count,
                    COALESCE(t.treatment_count, 0) AS treatment_count,
                    COALESCE(a.anomaly_count, 0) AS anomaly_count,
                    COALESCE(a.open_anomaly_count, 0) AS open_anomaly_count,
                    COALESCE(r.reservice_count, 0) AS reservice_count,
                    COALESCE(q.quality_check_count, 0) AS quality_check_count,
                    COALESCE(q.open_quality_nc_count, 0) AS open_quality_nc_count,
                    COALESCE(sc.stock_consumption_qty, 0) AS stock_consumption_qty,
                    COALESCE(b.billable_amount, 0) AS billable_amount,
                    c.currency_id AS currency_id
                FROM pest_visit v
                JOIN pest_site s ON s.id = v.site_id
                JOIN res_company c ON c.id = v.company_id
                LEFT JOIN (
                    SELECT visit_id, COUNT(*) AS inspection_count
                    FROM pest_inspection
                    GROUP BY visit_id
                ) i ON i.visit_id = v.id
                LEFT JOIN (
                    SELECT visit_id, COUNT(*) AS treatment_count
                    FROM pest_treatment
                    GROUP BY visit_id
                ) t ON t.visit_id = v.id
                LEFT JOIN (
                    SELECT visit_id,
                           COUNT(*) AS anomaly_count,
                           COUNT(*) FILTER (WHERE state IN ('open', 'in_progress')) AS open_anomaly_count
                    FROM pest_anomaly
                    GROUP BY visit_id
                ) a ON a.visit_id = v.id
                LEFT JOIN (
                    SELECT origin_visit_id AS visit_id, COUNT(*) AS reservice_count
                    FROM pest_reservice
                    GROUP BY origin_visit_id
                ) r ON r.visit_id = v.id
                LEFT JOIN (
                    SELECT visit_id,
                           COUNT(*) AS quality_check_count,
                           COUNT(*) FILTER (WHERE id IN (
                               SELECT check_id FROM pest_quality_nonconformity WHERE state IN ('open', 'in_progress')
                           )) AS open_quality_nc_count
                    FROM pest_quality_check
                    GROUP BY visit_id
                ) q ON q.visit_id = v.id
                LEFT JOIN (
                    SELECT visit_id, SUM(quantity) AS stock_consumption_qty
                    FROM pest_stock_trace
                    GROUP BY visit_id
                ) sc ON sc.visit_id = v.id
                LEFT JOIN (
                    SELECT visit_id, SUM(amount) AS billable_amount
                    FROM pest_billing_item
                    WHERE visit_id IS NOT NULL AND state != 'cancelled'
                    GROUP BY visit_id
                ) b ON b.visit_id = v.id
            )
        ''')
