# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PriceWatchRule(models.Model):
    _name = "price.watch.rule"
    _description = "Price Watch Rule"
    _order = "id"

    name = fields.Char(required=True)
    threshold_pct = fields.Float(
        string="Threshold (%)", default=5.0, required=True,
        help="At least this variation between two purchases of the same "
             "product raises an alert.")
    notify_user_id = fields.Many2one("res.users", string="Notify")
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
    note = fields.Text()

    @api.constrains("threshold_pct")
    def _check_threshold(self):
        for rule in self:
            if rule.threshold_pct < 0.0:
                raise ValidationError(
                    _("The threshold cannot be negative."))
