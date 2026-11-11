# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RetainerUsage(models.Model):
    _name = "retainer.usage"
    _description = "Retainer Usage"
    _inherit = ["mail.thread"]
    _order = "usage_date desc, id desc"

    bank_id = fields.Many2one(
        "retainer.bank", string="Retainer Bank", required=True,
        ondelete="cascade", index=True)
    partner_id = fields.Many2one(
        related="bank_id.partner_id", store=True, string="Customer")
    usage_date = fields.Date(
        string="Date", required=True, default=fields.Date.context_today, tracking=True)
    hours = fields.Float(string="Hours", required=True, tracking=True)
    description = fields.Char(help="Short description of the work performed.")
    company_id = fields.Many2one(
        related="bank_id.company_id", store=True, readonly=True, index=True)

    @api.constrains("hours")
    def _check_hours(self):
        for usage in self:
            if usage.hours <= 0:
                raise ValidationError(_(
                    "The usage hours on %s must be above zero.",
                    usage.bank_id.name))

    @api.constrains("hours", "bank_id")
    def _check_balance(self):
        for usage in self:
            bank = usage.bank_id
            if not bank:
                continue
            total = sum(bank.usage_ids.mapped("hours"))
            if total - bank.hours_purchased > 0.00001:
                raise ValidationError(_(
                    "The usage on %s exceeds the remaining hours of the retainer.",
                    bank.name))
