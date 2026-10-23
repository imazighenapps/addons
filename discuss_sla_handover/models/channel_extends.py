# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models


class DiscussChannel(models.Model):
    _inherit = "discuss.channel"

    sla_case_ids = fields.One2many("discuss.sla.case", "channel_id",
                                   string="SLA Cases")
    sla_case_id = fields.Many2one(
        "discuss.sla.case", compute="_compute_open_sla_case")
    open_sla_case_count = fields.Integer(compute="_compute_open_sla_case")
    handover_ids = fields.Many2many(
        "discuss.handover.log", string="Handover Logs")
    archive_after_days = fields.Integer(
        string="Auto-archive After (days)",
        help="Archive this channel when inactive for N days. 0 disables.")
    last_activity_date = fields.Datetime(
        compute="_compute_last_activity",
        help="Read-only, computed on demand to avoid a costly stored dependency.")

    def _compute_open_sla_case(self):
        cases = self.env["discuss.sla.case"].search(
            [("channel_id", "in", self.ids), ("state", "!=", "resolved")])
        for channel in self:
            mine = cases.filtered(lambda c: c.channel_id == channel)
            channel.open_sla_case_count = len(mine)
            channel.sla_case_id = mine[:1]

    def _compute_last_activity(self):
        """Read the latest message date via SQL, never loading the messages."""
        self.env.cr.execute(
            """
            SELECT c.id, MAX(m.write_date)
            FROM discuss_channel c
            LEFT JOIN mail_message m ON m.res_id = c.id AND m.model = 'discuss.channel'
            WHERE c.id IN %s
            GROUP BY c.id
            """,
            [tuple(self.ids)],
        )
        latest = {cid: dt for cid, dt in self.env.cr.fetchall()}
        for channel in self:
            channel.last_activity_date = latest.get(channel.id) or \
                channel.create_date

    def action_open_sla_case(self):
        self.ensure_one()
        for policy in self.env["discuss.sla.policy"].search(
                [("active", "=", True)]):
            if not policy._match(self):
                continue
            case = self.env["discuss.sla.case"].create({
                "channel_id": self.id,
                "policy_id": policy.id,
                "priority": policy.priority,
            })
            return {
                "type": "ir.actions.act_window",
                "res_model": "discuss.sla.case",
                "res_id": case.id,
                "view_mode": "form",
                "target": "new",
            }
        return False

    @api.model
    def _cron_archive_idle(self):
        now = fields.Datetime.now()
        archived = 0
        for channel in self.search([("archive_after_days", ">", 0),
                                    ("channel_type", "=", "channel")]):
            limit = now - timedelta(days=channel.archive_after_days)
            if channel.last_activity_date and channel.last_activity_date < limit:
                channel.sudo()._sla_archive_channel()
                archived += 1
        return archived

    def _sla_archive_channel(self):
        """Close the channel so it stops appearing in the inbox."""
        return self.write({"active": False})