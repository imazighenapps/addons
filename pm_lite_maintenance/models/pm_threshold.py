# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PmThreshold(models.Model):
    _name = "pm.threshold"
    _description = "Alert Threshold"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    counter_id = fields.Many2one("pm.counter", ondelete="cascade")
    equipment_id = fields.Many2one("maintenance.equipment")
    metric = fields.Selection(
        [("counter", "Counter Value"), ("measure", "Manual Measure (e.g. T°)")],
        default="counter",
    )
    operator = fields.Selection([("gt", ">"), ("lt", "<")], default="gt")
    warn_level = fields.Float(string="Warning Level", required=True)
    crit_level = fields.Float(string="Critical Level", required=True)
    hysteresis = fields.Float(default=0.0)
    active = fields.Boolean(default=True)
    cooldown_hours = fields.Integer(string="Cooldown (hours)", default=24)
    last_trigger = fields.Datetime(readonly=True)

    @api.model
    def _evaluate_counter(self, counter, reading):
        from datetime import timedelta
        now = fields.Datetime.now()
        for th in self.search([("counter_id", "=", counter.id), ("active", "=", True)]):
            value = reading.value
            over_crit = (value >= th.crit_level - th.hysteresis if th.operator == "gt"
                         else value <= th.crit_level + th.hysteresis)
            over_warn = (value >= th.warn_level - th.hysteresis if th.operator == "gt"
                         else value <= th.warn_level + th.hysteresis)
            level = "crit" if over_crit else ("warn" if over_warn else False)
            if not level:
                continue
            if th.last_trigger and th.last_trigger + timedelta(hours=th.cooldown_hours or 0) > now:
                continue
            self.env["pm.alert"]._raise(counter.equipment_id, th, counter, level, reading)
            th.last_trigger = now

    @api.model
    def _cron_evaluate_all(self):
        for counter in self.env["pm.counter"].search([("active", "=", True)]):
            reading = self.env["pm.reading"].search(
                [("counter_id", "=", counter.id)], order="date desc", limit=1)
            if reading:
                self._evaluate_counter(counter, reading)
        return True
