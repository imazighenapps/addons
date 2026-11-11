# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VatCheckLine(models.Model):
    _name = "vat.check.line"
    _description = "VAT Cross Check Line"
    _inherit = ["mail.thread"]
    _order = "box_name, id"

    name = fields.Char(
        compute="_compute_name", store=True,
        help="Display name combining the box and the period.")
    check_id = fields.Many2one(
        "vat.check", string="Cross Check", required=True,
        ondelete="cascade", index=True, tracking=True)
    box_name = fields.Char(
        string="VAT Box", required=True, tracking=True,
        help="Code or label of the VAT box being verified.")
    reported_amount = fields.Monetary(
        string="Reported Amount", currency_field="currency_id", required=True,
        help="Amount declared in the VAT report for this box.")
    ledger_amount = fields.Monetary(
        string="Ledger Amount", currency_field="currency_id", required=True,
        help="Amount recomputed from the underlying journal entries.")
    difference_amount = fields.Monetary(
        string="Difference", currency_field="currency_id",
        compute="_compute_difference", store=True,
        help="Gap between the reported amount and the ledger amount.")
    explanation = fields.Text(
        help="Reason for the difference, filled in during the review.")
    reviewed = fields.Boolean(
        default=False, tracking=True,
        help="Ticked once the difference has been explained and reviewed.")
    currency_id = fields.Many2one(
        "res.currency", related="check_id.company_id.currency_id",
        store=True, readonly=True)
    company_id = fields.Many2one(
        related="check_id.company_id", store=True, readonly=True, index=True)
    state = fields.Selection(
        related="check_id.state", store=True, readonly=True)

    @api.depends("box_name", "check_id.name")
    def _compute_name(self):
        for line in self:
            if line.box_name and line.check_id:
                line.name = "%s / %s" % (line.check_id.name, line.box_name)
            else:
                line.name = line.box_name or _("VAT Box")

    @api.depends("reported_amount", "ledger_amount")
    def _compute_difference(self):
        for line in self:
            line.difference_amount = line.reported_amount - line.ledger_amount

    @api.constrains("reviewed", "difference_amount", "explanation")
    def _check_explanation(self):
        for line in self:
            if (line.reviewed and abs(line.difference_amount) > 0.00001
                    and not (line.explanation and line.explanation.strip())):
                raise ValidationError(_(
                    "Explain the difference on box %s before marking it as "
                    "reviewed.", line.box_name))

    def action_mark_reviewed(self):
        for line in self:
            if line.check_id.state == "closed":
                raise ValidationError(_(
                    "A closed VAT cross-check cannot be reviewed again."))
            line.reviewed = True
            line.message_post(body=_("The VAT box was marked as reviewed."))
        return True
