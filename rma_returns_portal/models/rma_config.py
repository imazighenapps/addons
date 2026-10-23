# -*- coding: utf-8 -*-
from odoo import api, fields, models


class RmaConfig(models.TransientModel):
    _name = "rma.config"
    _description = "RMA Configuration"

    return_window_days = fields.Integer(default=30)
    warranty_days = fields.Integer(default=730)
    auto_approve_amount = fields.Float(string="Auto-approve Below (€)")
    withdrawal_text = fields.Text(string="Withdrawal Information Text")

    @api.model
    def _get_param(self, key, default=""):
        return self.env["ir.config_parameter"].sudo().get_param(key, default)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        res["return_window_days"] = int(self._get_param("rma_returns_portal.window_days", "30"))
        res["warranty_days"] = int(self._get_param("rma_returns_portal.warranty_days", "730"))
        res["auto_approve_amount"] = float(self._get_param("rma_returns_portal.auto_amount", "0"))
        res["withdrawal_text"] = self._get_param("rma_returns_portal.withdrawal_text", "")
        return res

    def action_save(self):
        self.ensure_one()
        params = self.env["ir.config_parameter"].sudo()
        params.set_param("rma_returns_portal.window_days", self.return_window_days)
        params.set_param("rma_returns_portal.warranty_days", self.warranty_days)
        params.set_param("rma_returns_portal.auto_amount",
                         self.auto_approve_amount)
        params.set_param("rma_returns_portal.withdrawal_text",
                       self.withdrawal_text or "")
        return {"type": "ir.actions.act_window_close"}
