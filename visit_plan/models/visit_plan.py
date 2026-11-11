# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VisitPlan(models.Model):
    _name = "visit.plan"
    _description = "Visit Plan"
    _inherit = ["mail.thread"]
    _order = "week_start desc, id desc"

    name = fields.Char(
        required=True, tracking=True,
        default=lambda self: _("Weekly Route"),
        help="Reference of the weekly route plan.")
    technician_id = fields.Many2one(
        "res.users", string="Technician", required=True,
        default=lambda self: self.env.user, tracking=True,
        help="Person responsible for executing the planned visits.")
    week_start = fields.Date(
        string="Week Start", required=True, tracking=True,
        default=fields.Date.context_today,
        help="First day of the planned visit week.")
    state = fields.Selection(
        [("draft", "Draft"), ("planned", "Planned"), ("done", "Done")],
        default="draft", required=True, tracking=True, index=True)
    stop_ids = fields.One2many(
        "visit.stop", "plan_id", string="Stops")
    stop_count = fields.Integer(
        string="Stops", compute="_compute_stop_counts", store=True,
        help="Total number of stops in this route.")
    planned_stop_count = fields.Integer(
        string="Pending Stops", compute="_compute_stop_counts", store=True,
        help="Stops that are still pending on this route.")
    done_stop_count = fields.Integer(
        string="Done Stops", compute="_compute_stop_counts", store=True,
        help="Stops already completed on this route.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("stop_ids.state")
    def _compute_stop_counts(self):
        for plan in self:
            stops = plan.stop_ids
            plan.stop_count = len(stops)
            plan.planned_stop_count = len(
                stops.filtered(lambda stop: stop.state == "planned"))
            plan.done_stop_count = len(
                stops.filtered(lambda stop: stop.state == "done"))

    @api.constrains("week_start")
    def _check_week_start(self):
        for plan in self:
            if not plan.week_start:
                raise ValidationError(_(
                    "Please set a week start date for %s.", plan.name))

    def action_plan(self):
        for plan in self:
            if not plan.stop_ids:
                raise ValidationError(_(
                    "Add at least one stop before planning %s.", plan.name))
            plan.state = "planned"
            plan.message_post(body=_("The route has been planned."))
        return True

    def action_done(self):
        for plan in self:
            pending = plan.stop_ids.filtered(lambda stop: stop.state != "done")
            if pending:
                raise ValidationError(_(
                    "Complete every stop before closing %s.", plan.name))
            plan.state = "done"
            plan.message_post(body=_("The route has been completed."))
        return True
