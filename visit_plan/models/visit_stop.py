# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VisitStop(models.Model):
    _name = "visit.stop"
    _description = "Visit Stop"
    _inherit = ["mail.thread"]
    _order = "plan_id, sequence, id"

    name = fields.Char(
        compute="_compute_name", store=True,
        help="Display name of the planned stop.")
    plan_id = fields.Many2one(
        "visit.plan", string="Route", required=True, ondelete="cascade",
        index=True, tracking=True)
    sequence = fields.Integer(
        default=10, help="Travel order of the stop within the route.")
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True,
        help="Customer or site contact for this visit.")
    site_name = fields.Char(
        string="Site Reference",
        help="Optional site or location reference for the visit.")
    planned_date = fields.Date(
        string="Planned Date", required=True, default=fields.Date.context_today,
        tracking=True, help="Date on which the visit is planned.")
    state = fields.Selection(
        [("planned", "Planned"), ("done", "Done")],
        default="planned", required=True, tracking=True, index=True)
    done_date = fields.Date(
        string="Done Date", readonly=True, copy=False,
        help="Date on which the stop was completed.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("partner_id", "site_name", "planned_date")
    def _compute_name(self):
        for stop in self:
            label = stop.partner_id.display_name or _("Visit")
            if stop.site_name:
                label = "%s - %s" % (label, stop.site_name)
            if stop.planned_date:
                label = "%s (%s)" % (label, stop.planned_date)
            stop.name = label

    @api.constrains("planned_date", "done_date")
    def _check_dates(self):
        for stop in self:
            if stop.done_date and stop.planned_date \
                    and stop.done_date < stop.planned_date:
                raise ValidationError(_(
                    "The completion date of %s cannot be before its planned "
                    "date.", stop.display_name))

    def action_mark_done(self):
        for stop in self:
            if stop.state == "done":
                raise ValidationError(_(
                    "The stop for %s is already completed.",
                    stop.partner_id.display_name))
            today = fields.Date.context_today(stop)
            done_on = max(today, stop.planned_date or today)
            stop.write({
                "state": "done",
                "done_date": done_on,
            })
            stop.message_post(body=_("The visit stop has been completed."))
        return True
