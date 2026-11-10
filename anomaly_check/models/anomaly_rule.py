# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AnomalyRule(models.Model):
    _name = "anomaly.rule"
    _description = "Anomaly Rule"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    rule_type = fields.Selection(
        [("quantity", "Impossible Quantity"),
         ("vat", "VAT Mismatch"),
         ("duplicate", "Suspicious Doubling"),
         ("total", "Total Out Of Range")],
        required=True, default="quantity", tracking=True,
        help="Kind of control applied when scanning a bill.")
    tolerance = fields.Float(
        default=0.0, required=True,
        help="Accepted deviation before the rule raises a finding.")
    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        required=True, default="medium", tracking=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    flag_ids = fields.One2many("anomaly.flag", "rule_id", string="Flags")
    flag_count = fields.Integer(
        string="Flags", compute="_compute_flag_counts", store=True)
    open_flag_count = fields.Integer(
        string="Open Flags", compute="_compute_flag_counts", store=True)
    note = fields.Text()

    @api.depends("flag_ids", "flag_ids.state")
    def _compute_flag_counts(self):
        for rule in self:
            rule.flag_count = len(rule.flag_ids)
            rule.open_flag_count = len(rule.flag_ids.filtered(
                lambda flag: flag.state in ("new", "confirmed")))
