from odoo import fields, models, tools


class PestAnalyticsCompanyKpi(models.Model):
    _name = 'pest.analytics.company.kpi'
    _description = 'PestOps Executive Company KPI'
    _auto = False
    _rec_name = 'company_id'
    _order = 'company_id'

    company_id = fields.Many2one('res.company', readonly=True)
    active_site_count = fields.Integer(readonly=True)
    active_contract_count = fields.Integer(readonly=True)
    visits_next_7d = fields.Integer(readonly=True)
    visits_done_30d = fields.Integer(readonly=True)
    late_visit_count = fields.Integer(readonly=True)
    open_anomaly_count = fields.Integer(readonly=True)
    critical_anomaly_count = fields.Integer(readonly=True)
    open_reservice_count = fields.Integer(readonly=True)
    open_quality_nc_count = fields.Integer(readonly=True)
    critical_quality_nc_count = fields.Integer(readonly=True)
    stock_alert_count = fields.Integer(readonly=True)
    equipment_due_count = fields.Integer(readonly=True)
    billing_to_invoice_amount = fields.Monetary(readonly=True)
    invoiced_30d_amount = fields.Monetary(readonly=True)
    maintenance_cost_30d = fields.Monetary(readonly=True)
    stock_consumption_30d_qty = fields.Float(readonly=True)
    currency_id = fields.Many2one('res.currency', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f'''\
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    c.id AS id,
                    c.id AS company_id,
                    COALESCE(s.active_site_count, 0) AS active_site_count,
                    COALESCE(ct.active_contract_count, 0) AS active_contract_count,
                    COALESCE(v7.visits_next_7d, 0) AS visits_next_7d,
                    COALESCE(v30.visits_done_30d, 0) AS visits_done_30d,
                    COALESCE(vlate.late_visit_count, 0) AS late_visit_count,
                    COALESCE(a.open_anomaly_count, 0) AS open_anomaly_count,
                    COALESCE(a.critical_anomaly_count, 0) AS critical_anomaly_count,
                    COALESCE(r.open_reservice_count, 0) AS open_reservice_count,
                    COALESCE(q.open_quality_nc_count, 0) AS open_quality_nc_count,
                    COALESCE(q.critical_quality_nc_count, 0) AS critical_quality_nc_count,
                    COALESCE(st.stock_alert_count, 0) AS stock_alert_count,
                    COALESCE(eq.equipment_due_count, 0) AS equipment_due_count,
                    COALESCE(b.to_invoice_amount, 0) AS billing_to_invoice_amount,
                    COALESCE(b.invoiced_30d_amount, 0) AS invoiced_30d_amount,
                    COALESCE(m.maintenance_cost_30d, 0) AS maintenance_cost_30d,
                    COALESCE(sc.stock_consumption_30d_qty, 0) AS stock_consumption_30d_qty,
                    c.currency_id AS currency_id
                FROM res_company c
                LEFT JOIN (
                    SELECT company_id, COUNT(*) AS active_site_count
                    FROM pest_site
                    WHERE active = TRUE
                    GROUP BY company_id
                ) s ON s.company_id = c.id
                LEFT JOIN (
                    SELECT company_id, COUNT(*) AS active_contract_count
                    FROM pest_contract
                    WHERE state IN ('confirmed', 'suspended', 'to_renew')
                      AND start_date <= CURRENT_DATE
                      AND (end_date IS NULL OR end_date >= CURRENT_DATE)
                    GROUP BY company_id
                ) ct ON ct.company_id = c.id
                LEFT JOIN (
                    SELECT company_id, COUNT(*) AS visits_next_7d
                    FROM pest_visit
                    WHERE state IN ('draft', 'scheduled')
                      AND scheduled_start >= NOW()
                      AND scheduled_start < NOW() + INTERVAL '7 days'
                    GROUP BY company_id
                ) v7 ON v7.company_id = c.id
                LEFT JOIN (
                    SELECT company_id, COUNT(*) AS visits_done_30d
                    FROM pest_visit
                    WHERE state = 'done'
                      AND actual_end >= NOW() - INTERVAL '30 days'
                    GROUP BY company_id
                ) v30 ON v30.company_id = c.id
                LEFT JOIN (
                    SELECT company_id, COUNT(*) AS late_visit_count
                    FROM pest_visit
                    WHERE state IN ('draft', 'scheduled')
                      AND scheduled_start < NOW()
                    GROUP BY company_id
                ) vlate ON vlate.company_id = c.id
                LEFT JOIN (
                    SELECT company_id,
                           COUNT(*) FILTER (WHERE state IN ('open', 'in_progress')) AS open_anomaly_count,
                           COUNT(*) FILTER (WHERE severity = 'critical' AND state IN ('open', 'in_progress')) AS critical_anomaly_count
                    FROM pest_anomaly
                    GROUP BY company_id
                ) a ON a.company_id = c.id
                LEFT JOIN (
                    SELECT v.company_id,
                           COUNT(*) FILTER (WHERE r.state IN ('draft', 'open', 'in_progress')) AS open_reservice_count
                    FROM pest_reservice r
                    JOIN pest_visit v ON v.id = r.origin_visit_id
                    GROUP BY v.company_id
                ) r ON r.company_id = c.id
                LEFT JOIN (
                    SELECT company_id,
                           COUNT(*) FILTER (WHERE state IN ('open', 'in_progress')) AS open_quality_nc_count,
                           COUNT(*) FILTER (WHERE severity = 'critical' AND state IN ('open', 'in_progress')) AS critical_quality_nc_count
                    FROM pest_quality_nonconformity
                    GROUP BY company_id
                ) q ON q.company_id = c.id
                LEFT JOIN (
                    SELECT th.company_id, COUNT(*) AS stock_alert_count
                    FROM pest_stock_threshold th
                    LEFT JOIN (
                        SELECT company_id, product_id, location_id,
                               SUM(quantity - reserved_quantity) AS current_qty
                        FROM stock_quant
                        GROUP BY company_id, product_id, location_id
                    ) sq ON sq.company_id = th.company_id
                       AND sq.product_id = th.product_id
                       AND sq.location_id = th.location_id
                    WHERE th.active = TRUE
                      AND COALESCE(sq.current_qty, 0) <= th.minimum_qty
                    GROUP BY th.company_id
                ) st ON st.company_id = c.id
                LEFT JOIN (
                    SELECT company_id, COUNT(*) AS equipment_due_count
                    FROM pest_equipment
                    WHERE active = TRUE AND has_due_action = TRUE
                    GROUP BY company_id
                ) eq ON eq.company_id = c.id
                LEFT JOIN (
                    SELECT company_id,
                           SUM(amount) FILTER (WHERE state = 'to_invoice') AS to_invoice_amount,
                           SUM(amount) FILTER (WHERE state = 'invoiced' AND invoice_date >= CURRENT_DATE - INTERVAL '30 days') AS invoiced_30d_amount
                    FROM pest_billing_item
                    GROUP BY company_id
                ) b ON b.company_id = c.id
                LEFT JOIN (
                    SELECT e.company_id,
                           SUM(m.cost) FILTER (WHERE m.state = 'done' AND m.completed_date >= CURRENT_DATE - INTERVAL '30 days') AS maintenance_cost_30d
                    FROM pest_equipment_maintenance m
                    JOIN pest_equipment e ON e.id = m.equipment_id
                    GROUP BY e.company_id
                ) m ON m.company_id = c.id
                LEFT JOIN (
                    SELECT company_id, SUM(quantity) AS stock_consumption_30d_qty
                    FROM pest_stock_trace
                    WHERE consumed_at >= NOW() - INTERVAL '30 days'
                    GROUP BY company_id
                ) sc ON sc.company_id = c.id
            )
        ''')
