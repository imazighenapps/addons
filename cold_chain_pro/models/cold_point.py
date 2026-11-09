# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ColdPoint(models.Model):
    _name = "cold.point"
    _description = "Cold Chain Point"
    _inherit = ["mail.thread"]
    _order = "location, name"

    name = fields.Char(required=True, tracking=True)
    ref = fields.Char(
        string="Reference",
        help="Short code printed next to the point, for example CR1.")
    location = fields.Char(
        help="Where the point sits, for example Building A - Cold room 2.")
    min_temp = fields.Float(
        string="Min Temp", required=True, tracking=True,
        help="Coldest temperature the point may reach safely.")
    max_temp = fields.Float(
        string="Max Temp", required=True, tracking=True,
        help="Warmest temperature the point may reach safely.")
    frequency = fields.Selection(
        [("per_shift", "Each Shift"), ("hours_4", "Every 4 Hours"),
         ("hours_8", "Every 8 Hours"), ("daily", "Daily")],
        default="per_shift", required=True,
        help="How often the temperature must be checked, from your HACCP "
             "plan.")
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", tracking=True,
        default=lambda self: self.env.user,
        help="User in charge of the checks on this point.")
    line_ids = fields.One2many(
        "cold.reading", "point_id", string="Readings")
    reading_count = fields.Integer(
        string="Readings", compute="_compute_reading", store=True)
    open_breach_count = fields.Integer(
        string="Open Breaches", compute="_compute_reading", store=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)
    note = fields.Text()

    @api.constrains("min_temp", "max_temp")
    def _check_range(self):
        for point in self:
            if point.max_temp <= point.min_temp:
                raise ValidationError(_(
                    "The maximum temperature of \"%s\" must be above its "
                    "minimum temperature.", point.name))

    @api.depends("line_ids", "line_ids.status", "line_ids.corrected")
    def _compute_reading(self):
        for point in self:
            point.reading_count = len(point.line_ids)
            point.open_breach_count = len(point.line_ids.filtered(
                lambda reading: reading.status == "breach"
                and not reading.corrected))
