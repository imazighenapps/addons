# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request


class PmApi(http.Controller):
    @http.route("/api/pm/v1/readings", type="json", auth="public", methods=["POST"],
                csrf=False)
    def push_reading(self, **payload):
        data = payload or {}
        token = data.get("token", "")
        expected = request.env["ir.config_parameter"].sudo().get_param("pm_lite.api_token", "")
        if not expected or token != expected:
            return {"ok": False, "error": "invalid token"}
        equipment = request.env["maintenance.equipment"].sudo().search(
            [("name", "=", data.get("equipment_ref", ""))], limit=1)
        if not equipment:
            return {"ok": False, "error": "unknown equipment"}
        counter = request.env["pm.counter"].sudo().search(
            [("equipment_id", "=", equipment.id),
             ("type_id.code", "=", data.get("counter_code", "hours"))], limit=1)
        if not counter:
            return {"ok": False, "error": "unknown counter"}
        if str(data.get("external_id")) and request.env["pm.reading"].sudo().search_count(
                [("external_id", "=", str(data.get("external_id"))) ]):
            return {"ok": True, "duplicate": True}
        reading = request.env["pm.reading"].sudo().create({
            "counter_id": counter.id,
            "value": float(data.get("value", 0)),
            "source": "api",
            "external_id": str(data.get("external_id") or ""),
            "note": str(data.get("at", "")),
        })
        return {"ok": True, "id": reading.id}
