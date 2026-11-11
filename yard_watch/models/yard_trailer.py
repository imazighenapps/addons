# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class YardTrailer(models.Model):
    _name = "yard.trailer"
    _description = "Yard Trailer"
    _inherit = ["mail.thread"]
    _order = "arrived_on desc, id desc"

    name = fields.Char(
        string="Trailer Reference", required=True, tracking=True,
        help="Plate number or transport reference of the trailer.")
    carrier = fields.Char(
        tracking=True,
        help="Carrier or transport company bringing the trailer.")
    slot_id = fields.Many2one(
        "yard.slot", string="Yard Slot", required=True,
        ondelete="restrict", index=True, tracking=True)
    arrived_on = fields.Datetime(
        string="Arrived On", required=True,
        default=fields.Datetime.now, tracking=True)
    docked_on = fields.Datetime(string="Docked On", readonly=True, copy=False)
    departed_on = fields.Datetime(
        string="Departed On", readonly=True, copy=False)
    wait_hours = fields.Float(
        string="Waiting Hours", compute="_compute_wait_hours", store=True,
        help="Hours between arrival and departure, or until now while present.")
    state = fields.Selection(
        [("waiting", "Waiting"), ("docked", "Docked"),
         ("departed", "Departed")],
        default="waiting", required=True, copy=False, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("arrived_on", "departed_on", "state")
    def _compute_wait_hours(self):
        now = fields.Datetime.now()
        for trailer in self:
            if trailer.arrived_on:
                end = trailer.departed_on or now
                delta = end - trailer.arrived_on
                trailer.wait_hours = max(delta.total_seconds() / 3600.0, 0.0)
            else:
                trailer.wait_hours = 0.0

    @api.constrains("arrived_on", "docked_on", "departed_on")
    def _check_dates(self):
        for trailer in self:
            if trailer.docked_on and trailer.docked_on < trailer.arrived_on:
                raise ValidationError(_(
                    "The dock time of trailer %s cannot come before its "
                    "arrival.", trailer.name))
            if trailer.departed_on and trailer.departed_on < trailer.arrived_on:
                raise ValidationError(_(
                    "The departure of trailer %s cannot come before its "
                    "arrival.", trailer.name))
            if trailer.departed_on and trailer.docked_on \
                    and trailer.departed_on < trailer.docked_on:
                raise ValidationError(_(
                    "The departure of trailer %s cannot come before it was "
                    "docked.", trailer.name))

    def action_dock(self):
        for trailer in self:
            if trailer.state != "waiting":
                raise ValidationError(_(
                    "Only a waiting trailer can be docked."))
            trailer.write({
                "state": "docked",
                "docked_on": fields.Datetime.now(),
            })
            trailer.message_post(body=_("Trailer moved to the dock."))
        return True

    def action_depart(self):
        for trailer in self:
            if trailer.state == "departed":
                raise ValidationError(_(
                    "Trailer %s has already departed.", trailer.name))
            trailer.write({
                "state": "departed",
                "departed_on": fields.Datetime.now(),
            })
            trailer.message_post(body=_("Trailer departed from the yard."))
        return True
