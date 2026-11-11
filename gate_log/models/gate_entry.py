# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class GateEntry(models.Model):
    _name = "gate.entry"
    _description = "Gate Entry"
    _inherit = ["mail.thread"]
    _order = "entered_at desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True,
        help="Reference of the visit, for example a delivery or pickup number.")
    gate_id = fields.Many2one(
        "gate.point", string="Gate", required=True, ondelete="cascade",
        index=True, tracking=True)
    truck_plate = fields.Char(
        string="Plate", required=True, tracking=True,
        help="License plate of the truck or vehicle.")
    carrier_id = fields.Many2one(
        "res.partner", string="Carrier",
        help="Carrier or transport company, when known.")
    driver_name = fields.Char(string="Driver")
    purpose = fields.Selection(
        [("delivery", "Delivery"), ("pickup", "Pickup"),
         ("service", "Service"), ("other", "Other")],
        default="delivery", required=True, tracking=True)
    entered_at = fields.Datetime(
        string="Entered At", required=True, tracking=True,
        default=fields.Datetime.now)
    exited_at = fields.Datetime(
        string="Exited At", readonly=True, copy=False, tracking=True)
    wait_minutes = fields.Float(
        string="Wait (Minutes)", compute="_compute_wait_minutes", store=True,
        help="Total time spent on site between entry and exit.")
    state = fields.Selection(
        [("on_site", "On Site"), ("closed", "Closed")],
        default="on_site", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("entered_at", "exited_at")
    def _compute_wait_minutes(self):
        for entry in self:
            if entry.entered_at and entry.exited_at:
                delta = entry.exited_at - entry.entered_at
                entry.wait_minutes = delta.total_seconds() / 60.0
            else:
                entry.wait_minutes = 0.0

    @api.constrains("entered_at", "exited_at")
    def _check_dates(self):
        for entry in self:
            if entry.exited_at and entry.entered_at \
                    and entry.exited_at < entry.entered_at:
                raise ValidationError(_(
                    "The exit time of \"%s\" cannot be before the entry "
                    "time.", entry.name))

    def action_close(self):
        for entry in self:
            if entry.state != "on_site":
                raise UserError(_(
                    "Only an on-site entry can be closed."))
            entry.write({
                "state": "closed",
                "exited_at": fields.Datetime.now(),
            })
            entry.message_post(body=_(
                "The vehicle has left the site."))
        return True

    def action_reopen(self):
        for entry in self:
            if entry.state != "closed":
                raise UserError(_(
                    "Only a closed entry can be reopened."))
            entry.write({
                "state": "on_site",
                "exited_at": False,
            })
            entry.message_post(body=_(
                "The entry has been reopened and is back on site."))
        return True
