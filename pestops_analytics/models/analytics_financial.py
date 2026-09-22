from odoo import fields, models, tools


class PestAnalyticsFinancialReport(models.Model):
    _name = 'pest.analytics.financial.report'
    _description = 'PestOps Financial Analytics'
    _auto = False
    _rec_name = 'billing_item_id'
    _order = 'invoice_date desc, billing_item_id desc'

    billing_item_id = fields.Many2one('pest.billing.item', readonly=True)
    company_id = fields.Many2one('res.company', readonly=True)
    contract_id = fields.Many2one('pest.contract', readonly=True)
    partner_id = fields.Many2one('res.partner', readonly=True)
    visit_id = fields.Many2one('pest.visit', readonly=True)
    product_id = fields.Many2one('product.product', readonly=True)
    source_type = fields.Selection([
        ('contract_period', 'Contract Period'), ('visit', 'Service Visit'), ('manual', 'Additional Service')
    ], readonly=True)
    state = fields.Selection([
        ('to_invoice', 'To Invoice'), ('invoiced', 'Invoiced'), ('cancelled', 'Cancelled')
    ], readonly=True)
    invoice_date = fields.Date(readonly=True)
    invoice_month = fields.Date(readonly=True)
    period_start = fields.Date(readonly=True)
    period_end = fields.Date(readonly=True)
    quantity = fields.Float(readonly=True)
    unit_price = fields.Monetary(readonly=True)
    amount = fields.Monetary(readonly=True)
    currency_id = fields.Many2one('res.currency', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f'''\
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    b.id AS id,
                    b.id AS billing_item_id,
                    b.company_id AS company_id,
                    b.contract_id AS contract_id,
                    b.partner_id AS partner_id,
                    b.visit_id AS visit_id,
                    b.product_id AS product_id,
                    b.source_type AS source_type,
                    b.state AS state,
                    b.invoice_date AS invoice_date,
                    DATE_TRUNC('month', b.invoice_date)::date AS invoice_month,
                    b.period_start AS period_start,
                    b.period_end AS period_end,
                    b.quantity AS quantity,
                    b.unit_price AS unit_price,
                    b.amount AS amount,
                    b.currency_id AS currency_id
                FROM pest_billing_item b
            )
        ''')
