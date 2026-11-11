# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PestStation(models.Model):
    _name = "pest.station"
    _description = "Pest Control Station"
    _inherit = ["mail.thread"]
    _order = "next_check asc, name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        required=True, tracking=True,
        help="Station identifier printed on the map or label.")
    location = fields.Char(
        required=True, help="Area or room where the station is installed.")
    station_type = fields.Selection(
        [("bait", "Bait Station"), ("trap", "Trap"),
         ("monitor", "Monitor"), ("electric", "Electric Fly Killer"),
         ("other", "Other")],
        default="bait", required=True,
        help="Type of monitoring device installed.")
    interval_days = fields.Integer(
        string="Check Interval (days)", default=30, required=True,
        help="Number of days between two inspections.")
    last_check = fields.Date(
        string="Last Check", tracking=True,
        help="Date of the latest confirmed inspection.")
    next_check = fields.Date(
        string="Next Check", compute="_compute_next_check", store=True,
        help="Date the next inspection is due.")
    is_overdue = fields.Boolean(
        string="Overdue", compute="_compute_next_check", store=True,
        help="True when the next check date is in the past.")
    state = fields.Selection(
        [("active", "Active"), ("out_of_service", "Out of Service")],
        default="active", required=True, copy=False,
        tracking=True, index=True)
    inspection_ids = fields.One2many(
        "pest.inspection", "station_id", string="Inspections", copy=False)
    inspection_count = fields.Integer(
        string="Inspections", compute="_compute_inspection_counts",
        store=True)
    open_finding_count = fields.Integer(
        string="Open Findings", compute="_compute_inspection_counts",
        store=True)
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", tracking=True,
        default=lambda self: self.env.user)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "The station code must be unique per company.")

    @api.depends("last_check", "interval_days")
    def _compute_next_check(self):
        today = fields.Date.context_today(self)
        for station in self:
            if station.last_check and station.interval_days > 0:
                station.next_check = station.last_check + relativedelta(
                    days=station.interval_days)
                station.is_overdue = station.next_check < today
            else:
                station.next_check = False
                station.is_overdue = False

    @api.depends("inspection_ids", "inspection_ids.finding_state")
    def _compute_inspection_counts(self):
        for station in self:
            station.inspection_count = len(station.inspection_ids)
            station.open_finding_count = len(station.inspection_ids.filtered(
                lambda i: i.finding_state == "open"))

    @api.constrains("interval_days")
    def _check_interval(self):
        for station in self:
            if station.interval_days <= 0:
                raise ValidationError(_(
                    "The check interval of %s must be above zero.",
                    station.name))

    def action_out_of_service(self):
        for station in self:
            if station.state == "out_of_service":
                raise UserError(_("The station is already out of service."))
            station.state = "out_of_service"
            station.message_post(body=_("Station taken out of service."))
        return True

    def action_activate(self):
        for station in self:
            if station.state == "active":
                raise UserError(_("The station is already active."))
            station.state = "active"
            station.message_post(body=_("Station returned to service."))
        return True
