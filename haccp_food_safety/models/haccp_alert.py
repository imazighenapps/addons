# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HaccpExpiryAlert(models.Model):
    _name = "haccp.expiry.alert"
    _description = "HACCP Expiry Alert"
    _order = "days_left"

    lot_id = fields.Many2one("stock.lot", required=True, ondelete="cascade")
    days_left = fields.Integer()
    state = fields.Selection(
        [("new", "New"), ("ack", "Acknowledged"), ("done", "Done")],
        default="new",
    )

    @api.model
    def _cron_check_expiry(self, horizon_days=14):
        from datetime import date, timedelta
        limit = date.today() + timedelta(days=horizon_days)
        lots = self.env["stock.lot"].search(
            [("removal_date", "!=", False), ("removal_date", "<=", limit)])
        existing = self.search([("state", "=", "new")]).mapped("lot_id").ids
        for lot in lots.filtered(lambda l: l.id not in existing):
            delta = (lot.removal_date.date() - date.today()).days if lot.removal_date else 0
            self.create({"lot_id": lot.id, "days_left": delta})
        return True
