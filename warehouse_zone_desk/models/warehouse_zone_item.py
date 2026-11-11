# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WarehouseZoneItem(models.Model):
    _name = "warehouse_zone.item"
    _description = "ZoneBook Line"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    entry_id = fields.Many2one(
        "warehouse_zone.entry", string="Entry", required=True, ondelete="cascade", index=True)
    name = fields.Char(string="Description", required=True)
    quantity = fields.Float(default=1.0)
    price = fields.Monetary(currency_field="currency_id")
    subtotal = fields.Monetary(compute="_compute_subtotal", store=True, currency_field="currency_id")
    currency_id = fields.Many2one(related="entry_id.currency_id", store=True, readonly=True)
    company_id = fields.Many2one(related="entry_id.company_id", store=True, readonly=True, index=True)

    @api.depends("quantity", "price")
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.quantity * rec.price

    @api.constrains("quantity")
    def _check_quantity(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError(_("Quantity must be positive."))
