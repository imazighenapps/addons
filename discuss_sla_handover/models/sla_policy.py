# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SlaPolicy(models.Model):
    _name = "discuss.sla.policy"
    _description = "Discuss SLA Policy"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    channel_ids = fields.Many2many("discuss.channel", string="Channels")
    priority = fields.Selection(
        [("low", "Low"), ("normal", "Normal"), ("high", "High")],
        default="normal", required=True)
    first_response_hours = fields.Float(string="First Response (h)", default=4.0)
    resolution_hours = fields.Float(string="Resolution (h)", default=24.0)
    warn_ratio = fields.Float(
        string="Warn At (%)", default=0.8,
        help="Share of the deadline after which the case turns amber.")
    active = fields.Boolean(default=True)

    def _match(self, channel):
        self.ensure_one()
        if not self.active:
            return False
        if self.channel_ids and channel not in self.channel_ids:
            return False
        if self.channel_ids:
            return True
        # no channel set: apply only to internal channels
        return channel.channel_type == "channel"


class SlaCase(models.Model):
    _name = "discuss.sla.case"
    _description = "SLA-tracked Channel"
    _inherit = ["mail.thread"]
    _order = "resolution_deadline asc"

    name = fields.Char(default="/", copy=False, readonly=True)
    channel_id = fields.Many2one("discuss.channel", required=True,
                                  ondelete="cascade")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    policy_id = fields.Many2one("discuss.sla.policy", string="Policy",
                                 ondelete="set null")
    priority = fields.Selection(
        [("low", "Low"), ("normal", "Normal"), ("high", "High")],
        default="normal", tracking=True)
    open_date = fields.Datetime(default=fields.Datetime.now, required=True)
    first_response_date = fields.Datetime(readonly=True)
    close_date = fields.Datetime(readonly=True)
    response_deadline = fields.Datetime(compute="_compute_deadlines", store=True)
    resolution_deadline = fields.Datetime(compute="_compute_deadlines", store=True)
    state = fields.Selection(
        [("open", "Open"), ("responded", "Responded"), ("resolved", "Resolved")],
        default="open", tracking=True)
    breach = fields.Boolean(compute="_compute_deadlines", store=True)
    level = fields.Selection(
        [("ok", "On Track"), ("warn", "At Risk"), ("breach", "Breached")],
        compute="_compute_deadlines", store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("discuss.sla") or "/"
        return super().create(vals_list)

    @api.depends("open_date", "policy_id.first_response_hours",
                 "policy_id.resolution_hours", "first_response_date", "close_date",
                 "policy_id.warn_ratio")
    def _compute_deadlines(self):
        from datetime import timedelta
        now = fields.Datetime.now()
        for case in self:
            resp_h = case.policy_id.first_response_hours or 0.0
            res_h = case.policy_id.resolution_hours or 0.0
            case.response_deadline = (
                case.open_date + timedelta(hours=resp_h)) if resp_h else False
            case.resolution_deadline = (
                case.open_date + timedelta(hours=res_h)) if res_h else False
            breach = False
            if case.close_date:
                breach = bool(
                    (case.response_deadline and case.close_date > case.response_deadline)
                    or (case.resolution_deadline and case.close_date > case.resolution_deadline))
            else:
                breach = bool(case.resolution_deadline and now > case.resolution_deadline)
            case.breach = breach
            target = case.resolution_deadline or case.response_deadline
            if breach:
                case.level = "breach"
            elif target:
                span = (target - case.open_date).total_seconds() or 1.0
                ratio = (now - case.open_date).total_seconds() / span
                case.level = "warn" if ratio >= (case.policy_id.warn_ratio or 0.8) else "ok"
            else:
                case.level = "ok"

    def action_set_response(self):
        self.write({"first_response_date": fields.Datetime.now(),
                    "state": "responded"})

    def action_resolve(self):
        self.write({"close_date": fields.Datetime.now(), "state": "resolved"})

    def action_reopen(self):
        self.write({"close_date": False, "state": "open"})

    @api.model
    def _cron_check(self):
        cases = self.search([("state", "in", ("open", "responded"))])
        cases.invalidate_recordset(["response_deadline", "resolution_deadline"])
        for case in cases:
            if case.level == "breach":
                case.message_post(body="SLA breached.")
        return True