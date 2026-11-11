# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DowntimeMachine(models.Model):
    _name = "downtime.machine"
    _description = "Machine"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(help="Internal reference of the machine.")
    planned_minutes = fields.Integer(
        string="Planned Minutes", default=480, required=True,
        help="Planned operating minutes used as availability baseline.")
    stop_ids = fields.One2many(
        "downtime.event", "machine_id", string="Stops")
    stop_count = fields.Integer(
        string="Stops", compute="_compute_metrics", store=True)
    open_stop_count = fields.Integer(
        string="Open Stops", compute="_compute_metrics", store=True)
    downtime_minutes = fields.Float(
        string="Downtime (min)", compute="_compute_metrics", store=True,
        help="Total duration of closed stop events in minutes.")
    mttr_minutes = fields.Float(
        string="MTTR (min)", compute="_compute_metrics", store=True,
        help="Average duration of closed stop events.")
    availability_rate = fields.Float(
        string="Availability (%)", compute="_compute_metrics", store=True,
        help="Availability based on planned minutes minus downtime.")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends(
        "planned_minutes", "stop_ids.state", "stop_ids.duration_minutes")
    def _compute_metrics(self):
        for machine in self:
            stops = machine.stop_ids
            closed = stops.filtered(lambda event: event.state == "closed")
            durations = [event.duration_minutes for event in closed]
            total = sum(durations)
            machine.stop_count = len(stops)
            machine.open_stop_count = len(
                stops.filtered(lambda event: event.state == "open"))
            machine.downtime_minutes = total
            machine.mttr_minutes = (total / len(durations)) if durations else 0.0
            if machine.planned_minutes > 0:
                available = machine.planned_minutes - total
                rate = (available / machine.planned_minutes) * 100.0
                machine.availability_rate = max(min(rate, 100.0), 0.0)
            else:
                machine.availability_rate = 0.0

    @api.constrains("planned_minutes")
    def _check_planned_minutes(self):
        for machine in self:
            if machine.planned_minutes <= 0:
                raise ValidationError(_(
                    "The planned operating time for %s must be greater than "
                    "zero.", machine.name))
