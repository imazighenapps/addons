# -*- coding: utf-8 -*-
from odoo import fields, models


class HaccpPlan(models.Model):
    _name = "haccp.plan"
    _description = "HACCP Plan"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    version = fields.Char(default="1.0", required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("validated", "Validated"), ("archived", "Archived")],
        default="draft",
        tracking=True,
    )
    team_ids = fields.Many2many("res.users", string="HACCP Team")
    date_valid_from = fields.Date()
    date_valid_to = fields.Date()
    validated_by_id = fields.Many2one("res.users", string="Validated By")
    validated_on = fields.Date()
    diagram_note = fields.Text(string="Process Diagram Notes")
    attachment_ids = fields.Many2many("ir.attachment", string="Documents")
    ccp_ids = fields.One2many("haccp.ccp", "plan_id")
    active = fields.Boolean(default=True)

    _name_version_unique = models.Constraint(
        "UNIQUE(name, version)", "Plan name and version must be unique.")

    def action_validate(self):
        self.write({"state": "validated", "validated_on": fields.Date.today(),
                    "validated_by_id": self.env.uid})

    def action_archive(self):
        self.write({"state": "archived"})
