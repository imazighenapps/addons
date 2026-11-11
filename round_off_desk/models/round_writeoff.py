# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RoundWriteoff(models.Model):
    _name = "round.writeoff"
    _description = "Rounding Write-Off"
    _inherit = ["mail.thread"]
    _order = "writeoff_on desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Write-Off %s")
        % fields.Date.context_today(self),
        help="Reference of the write-off, generated at creation.")
    rule_id = fields.Many2one(
        "round.rule", string="Rule", required=True,
        ondelete="restrict", index=True, tracking=True)
    source_ref = fields.Char(
        string="Source Reference", required=True, tracking=True,
        help="Invoice, payment or statement reference carrying the gap.")
    amount = fields.Monetary(
        string="Difference", currency_field="currency_id", required=True,
        tracking=True, help="Small amount to absorb with this write-off.")
    writeoff_on = fields.Date(
        string="Date", required=True, default=fields.Date.context_today,
        tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("posted", "Posted")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    posted_on = fields.Date(string="Posted On", readonly=True, copy=False)
    currency_id = fields.Many2one(
        "res.currency", related="rule_id.currency_id", store=True,
        readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.constrains("amount", "rule_id")
    def _check_amount(self):
        for writeoff in self:
            if writeoff.amount <= 0.0:
                raise ValidationError(_(
                    "The difference on %s must be above zero.",
                    writeoff.name))
            if (writeoff.rule_id
                    and writeoff.amount > writeoff.rule_id.max_amount):
                raise ValidationError(_(
                    "The difference of %s exceeds the maximum allowed by "
                    "rule %s.", writeoff.name, writeoff.rule_id.name))

    def action_post(self):
        for writeoff in self:
            if writeoff.state != "draft":
                raise ValidationError(_(
                    "Only a draft write-off can be posted."))
            writeoff.write({
                "state": "posted",
                "posted_on": fields.Date.context_today(writeoff),
            })
            writeoff.message_post(body=_(
                "The rounding difference was posted and cleared."))
        return True
