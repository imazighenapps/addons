# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class OfficeSupply(models.Model):
    _name = "office.supply"
    _description = "Office Supply"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    location = fields.Char(
        help="Office or storage location where the supply is kept.")
    on_hand_qty = fields.Integer(
        string="On Hand", default=0, required=True,
        help="Current quantity available on the shelf.")
    min_qty = fields.Integer(
        string="Minimum Quantity", default=0, required=True,
        help="Level below which a restock should be requested.")
    shortage_qty = fields.Integer(
        string="Shortage", compute="_compute_shortage", store=True,
        help="Quantity missing to reach the minimum level.")
    request_ids = fields.One2many(
        "office.restock", "supply_id", string="Restock Requests")
    request_count = fields.Integer(
        string="Requests", compute="_compute_requests")
    open_request_count = fields.Integer(
        string="Open Requests", compute="_compute_requests")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)
    note = fields.Text()

    @api.depends("on_hand_qty", "min_qty")
    def _compute_shortage(self):
        for supply in self:
            shortage = supply.min_qty - supply.on_hand_qty
            supply.shortage_qty = shortage if shortage > 0 else 0

    @api.depends("request_ids", "request_ids.state")
    def _compute_requests(self):
        for supply in self:
            supply.request_count = len(supply.request_ids)
            supply.open_request_count = len(supply.request_ids.filtered(
                lambda req: req.state == "pending"))

    @api.constrains("on_hand_qty")
    def _check_on_hand_qty(self):
        for supply in self:
            if supply.on_hand_qty < 0:
                raise ValidationError(_(
                    "The on-hand quantity of %s cannot be negative.",
                    supply.name))

    @api.constrains("min_qty")
    def _check_min_qty(self):
        for supply in self:
            if supply.min_qty < 0:
                raise ValidationError(_(
                    "The minimum quantity of %s cannot be negative.",
                    supply.name))
