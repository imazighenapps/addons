# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class VisitorLog(models.Model):
    _name = "visitor.log"
    _description = "Visitor Log"
    _inherit = ["mail.thread"]
    _order = "check_in desc, id desc"
    _rec_name = "visitor_name"

    name = fields.Char(
        required=True,
        default=lambda self: _("Visitor %s")
        % fields.Datetime.now().strftime("%Y-%m-%d %H:%M"),
        help="Badge name of the visit, generated from the date and time.")
    visitor_name = fields.Char(required=True, tracking=True)
    company_name = fields.Char(
        string="Visitor Company",
        help="Company the visitor works for, not the company of the visit.")
    phone = fields.Char()
    email = fields.Char()
    host_id = fields.Many2one(
        "res.users", string="Host", required=True, tracking=True,
        default=lambda self: self.env.user,
        help="Employee who receives the visitor.")
    purpose = fields.Selection(
        [("meeting", "Meeting"), ("delivery", "Delivery"),
         ("interview", "Interview"), ("maintenance", "Maintenance"),
         ("other", "Other")],
        default="meeting", required=True,
        help="Reason of the visit, used by the front desk statistics.")
    check_in = fields.Datetime(default=fields.Datetime.now, tracking=True)
    check_out = fields.Datetime(tracking=True)
    badge = fields.Char(help="Badge number handed to the visitor.")
    state = fields.Selection(
        [("expected", "Expected"), ("on_site", "On Site"),
         ("checked_out", "Checked Out"), ("cancelled", "Cancelled")],
        default="on_site", required=True, copy=False, tracking=True,
        index=True)
    duration_hours = fields.Float(
        string="Duration (hours)", compute="_compute_duration", store=True,
        help="Time spent on site, from the check-in to the check-out.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)
    note = fields.Text()

    @api.depends("check_in", "check_out")
    def _compute_duration(self):
        for visit in self:
            if visit.check_in and visit.check_out \
                    and visit.check_out >= visit.check_in:
                seconds = (visit.check_out - visit.check_in).total_seconds()
                visit.duration_hours = round(seconds / 3600.0, 2)
            else:
                visit.duration_hours = 0.0

    @api.constrains("check_in", "check_out")
    def _check_times(self):
        for visit in self:
            if visit.check_in and visit.check_out \
                    and visit.check_out < visit.check_in:
                raise ValidationError(_(
                    "The visit of \"%s\" cannot be checked out before it is "
                    "checked in.", visit.visitor_name))

    def action_check_in(self):
        for visit in self:
            if visit.state == "checked_out":
                raise UserError(_(
                    "The visit of \"%s\" is already checked out. Create a "
                    "new visit instead.", visit.visitor_name))
            visit.state = "on_site"
            if not visit.check_in:
                visit.check_in = fields.Datetime.now()
            visit.message_post(body=_(
                "Visitor checked in at the front desk."))
        return True

    def action_check_out(self):
        for visit in self:
            if visit.state == "checked_out":
                raise UserError(_(
                    "The visit of \"%s\" is already checked out.",
                    visit.visitor_name))
            visit.write({
                "state": "checked_out",
                "check_out": fields.Datetime.now(),
            })
            visit.message_post(body=_(
                "Visitor checked out after %s hour(s) on site.",
                visit.duration_hours))
        return True

    def action_cancel(self):
        for visit in self:
            if visit.state == "checked_out":
                raise UserError(_(
                    "The visit of \"%s\" is already checked out and cannot "
                    "be cancelled.", visit.visitor_name))
            visit.state = "cancelled"
            visit.message_post(body=_("Visit cancelled."))
        return True
