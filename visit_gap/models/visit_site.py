# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VisitSite(models.Model):
    _name = "visit.site"
    _description = "Monitored Site"
    _inherit = ["mail.thread"]
    _order = "overdue_days desc, next_visit_date, id"

    name = fields.Char(
        required=True, tracking=True,
        help="Name of the site or location to monitor.")
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True,
        help="Customer linked to the monitored site.")
    responsible_id = fields.Many2one(
        "res.users", string="Owner", default=lambda self: self.env.user,
        tracking=True, help="Person responsible for keeping visits on time.")
    frequency_days = fields.Integer(
        string="Frequency (days)", required=True, default=30,
        help="Maximum number of days allowed between two visits.")
    last_visit_date = fields.Date(
        string="Last Visit", default=fields.Date.context_today,
        tracking=True, help="Date of the last completed visit.")
    next_visit_date = fields.Date(
        string="Next Due", compute="_compute_schedule", store=True,
        help="Date by which the next visit should happen.")
    overdue_days = fields.Integer(
        string="Overdue Days", compute="_compute_schedule", store=True,
        help="Number of days elapsed since the visit became due.")
    is_overdue = fields.Boolean(
        string="Overdue", compute="_compute_schedule", store=True,
        help="Indicates whether the site has missed its visit frequency.")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("frequency_days", "last_visit_date")
    def _compute_schedule(self):
        today = fields.Date.context_today(self)
        for site in self:
            if site.frequency_days > 0 and site.last_visit_date:
                next_date = site.last_visit_date + timedelta(
                    days=site.frequency_days)
            else:
                next_date = False
            site.next_visit_date = next_date
            overdue = bool(next_date and next_date < today)
            site.is_overdue = overdue
            site.overdue_days = (today - next_date).days if overdue else 0

    @api.constrains("frequency_days")
    def _check_frequency_days(self):
        for site in self:
            if site.frequency_days <= 0:
                raise ValidationError(_(
                    "The visit frequency for %s must be greater than zero.",
                    site.name))

    @api.constrains("last_visit_date")
    def _check_last_visit_date(self):
        for site in self:
            if not site.last_visit_date:
                raise ValidationError(_(
                    "Please set the last visit date for %s.", site.name))

    def action_mark_visited(self):
        for site in self:
            site.last_visit_date = fields.Date.context_today(site)
            site.message_post(body=_(
                "A visit was recorded and the schedule has been refreshed."))
        return True
