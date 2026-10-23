# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    pm_counter_ids = fields.One2many("pm.counter", "equipment_id")
    pm_health = fields.Float(string="Health Score", compute="_compute_pm_health",
                             store=True)
    pm_health_detail = fields.Text(string="Health Detail")
    pm_last_reading_date = fields.Datetime(compute="_compute_pm_health", store=True)
    pm_stale = fields.Boolean(compute="_compute_pm_health", store=True)

    @api.depends("pm_counter_ids.last_value")
    def _compute_pm_health(self):
        from datetime import timedelta
        for equip in self:
            score, reasons = 100.0, []
            alerts = self.env["pm.alert"].search(
                [("equipment_id", "=", equip.id), ("state", "=", "open")])
            crit = len(alerts.filtered(lambda a: a.level == "crit"))
            warn = len(alerts.filtered(lambda a: a.level == "warn"))
            score -= 30 * crit
            score -= 15 * warn
            if crit:
                reasons.append("%d critical alert(s)" % crit)
            if warn:
                reasons.append("%d warning(s)" % warn)
            overdue = 0
            latest = False
            for counter in equip.pm_counter_ids:
                if counter.next_due_value and counter.last_value >= counter.next_due_value:
                    overdue += 1
                if counter.last_reading_date and (not latest or counter.last_reading_date > latest):
                    latest = counter.last_reading_date
            score -= 20 * overdue
            if overdue:
                reasons.append("%d overdue service(s)" % overdue)
            equip.pm_last_reading_date = latest
            stale = not latest or latest < fields.Datetime.now() - timedelta(days=30)
            equip.pm_stale = stale
            if stale:
                score -= 10
                reasons.append("stale data")
            equip.pm_health = max(0.0, score)
            equip.pm_health_detail = "; ".join(reasons) if reasons else "All signals nominal."

    def _pm_refresh_health(self):
        self._compute_pm_health()
