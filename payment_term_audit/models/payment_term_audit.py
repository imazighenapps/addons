# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PaymentTermAudit(models.Model):
    _name = "payment.term.audit"
    _description = "Payment Term Audit"
    _inherit = ["mail.thread"]
    _order = "date_to desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: "Audit %s"
        % fields.Date.context_today(self))
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    tolerance = fields.Integer(
        default=0,
        help="Number of days between the contract and the invoice that is "
             "still accepted as a match.")
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    line_ids = fields.One2many(
        "payment.term.audit.line", "audit_id", string="Anomalies")
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done")],
        default="draft", required=True, tracking=True, index=True)
    checked_count = fields.Integer(compute="_compute_counts")
    anomaly_count = fields.Integer(compute="_compute_counts")
    note = fields.Text()

    _sql_constraints = [
        ('period_uniq', "unique(company_id, date_from, date_to)", "An audit already covers this period for this company."),
    ]

    @api.depends("line_ids")
    def _compute_counts(self):
        for audit in self:
            audit.checked_count = len(audit.line_ids)
            audit.anomaly_count = len(audit.line_ids.mapped(
                "move_id"))

    def _expected_days(self, partner):
        """Contract days promised by the partner payment term.

        The number of days lives on the term line, but the field was renamed
        across versions (nb_days in 20.0, delay before): detect it once.
        """
        term = partner.with_company(
            self.company_id).property_payment_term_id
        if not term:
            return 0, False
        line_fields = term.line_ids._fields
        days_name = "nb_days" if "nb_days" in line_fields else "delay"
        return sum(term.line_ids.mapped(days_name)), term

    def action_run(self):
        for audit in self:
            scans = self.env["account.move"].search([
                ("move_type", "=", "out_invoice"),
                ("state", "=", "posted"),
                ("invoice_date", ">=", audit.date_from),
                ("invoice_date", "<=", audit.date_to),
                ("company_id", "=", audit.company_id.id),
            ])
            for move in scans:
                existing = audit.line_ids.filtered(
                    lambda line: line.move_id == move)
                if existing:
                    continue
                expected_days, term = audit._expected_days(move.partner_id)
                actual_days = 0
                if move.invoice_date and move.invoice_date_due:
                    actual_days = (
                        move.invoice_date_due - move.invoice_date).days
                gap_days = actual_days - expected_days
                if not term:
                    kind = "missing_term"
                elif abs(gap_days) > audit.tolerance:
                    kind = "mismatch"
                else:
                    continue
                audit.write({"line_ids": [(0, 0, {
                    "partner_id": move.partner_id.id,
                    "move_id": move.id,
                    "invoice_date": move.invoice_date,
                    "invoice_date_due": move.invoice_date_due,
                    "expected_days": expected_days,
                    "actual_days": actual_days,
                    "gap_days": gap_days,
                    "kind": kind,
                })]})
            audit.write({"state": "done"})
        return True

    def action_reset(self):
        for audit in self:
            audit.line_ids.unlink()
            audit.write({"state": "draft"})
        return True
