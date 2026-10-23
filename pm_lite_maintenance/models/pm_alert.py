# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PmAlert(models.Model):
    _name = "pm.alert"
    _description = "Predictive Alert"
    _inherit = ["mail.thread"]
    _order = "create_date desc"

    name = fields.Char(compute="_compute_name", store=True)
    equipment_id = fields.Many2one("maintenance.equipment", required=True,
                                   ondelete="cascade")
    company_id = fields.Many2one("res.company", related="equipment_id.company_id",
                                 store=True)
    threshold_id = fields.Many2one("pm.threshold", ondelete="set null")
    counter_id = fields.Many2one("pm.counter", ondelete="set null")
    level = fields.Selection(
        [("info", "Info"), ("warn", "Warning"), ("crit", "Critical")],
        default="warn",
        tracking=True,
    )
    state = fields.Selection(
        [("open", "Open"), ("ack", "Acknowledged"), ("done", "Done")],
        default="open",
        tracking=True,
    )
    reading_id = fields.Many2one("pm.reading", ondelete="set null")
    request_id = fields.Many2one("maintenance.request", string="Maintenance Request",
                                 copy=False)
    message = fields.Text()

    @api.depends("equipment_id", "level")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s - %s" % (rec.equipment_id.name or "?",
                                    dict(rec._fields["level"].selection).get(rec.level, ""))

    @api.model
    def _raise(self, equipment, threshold, counter, level, reading):
        existing = self.search([
            ("equipment_id", "=", equipment.id),
            ("threshold_id", "=", threshold.id),
            ("state", "=", "open"),
        ], limit=1)
        if existing:
            return existing
        alert = self.create({
            "equipment_id": equipment.id,
            "threshold_id": threshold.id,
            "counter_id": counter.id if counter else False,
            "level": level,
            "reading_id": reading.id if reading else False,
            "message": _("Threshold '%s' crossed at %s.") % (threshold.name, reading.value if reading else "?"),
        })
        request = self.env["maintenance.request"].create({
            "name": _("PM Lite: %s") % alert.name,
            "equipment_id": equipment.id,
            "maintenance_type": "preventive",
            "priority": "3" if level == "crit" else "1",
            "description": alert.message,
        })
        alert.request_id = request.id
        return alert

    def action_ack(self):
        self.write({"state": "ack"})

    def action_done(self):
        self.write({"state": "done"})
