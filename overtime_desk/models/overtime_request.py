# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class OvertimeRequest(models.Model):
    _name = "overtime.request"
    _description = "Overtime Request"
    _inherit = ["mail.thread"]
    _order = "request_date desc, id desc"

    name = fields.Char(
        required=True, default=lambda self: _("Overtime %s")
        % fields.Date.context_today(self),
        help="Reference of the overtime request.")
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, tracking=True,
        index=True)
    department_id = fields.Many2one(
        "hr.department", string="Department",
        related="employee_id.department_id", store=True, readonly=True)
    request_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True,
        index=True)
    hours_requested = fields.Float(
        string="Hours Requested", required=True, tracking=True,
        help="Number of extra hours requested by the employee.")
    hours_approved = fields.Float(
        string="Hours Approved", compute="_compute_hours_approved",
        store=True, help="Approved hours, equal to requested hours when "
        "the request is approved.")
    reason = fields.Text(help="Why the overtime is needed.")
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"),
         ("rejected", "Rejected")],
        default="draft", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    active = fields.Boolean(default=True)

    @api.depends("hours_requested", "state")
    def _compute_hours_approved(self):
        for request in self:
            if request.state == "approved":
                request.hours_approved = request.hours_requested
            else:
                request.hours_approved = 0.0

    @api.constrains("hours_requested")
    def _check_hours_requested(self):
        for request in self:
            if request.hours_requested <= 0:
                raise ValidationError(_(
                    "The requested hours for %s must be greater than zero.",
                    request.employee_id.name))

    @api.constrains("request_date")
    def _check_request_date(self):
        for request in self:
            if not request.request_date:
                raise ValidationError(_(
                    "A request date is required for %s.",
                    request.employee_id.name))

    def action_approve(self):
        for request in self:
            if request.state != "draft":
                raise ValidationError(_(
                    "Only draft requests can be approved."))
            request.state = "approved"
            request.message_post(body=_(
                "Overtime request approved for %.2f hours.")
                % request.hours_requested)
        return True

    def action_reject(self):
        for request in self:
            if request.state != "draft":
                raise ValidationError(_(
                    "Only draft requests can be rejected."))
            request.state = "rejected"
            request.message_post(body=_("Overtime request rejected."))
        return True

    def action_reset_draft(self):
        for request in self:
            if request.state == "draft":
                raise ValidationError(_(
                    "The request is already in draft."))
            request.state = "draft"
            request.message_post(body=_("Overtime request reset to draft."))
        return True
