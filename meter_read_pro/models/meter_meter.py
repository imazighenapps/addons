# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MeterMeter(models.Model):
    _name = "meter.meter"
    _description = "Utility Meter"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        help="Reference of the meter, printed on the device or the bill.")
    utility = fields.Selection(
        [("electricity", "Electricity"), ("water", "Water"),
         ("gas", "Gas"), ("other", "Other")],
        default="electricity", required=True,
        help="Which network the meter measures.")
    location = fields.Char(
        help="Where the meter sits, for example Main switchboard, cellar.")
    unit = fields.Char(
        help="Unit of the readings, for example kWh, m3 or L.")
    reading_count = fields.Integer(
        string="Readings", compute="_compute_last")
    last_reading_date = fields.Date(
        string="Last Reading", compute="_compute_last")
    last_value = fields.Float(string="Last Value", compute="_compute_last")
    last_delta = fields.Float(
        string="Last Consumption", compute="_compute_last",
        help="Difference between the last two readings.")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)
    note = fields.Text()

    @api.depends("active")
    def _compute_last(self):
        for meter in self:
            readings = self.env["meter.reading"].search([
                ("meter_id", "=", meter.id)], order="reading_date, id")
            meter.reading_count = len(readings)
            older = readings[-2:-1] if len(readings) >= 2 else readings
            if readings:
                meter.last_value = readings[-1].value
                meter.last_reading_date = readings[-1].reading_date
                if older:
                    meter.last_delta = readings[-1].value - older[-1].value
                else:
                    meter.last_delta = 0.0
            else:
                meter.last_value = 0.0
                meter.last_reading_date = False
                meter.last_delta = 0.0
