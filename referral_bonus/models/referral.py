# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError


class ReferralCase(models.Model):
    _name = "referral.case"
    _description = "Employee Referral"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(default="/", copy=False, readonly=True)
    campaign_id = fields.Many2one("referral.campaign", required=True,
                                  ondelete="restrict")
    referrer_id = fields.Many2one("hr.employee", string="Referrer", required=True)
    candidate_name = fields.Char(required=True)
    candidate_email = fields.Char()
    candidate_phone = fields.Char()
    job_id = fields.Many2one("hr.job", string="Position")
    application_id = fields.Many2one("hr.applicant", string="Application",
                                     ondelete="set null")
    employee_id = fields.Many2one("hr.employee", string="Hired Employee",
                                  ondelete="set null")
    currency_id = fields.Many2one(
        "res.currency", related="campaign_id.currency_id", store=True)
    bonus_on_hire = fields.Monetary(related="campaign_id.bonus_on_hire")
    bonus_on_retention = fields.Monetary(
        related="campaign_id.bonus_on_retention")
    paid_amount = fields.Monetary(readonly=True)
    retention_due = fields.Date(compute="_compute_retention", store=True)
    state = fields.Selection(
        [("submitted", "Submitted"), ("screening", "Screening"),
         ("hired", "Hired"), ("retained", "Retained"),
         ("rejected", "Not Hired")],
        default="submitted", tracking=True)
    rejection_reason = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "referral.case") or "/"
        return super().create(vals_list)

    @api.depends("campaign_id.probation_days", "employee_id.date_start")
    def _compute_retention(self):
        for rec in self:
            emp = rec.employee_id
            base = emp.date_start if emp and emp.date_start else \
                (rec.create_date.date() if rec.create_date else fields.Date.today())
            days = rec.campaign_id.probation_days or 0
            rec.retention_due = base + timedelta(days=days) if days else False

    def action_screening(self):
        self.write({"state": "screening"})

    def action_hire(self, employee_id):
        """Confirm the referral was hired. Accepts an id or a record."""
        for rec in self:
            if rec.state == "hired":
                raise UserError("This referral is already marked as hired.")
            employee = employee_id
            if not hasattr(employee, "_name"):
                employee = self.env["hr.employee"].browse(employee_id)
            if not employee.exists():
                raise UserError("The hired employee does not exist.")
            rec.write({
                "employee_id": employee.id,
                "state": "hired",
                "paid_amount": rec.bonus_on_hire,
            })
            rec.message_post(body="Referred hire confirmed, bonus accrued.")

    def action_reject(self, reason=None):
        self.write({"state": "rejected",
                    "rejection_reason": reason or self.rejection_reason or ""})

    def action_confirm_retention(self):
        for rec in self:
            if rec.state != "hired":
                raise UserError("Only hired referrals can be confirmed as retained.")
            rec.write({
                "state": "retained",
                "paid_amount": rec.bonus_on_hire + rec.bonus_on_retention,
            })
            rec.message_post(body="Probation passed, retention bonus accrued.")