# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PalletAccount(models.Model):
    _name = "pallet.account"
    _description = "Pallet Account"
    _inherit = ["mail.thread"]
    _order = "partner_name"

    name = fields.Char(
        required=True, tracking=True,
        help="Display name of the pallet account.")
    partner_name = fields.Char(
        string="Partner", required=True, tracking=True,
        help="Partner holding or owing returnable pallets.")
    movement_ids = fields.One2many(
        "pallet.movement", "account_id", string="Movements")
    lent_qty = fields.Integer(
        string="Lent", compute="_compute_totals", store=True,
        help="Total pallets lent to the partner.")
    returned_qty = fields.Integer(
        string="Returned", compute="_compute_totals", store=True,
        help="Total pallets returned by the partner.")
    balance_qty = fields.Integer(
        string="Balance", compute="_compute_totals", store=True,
        help="Pallets currently owed by the partner.")
    movement_count = fields.Integer(
        string="Movements", compute="_compute_totals", store=True,
        help="Number of pallet movements on this account.")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("movement_ids", "movement_ids.direction", "movement_ids.quantity", "movement_ids.state")
    def _compute_totals(self):
        for record in self:
            confirmed = record.movement_ids.filtered(lambda m: m.state == "confirmed")
            lent = sum(confirmed.filtered(lambda m: m.direction == "lent").mapped("quantity"))
            returned = sum(confirmed.filtered(lambda m: m.direction == "returned").mapped("quantity"))
            record.lent_qty = lent
            record.returned_qty = returned
            record.balance_qty = lent - returned
            record.movement_count = len(record.movement_ids)

    @api.constrains("partner_name", "company_id")
    def _check_partner_unique(self):
        for record in self:
            if self.search_count([
                ("id", "!=", record.id),
                ("partner_name", "=", record.partner_name),
                ("company_id", "=", record.company_id.id),
            ]):
                raise ValidationError(_(
                    "An account for %s already exists in this company.",
                    record.partner_name))
