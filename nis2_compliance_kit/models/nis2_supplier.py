# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Nis2Supplier(models.Model):
    _name = "nis2.supplier"
    _description = "NIS2 Supplier Cyber Review"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True, tracking=True)
    partner_id = fields.Many2one("res.partner", string="Supplier", required=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True
    )
    criticality = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        default="medium",
        required=True,
    )
    state = fields.Selection(
        [
            ("toreview", "To Review"),
            ("inreview", "Under Review"),
            ("approved", "Approved"),
            ("exception", "Approved with Exception"),
            ("rejected", "Rejected"),
            ("expired", "Expired"),
        ],
        default="toreview",
        tracking=True,
    )
    last_review = fields.Date()
    expiry_date = fields.Date(string="Review Valid Until")
    expired = fields.Boolean(compute="_compute_expired", store=True)
    security_clause = fields.Boolean(string="Security Clause in Contract")
    attestation = fields.Text(string="Attestations / Certifications")
    note = fields.Text()

    @api.depends("expiry_date")
    def _compute_expired(self):
        today = fields.Date.today()
        for rec in self:
            rec.expired = bool(rec.expiry_date and rec.expiry_date < today)

    @api.model
    def _cron_flag_expired(self):
        expired = self.search([("expiry_date", "<", fields.Date.today()),
                               ("state", "not in", ("expired", "rejected"))])
        expired.write({"state": "expired"})
        return True
