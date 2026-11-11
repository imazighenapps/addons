# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ToolCribTool(models.Model):
    _name = "tool.crib.tool"
    _description = "Workshop Tool"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        help="Reference or asset tag printed on the tool.")
    condition = fields.Selection(
        [("good", "Good"), ("worn", "Worn"), ("repair", "Needs Repair")],
        default="good", required=True, tracking=True,
        help="Current condition of the tool.")
    loan_ids = fields.One2many(
        "tool.crib.loan", "tool_id", string="Loans")
    loan_count = fields.Integer(
        string="Loans", compute="_compute_loans", store=True)
    open_loan_count = fields.Integer(
        string="Open Loans", compute="_compute_loans", store=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("loan_ids", "loan_ids.state")
    def _compute_loans(self):
        for tool in self:
            tool.loan_count = len(tool.loan_ids)
            tool.open_loan_count = len(tool.loan_ids.filtered(
                lambda loan: loan.state == "out"))
