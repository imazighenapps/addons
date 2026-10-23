# -*- coding: utf-8 -*-
from odoo import fields, models


class GdprActivity(models.Model):
    _name = "gdpr.activity"
    _description = "GDPR Processing Activity (Art.30)"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    role = fields.Selection(
        [("controller", "Controller"), ("processor", "Processor"),
         ("joint", "Joint Controllers")],
        default="controller",
        required=True,
    )
    purposes = fields.Html(required=True)
    legal_basis = fields.Selection(
        [("consent", "Consent (Art.6.1.a)"), ("contract", "Contract (Art.6.1.b)"),
         ("legal", "Legal Obligation (Art.6.1.c)"),
         ("vital", "Vital Interests (Art.6.1.d)"),
         ("public", "Public Interest (Art.6.1.e)"),
         ("legitimate", "Legitimate Interest (Art.6.1.f)")],
        required=True,
    )
    legal_justification = fields.Text()
    data_categories = fields.Text(string="Data Categories")
    subject_categories = fields.Text(string="Data Subject Categories")
    recipients = fields.Text(string="Recipients")
    transfer_country_id = fields.Many2one("res.country", string="Transfer Country")
    safeguard = fields.Selection(
        [("none", "None / EU only"), ("adequacy", "Adequacy Decision"),
         ("scc", "Standard Contractual Clauses"), ("bcr", "Binding Corporate Rules"),
         ("derogation", "Art.49 Derogation")],
        default="none",
    )
    retention_summary = fields.Text(string="Erasure Deadlines Summary")
    security_measures = fields.Text(string="Security Measures (Art.32)")
    subcontractor_ids = fields.Many2many("res.partner", string="Subprocessors")
    owner_id = fields.Many2one("res.users", string="Owner", tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("archived", "Archived")],
        default="draft",
        tracking=True,
    )
    version = fields.Integer(default=1)
    retention_rule_ids = fields.One2many("gdpr.retention.rule", "activity_id")


class GdprRetentionRule(models.Model):
    _name = "gdpr.retention.rule"
    _description = "GDPR Retention Rule"

    activity_id = fields.Many2one("gdpr.activity", required=True, ondelete="cascade")
    data_category = fields.Char(required=True)
    duration_months = fields.Integer(string="Keep (months)", required=True)
    trigger = fields.Selection(
        [("collect_end", "End of Collection"), ("contract_end", "End of Contract"),
         ("consent_withdraw", "Consent Withdrawal")],
        default="contract_end",
    )
    legal_hold = fields.Char(string="Legal Hold (e.g. accounting 10y)")
    action = fields.Selection(
        [("anonymize", "Anonymize"), ("delete", "Delete"), ("review", "Manual Review")],
        default="review",
    )
