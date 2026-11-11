# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ProvisionMovement(models.Model):
    _name = "provision.movement"
    _description = "Provision Movement"
    _order = "date desc, id desc"

    provision_id = fields.Many2one(
        "provision.book", string="Provision", required=True,
        ondelete="cascade", index=True)
    date = fields.Date(
        required=True, default=fields.Date.context_today, index=True)
    movement_type = fields.Selection(
        [("increase", "Increase"), ("decrease", "Decrease")],
        required=True, default="increase",
        help="Whether this movement increases or decreases the provision.")
    amount = fields.Monetary(required=True)
    currency_id = fields.Many2one(
        related="provision_id.currency_id", store=True, readonly=True)
    reason = fields.Char(
        required=True,
        help="Short explanation of why the provision moved.")
    company_id = fields.Many2one(
        related="provision_id.company_id", store=True, readonly=True)

    @api.constrains("amount")
    def _check_amount(self):
        for move in self:
            if move.amount <= 0:
                raise ValidationError(_(
                    "The amount of a provision movement must be greater than "
                    "zero."))

    @api.model_create_multi
    def create(self, vals_list):
        prov_ids = {v["provision_id"] for v in vals_list if v.get("provision_id")}
        if prov_ids:
            closed = self.env["provision.book"].browse(
                sorted(prov_ids)).filtered(lambda p: p.state == "closed")
            if closed:
                raise UserError(_(
                    "Provision %s is closed: no movement can be added.",
                    closed[0].name))
        return super().create(vals_list)

    def write(self, vals):
        for move in self:
            if move.provision_id.state == "closed":
                raise UserError(_(
                    "Provision %s is closed: its movements cannot be changed.",
                    move.provision_id.name))
        return super().write(vals)
