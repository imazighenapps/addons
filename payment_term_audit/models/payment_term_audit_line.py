# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import UserError


class PaymentTermAuditLine(models.Model):
    _name = "payment.term.audit.line"
    _description = "Payment Term Anomaly"
    _order = "gap_days desc, id desc"

    audit_id = fields.Many2one(
        "payment.term.audit", string="Audit", required=True,
        ondelete="cascade", index=True)
    company_id = fields.Many2one(
        related="audit_id.company_id", store=True, readonly=True)
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True)
    move_id = fields.Many2one(
        "account.move", string="Invoice", required=True)
    invoice_date = fields.Date()
    invoice_date_due = fields.Date()
    currency_id = fields.Many2one(
        related="move_id.currency_id", store=True, readonly=True)
    amount_residual = fields.Monetary(
        string="Amount due", currency_field="currency_id",
        readonly=True)
    expected_days = fields.Integer()
    actual_days = fields.Integer()
    gap_days = fields.Integer()
    kind = fields.Selection(
        [("mismatch", "Term mismatch"),
         ("missing_term", "No payment term"),
         ("no_due_date", "No due date")], required=True)
    state = fields.Selection(
        [("new", "New"), ("ignored", "Ignored")],
        default="new", required=True)
    note = fields.Text()

    _sql_constraints = [
        ('move_uniq', "unique(audit_id, move_id)", "This invoice is already flagged by the audit."),
    ]

    def action_ignore(self):
        for line in self.filtered(lambda item: item.state != "ignored"):
            line.write({"state": "ignored"})
        return True

    def action_reopen(self):
        for line in self.filtered(lambda item: item.state == "ignored"):
            line.write({"state": "new"})
        return True
