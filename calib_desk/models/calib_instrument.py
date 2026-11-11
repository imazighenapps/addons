# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CalibInstrument(models.Model):
    _name = "calib.instrument"
    _description = "Calibration Instrument"
    _inherit = ["mail.thread"]
    _order = "next_due asc, name"

    name = fields.Char(required=True, tracking=True)
    serial = fields.Char(
        string="Serial Number", tracking=True,
        help="Manufacturer serial number of the instrument.")
    location = fields.Char(
        help="Workshop, line or bench where the instrument is kept.")
    interval_months = fields.Integer(
        string="Calibration Interval (months)", default=12, required=True,
        help="Number of months between two calibrations.")
    last_calibration = fields.Date(
        string="Last Calibration", tracking=True,
        help="Date of the latest confirmed calibration.")
    next_due = fields.Date(
        string="Next Due", compute="_compute_next_due", store=True,
        help="Date the next calibration is due.")
    is_overdue = fields.Boolean(
        string="Overdue", compute="_compute_next_due", store=True,
        help="True when the next due date is in the past.")
    state = fields.Selection(
        [("in_service", "In Service"), ("blocked", "Blocked")],
        default="in_service", required=True, copy=False,
        tracking=True, index=True)
    calibration_ids = fields.One2many(
        "calib.event", "instrument_id", string="Calibrations", copy=False)
    calibration_count = fields.Integer(
        string="Calibrations", compute="_compute_calibration_count",
        store=True)
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", tracking=True,
        default=lambda self: self.env.user)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("last_calibration", "interval_months")
    def _compute_next_due(self):
        today = fields.Date.context_today(self)
        for instrument in self:
            if instrument.last_calibration and instrument.interval_months > 0:
                instrument.next_due = instrument.last_calibration + relativedelta(
                    months=instrument.interval_months)
                instrument.is_overdue = instrument.next_due < today
            else:
                instrument.next_due = False
                instrument.is_overdue = False

    @api.depends("calibration_ids")
    def _compute_calibration_count(self):
        for instrument in self:
            instrument.calibration_count = len(instrument.calibration_ids)

    @api.constrains("interval_months")
    def _check_interval(self):
        for instrument in self:
            if instrument.interval_months <= 0:
                raise ValidationError(_(
                    "The calibration interval of %s must be above zero.",
                    instrument.name))

    def action_block(self):
        for instrument in self:
            if instrument.state == "blocked":
                raise UserError(_("The instrument is already blocked."))
            instrument.state = "blocked"
            instrument.message_post(body=_(
                "Instrument blocked from use until recalibration."))
        return True

    def action_unblock(self):
        for instrument in self:
            if instrument.state != "blocked":
                raise UserError(_("Only a blocked instrument can be unblocked."))
            instrument.state = "in_service"
            instrument.message_post(body=_("Instrument returned to service."))
        return True
