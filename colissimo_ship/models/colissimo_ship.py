# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ColissimoConnection(models.Model):
    _name = "colissimo.connection"
    _description = "Colissimo Connection"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)
    contract_number = fields.Char()
    password_ref = fields.Char(string="Password Reference")
    environment = fields.Selection(
        [("test", "Test"), ("production", "Production")], default="test", required=True)
    state = fields.Selection([("draft", "Draft"), ("active", "Active")], default="draft")
    active = fields.Boolean(default=True)

    def action_activate(self):
        for rec in self:
            if not rec.contract_number:
                raise UserError(_("Set the contract number before activating."))
            rec.state = "active"
        return True


class ColissimoShipment(models.Model):
    _name = "colissimo.shipment"
    _description = "Colissimo Shipment"
    _inherit = ["mail.thread"]
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, copy=False, default="New")
    connection_id = fields.Many2one("colissimo.connection", required=True, ondelete="restrict")
    company_id = fields.Many2one(related="connection_id.company_id", store=True)
    picking_id = fields.Many2one("stock.picking", string="Delivery")
    partner_id = fields.Many2one("res.partner", string="Recipient")
    service_type = fields.Selection(
        [("home", "Home"), ("pickup", "Pickup Point"), ("signed", "Signed")],
        default="home", required=True)
    weight = fields.Float(default=1.0)
    label_ref = fields.Char()
    tracking_number = fields.Char(copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("ready", "Ready"), ("label", "Label Created"),
         ("in_transit", "In Transit"), ("delivered", "Delivered"), ("exception", "Exception")],
        default="draft", required=True, tracking=True)
    note = fields.Text()
    event_ids = fields.One2many("colissimo.event", "shipment_id")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("colissimo.shipment") or "COL"
        return super().create(vals_list)

    @api.constrains("weight")
    def _check_weight(self):
        for rec in self:
            if rec.weight <= 0:
                raise ValidationError(_("Weight must be positive."))

    def _log(self, status, message):
        self.env["colissimo.event"].create({
            "shipment_id": self.id, "status": status, "message": message})

    def action_prepare(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only draft shipments can be prepared."))
            if not rec.partner_id:
                raise UserError(_("Set the recipient before preparing."))
            rec.state = "ready"
            rec._log("ready", _("Shipment prepared."))
        return True

    def action_label(self):
        for rec in self:
            if rec.state != "ready":
                raise UserError(_("Only ready shipments can get a label."))
            rec.state = "label"
            rec.label_ref = rec.label_ref or ("LBL-%s" % rec.id)
            rec.tracking_number = rec.tracking_number or ("COL%s" % rec.id)
            rec._log("label", _("Label created."))
        return True

    def action_ship(self):
        for rec in self:
            if rec.state != "label":
                raise UserError(_("Create the label before shipping."))
            rec.state = "in_transit"
            rec._log("in_transit", _("Parcel shipped."))
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


class ColissimoEvent(models.Model):
    _name = "colissimo.event"
    _description = "Colissimo Event"
    _order = "create_date desc, id desc"

    shipment_id = fields.Many2one("colissimo.shipment", required=True, ondelete="cascade")
    status = fields.Char(required=True)
    message = fields.Text()
