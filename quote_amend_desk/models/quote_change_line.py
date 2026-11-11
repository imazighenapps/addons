# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class QuoteChangeLine(models.Model):
    _name = "quote.change.line"
    _description = "Quotation Change"
    _order = "id"

    amendment_id = fields.Many2one(
        "quote.amendment", string="Amendment", required=True,
        ondelete="cascade", index=True)
    field_label = fields.Char(
        string="Changed Item",
        help="What changed on the quotation, for example Price, "
             "Quantity or Delivery Date.")
    old_value = fields.Char(
        string="Previous Value",
        help="The value shown in the version the customer knew.")
    new_value = fields.Char(
        required=True,
        help="The value shown in the revised version.")
    company_id = fields.Many2one(
        related="amendment_id.company_id", store=True, readonly=True)

    @api.constrains("field_label", "old_value", "new_value")
    def _check_captures_change(self):
        for line in self:
            if not line.field_label:
                raise ValidationError(_(
                    "A change always names the item that changed."))
            if (line.old_value or "") == (line.new_value or ""):
                raise ValidationError(_(
                    "The change %s records no difference: the previous "
                    "value and the new value are the same.",
                    line.field_label))
