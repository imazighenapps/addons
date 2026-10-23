# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrJob(models.Model):
    _inherit = "hr.job"

    referral_campaign_id = fields.Many2one(
        "referral.campaign", string="Referral Campaign")
    referral_currency_id = fields.Many2one(
        "res.currency", related="company_id.currency_id", readonly=True)
    referral_bonus = fields.Monetary(
        related="referral_campaign_id.bonus_on_hire",
        currency_field="referral_currency_id", readonly=True)
    referral_count = fields.Integer(compute="_compute_referral_stats")

    @api.depends("referral_campaign_id")
    def _compute_referral_stats(self):
        cases = self.env["referral.case"].search(
            [("job_id", "in", self.ids), ("state", "=", "hired")])
        for job in self:
            job.referral_count = len(cases.filtered(lambda c: c.job_id == job))


class HrApplicant(models.Model):
    _inherit = "hr.applicant"

    referral_case_id = fields.Many2one(
        "referral.case", string="Referral Source", ondelete="set null")
    referred_by_id = fields.Many2one(
        "hr.employee", string="Referred By")


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # Odoo 18 ne fournit pas de date d'embauche sur hr.employee.
    date_start = fields.Date(string="Hire Date")

    referral_case_id = fields.Many2one(
        "referral.case", string="Referred By (case)", ondelete="set null")
    referrals_made = fields.Integer(
        compute="_compute_referrals_made",
        help="Number of people this employee successfully referred.")

    def _compute_referrals_made(self):
        cases = self.env["referral.case"].search(
            [("referrer_id", "in", self.ids), ("state", "in", ("hired", "retained"))])
        for emp in self:
            emp.referrals_made = len(cases.filtered(lambda c: c.referrer_id == emp))