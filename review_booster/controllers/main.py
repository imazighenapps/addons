# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import http
from odoo.http import request


class ReviewRedirect(http.Controller):
    @http.route("/r/<string:token>", type="http", auth="public", website=True)
    def go(self, token, **kwargs):
        req = request.env["review.request"].sudo().search(
            [("token", "=", token)], limit=1)
        if not req:
            return request.not_found()
        req.write({"state": "clicked", "clicked_on": datetime.now()})
        return request.redirect(req.campaign_id.google_url)
