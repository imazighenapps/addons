# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Nis2Risk(models.Model):
    _name = "nis2.risk"
    _description = "NIS2 Risk"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True
    )
    asset_ids = fields.Many2many("nis2.asset", string="Assets")
    control_ids = fields.Many2many("nis2.control", string="Related Controls")
    likelihood = fields.Selection(
        [("1", "1 - Rare"), ("2", "2 - Possible"), ("3", "3 - Likely"), ("4", "4 - Almost Certain")],
        default="2",
        required=True,
    )
    impact = fields.Selection(
        [("1", "1 - Minor"), ("2", "2 - Significant"), ("3", "3 - Major"), ("4", "4 - Critical")],
        default="2",
        required=True,
    )
    inherent = fields.Integer(compute="_compute_scores", store=True)
    residual_likelihood = fields.Selection(
        [("1", "1 - Rare"), ("2", "2 - Possible"), ("3", "3 - Likely"), ("4", "4 - Almost Certain")],
        default="1",
    )
    residual_impact = fields.Selection(
        [("1", "1 - Minor"), ("2", "2 - Significant"), ("3", "3 - Major"), ("4", "4 - Critical")],
        default="1",
    )
    residual = fields.Integer(compute="_compute_scores", store=True)
    state = fields.Selection(
        [("draft", "Draft"), ("review", "Under Review"), ("accepted", "Accepted"), ("closed", "Closed")],
        default="draft",
        tracking=True,
    )
    acceptance_by = fields.Many2one("res.users", string="Accepted By")
    acceptance_date = fields.Date()
    treatment = fields.Text(string="Treatment Plan")

    @api.depends("likelihood", "impact", "residual_likelihood", "residual_impact")
    def _compute_scores(self):
        for rec in self:
            rec.inherent = int(rec.likelihood) * int(rec.impact)
            rec.residual = int(rec.residual_likelihood) * int(rec.residual_impact)
