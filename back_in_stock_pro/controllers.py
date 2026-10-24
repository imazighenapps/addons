# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class StockAlertController(http.Controller):
    @http.route("/stock-alert/subscribe", type="jsonrpc", auth="public",
                csrf=False)
    def subscribe(self, product_id=None, email=None, **kwargs):
        try:
            alert = request.env["stock.alert.request"].sudo().subscribe(
                product_id, email)
        except Exception as error:
            return {"ok": False, "error": str(error)}
        return {"ok": True, "id": alert.id, "state": alert.state}
