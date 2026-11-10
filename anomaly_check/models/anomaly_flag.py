# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AnomalyFlag(models.Model):
    _name = "anomaly.flag"
    _description = "Anomaly Flag"
    _inherit = ["mail.thread"]
    _order = "flag_date desc, id desc"

    name = fields.Char(
        required=True, default=lambda self: _("Check %s")
        % fields.Date.context_today(self),
        help="Reference of the flagged check.")
    rule_id = fields.Many2one(
        "anomaly.rule", string="Rule", required=True, ondelete="restrict",
        index=True, tracking=True)
    document_ref = fields.Char(
        string="Document Reference", required=True, tracking=True,
        help="Reference of the bill or document under review.")
    partner_name = fields.Char(
        string="Supplier", help="Name of the supplier on the document.")
    quantity = fields.Float(default=1.0)
    tax_amount = fields.Float(string="Tax Amount")
    total_amount = fields.Float(string="Total Amount")
    flag_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    state = fields.Selection(
        [("new", "New"), ("confirmed", "Confirmed"),
         ("resolved", "Resolved"), ("rejected", "Rejected")],
        default="new", required=True, tracking=True, index=True)
    reason = fields.Text(help="Why this document was flagged.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.constrains("total_amount", "tax_amount")
    def _check_amounts(self):
        for flag in self:
            if flag.total_amount < 0:
                raise ValidationError(_(
                    "The total amount of %s cannot be negative.",
                    flag.document_ref))
            if flag.tax_amount < 0:
                raise ValidationError(_(
                    "The tax amount of %s cannot be negative.",
                    flag.document_ref))
            if flag.tax_amount > flag.total_amount and flag.total_amount:
                raise ValidationError(_(
                    "The tax amount of %s cannot exceed the total amount.",
                    flag.document_ref))

    @api.constrains("quantity")
    def _check_quantity(self):
        for flag in self:
            if flag.quantity <= 0:
                raise ValidationError(_(
                    "The quantity on %s must be greater than zero.",
                    flag.document_ref))

    def action_confirm(self):
        for flag in self:
            if flag.state != "new":
                raise ValidationError(_(
                    "Only new checks can be confirmed."))
            flag.state = "confirmed"
            flag.message_post(body=_("The finding was confirmed for review."))
        return True

    def action_resolve(self):
        for flag in self:
            if flag.state not in ("new", "confirmed"):
                raise ValidationError(_(
                    "Only open checks can be resolved."))
            flag.state = "resolved"
            flag.message_post(body=_("The finding was resolved."))
        return True

    def action_reject(self):
        for flag in self:
            if flag.state not in ("new", "confirmed"):
                raise ValidationError(_(
                    "Only open checks can be rejected."))
            flag.state = "rejected"
            flag.message_post(body=_("The finding was rejected."))
        return True
