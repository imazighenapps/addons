# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PmCounterType(models.Model):
    _name = "pm.counter.type"
    _description = "Counter Type"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    unit = fields.Char(default="h")
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint("UNIQUE(code)", "Counter type code must be unique.")


class PmCounter(models.Model):
    _name = "pm.counter"
    _description = "Equipment Usage Counter"
    _inherit = ["mail.thread"]

    name = fields.Char(compute="_compute_name", store=True)
    equipment_id = fields.Many2one("maintenance.equipment", required=True,
                                   ondelete="cascade")
    company_id = fields.Many2one("res.company", related="equipment_id.company_id",
                                 store=True)
    type_id = fields.Many2one("pm.counter.type", string="Type", required=True)
    warning_target = fields.Float(string="Warning At")
    critical_target = fields.Float(string="Critical At")
    interval_target = fields.Float(string="Service Every")
    tolerance = fields.Float(default=0.0)
    last_value = fields.Float(readonly=True)
    last_reading_date = fields.Datetime(readonly=True)
    next_due_value = fields.Float(compute="_compute_due", store=True)
    active = fields.Boolean(default=True)

    @api.depends("type_id")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s - %s" % (rec.equipment_id.name or "?",
                                    rec.type_id.name or "?")

    @api.depends("last_value", "interval_target")
    def _compute_due(self):
        for rec in self:
            rec.next_due_value = ((rec.last_value or 0.0) + (rec.interval_target or 0.0)
                                  if rec.interval_target else 0.0)


class PmReading(models.Model):
    _name = "pm.reading"
    _description = "Counter Reading (append-only)"
    _order = "date desc"

    counter_id = fields.Many2one("pm.counter", required=True, ondelete="cascade")
    equipment_id = fields.Many2one("maintenance.equipment",
                                   related="counter_id.equipment_id", store=True)
    date = fields.Datetime(default=fields.Datetime.now, required=True)
    value = fields.Float(required=True)
    source = fields.Selection(
        [("manual", "Manual"), ("csv", "CSV Import"), ("api", "API")],
        default="manual",
    )
    user_id = fields.Many2one("res.users", default=lambda self: self.env.user)
    note = fields.Char()
    external_id = fields.Char(string="External ID", copy=False)

    _external_unique = models.Constraint(
        "UNIQUE(external_id)", "External reading ID must be unique.")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.value < 0:
                raise ValueError("Reading value cannot be negative.")
            rec.counter_id.write({"last_value": rec.value,
                                  "last_reading_date": rec.date})
            rec.counter_id.equipment_id._pm_refresh_health()
            self.env["pm.threshold"]._evaluate_counter(rec.counter_id, rec)
            rec.counter_id.equipment_id._pm_refresh_health()
        return records
