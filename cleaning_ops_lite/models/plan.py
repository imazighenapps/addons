# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CleaningPlan(models.Model):
    _name = "cleaning.plan"
    _description = "Recurring Visit Plan"
    _inherit = ["mail.thread"]
    _order = "site_id"

    name = fields.Char(required=True)
    site_id = fields.Many2one("cleaning.site", required=True,
                              ondelete="cascade")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    frequency = fields.Selection(
        [("daily", "Daily"), ("weekly", "Weekly"), ("biweekly", "Every 2 Weeks"),
         ("monthly", "Monthly"), ("quarterly", "Quarterly")],
        default="weekly", required=True)
    weekday = fields.Selection(
        [("0", "Monday"), ("1", "Tuesday"), ("2", "Wednesday"),
         ("3", "Thursday"), ("4", "Friday"), ("5", "Saturday"),
         ("6", "Sunday")], default="0")
    start_hour = fields.Float(string="Start Hour", default=9.0)
    duration_hours = fields.Float(string="Duration (h)", default=2.0)
    agent_id = fields.Many2one("cleaning.agent", string="Default Agent")
    active = fields.Boolean(default=True)
    next_date = fields.Date(compute="_compute_next_date", store=True)
    visits_done = fields.Integer(compute="_compute_visits_done")

    @api.depends("frequency", "weekday", "start_hour")
    def _compute_next_date(self):
        from datetime import date, timedelta
        today = date.today()
        for plan in self:
            if plan.frequency == "daily":
                plan.next_date = today + timedelta(days=1)
                continue
            if plan.frequency == "weekly":
                target = int(plan.weekday or 0)
            elif plan.frequency == "biweekly":
                target = int(plan.weekday or 0)
            else:
                target = None
            if target is None:
                if plan.frequency == "monthly":
                    plan.next_date = (today.replace(day=1) +
                                      timedelta(days=31)).replace(day=1)
                else:
                    plan.next_date = today + timedelta(days=90)
                continue
            delta = (target - today.weekday()) % 7
            nxt = today + timedelta(days=delta or 7)
            if plan.frequency == "biweekly" and delta == 0:
                nxt = today + timedelta(days=7)
            plan.next_date = nxt

    def _compute_visits_done(self):
        visits = self.env["cleaning.visit"].search([("plan_id", "in", self.ids)])
        for plan in self:
            plan.visits_done = len(visits.filtered(lambda v: v.plan_id == plan))

    def action_create_visit(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "New Visit",
            "res_model": "cleaning.visit",
            "view_mode": "form",
            "target": "new",
            "context": {"default_site_id": self.site_id.id,
                        "default_plan_id": self.id,
                        "default_agent_id": self.agent_id.id},
        }