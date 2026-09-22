from odoo import fields, models, tools


class PestAnalyticsTechnicianKpi(models.Model):
    _name = 'pest.analytics.technician.kpi'
    _description = 'PestOps Technician KPI'
    _auto = False
    _rec_name = 'technician_id'
    _order = 'technician_id'

    technician_id = fields.Many2one('res.users', readonly=True)
    company_id = fields.Many2one('res.company', readonly=True)
    visit_count = fields.Integer(readonly=True)
    done_visit_count = fields.Integer(readonly=True)
    high_priority_done_count = fields.Integer(readonly=True)
    duration_hours = fields.Float(readonly=True)
    treatment_count = fields.Integer(readonly=True)
    anomaly_count = fields.Integer(readonly=True)
    open_anomaly_count = fields.Integer(readonly=True)
    reservice_count = fields.Integer(readonly=True)
    quality_check_count = fields.Integer(readonly=True)
    failed_quality_check_count = fields.Integer(readonly=True)
    open_quality_nc_count = fields.Integer(readonly=True)
    stock_consumption_qty = fields.Float(readonly=True)
    visit_billable_amount = fields.Monetary(readonly=True)
    currency_id = fields.Many2one('res.currency', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f'''\
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    u.id AS id,
                    u.id AS technician_id,
                    u.company_id AS company_id,
                    COALESCE(v.visit_count, 0) AS visit_count,
                    COALESCE(v.done_visit_count, 0) AS done_visit_count,
                    COALESCE(v.high_priority_done_count, 0) AS high_priority_done_count,
                    COALESCE(v.duration_hours, 0) AS duration_hours,
                    COALESCE(t.treatment_count, 0) AS treatment_count,
                    COALESCE(a.anomaly_count, 0) AS anomaly_count,
                    COALESCE(a.open_anomaly_count, 0) AS open_anomaly_count,
                    COALESCE(r.reservice_count, 0) AS reservice_count,
                    COALESCE(q.quality_check_count, 0) AS quality_check_count,
                    COALESCE(q.failed_quality_check_count, 0) AS failed_quality_check_count,
                    COALESCE(q.open_quality_nc_count, 0) AS open_quality_nc_count,
                    COALESCE(sc.stock_consumption_qty, 0) AS stock_consumption_qty,
                    COALESCE(b.visit_billable_amount, 0) AS visit_billable_amount,
                    c.currency_id AS currency_id
                FROM res_users u
                LEFT JOIN res_company c ON c.id = u.company_id
                LEFT JOIN (
                    SELECT technician_id,
                           COUNT(*) AS visit_count,
                           COUNT(*) FILTER (WHERE state = 'done') AS done_visit_count,
                           COUNT(*) FILTER (WHERE state = 'done' AND priority = '1') AS high_priority_done_count,
                           SUM(CASE WHEN actual_start IS NOT NULL AND actual_end IS NOT NULL
                                    THEN EXTRACT(EPOCH FROM (actual_end - actual_start)) / 3600.0 ELSE 0 END) AS duration_hours
                    FROM pest_visit
                    WHERE technician_id IS NOT NULL
                    GROUP BY technician_id
                ) v ON v.technician_id = u.id
                LEFT JOIN (
                    SELECT technician_id, COUNT(*) AS treatment_count
                    FROM pest_treatment
                    WHERE technician_id IS NOT NULL
                    GROUP BY technician_id
                ) t ON t.technician_id = u.id
                LEFT JOIN (
                    SELECT technician_id,
                           COUNT(*) AS anomaly_count,
                           COUNT(*) FILTER (WHERE state IN ('open', 'in_progress')) AS open_anomaly_count
                    FROM pest_anomaly
                    WHERE technician_id IS NOT NULL
                    GROUP BY technician_id
                ) a ON a.technician_id = u.id
                LEFT JOIN (
                    SELECT technician_id, COUNT(*) AS reservice_count
                    FROM pest_visit v
                    JOIN pest_reservice r ON r.origin_visit_id = v.id
                    WHERE v.technician_id IS NOT NULL
                    GROUP BY technician_id
                ) r ON r.technician_id = u.id
                LEFT JOIN (
                    SELECT qc.technician_id,
                           COUNT(*) AS quality_check_count,
                           COUNT(*) FILTER (WHERE qc.result = 'non_compliant') AS failed_quality_check_count,
                           COUNT(DISTINCT nc.id) FILTER (WHERE nc.state IN ('open', 'in_progress')) AS open_quality_nc_count
                    FROM pest_quality_check qc
                    LEFT JOIN pest_quality_nonconformity nc ON nc.check_id = qc.id
                    WHERE qc.technician_id IS NOT NULL
                    GROUP BY qc.technician_id
                ) q ON q.technician_id = u.id
                LEFT JOIN (
                    SELECT technician_id, SUM(quantity) AS stock_consumption_qty
                    FROM pest_stock_trace
                    WHERE technician_id IS NOT NULL
                    GROUP BY technician_id
                ) sc ON sc.technician_id = u.id
                LEFT JOIN (
                    SELECT v.technician_id, SUM(b.amount) AS visit_billable_amount
                    FROM pest_billing_item b
                    JOIN pest_visit v ON v.id = b.visit_id
                    WHERE b.state != 'cancelled' AND v.technician_id IS NOT NULL
                    GROUP BY v.technician_id
                ) b ON b.technician_id = u.id
                WHERE u.active = TRUE
                  AND COALESCE(v.visit_count, 0) > 0
            )
        ''')
