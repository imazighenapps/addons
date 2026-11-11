# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProbationPeriod(models.Model):
    _name = "probation.period"
    _description = "Probation Period"
    _inherit = ["mail.thread"]
    _order = "review_date, id"

    name = fields.Char(
        required=True, default=lambda self: _("Probation %s") % fields.Date.context_today(self),
        tracking=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, tracking=True, index=True)
    start_date = fields.Date(string="Start Date", required=True, tracking=True)
    end_date = fields.Date(string="Planned End Date", required=True, tracking=True)
    review_date = fields.Date(string="Review Date", required=True, tracking=True)
    decision_date = fields.Date(string="Decision Date", readonly=True, copy=False)
    decision = fields.Selection(
        [("confirm", "Confirmed"), ("extend", "Extended"), ("close", "Closed")],
        string="Decision", readonly=True, copy=False)
    is_overdue = fields.Boolean(
        string="Overdue", compute="_compute_overdue", store=True)
    state = fields.Selection(
        [("ongoing", "Ongoing"), ("decided", "Decided")],
        default="ongoing", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company, index=True)
    note = fields.Text()

    @api.depends("review_date", "state")
    def _compute_overdue(self):
        today = fields.Date.context_today(self)
        for period in self:
            period.is_overdue = bool(
                period.state == "ongoing" and period.review_date
                and period.review_date < today)

    @api.constrains("start_date", "end_date", "review_date")
    def _check_dates(self):
        for period in self:
            if period.end_date < period.start_date:
                raise ValidationError(_(
                    "The planned end date of %s cannot come before the start date.",
                    period.name))
            if period.review_date < period.start_date:
                raise ValidationError(_(
                    "The review date of %s cannot come before the start date.",
                    period.name))

    def _decide(self, decision):
        for period in self:
            if period.state != "ongoing":
                raise ValidationError(_(
                    "Only an ongoing probation period can receive a decision."))
            period.write({
                "state": "decided",
                "decision": decision,
                "decision_date": fields.Date.context_today(period),
            })
        return True

    def action_confirm(self):
        return self._decide("confirm")

    def action_close(self):
        return self._decide("close")

    def action_extend(self):
        self.ensure_one()
        if self.state != "ongoing":
            raise ValidationError(_(
                "Only an ongoing probation period can be extended."))
        # Extension is represented as a decided state with extension decision;
        # callers should update end/review dates before or via a follow-up record.
        self.write({
            "state": "decided",
            "decision": "extend",
            "decision_date": fields.Date.context_today(self),
        })
        return True

    def action_reopen(self):
        for period in self:
            if period.state != "decided":
                raise ValidationError(_(
                    "Only a decided probation period can be reopened."))
            period.write({"state": "ongoing", "decision": False, "decision_date": False})
        return True
