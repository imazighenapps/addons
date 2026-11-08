# -*- coding: utf-8 -*-
from odoo import fields, models, _

NEGLIGIBLE = 0.0001


class BillableScan(models.TransientModel):
    _name = "billable.gap.scan"
    _description = "Scan Unbilled Time"

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    project_ids = fields.Many2many("project.project", string="Projects")
    employee_ids = fields.Many2many("hr.employee", string="Employees")
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    min_hours = fields.Float(
        string="Minimum Hours", default=0.5,
        help="Ignore a group of hours below this threshold.")

    def action_run(self):
        self.ensure_one()
        domain = [
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
            ("company_id", "=", self.company_id.id),
            ("project_id", "!=", False),
        ]
        if self.project_ids:
            domain.append(("project_id", "in", self.project_ids.ids))
        if self.employee_ids:
            domain.append(("employee_id", "in", self.employee_ids.ids))
        lines = self.env["account.analytic.line"].search(domain)
        groups = {}
        for line in lines:
            if not line._is_not_billed():
                continue
            so_line = getattr(line, "so_line", False)
            key = (
                line.project_id.id,
                line.task_id.id or False,
                line.employee_id.id or False,
                so_line.id if so_line else False,
            )
            groups[key] = groups.get(key, 0.0) + (line.unit_amount or 0.0)
        Gap = self.env["billable.gap"]
        created = Gap
        for key, hours in groups.items():
            if hours <= self.min_hours + NEGLIGIBLE:
                continue
            project_id, task_id, employee_id, so_line_id = key
            so_line = self.env["sale.order.line"].browse(so_line_id) \
                if so_line_id else self.env["sale.order.line"]
            existing = Gap.search([
                ("project_id", "=", project_id),
                ("task_id", "=", task_id or False),
                ("employee_id", "=", employee_id or False),
                ("date_from", "=", self.date_from),
                ("date_to", "=", self.date_to),
            ], limit=1)
            values = {
                "project_id": project_id,
                "task_id": task_id or False,
                "employee_id": employee_id or False,
                "sale_line_id": so_line.id if so_line else False,
                "hours_logged": hours,
                "hours_invoiced": so_line.qty_delivered if so_line else 0.0,
                "date_from": self.date_from,
                "date_to": self.date_to,
                "company_id": self.company_id.id,
            }
            if existing:
                existing.write(values)
                created |= existing
            else:
                created |= Gap.create(values)
        action = {
            "type": "ir.actions.act_window",
            "name": _("Unbilled Time"),
            "res_model": "billable.gap",
            "view_mode": "list,form",
        }
        if created:
            action["domain"] = [("id", "in", created.ids)]
        else:
            action["domain"] = [
                ("company_id", "=", self.company_id.id),
                ("state", "=", "open"),
            ]
        return action
