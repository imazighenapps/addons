# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ProbationReviewLog(models.Model):
    _name = "probation.review.log"
    _description = "Probation Review"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "review_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, index=True,
        tracking=True)
    reviewer_id = fields.Many2one(
        "hr.employee", string="Reviewer", tracking=True)
    date_start = fields.Date(
        string="Probation Start", required=True,
        default=fields.Date.context_today, tracking=True)
    date_end = fields.Date(string="Probation End", required=True, tracking=True)
    review_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    score = fields.Integer(default=0)
    outcome = fields.Selection(
        [("pending", "Pending"), ("passed", "Passed"),
         ("extended", "Extended"), ("failed", "Failed")],
        default="pending", required=True, tracking=True)
    notes = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"),
         ("closed", "Closed"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("probation.review.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.constrains("date_start", "date_end", "review_date")
    def _check_dates(self):
        for record in self:
            if record.date_end and record.date_start \
                    and record.date_end < record.date_start:
                raise ValidationError(
                    _("The probation end date cannot be before the start date."))
            if record.review_date and record.date_start \
                    and record.review_date < record.date_start:
                raise ValidationError(
                    _("The review date cannot be before the probation start."))

    @api.constrains("score")
    def _check_score(self):
        for record in self:
            if record.score < 0 or record.score > 100:
                raise ValidationError(_("The score must be between 0 and 100."))

    def action_submit(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft review can be submitted."))
            record.state = "submitted"
        return True

    def action_close(self):
        for record in self:
            if record.state != "submitted":
                raise UserError(_("Only a submitted review can be closed."))
            if record.outcome == "pending":
                raise UserError(_("Set a decision before closing the review."))
            record.state = "closed"
        return True

    def action_cancel(self):
        for record in self:
            if record.state in ("closed", "cancelled"):
                raise UserError(_("A closed or cancelled review cannot be cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state != "cancelled":
                raise UserError(_("Only a cancelled review can be reset."))
            record.state = "draft"
        return True
