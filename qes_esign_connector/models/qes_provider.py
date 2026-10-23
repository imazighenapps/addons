# -*- coding: utf-8 -*-
from odoo import fields, models

LEVELS = [
    ("ses", "SES - Simple"),
    ("ades", "AdES - Advanced"),
    ("qes", "QES - Qualified"),
]


class QesProvider(models.Model):
    _name = "qes.provider"
    _description = "QES Provider (eIDAS QTSP adapter)"

    name = fields.Char(required=True)
    code = fields.Selection(
        [("demo", "Demo (local)"), ("universign", "Universign"), ("docusign", "DocuSign (stub)")],
        required=True,
    )
    api_base = fields.Char(string="API Base URL")
    auth_type = fields.Selection(
        [("none", "None (demo)"), ("apikey", "API Key"), ("oauth", "OAuth2")],
        default="none",
    )
    qcert_esig = fields.Boolean(string="QCert for ESig capable")
    active = fields.Boolean(default=True)
    note = fields.Text()

    _sql_constraints = [
        ("code_unique", "UNIQUE(code)", "Provider code must be unique."),
    ]


class QesAccount(models.Model):
    _name = "qes.account"
    _description = "QES Provider Account"

    name = fields.Char(required=True)
    provider_id = fields.Many2one("qes.provider", required=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True
    )
    environment = fields.Selection(
        [("preprod", "Pre-production"), ("prod", "Production")],
        default="preprod",
        required=True,
    )
    api_key = fields.Char(string="API Key / Token")
    workspace_id = fields.Char(string="Workspace / Account ID")
    webhook_secret = fields.Char(string="Webhook Secret")
    dashboard_url = fields.Char(string="Provider Dashboard URL")
    active = fields.Boolean(default=True)
