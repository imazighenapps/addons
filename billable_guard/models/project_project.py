# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    billable_gap_ids = fields.One2many(
        "billable.gap", "project_id", string="Unbilled Time")
    billable_gap_count = fields.Integer(
        string="Unbilled Count", compute="_compute_billable_risk")
    billable_risk = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        string="Billing Risk", compute="_compute_billable_risk")

    @api.depends("billable_gap_ids.state", "billable_gap_ids.hours_gap")
    def _compute_billable_risk(self):
        for project in self:
            open_gaps = project.billable_gap_ids.filtered(
                lambda gap: gap.state == "open")
            project.billable_gap_count = len(open_gaps)
            if len(open_gaps) >= 2:
                project.billable_risk = "high"
            elif open_gaps:
                project.billable_risk = "medium"
            else:
                project.billable_risk = "low"
