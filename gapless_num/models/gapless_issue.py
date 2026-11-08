# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class GaplessIssue(models.Model):
    _name = "gapless.issue"
    _description = "Numbering Anomaly"
    _inherit = ["mail.thread"]
    _order = "issue_date desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    rule_id = fields.Many2one("gapless.rule", string="Rule")
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    journal_id = fields.Many2one("account.journal", string="Journal")
    kind = fields.Selection(
        [("gap", "Missing number"),
         ("duplicate", "Duplicate number"),
         ("out_of_order", "Out of order"),
         ("manual", "Manually changed")],
        required=True, default="gap", tracking=True)
    move_id = fields.Many2one("account.move", string="Entry")
    move_name = fields.Char(string="Entry Number")
    expected = fields.Char(help="The number the sequence expected.")
    found = fields.Char(help="The number actually found.")
    issue_date = fields.Date(default=fields.Date.context_today, required=True)
    state = fields.Selection(
        [("open", "Open"), ("resolved", "Resolved"), ("ignored", "Ignored")],
        default="open", required=True, tracking=True, index=True)
    note = fields.Text()

    @api.depends("journal_id", "kind", "move_name")
    def _compute_name(self):
        for issue in self:
            parts = [
                issue.journal_id.code or issue.journal_id.name or "",
                dict(issue._fields["kind"].selection).get(issue.kind, ""),
                issue.move_name or issue.expected or "",
            ]
            issue.name = " / ".join(part for part in parts if part) \
                or _("Numbering anomaly")

    def action_resolve(self):
        for issue in self:
            issue.state = "resolved"
        return True

    def action_ignore(self):
        for issue in self:
            issue.state = "ignored"
        return True

    def action_reopen(self):
        for issue in self:
            issue.state = "open"
        return True
