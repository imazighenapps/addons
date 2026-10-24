# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class FeedController(http.Controller):
    @http.route("/feed/<string:token>", type="http", auth="public",
                csrf=False, website=True, sitemap=False)
    def feed(self, token, **kwargs):
        channel = request.env["feed.channel"].sudo().search(
            [("token", "=", token), ("active", "=", True)], limit=1)
        if not channel or not channel.content:
            return request.not_found()
        return request.make_response(
            channel.content,
            headers=[
                ("Content-Type", channel.mimetype or "application/xml"),
                ("Content-Disposition", "inline; filename=feed.%s"
                 % ("csv" if channel.format == "csv" else "xml")),
            ])
