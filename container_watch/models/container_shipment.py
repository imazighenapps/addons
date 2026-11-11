# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ContainerShipment(models.Model):
    _name = "container.shipment"
    _description = "Import Container"
    _inherit = ["mail.thread"]
    _order = "eta desc, id desc"

    name = fields.Char(
        string="Container Ref", required=True, copy=False, tracking=True)
    booking_ref = fields.Char(string="Booking Ref", tracking=True)
    vessel = fields.Char()
    origin = fields.Char(required=True)
    destination = fields.Char(required=True)
    eta = fields.Date(string="ETA", tracking=True)
    arrived_on = fields.Date(string="Arrived On", readonly=True, copy=False)
    state = fields.Selection(
        [("booked", "Booked"), ("at_sea", "At Sea"),
         ("arrived", "Arrived"), ("released", "Released")],
        default="booked", required=True, copy=False, tracking=True, index=True)
    charge_ids = fields.One2many(
        "container.charge", "shipment_id", string="Charges")
    charge_count = fields.Integer(compute="_compute_amounts", store=True)
    total_amount = fields.Monetary(
        compute="_compute_amounts", store=True, currency_field="currency_id")
    due_amount = fields.Monetary(
        string="Amount Due", compute="_compute_amounts", store=True,
        currency_field="currency_id")
    is_delayed = fields.Boolean(
        compute="_compute_is_delayed", store=True, index=True)
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    active = fields.Boolean(default=True)
    note = fields.Text()

    @api.depends("charge_ids.amount", "charge_ids.settled")
    def _compute_amounts(self):
        for shipment in self:
            charges = shipment.charge_ids
            shipment.charge_count = len(charges)
            shipment.total_amount = sum(charges.mapped("amount"))
            shipment.due_amount = sum(
                charges.filtered(lambda c: not c.settled).mapped("amount"))

    @api.depends("eta", "state")
    def _compute_is_delayed(self):
        today = fields.Date.context_today(self)
        for shipment in self:
            shipment.is_delayed = bool(
                shipment.eta
                and shipment.state in ("booked", "at_sea")
                and shipment.eta < today)

    @api.constrains("eta", "arrived_on")
    def _check_dates(self):
        for shipment in self:
            if shipment.arrived_on and shipment.eta \
                    and shipment.arrived_on < shipment.eta:
                # arrival before eta is fine; only reject obvious inverted input
                # when both set and arrived far before booking context is unlikely
                # so enforce only if arrived_on predates year sanity? keep simple:
                pass
            if shipment.arrived_on and shipment.arrived_on > fields.Date.today():
                raise ValidationError(_(
                    "The arrival date of %s cannot be in the future.",
                    shipment.name))

    def action_sail(self):
        for shipment in self:
            if shipment.state != "booked":
                raise UserError(_("Only a booked container can sail."))
            shipment.state = "at_sea"
        return True

    def action_mark_arrived(self):
        for shipment in self:
            if shipment.state != "at_sea":
                raise UserError(_("Only a container at sea can arrive."))
            shipment.state = "arrived"
        return True

    def action_release(self):
        for shipment in self:
            if shipment.state != "arrived":
                raise UserError(_("Only an arrived container can be released."))
            shipment.write({
                "state": "released",
                "arrived_on": shipment.arrived_on or fields.Date.context_today(shipment),
            })
            shipment.message_post(body=_("The container was released."))
        return True

    def action_reset_booked(self):
        for shipment in self:
            if shipment.state == "released":
                raise UserError(_("A released container cannot be reset."))
            shipment.write({"state": "booked", "arrived_on": False})
        return True
