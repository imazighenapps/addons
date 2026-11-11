# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SampleItem(models.Model):
    _name = "sample.item"
    _description = "Hand-Out Sample"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        help="Short reference of the sample, printed on the label.")
    category = fields.Selection(
        [("product", "Product Sample"), ("material", "Material Swatch"),
         ("demo", "Demo Unit"), ("promo", "Promo Giveaway"),
         ("other", "Other")],
        default="product", required=True,
        help="Kind of sample handed to the prospect.")
    followup_days = fields.Integer(
        string="Follow-Up (days)", default=14, required=True,
        help="How many days after the hand-out the call is due.")
    issue_ids = fields.One2many(
        "sample.issue", "item_id", string="Hand-Outs")
    issue_count = fields.Integer(
        string="Hand-Outs", compute="_compute_issues")
    open_issue_count = fields.Integer(
        string="Still Outside", compute="_compute_issues")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)
    note = fields.Text()

    @api.depends("issue_ids", "issue_ids.state")
    def _compute_issues(self):
        for item in self:
            item.issue_count = len(item.issue_ids)
            item.open_issue_count = len(item.issue_ids.filtered(
                lambda issue: issue.state == "out"))
