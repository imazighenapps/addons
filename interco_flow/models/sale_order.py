# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    interco_transfer_ids = fields.One2many(
        "interco.transfer", "sale_order_id", string="Intercompany Transfers")
    interco_transfer_count = fields.Integer(
        string="Intercompany Transfers", compute="_compute_interco_count")

    @api.depends("interco_transfer_ids")
    def _compute_interco_count(self):
        for order in self:
            order.interco_transfer_count = len(order.interco_transfer_ids)

    def _interco_rule(self):
        self.ensure_one()
        return self.env["interco.rule"].search([
            ("company_id", "=", self.company_id.id),
            ("active", "=", True),
        ], limit=1)

    def action_create_interco_transfer(self):
        self.ensure_one()
        rule = self._interco_rule()
        if not rule:
            raise UserError(_(
                "No intercompany rule is configured for this company."))
        transfer = rule._create_transfer(self)
        return {
            "type": "ir.actions.act_window",
            "name": _("Intercompany Transfer"),
            "res_model": "interco.transfer",
            "view_mode": "form",
            "res_id": transfer.id,
        }

    def action_open_interco_transfer(self):
        self.ensure_one()
        transfer = self.interco_transfer_ids[:1]
        if not transfer:
            return self.action_create_interco_transfer()
        return {
            "type": "ir.actions.act_window",
            "name": _("Intercompany Transfer"),
            "res_model": "interco.transfer",
            "view_mode": "form",
            "res_id": transfer.id,
        }
