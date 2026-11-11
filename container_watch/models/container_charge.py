# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ContainerCharge(models.Model):
    _name = "container.charge"
    _description = "Container Charge"
    _order = "shipment_id, id"

    shipment_id = fields.Many2one(
        "container.shipment", required=True, ondelete="cascade", index=True)
    name = fields.Char(required=True)
    charge_type = fields.Selection(
        [("freight", "Freight"), ("demurrage", "Demurrage"),
         ("release", "Release"), ("handling", "Handling"),
         ("other", "Other")],
        default="freight", required=True)
    payer = fields.Selection(
        [("us", "Our Company"), ("supplier", "Supplier"),
         ("forwarder", "Forwarder"), ("other", "Other")],
        default="us", required=True)
    amount = fields.Monetary(required=True, currency_field="currency_id")
    currency_id = fields.Many2one(
        related="shipment_id.currency_id", store=True, readonly=True)
    settled = fields.Boolean(default=False)
    company_id = fields.Many2one(
        related="shipment_id.company_id", store=True, readonly=True)

    @api.constrains("amount")
    def _check_amount(self):
        for charge in self:
            if charge.amount < 0:
                raise ValidationError(_(
                    "The amount of charge %s cannot be negative.", charge.name))

    @api.model_create_multi
    def create(self, vals_list):
        shipments = self.env["container.shipment"].browse(
            [v.get("shipment_id") for v in vals_list if v.get("shipment_id")])
        for shipment in shipments:
            if shipment.state == "released":
                raise UserError(_(
                    "Cannot add a charge to released container %s.", shipment.name))
        return super().create(vals_list)

    def write(self, vals):
        for charge in self:
            if charge.shipment_id.state == "released":
                raise UserError(_(
                    "Charges of released container %s cannot be changed.",
                    charge.shipment_id.name))
        return super().write(vals)
