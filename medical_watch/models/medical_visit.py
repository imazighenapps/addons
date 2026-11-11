# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalVisit(models.Model):
    _name = "medical.visit"
    _description = "Medical Visit"
    _inherit = ["mail.thread"]
    _order = "due_date, id"

    name = fields.Char(
        required=True, default=lambda self: _("Visit %s") % fields.Date.context_today(self),
        tracking=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, tracking=True, index=True)
    visit_type = fields.Selection(
        [("initial", "Initial"), ("periodic", "Periodic"),
         ("return", "Return to Work"), ("special", "Special")],
        default="periodic", required=True, tracking=True)
    scheduled_date = fields.Date(string="Scheduled Date", required=True, tracking=True)
    due_date = fields.Date(string="Due Date", required=True, tracking=True)
    done_date = fields.Date(string="Completion Date", tracking=True, copy=False)
    practitioner = fields.Char(help="Name of the occupational health practitioner.")
    is_overdue = fields.Boolean(
        string="Overdue", compute="_compute_overdue", store=True)
    state = fields.Selection(
        [("planned", "Planned"), ("done", "Done"), ("cancelled", "Cancelled")],
        default="planned", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company, index=True)
    note = fields.Text()

    @api.depends("due_date", "state")
    def _compute_overdue(self):
        today = fields.Date.context_today(self)
        for visit in self:
            visit.is_overdue = bool(
                visit.state == "planned" and visit.due_date and visit.due_date < today)

    @api.constrains("scheduled_date", "due_date")
    def _check_dates(self):
        for visit in self:
            if visit.due_date < visit.scheduled_date:
                raise ValidationError(_(
                    "The due date of %s cannot come before its scheduled date.",
                    visit.name))

    @api.constrains("done_date", "state")
    def _check_done_date(self):
        for visit in self:
            if visit.state == "done" and not visit.done_date:
                raise ValidationError(_(
                    "A completed visit for %s must have a completion date.",
                    visit.employee_id.name))

    def action_done(self):
        for visit in self:
            if visit.state != "planned":
                raise ValidationError(_(
                    "Only a planned visit can be completed."))
            visit.write({
                "state": "done",
                "done_date": visit.done_date or fields.Date.context_today(visit),
            })
        return True

    def action_cancel(self):
        for visit in self:
            if visit.state != "planned":
                raise ValidationError(_(
                    "Only a planned visit can be cancelled."))
            visit.state = "cancelled"
        return True

    def action_reopen(self):
        for visit in self:
            if visit.state == "planned":
                raise ValidationError(_(
                    "Only a done or cancelled visit can be reopened."))
            visit.write({"state": "planned", "done_date": False})
        return True
