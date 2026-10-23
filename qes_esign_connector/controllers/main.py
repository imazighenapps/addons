# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class QesWebhook(http.Controller):
    @http.route("/qes/webhook/<string:token>", type="http", auth="public",
                methods=["POST"], csrf=False)
    def webhook(self, token, **kwargs):
        account = request.env["qes.account"].sudo().search(
            [("webhook_secret", "=", token)], limit=1)
        if not account:
            return request.make_response("unknown webhook", status=404)
        try:
            payload = json.loads(request.httprequest.data.decode("utf-8"))
        except Exception:
            return request.make_response("bad payload", status=400)
        event_id = str(payload.get("event_id") or payload.get("id") or "")
        if event_id and request.env["qes.event"].sudo().search_count(
                [("provider_event_id", "=", event_id)]):
            return request.make_response("duplicate", status=200)
        envelope = request.env["qes.envelope"].sudo().search(
            [("provider_tx_id", "=", str(payload.get("transaction", "")))], limit=1)
        if envelope:
            envelope.sudo()._log(
                "webhook", json.dumps(payload)[:2000],
                actor="provider", ip=request.httprequest.remote_addr)
            if event_id:
                envelope.event_ids[:1].sudo().write({"provider_event_id": event_id})
            state = str(payload.get("state", ""))
            if state == "closed":
                envelope.sudo().write({"state": "signed"})
            elif state in ("expired", "cancelled"):
                envelope.sudo().write({"state": "expired" if state == "expired" else "refused"})
        return request.make_response("ok", status=200)
