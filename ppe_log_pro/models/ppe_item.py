# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PpeItem(models.Model):
    _name = "ppe.item"
    _description = "Protective Equipment"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        help="Short reference of the equipment, printed on the label.")
    category = fields.Selection(
        [("head", "Head Protection"), ("hand", "Hand Protection"),
         ("eye", "Eye Protection"), ("foot", "Foot Protection"),
         ("hearing", "Hearing Protection"), ("respiration",
         "Respiratory Protection"), ("clothing", "Clothing"),
         ("other", "Other")],
        default="head", required=True,
        help="Which part of the body the equipment protects.")
    standard = fields.Char(
        help="Norm the equipment complies with, for example EN 388.")
    validity_months = fields.Integer(
        string="Renewal Period (months)", default=12, required=True,
        help="How long an issue stays in service before the equipment "
             "must be renewed.")
    issue_ids = fields.One2many(
        "ppe.issue", "item_id", string="Issues")
    issue_count = fields.Integer(
        string="Issues", compute="_compute_issues")
    open_issue_count = fields.Integer(
        string="Open Issues", compute="_compute_issues")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)
    note = fields.Text()

    @api.depends("issue_ids", "issue_ids.state")
    def _compute_issues(self):
        for item in self:
            item.issue_count = len(item.issue_ids)
            item.open_issue_count = len(item.issue_ids.filtered(
                lambda issue: issue.state == "issued"))
