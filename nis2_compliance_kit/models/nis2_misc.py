# -*- coding: utf-8 -*-
from odoo import fields, models


class Nis2Evidence(models.Model):
    _name = "nis2.evidence"
    _description = "NIS2 Evidence"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True
    )
    evidence_type = fields.Selection(
        [
            ("policy", "Policy"),
            ("procedure", "Procedure"),
            ("test", "Test / Audit Result"),
            ("attestation", "Attestation"),
            ("minutes", "Meeting Minutes"),
            ("contract", "Contract Extract"),
        ],
        default="policy",
        required=True,
    )
    attachment_id = fields.Many2one("ir.attachment", string="Document")
    lifecycle = fields.Selection(
        [("draft", "Draft"), ("valid", "Valid"), ("expired", "Expired")],
        default="draft",
        tracking=True,
    )
    valid_until = fields.Date()
    control_ids = fields.Many2many("nis2.control", string="Controls")
    note = fields.Text()


class Nis2Training(models.Model):
    _name = "nis2.training"
    _description = "NIS2 Training Record"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True, tracking=True)
    user_id = fields.Many2one("res.users", string="Person", required=True)
    audience = fields.Selection(
        [("board", "Board"), ("responder", "Incident Responders"), ("staff", "Staff")],
        default="staff",
        required=True,
    )
    due_date = fields.Date()
    done_date = fields.Date()
    state = fields.Selection(
        [("assigned", "Assigned"), ("done", "Done"), ("overdue", "Overdue")],
        default="assigned",
        tracking=True,
    )
    proof = fields.Text(string="Proof / Certificate Ref")


class Nis2Review(models.Model):
    _name = "nis2.review"
    _description = "NIS2 Management Review (Art. 20)"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True
    )
    review_date = fields.Date(default=fields.Date.today, required=True)
    attendees = fields.Text(string="Attendees")
    decisions = fields.Text(string="Decisions")
    approved = fields.Boolean(string="Approved by Management", tracking=True)
    next_date = fields.Date(string="Next Review")


class Nis2Action(models.Model):
    _name = "nis2.action"
    _description = "NIS2 Corrective Action"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True
    )
    source = fields.Selection(
        [("incident", "Incident"), ("risk", "Risk"), ("audit", "Audit"), ("review", "Management Review")],
        default="incident",
    )
    owner_id = fields.Many2one("res.users", string="Owner", tracking=True)
    deadline = fields.Date(tracking=True)
    state = fields.Selection(
        [("open", "Open"), ("progress", "In Progress"), ("overdue", "Overdue"), ("done", "Done")],
        default="open",
        tracking=True,
    )
    result = fields.Text(string="Result")
