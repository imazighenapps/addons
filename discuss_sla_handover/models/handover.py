# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HandoverLog(models.Model):
    _name = "discuss.handover.log"
    _description = "Shift Handover Log"
    _inherit = ["mail.thread"]
    _order = "date desc"

    name = fields.Char(default="/", copy=False, readonly=True)
    date = fields.Datetime(default=fields.Datetime.now, required=True)
    channel_ids = fields.Many2many("discuss.channel", string="Channels")
    from_user_id = fields.Many2one("res.users", string="Handed Over By",
                                   default=lambda self: self.env.user)
    to_user_id = fields.Many2one("res.users", string="Handed Over To",
                                 required=True)
    open_cases = fields.Integer(string="Open Cases")
    breached_cases = fields.Integer(string="Breached Cases")
    summary = fields.Text(string="Situation Summary", required=True)
    pending_actions = fields.Text(string="Pending Actions")
    risks = fields.Text(string="Risks & Blockers")
    state = fields.Selection(
        [("draft", "Draft"), ("given", "Given"), ("received", "Received")],
        default="draft", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "discuss.handover") or "/"
        return super().create(vals_list)

    def action_snapshot_cases(self):
        for rec in self:
            domain = [("state", "!=", "resolved")]
            if rec.channel_ids:
                domain.append(("channel_id", "in", rec.channel_ids.ids))
            cases = self.env["discuss.sla.case"].search(domain)
            rec.open_cases = len(cases)
            rec.breached_cases = len(cases.filtered(lambda c: c.breach))
        return True

    def action_give(self):
        self.write({"state": "given"})

    def action_receive(self):
        self.write({"state": "received"})