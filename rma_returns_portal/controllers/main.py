# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class RmaPortal(http.Controller):
    def _check_order(self, order_id):
        order = request.env["sale.order"].browse(int(order_id))
        if not order.exists() or order.partner_id != request.env.user.partner_id.commercial_partner_id:
            return False
        return order.sudo()

    @http.route("/my/returns", type="http", auth="user", website=True)
    def my_returns(self, **kwargs):
        partner = request.env.user.partner_id.commercial_partner_id
        requests = request.env["rma.request"].search(
            [("partner_id", "child_of", partner.id)], order="create_date desc")
        return request.render("rma_returns_portal.portal_returns_list", {
            "requests": requests,
        })

    @http.route("/my/returns/<int:request_id>", type="http", auth="user", website=True)
    def my_return(self, request_id, **kwargs):
        rec = request.env["rma.request"].browse(request_id)
        partner = request.env.user.partner_id.commercial_partner_id
        if not rec.exists() or rec.partner_id.commercial_partner_id != partner:
            return request.not_found()
        return request.render("rma_returns_portal.portal_return_detail", {
            "rma": rec.sudo(),
        })

    @http.route("/my/returns/new/<int:order_id>", type="http", auth="user",
                website=True, methods=["GET", "POST"])
    def my_return_new(self, order_id, **kwargs):
        order = self._check_order(order_id)
        if not order:
            return request.not_found()
        reasons = request.env["rma.reason"].sudo().search(
            [("website_visible", "=", True)])
        if request.httprequest.method == "POST":
            lines = []
            for line in order.order_line:
                qty = float(kwargs.get("qty_%d" % line.id, 0) or 0)
                if qty > 0:
                    lines.append((0, 0, {
                        "sale_line_id": line.id,
                        "product_id": line.product_id.id,
                        "qty_delivered": line.qty_delivered,
                        "qty_requested": qty,
                        "price_unit": line.price_unit,
                    }))
            if not lines:
                return request.render("rma_returns_portal.portal_return_new", {
                    "order": order, "reasons": reasons,
                    "error": "Select at least one quantity.",
                })
            rma = request.env["rma.request"].sudo().create({
                "partner_id": order.partner_id.id,
                "sale_order_id": order.id,
                "request_type": kwargs.get("request_type", "withdrawal"),
                "reason_id": int(kwargs.get("reason_id")) if kwargs.get("reason_id") else False,
                "line_ids": lines,
            })
            try:
                rma.action_submit()
            except Exception as exc:
                return request.render("rma_returns_portal.portal_return_new", {
                    "order": order, "reasons": reasons, "error": str(exc),
                })
            return request.redirect("/my/returns/%d" % rma.id)
        return request.render("rma_returns_portal.portal_return_new", {
            "order": order, "reasons": reasons,
        })
