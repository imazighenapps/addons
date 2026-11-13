# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class DpdConnection(models.Model):
    _name = "dpd.connection"
    _description = "DPD Connection"

    name = fields.Char(required=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    customer_number = fields.Char()
    depot_code = fields.Char()
    environment = fields.Selection([("test", "Test"), ("production", "Production")], default="test", required=True)
    state = fields.Selection([("draft", "Draft"), ("active", "Active")], default="draft")
    active = fields.Boolean(default=True)

    def action_activate(self):
        for rec in self:
            if not rec.customer_number:
                raise UserError(_("Set the customer number before activating."))
            rec.state = "active"
        return True


class DpdShipment(models.Model):
    _name = "dpd.shipment"
    _description = "DPD Shipment"
    _inherit = ["mail.thread"]
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, copy=False, default="New")
    connection_id = fields.Many2one("dpd.connection", required=True, ondelete="restrict")
    company_id = fields.Many2one(related="connection_id.company_id", store=True)
    picking_id = fields.Many2one("stock.picking")
    partner_id = fields.Many2one("res.partner")
    weight = fields.Float(default=1.0)
    parcel_count = fields.Integer(default=1)
    label_ref = fields.Char()
    tracking_number = fields.Char(copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("ready", "Ready"), ("label", "Label Created"),
         ("in_transit", "In Transit"), ("delivered", "Delivered"), ("exception", "Exception")],
        default="draft", required=True, tracking=True)
    note = fields.Text()
    event_ids = fields.One2many("dpd.event", "shipment_id")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("dpd.shipment") or "DPD"
        return super().create(vals_list)

    @api.constrains("weight", "parcel_count")
    def _check_vals(self):
        for rec in self:
            if rec.weight <= 0:
                raise ValidationError(_("Weight must be positive."))
            if rec.parcel_count < 1:
                raise ValidationError(_("Parcel count must be at least 1."))

    def _log(self, status, msg):
        self.env["dpd.event"].create({"shipment_id": self.id, "status": status, "message": msg})

    def action_prepare(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only draft shipments can be prepared."))
            rec.state = "ready"; rec._log("ready", _("Prepared."))
        return True

    def action_label(self):
        for rec in self:
            if rec.state != "ready":
                raise UserError(_("Only ready shipments can get a label."))
            rec.state = "label"
            rec.label_ref = rec.label_ref or ("LBL-%s" % rec.id)
            rec.tracking_number = rec.tracking_number or ("DPD%s" % rec.id)
            rec._log("label", _("Label created."))
        return True

    def action_ship(self):
        for rec in self:
            if rec.state != "label":
                raise UserError(_("Create the label before shipping."))
            rec.state = "in_transit"; rec._log("in_transit", _("Shipped."))
        return True

    def action_deliver(self):
        for rec in self:
            if rec.state != "in_transit":
                raise UserError(_("Only in-transit shipments can be delivered."))
            rec.state = "delivered"; rec._log("delivered", _("Delivered."))
        return True

    def action_reset(self):
        for rec in self:
            if rec.state == "delivered":
                raise UserError(_("Delivered shipments cannot be reset."))
            rec.state = "draft"; rec.label_ref = False; rec.tracking_number = False
        return True


class DpdEvent(models.Model):
    _name = "dpd.event"
    _description = "DPD Event"
    _order = "create_date desc, id desc"

    shipment_id = fields.Many2one("dpd.shipment", required=True, ondelete="cascade")
    status = fields.Char(required=True)
    message = fields.Text()
