# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class LotRecallLine(models.Model):
    _name = "lot.recall.line"
    _description = "Recall Impact Line"
    _order = "id"

    recall_id = fields.Many2one(
        "lot.recall", string="Recall", required=True, ondelete="cascade",
        index=True)
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, index=True)
    lot_name = fields.Char(
        string="Lot / Serial", required=True,
        help="Lot or serial number affected by the recall.")
    quantity = fields.Float(
        required=True, default=1.0, digits="Product Unit of Measure")
    reference = fields.Char(
        string="Delivery Reference",
        help="Delivery, picking or order reference for the impacted lot.")
    notified = fields.Boolean(default=False, copy=False)
    notified_on = fields.Date(string="Notified On", copy=False)
    company_id = fields.Many2one(
        "res.company", related="recall_id.company_id", store=True,
        readonly=True, index=True)

    @api.constrains("quantity")
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_(
                    "The impacted quantity for lot %s must be above zero.",
                    line.lot_name))

    @api.constrains("notified", "notified_on")
    def _check_notified_date(self):
        for line in self:
            if line.notified and not line.notified_on:
                raise ValidationError(_(
                    "A notified impact line for lot %s must have a notification date.",
                    line.lot_name))
