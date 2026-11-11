# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FirstaidItem(models.Model):
    _name = "firstaid.item"
    _description = "First Aid Item"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    kit_id = fields.Many2one(
        "firstaid.kit", string="Kit", required=True,
        ondelete="cascade", index=True, tracking=True)
    qty_required = fields.Integer(
        string="Required", default=1, required=True,
        help="Quantity that must be present in the kit.")
    qty_on_hand = fields.Integer(
        string="On Hand", default=0, required=True,
        help="Quantity currently present in the kit.")
    expiry_date = fields.Date(
        string="Expiry Date", tracking=True,
        help="Date after which the item must be replaced.")
    company_id = fields.Many2one(
        related="kit_id.company_id", store=True, readonly=True, index=True)

    @api.constrains("qty_required", "qty_on_hand")
    def _check_quantities(self):
        for item in self:
            if item.qty_required <= 0:
                raise ValidationError(_(
                    "The required quantity of %s must be above zero.",
                    item.name))
            if item.qty_on_hand < 0:
                raise ValidationError(_(
                    "The on-hand quantity of %s cannot be negative.",
                    item.name))
