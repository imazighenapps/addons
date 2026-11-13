# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MondialrelayConnection(models.Model):
    _name = "mondialrelay.connection"
    _description = "Mondial Relay Connection"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)
    merchant_id = fields.Char(string="Merchant ID")
    api_key_ref = fields.Char(string="API Key Reference")
    environment = fields.Selection(
        [("test", "Test"), ("production", "Production")], default="test", required=True)
    active = fields.Boolean(default=True)
    state = fields.Selection([("draft", "Draft"), ("active", "Active")], default="draft")

    def action_activate(self):
        for rec in self:
            if not rec.merchant_id:
                raise UserError(_("Set the merchant ID before activating."))
            rec.state = "active"
        return True


class MondialrelayPoint(models.Model):
    _name = "mondialrelay.point"
    _description = "Mondial Relay Point"

    name = fields.Char(required=True)
    relay_code = fields.Char(required=True, index=True)
    street = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    country_id = fields.Many2one("res.country")
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_uniq', "UNIQUE(relay_code)", "The relay point code must be unique."),
    ]


class MondialrelayShipment(models.Model):
    _name = "mondialrelay.shipment"
    _description = "Mondial Relay Shipment"
    _inherit = ["mail.thread"]
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, copy=False, default="New")
    connection_id = fields.Many2one(
        "mondialrelay.connection", required=True, ondelete="restrict")
    company_id = fields.Many2one(related="connection_id.company_id", store=True)
    picking_id = fields.Many2one("stock.picking", string="Delivery")
    partner_id = fields.Many2one("res.partner", string="Customer")
    relay_point_id = fields.Many2one("mondialrelay.point", string="Relay Point")
    weight = fields.Float(default=1.0)
    parcel_count = fields.Integer(default=1)
    label_ref = fields.Char(string="Label Reference")
    tracking_number = fields.Char(copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("ready", "Ready"), ("label", "Label Created"),
         ("in_transit", "In Transit"), ("delivered", "Delivered"), ("exception", "Exception")],
        default="draft", required=True, tracking=True)
    note = fields.Text()
    event_ids = fields.One2many("mondialrelay.event", "shipment_id")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "mondialrelay.shipment") or "MR"
        return super().create(vals_list)

    @api.constrains("weight", "parcel_count")
    def _check_values(self):
        for rec in self:
            if rec.weight <= 0:
                raise ValidationError(_("Weight must be positive."))
            if rec.parcel_count < 1:
                raise ValidationError(_("Parcel count must be at least 1."))

    def _log(self, status, message):
        self.ensure_one()
        self.env["mondialrelay.event"].create({
            "shipment_id": self.id, "status": status, "message": message,
        })

    def action_prepare(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only draft shipments can be prepared."))
            if not rec.relay_point_id:
                raise UserError(_("Select a relay point before preparing."))
            rec.state = "ready"
            rec._log("ready", _("Shipment prepared."))
        return True

    def action_label(self):
        for rec in self:
            if rec.state != "ready":
                raise UserError(_("Only ready shipments can get a label."))
            rec.state = "label"
            rec.label_ref = rec.label_ref or ("LBL-%s" % rec.id)
            rec.tracking_number = rec.tracking_number or ("MR%s" % rec.id)
            rec._log("label", _("Label created."))
        return True

    def action_ship(self):
        for rec in self:
            if rec.state != "label":
                raise UserError(_("Create the label before shipping."))
            rec.state = "in_transit"
            rec._log("in_transit", _("Parcel handed over."))
        return True

    def action_deliver(self):
        for rec in self:
            if rec.state != "in_transit":
                raise UserError(_("Only in-transit shipments can be delivered."))
            rec.state = "delivered"
            rec._log("delivered", _("Parcel delivered."))
        return True

    def action_reset(self):
        for rec in self:
            if rec.state == "delivered":
                raise UserError(_("Delivered shipments cannot be reset."))
            rec.state = "draft"
            rec.label_ref = False
            rec.tracking_number = False
        return True


class MondialrelayEvent(models.Model):
    _name = "mondialrelay.event"
    _description = "Mondial Relay Event"
    _order = "create_date desc, id desc"

    shipment_id = fields.Many2one(
        "mondialrelay.shipment", required=True, ondelete="cascade", index=True)
    status = fields.Char(required=True)
    message = fields.Text()
