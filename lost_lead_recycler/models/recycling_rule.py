# -*- coding: utf-8 -*-
from datetime import date, timedelta
from odoo import api, fields, models, _


class RecyclingRule(models.Model):
    _name = "lead.recycling.rule"
    _description = "Lost Lead Recycling Rule"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company)
    inactivity_days = fields.Integer(string="Dormant After (days)", default=90)
    include_lost = fields.Boolean(string="Include Lost Leads", default=True)
    target_stage_id = fields.Many2one("crm.stage", string="Nurturing Stage",
                                      required=True)
    assignee_id = fields.Many2one("res.users", string="Reassign To")
    max_recycles = fields.Integer(string="Max Recycles per Lead", default=2)
    active = fields.Boolean(default=True)
    last_run = fields.Datetime(readonly=True)
    recycled_total = fields.Integer(readonly=True)

    def action_run_now(self):
        """Run only this rule, not every configured rule."""
        self.ensure_one()
        self._run_rules(self)
        return True

    @api.model
    def _run_rules(self, rules=None):
        """Recycle dormant leads.

        A lead is recycled at most once per run: without this guard every
        active rule matches the same lead, recycled_count is incremented
        once per rule (exhausting max_recycles far too early) and the
        stage/assignee of whichever rule happened to run last wins.
        """
        if rules is None:
            rules = self.search([("active", "=", True)])
        handled = set()
        for rule in rules:
            if not rule.active:
                continue
            cutoff = date.today() - timedelta(days=rule.inactivity_days)
            domain = [
                ("type", "=", "opportunity"),
                ("recycled_count", "<", rule.max_recycles),
                "|",
                ("active", "=", False),
                ("write_date", "<", cutoff.strftime("%Y-%m-%d")),
            ]
            if not rule.include_lost:
                domain = [
                    ("type", "=", "opportunity"),
                    ("active", "=", True),
                    ("write_date", "<", cutoff.strftime("%Y-%m-%d")),
                    ("recycled_count", "<", rule.max_recycles),
                ]
            leads = self.env["crm.lead"].search(domain)
            count = 0
            for lead in leads:
                if lead.id in handled:
                    continue
                handled.add(lead.id)
                vals = {
                    "active": True,
                    "stage_id": rule.target_stage_id.id,
                    "recycled_count": lead.recycled_count + 1,
                    "last_recycled_date": fields.Date.today(),
                }
                if rule.assignee_id:
                    vals["user_id"] = rule.assignee_id.id
                lead.write(vals)
                lead.message_post(body=_(
                    "Recycled by rule '%s' (cycle %d).") % (rule.name, vals["recycled_count"]))
                count += 1
            rule.write({"last_run": fields.Datetime.now(),
                        "recycled_total": rule.recycled_total + count})
        return True

    @api.model
    def _cron_recycle(self):
        return self._run_rules()


class CrmLead(models.Model):
    _inherit = "crm.lead"

    recycled_count = fields.Integer(string="Recycling Cycles", default=0,
                                    copy=False)
    last_recycled_date = fields.Date(copy=False)
