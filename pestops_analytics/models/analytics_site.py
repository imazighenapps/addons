from odoo import fields, models, tools


class PestAnalyticsSiteKpi(models.Model):
    _name = 'pest.analytics.site.kpi'
    _description = 'PestOps Site KPI'
    _auto = False
    _rec_name = 'site_id'
    _order = 'site_id'

    site_id = fields.Many2one('pest.site', readonly=True)
    company_id = fields.Many2one('res.company', readonly=True)
    partner_id = fields.Many2one('res.partner', readonly=True)
    site_type = fields.Selection([
        ('hotel', 'Hotel'), ('restaurant', 'Restaurant'), ('industry', 'Industrial'),
        ('warehouse', 'Warehouse'), ('retail', 'Retail'), ('healthcare', 'Healthcare'),
        ('education', 'Education'), ('office', 'Office'), ('residential', 'Residential'), ('other', 'Other')
    ], readonly=True)
    risk_level_id = fields.Many2one('pest.risk.level', readonly=True)
    active = fields.Boolean(readonly=True)
    visit_count = fields.Integer(readonly=True)
    done_visit_count = fields.Integer(readonly=True)
    late_visit_count = fields.Integer(readonly=True)
    treatment_count = fields.Integer(readonly=True)
    open_anomaly_count = fields.Integer(readonly=True)
    critical_anomaly_count = fields.Integer(readonly=True)
    open_reservice_count = fields.Integer(readonly=True)
    quality_check_count = fields.Integer(readonly=True)
    open_quality_nc_count = fields.Integer(readonly=True)
    critical_quality_nc_count = fields.Integer(readonly=True)
    stock_consumption_qty = fields.Float(readonly=True)
    billable_amount = fields.Monetary(readonly=True)
    maintenance_cost = fields.Monetary(readonly=True)
    currency_id = fields.Many2one('res.currency', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f'''\
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    s.id AS id,
                    s.id AS site_id,
                    s.company_id AS company_id,
                    s.partner_id AS partner_id,
                    s.site_type AS site_type,
                    s.risk_level_id AS risk_level_id,
                    s.active AS active,
                    COALESCE(v.visit_count, 0) AS visit_count,
                    COALESCE(v.done_visit_count, 0) AS done_visit_count,
                    COALESCE(v.late_visit_count, 0) AS late_visit_count,
                    COALESCE(v.treatment_count, 0) AS treatment_count,
                    COALESCE(a.open_anomaly_count, 0) AS open_anomaly_count,
                    COALESCE(a.critical_anomaly_count, 0) AS critical_anomaly_count,
                    COALESCE(r.open_reservice_count, 0) AS open_reservice_count,
                    COALESCE(q.quality_check_count, 0) AS quality_check_count,
                    COALESCE(q.open_quality_nc_count, 0) AS open_quality_nc_count,
                    COALESCE(q.critical_quality_nc_count, 0) AS critical_quality_nc_count,
                    COALESCE(sc.stock_consumption_qty, 0) AS stock_consumption_qty,
                    COALESCE(b.billable_amount, 0) AS billable_amount,
                    COALESCE(m.maintenance_cost, 0) AS maintenance_cost,
                    c.currency_id AS currency_id
                FROM pest_site s
                JOIN res_company c ON c.id = s.company_id
                LEFT JOIN (
                    SELECT v.site_id,
                           COUNT(DISTINCT v.id) AS visit_count,
                           COUNT(DISTINCT v.id) FILTER (WHERE v.state = 'done') AS done_visit_count,
                           COUNT(DISTINCT v.id) FILTER (WHERE v.state IN ('draft', 'scheduled') AND v.scheduled_start < NOW()) AS late_visit_count,
                           COUNT(DISTINCT t.id) AS treatment_count
                    FROM pest_visit v
                    LEFT JOIN pest_treatment t ON t.visit_id = v.id
                    GROUP BY v.site_id
                ) v ON v.site_id = s.id
                LEFT JOIN (
                    SELECT site_id,
                           COUNT(*) FILTER (WHERE state IN ('open', 'in_progress')) AS open_anomaly_count,
                           COUNT(*) FILTER (WHERE severity = 'critical' AND state IN ('open', 'in_progress')) AS critical_anomaly_count
                    FROM pest_anomaly
                    GROUP BY site_id
                ) a ON a.site_id = s.id
                LEFT JOIN (
                    SELECT site_id, COUNT(*) FILTER (WHERE state IN ('draft', 'open', 'in_progress')) AS open_reservice_count
                    FROM pest_reservice
                    GROUP BY site_id
                ) r ON r.site_id = s.id
                LEFT JOIN (
                    SELECT q.site_id,
                           COALESCE(qc.quality_check_count, 0) AS quality_check_count,
                           q.open_quality_nc_count,
                           q.critical_quality_nc_count
                    FROM (
                        SELECT site_id,
                               COUNT(*) FILTER (WHERE state IN ('open', 'in_progress')) AS open_quality_nc_count,
                               COUNT(*) FILTER (WHERE severity = 'critical' AND state IN ('open', 'in_progress')) AS critical_quality_nc_count
                        FROM pest_quality_nonconformity
                        GROUP BY site_id
                    ) q
                    LEFT JOIN (
                        SELECT site_id, COUNT(*) AS quality_check_count
                        FROM pest_quality_check
                        GROUP BY site_id
                    ) qc ON qc.site_id = q.site_id
                    UNION ALL
                    SELECT qc.site_id, qc.quality_check_count, 0, 0
                    FROM (
                        SELECT site_id, COUNT(*) AS quality_check_count
                        FROM pest_quality_check
                        GROUP BY site_id
                    ) qc
                    WHERE NOT EXISTS (SELECT 1 FROM pest_quality_nonconformity n WHERE n.site_id = qc.site_id)
                ) q ON q.site_id = s.id
                LEFT JOIN (
                    SELECT site_id, SUM(quantity) AS stock_consumption_qty
                    FROM pest_stock_trace
                    GROUP BY site_id
                ) sc ON sc.site_id = s.id
                LEFT JOIN (
                    SELECT v.site_id, SUM(b.amount) AS billable_amount
                    FROM pest_billing_item b
                    JOIN pest_visit v ON v.id = b.visit_id
                    WHERE b.state != 'cancelled'
                    GROUP BY v.site_id
                ) b ON b.site_id = s.id
                LEFT JOIN (
                    SELECT e.assigned_site_id AS site_id, SUM(m.cost) AS maintenance_cost
                    FROM pest_equipment e
                    JOIN pest_equipment_maintenance m ON m.equipment_id = e.id
                    WHERE m.state = 'done'
                    GROUP BY e.assigned_site_id
                ) m ON m.site_id = s.id
            )
        ''')
