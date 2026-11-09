# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MeterReading(models.Model):
    _name = "meter.reading"
    _description = "Meter Reading"
    _inherit = ["mail.thread"]
    _order = "reading_date desc, id desc"

    meter_id = fields.Many2one(
        "meter.meter", string="Meter", required=True, ondelete="cascade",
        index=True, tracking=True)
    value = fields.Float(required=True, tracking=True)
    reading_date = fields.Date(
        string="Reading Date", required=True, default=fields.Date.context_today,
        tracking=True)
    measured_by = fields.Many2one(
        "res.users", string="Read By", required=True,
        default=lambda self: self.env.user)
    previous_value = fields.Float(
        string="Previous Value", compute="_compute_delta", store=True,
        help="Value of the reading taken before this one.")
    delta = fields.Float(
        string="Consumption", compute="_compute_delta", store=True,
        help="Value of this reading minus the previous one.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.constrains("value")
    def _check_value(self):
        for reading in self:
            if reading.value < 0:
                raise ValidationError(_(
                    "The reading of meter \"%s\" cannot be negative.")
                    % reading.meter_id.name)

    @api.constrains("meter_id", "reading_date")
    def _check_date(self):
        for reading in self:
            if not reading.reading_date:
                continue
            twin = self.env["meter.reading"].search([
                ("meter_id", "=", reading.meter_id.id),
                ("reading_date", "=", reading.reading_date),
                ("id", "!=", reading.id),
            ], limit=1)
            if twin:
                raise ValidationError(_(
                    "Meter \"%s\" already has a reading on %s: there is one "
                    "entry per meter and per day.")
                    % (reading.meter_id.name, reading.reading_date))

    @api.depends("meter_id", "value", "reading_date")
    def _compute_delta(self):
        for reading in self:
            previous = reading._get_previous()
            if previous:
                reading.previous_value = previous.value
                reading.delta = reading.value - previous.value
            else:
                reading.previous_value = 0.0
                reading.delta = reading.value

    def _get_previous(self):
        """The latest reading taken before this one, not the newest one."""
        self.ensure_one()
        Reading = self.env["meter.reading"]
        candidate = Reading.search([
            ("meter_id", "=", self.meter_id.id),
            ("reading_date", "<", self.reading_date),
            ("id", "!=", self.id),
        ], order="reading_date desc, id desc", limit=1)
        if not candidate:
            candidate = Reading.search([
                ("meter_id", "=", self.meter_id.id),
                ("reading_date", "=", self.reading_date),
                ("id", "<", self.id),
            ], order="id desc", limit=1)
        return candidate
