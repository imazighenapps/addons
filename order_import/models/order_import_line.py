# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class OrderImportLine(models.Model):
    _name = "order.import.line"
    _description = "Order Import Line"
    _inherit = ["mail.thread"]
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    name = fields.Char(
        required=True,
        default=lambda self: _("Line %s") % fields.Date.context_today(self))
    batch_id = fields.Many2one(
        "order.import.batch", string="Batch", required=True,
        ondelete="cascade", index=True, tracking=True)
    partner_id = fields.Many2one(
        related="batch_id.partner_id", store=True, readonly=True)
    source_ref = fields.Char(
        string="Source Reference",
        help="Line identifier coming from the customer file.")
    product_ref = fields.Char(
        string="Product Reference",
        help="Product code or description provided in the file.")
    quantity = fields.Float(required=True, default=1.0)
    status = fields.Selection(
        [("draft", "Draft"), ("accepted", "Accepted"),
         ("rejected", "Rejected")],
        default="draft", required=True, tracking=True, index=True)
    error_message = fields.Text(
        string="Error",
        help="Reason why the line was rejected during validation.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.constrains("quantity")
    def _check_quantity(self):
        for line in self:
            if line.quantity < 0:
                raise ValidationError(_(
                    "The quantity of %s cannot be negative.", line.name))
