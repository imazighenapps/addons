# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CalibEvent(models.Model):
    _name = "calib.event"
    _description = "Calibration Event"
    _inherit = ["mail.thread"]
    _order = "calibration_date desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Calibration %s")
        % fields.Date.context_today(self))
    instrument_id = fields.Many2one(
        "calib.instrument", string="Instrument", required=True,
        ondelete="cascade", index=True, tracking=True)
    calibration_date = fields.Date(
        string="Calibration Date", required=True,
        default=fields.Date.context_today, tracking=True)
    result = fields.Selection(
        [("pass", "Pass"), ("fail", "Fail"), ("adjusted", "Adjusted")],
        default="pass", required=True, tracking=True)
    certificate_ref = fields.Char(
        string="Certificate Reference",
        help="Reference of the calibration certificate.")
    technician = fields.Char(
        help="Person or lab that performed the calibration.")
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Confirmed")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    company_id = fields.Many2one(
        related="instrument_id.company_id", store=True, readonly=True)
    note = fields.Text()

    @api.constrains("calibration_date", "instrument_id")
    def _check_date(self):
        for event in self:
            if event.calibration_date > fields.Date.context_today(event):
                raise ValidationError(_(
                    "The calibration date of %s cannot be in the future.",
                    event.name))

    def action_confirm(self):
        for event in self:
            if event.state != "draft":
                raise UserError(_("Only a draft calibration can be confirmed."))
            event.state = "done"
            instrument = event.instrument_id
            instrument.write({"last_calibration": event.calibration_date})
            if event.result == "fail":
                instrument.state = "blocked"
                instrument.message_post(body=_(
                    "Instrument blocked after a failed calibration."))
            instrument.message_post(body=_(
                "Calibration %s confirmed on %s.",
                event.name, event.calibration_date))
        return True
