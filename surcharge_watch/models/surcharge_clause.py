# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SurchargeClause(models.Model):
    _name = "surcharge.clause"
    _description = "Surcharge Clause"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Supplier", required=True, tracking=True,
        index=True)
    material = fields.Char(
        required=True, help="Raw material covered by the clause, such as steel.")
    base_index = fields.Float(
        required=True, digits=(16, 4),
        help="Index value agreed as the base in the contract.")
    factor = fields.Float(
        required=True, default=1.0, digits=(16, 4),
        help="Multiplier applied to the index movement.")
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    line_ids = fields.One2many(
        "surcharge.line", "clause_id", string="Applied Surcharges")
    line_count = fields.Integer(
        string="Applications", compute="_compute_line_count", store=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("line_ids")
    def _compute_line_count(self):
        for clause in self:
            clause.line_count = len(clause.line_ids)

    @api.constrains("base_index", "factor")
    def _check_values(self):
        for clause in self:
            if clause.base_index <= 0:
                raise ValidationError(_(
                    "The base index of %s must be above zero.", clause.name))
            if clause.factor <= 0:
                raise ValidationError(_(
                    "The factor of %s must be above zero.", clause.name))
