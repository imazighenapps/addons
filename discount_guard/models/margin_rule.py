# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MarginRule(models.Model):
    _name = "margin.rule"
    _description = "Discount And Margin Floor"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    scope_type = fields.Selection(
        [("product", "Product"), ("category", "Category"),
         ("customer", "Customer"), ("global", "Every Line")],
        string="Rule Scope", default="product", required=True,
        tracking=True,
        help="What the floors protect: one product, one category, "
             "one customer or every order line.")
    scope_ref = fields.Char(
        string="Target",
        help="Exact name of the product, category or customer the "
             "floors apply to. Leave empty for a global rule.")
    discount_floor = fields.Float(
        string="Discount Floor (%)", default=0.0,
        help="Highest discount allowed on the target.")
    margin_floor = fields.Float(
        string="Margin Floor (%)", default=0.0,
        help="Lowest margin allowed on the target.")
    check_ids = fields.One2many(
        "margin.check", "rule_id", string="Checks")
    check_count = fields.Integer(
        string="Checks", compute="_compute_checks")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("check_ids", "check_ids.state")
    def _compute_checks(self):
        for rule in self:
            rule.check_count = len(rule.check_ids)

    @api.constrains("discount_floor", "margin_floor")
    def _check_floors(self):
        for rule in self:
            for floor in (rule.discount_floor, rule.margin_floor):
                if floor < 0.0 or floor > 100.0:
                    raise ValidationError(_(
                        "The floors of %s must stay between 0 and 100 "
                        "percent.", rule.name))
            if rule.discount_floor <= 0.0 and rule.margin_floor <= 0.0:
                raise ValidationError(_(
                    "The rule %s needs a discount floor or a margin "
                    "floor above zero.", rule.name))
