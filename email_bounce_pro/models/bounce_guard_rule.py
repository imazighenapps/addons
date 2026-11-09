# -*- coding: utf-8 -*-
from odoo import fields, models, _


class BounceGuardRule(models.Model):
    _name = "bounce.guard.rule"
    _description = "Bounce Alert Rule"
    _order = "id"

    name = fields.Char(required=True)
    threshold = fields.Integer(
        default=2,
        help="Number of unhandled bounces after which the contact email "
             "is flagged.")
    notify_user_id = fields.Many2one(
        "res.users", string="Notify",
        help="This user receives the activity when a rule trips and no "
             "owner is named.")
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
    note = fields.Text()
