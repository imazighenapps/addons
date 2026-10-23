# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models


class GdprBreach(models.Model):
    _name = "gdpr.breach"
    _description = "GDPR Personal Data Breach"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "awareness_date desc"

    name = fields.Char(default="/", copy=False, readonly=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    detection_date = fields.Datetime(string="Detected On")
    awareness_date = fields.Datetime(
        string="Known Since (legal T0)", required=True,
        help="Awareness starts the 72h notification clock.")
    nature = fields.Selection(
        [("confidentiality", "Confidentiality"), ("integrity", "Integrity"),
         ("availability", "Availability")],
        required=True,
    )
    categories = fields.Text(string="Data Categories Concerned")
    volume_persons = fields.Integer(string="Approx. Persons")
    volume_records = fields.Integer(string="Approx. Records")
    consequences = fields.Text(string="Likely Consequences")
    risk = fields.Selection(
        [("unlikely", "Risk Unlikely"), ("low", "Low Risk"), ("high", "High Risk")],
        default="low",
    )
    notify_authority = fields.Boolean(string="Notify Authority")
    notify_justification = fields.Text(string="Non-notification Justification")
    notify_deadline = fields.Datetime(compute="_compute_deadline", store=True)
    notified_date = fields.Datetime()
    delay_reason = fields.Text(string="Delay Reason")
    notify_persons = fields.Boolean(string="Inform Data Subjects")
    notify_method = fields.Char(string="Information Method")
    measures = fields.Text(string="Measures Taken / Planned")
    state = fields.Selection(
        [("detected", "Detected"), ("assessing", "Assessing"),
         ("notified", "Notified"), ("closed", "Closed")],
        default="detected",
        tracking=True,
    )
    processing_ids = fields.Many2many("gdpr.activity", string="Related Processing")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("gdpr.breach") or "/"
        return super().create(vals_list)

    @api.depends("awareness_date")
    def _compute_deadline(self):
        for rec in self:
            rec.notify_deadline = (
                rec.awareness_date + timedelta(hours=72)) if rec.awareness_date else False

    def action_assess(self):
        self.write({"state": "assessing"})

    def action_notify(self):
        self.write({"state": "notified", "notified_date": fields.Datetime.now()})

    def action_close(self):
        self.write({"state": "closed"})


class GdprAnonymLog(models.Model):
    _name = "gdpr.anonymization.log"
    _description = "GDPR Anonymization Proof Log"

    name = fields.Char(default="/", copy=False, readonly=True)
    model_name = fields.Char(string="Model", required=True)
    record_ref = fields.Char(string="Record Reference")
    fields_list = fields.Text(string="Anonymized Fields")
    by_user_id = fields.Many2one("res.users", string="Executed By",
                                 default=lambda self: self.env.user)
    date = fields.Datetime(default=fields.Datetime.now)
    rule_summary = fields.Text(string="Rule Applied")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("gdpr.anonym") or "/"
        return super().create(vals_list)
