from odoo import fields, models, tools


class PestAnalyticsContractKpi(models.Model):
    _name = 'pest.analytics.contract.kpi'
    _description = 'PestOps Contract KPI'
    _auto = False
    _rec_name = 'contract_id'
    _order = 'end_date asc, contract_id'

    contract_id = fields.Many2one('pest.contract', readonly=True)
    company_id = fields.Many2one('res.company', readonly=True)
    partner_id = fields.Many2one('res.partner', readonly=True)
    service_type = fields.Selection([
        ('preventive', 'Preventive Pest Control'), ('curative', 'Curative Pest Control'),
        ('integrated', 'Integrated Pest Management'), ('disinfection', 'Disinfection'),
        ('fumigation', 'Fumigation'), ('other', 'Other')
    ], readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'), ('confirmed', 'Confirmed'), ('suspended', 'Suspended'),
        ('to_renew', 'To Renew'), ('expired', 'Expired'), ('cancelled', 'Cancelled')
    ], readonly=True)
    start_date = fields.Date(readonly=True)
    end_date = fields.Date(readonly=True)
    days_remaining = fields.Integer(readonly=True)
    site_count = fields.Integer(readonly=True)
    visit_count = fields.Integer(readonly=True)
    done_visit_count = fields.Integer(readonly=True)
    late_visit_count = fields.Integer(readonly=True)
    open_anomaly_count = fields.Integer(readonly=True)
    open_reservice_count = fields.Integer(readonly=True)
    amount = fields.Monetary(readonly=True)
    to_invoice_amount = fields.Monetary(readonly=True)
    invoiced_amount = fields.Monetary(readonly=True)
    billed_ratio = fields.Float(readonly=True)
    currency_id = fields.Many2one('res.currency', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f'''\
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    c.id AS id,
                    c.id AS contract_id,
                    c.company_id AS company_id,
                    c.partner_id AS partner_id,
                    c.service_type AS service_type,
                    c.state AS state,
                    c.start_date AS start_date,
                    c.end_date AS end_date,
                    CASE WHEN c.end_date IS NULL THEN NULL ELSE (c.end_date - CURRENT_DATE) END AS days_remaining,
                    COALESCE(s.site_count, 0) AS site_count,
                    COALESCE(v.visit_count, 0) AS visit_count,
                    COALESCE(v.done_visit_count, 0) AS done_visit_count,
                    COALESCE(v.late_visit_count, 0) AS late_visit_count,
                    COALESCE(a.open_anomaly_count, 0) AS open_anomaly_count,
                    COALESCE(r.open_reservice_count, 0) AS open_reservice_count,
                    c.amount AS amount,
                    COALESCE(b.to_invoice_amount, 0) AS to_invoice_amount,
                    COALESCE(b.invoiced_amount, 0) AS invoiced_amount,
                    CASE WHEN COALESCE(c.amount, 0) > 0 THEN COALESCE(b.invoiced_amount, 0) / c.amount * 100 ELSE 0 END AS billed_ratio,
                    c.currency_id AS currency_id
                FROM pest_contract c
                LEFT JOIN (
                    SELECT contract_id, COUNT(*) AS site_count
                    FROM pest_contract_site
                    GROUP BY contract_id
                ) s ON s.contract_id = c.id
                LEFT JOIN (
                    SELECT contract_id,
                           COUNT(*) AS visit_count,
                           COUNT(*) FILTER (WHERE state = 'done') AS done_visit_count,
                           COUNT(*) FILTER (WHERE state IN ('draft', 'scheduled') AND scheduled_start < NOW()) AS late_visit_count
                    FROM pest_visit
                    WHERE contract_id IS NOT NULL
                    GROUP BY contract_id
                ) v ON v.contract_id = c.id
                LEFT JOIN (
                    SELECT v.contract_id, COUNT(*) FILTER (WHERE a.state IN ('open', 'in_progress')) AS open_anomaly_count
                    FROM pest_anomaly a
                    JOIN pest_visit v ON v.id = a.visit_id
                    WHERE v.contract_id IS NOT NULL
                    GROUP BY v.contract_id
                ) a ON a.contract_id = c.id
                LEFT JOIN (
                    SELECT contract_id, COUNT(*) FILTER (WHERE r.state IN ('draft', 'open', 'in_progress')) AS open_reservice_count
                    FROM pest_reservice r
                    JOIN pest_visit v ON v.id = r.origin_visit_id
                    WHERE v.contract_id IS NOT NULL
                    GROUP BY contract_id
                ) r ON r.contract_id = c.id
                LEFT JOIN (
                    SELECT contract_id,
                           SUM(amount) FILTER (WHERE state = 'to_invoice') AS to_invoice_amount,
                           SUM(amount) FILTER (WHERE state = 'invoiced') AS invoiced_amount
                    FROM pest_billing_item
                    GROUP BY contract_id
                ) b ON b.contract_id = c.id
            )
        ''')
