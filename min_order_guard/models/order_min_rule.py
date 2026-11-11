# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class OrderMinRule(models.Model):
    _name = "order.min.rule"
    _description = "Minimum Order Rule"
    _inherit = ["mail.thread"]
    _order = "partner_name"

    name = fields.Char(required=True, tracking=True)
    partner_name = fields.Char(
        string="Customer", required=True, tracking=True,
        help="Exact customer name the minimum applies to.")
    min_amount = fields.Float(
        string="Minimum Amount",
        help="Lowest order value accepted for the customer.")
    min_quantity = fields.Integer(
        string="Minimum Quantity",
        help="Lowest quantity accepted for the customer.")
    exception_ids = fields.One2many(
        "order.min.exception", "rule_id", string="Exceptions")
    exception_count = fields.Integer(
        string="Exceptions", compute="_compute_exceptions")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("exception_ids", "exception_ids.state")
    def _compute_exceptions(self):
        for rule in self:
            rule.exception_count = len(rule.exception_ids)

    @api.constrains("min_amount", "min_quantity")
    def _check_minimums(self):
        for rule in self:
            if rule.min_amount < 0.0 or rule.min_quantity < 0:
                raise ValidationError(_(
                    "The minimums of %s must be positive.",
                    rule.partner_name))
            if rule.min_amount <= 0.0 and rule.min_quantity <= 0:
                raise ValidationError(_(
                    "The rule for %s needs a minimum amount or a "
                    "minimum quantity above zero.", rule.partner_name))
