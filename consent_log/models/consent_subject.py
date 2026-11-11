# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ConsentSubject(models.Model):
    _name = "consent.subject"
    _description = "Consent Contact"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    email = fields.Char(help="Email address of the contact, if known.")
    partner_id = fields.Many2one(
        "res.partner", string="Contact",
        help="Linked contact record, when available.")
    consent_ids = fields.One2many(
        "consent.record", "subject_id", string="Consents")
    consent_count = fields.Integer(
        string="Consents", compute="_compute_consent_counts", store=True)
    active_consent_count = fields.Integer(
        string="Active Consents", compute="_compute_consent_counts",
        store=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("consent_ids", "consent_ids.state")
    def _compute_consent_counts(self):
        for subject in self:
            consents = subject.consent_ids
            subject.consent_count = len(consents)
            subject.active_consent_count = len(consents.filtered(
                lambda consent: consent.state == "active"))
