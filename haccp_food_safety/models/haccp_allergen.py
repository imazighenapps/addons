# -*- coding: utf-8 -*-
from odoo import fields, models


class HaccpAllergen(models.Model):
    _name = "haccp.allergen"
    _description = "HACCP EU Allergen (Reg. 1169/2011)"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
    description = fields.Text()

    _code_unique = models.Constraint("UNIQUE(code)", "Allergen code must be unique.")


class HaccpNc(models.Model):
    _name = "haccp.nonconformity"
    _description = "HACCP Non-Conformity"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    ccp_id = fields.Many2one("haccp.ccp", string="CCP")
    reading_id = fields.Many2one("haccp.reading", string="Reading")
    lot_ids = fields.Many2many("stock.lot", string="Lots")
    severity = fields.Selection(
        [("minor", "Minor"), ("major", "Major"), ("critical", "Critical")],
        default="minor",
        tracking=True,
    )
    state = fields.Selection(
        [("draft", "Draft"), ("open", "Open"), ("action", "Action Ongoing"),
         ("verify", "To Verify"), ("closed", "Closed")],
        default="draft",
        tracking=True,
    )
    immediate_action = fields.Text(string="Immediate Action")
    cause = fields.Text(string="Root Cause")
    corrective_action = fields.Text(string="Corrective Action")
    verification = fields.Text(string="Effectiveness Verification")
    closed_date = fields.Date()
    closed_by_id = fields.Many2one("res.users", string="Closed By")

    def action_open(self):
        self.write({"state": "open"})

    def action_start(self):
        self.write({"state": "action"})

    def action_verify(self):
        self.write({"state": "verify"})

    def action_close(self):
        self.write({"state": "closed", "closed_date": fields.Date.today(),
                    "closed_by_id": self.env.uid})


class HaccpAlert(models.Model):
    _name = "haccp.expiry.alert"
    _description = "HACCP Expiry Alert"

    lot_id = fields.Many2one("stock.lot", required=True, ondelete="cascade")
    days_left = fields.Integer()
    state = fields.Selection(
        [("new", "New"), ("ack", "Acknowledged"), ("done", "Done")],
        default="new",
    )
