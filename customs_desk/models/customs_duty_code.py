# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CustomsDutyCode(models.Model):
    _name = "customs.duty.code"
    _description = "Customs HS Code"
    _inherit = ["mail.thread"]
    _order = "code"

    name = fields.Char(
        string="Description", required=True, tracking=True,
        help="Short description of the goods covered by this HS code.")
    code = fields.Char(
        string="HS Code", required=True, tracking=True,
        help="Commodity code used on the customs declaration.")
    duty_rate = fields.Float(
        string="Duty Rate (%)", required=True, default=0.0, tracking=True,
        help="Percentage of the customs value charged as duty.")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.constrains("duty_rate")
    def _check_duty_rate(self):
        for duty_code in self:
            if duty_code.duty_rate < 0 or duty_code.duty_rate > 100:
                raise ValidationError(_(
                    "The duty rate of %s must be between 0 and 100.",
                    duty_code.code))
