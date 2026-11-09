# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

STARTER_LINES = {
    "onboarding": [
        ("Create the email and Odoo account", "it"),
        ("Prepare the desk and equipment", "admin"),
        ("Schedule the safety briefing", "manager"),
        ("Schedule the welcome meeting", "manager"),
    ],
    "offboarding": [
        ("Collect the equipment and the badge", "admin"),
        ("Plan the knowledge transfer", "manager"),
        ("Close the access rights", "it"),
        ("Final settlement with accounts", "admin"),
    ],
}


class HireCheck(models.Model):
    _name = "hire.check"
    _description = "Hire and Exit Checklist"
    _inherit = ["mail.thread"]
    _order = "start_date desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Check %s")
        % fields.Datetime.now().strftime("%Y-%m-%d %H:%M"),
        help="Reference of the checklist, generated at creation.")
    kind = fields.Selection(
        [("onboarding", "Onboarding"), ("offboarding", "Offboarding")],
        default="onboarding", required=True, tracking=True,
        help="Onboarding welcomes a new colleague, offboarding prepares "
             "an exit.")
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, tracking=True,
        help="The employee arriving or leaving.")
    start_date = fields.Date(
        default=fields.Date.context_today, tracking=True,
        help="When the checklist starts, usually the first or last day.")
    line_ids = fields.One2many(
        "hire.check.line", "check_id", string="Tasks")
    line_count = fields.Integer(string="Tasks", compute="_compute_lines")
    todo_count = fields.Integer(
        string="Open Tasks", compute="_compute_lines")
    state = fields.Selection(
        [("draft", "Draft"), ("in_progress", "In Progress"),
         ("done", "Done"), ("cancelled", "Cancelled")],
        default="draft", required=True, copy=False, tracking=True,
        index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)
    note = fields.Text()

    @api.depends("line_ids.state")
    def _compute_lines(self):
        for check in self:
            check.line_count = len(check.line_ids)
            check.todo_count = len(check.line_ids.filtered(
                lambda line: line.state == "todo"))

    @api.model_create_multi
    def create(self, vals_list):
        checks = super().create(vals_list)
        for check in checks:
            if check.line_ids:
                continue
            check.write({"line_ids": [
                fields.Command.create({"name": name, "category": category})
                for name, category in STARTER_LINES.get(check.kind, [])]})
        return checks

    def action_start(self):
        for check in self:
            if check.state != "draft":
                raise UserError(_(
                    "Only a draft checklist can be started."))
            check.state = "in_progress"
            check.message_post(body=_("The checklist has started."))
        return True

    def action_done(self):
        for check in self:
            if check.state == "done":
                raise UserError(_(
                    "Checklist \"%s\" is already done.", check.name))
            if not check.line_ids:
                raise UserError(_(
                    "Add at least one task before closing \"%s\".",
                    check.name))
            if check.todo_count:
                raise UserError(_(
                    "Checklist \"%s\" still has %s open task(s).",
                    check.name, check.todo_count))
            check.state = "done"
            check.message_post(body=_("Every task is done, file closed."))
        return True

    def action_reopen(self):
        for check in self:
            if check.state != "done":
                raise UserError(_(
                    "Only a done checklist can be reopened."))
            check.state = "in_progress"
            check.message_post(body=_("The checklist has been reopened."))
        return True

    def action_cancel(self):
        for check in self:
            check.state = "cancelled"
            check.message_post(body=_("The checklist has been cancelled."))
        return True
