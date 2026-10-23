# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ReferralCampaign(models.Model):
    _name = "referral.campaign"
    _description = "Employee Referral Campaign"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    bonus_on_hire = fields.Monetary(string="Bonus on Hire")
    bonus_on_retention = fields.Monetary(string="Bonus After Probation")
    probation_days = fields.Integer(string="Probation (days)", default=90)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id,
        required=True)
    job_ids = fields.Many2many("hr.job", string="Open Positions")
    eligible_employee_ids = fields.Many2many(
        "hr.employee", string="Eligible Referrers")
    active = fields.Boolean(default=True)
    hired_count = fields.Integer(compute="_compute_stats", store=True)
    total_paid = fields.Monetary(compute="_compute_stats", store=True)
    referral_ids = fields.One2many("referral.case", "campaign_id")

    _sql_constraints = [
        ("amount_total_check", "CHECK(bonus_on_hire >= 0 AND bonus_on_retention >= 0)", "Bonuses cannot be negative."),
    ]

    @api.depends("referral_ids.state", "referral_ids.paid_amount")
    def _compute_stats(self):
        for camp in self:
            cases = camp.referral_ids
            camp.hired_count = len(cases.filtered(lambda c: c.state == "hired"))
            camp.total_paid = sum(cases.mapped("paid_amount") or [0.0])