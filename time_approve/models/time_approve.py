# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


def _monday(value):
    return value - timedelta(days=value.weekday())


class TimesheetWeek(models.Model):
    _name = "timesheet.week"
    _description = "Weekly Timesheet"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, user_id"

    name = fields.Char(default="/", required=True, tracking=True)
    user_id = fields.Many2one(
        "res.users", string="Employee", required=True, tracking=True,
        default=lambda self: self.env.user)
    date_start = fields.Date(
        string="Week Start", required=True, tracking=True,
        default=lambda self: _monday(fields.Date.context_today(self)))
    date_end = fields.Date(
        string="Week End", compute="_compute_date_end", store=True)
    line_ids = fields.One2many(
        "account.analytic.line", "timesheet_week_id", string="Timesheets")
    total_hours = fields.Float(
        string="Total Hours", compute="_compute_totals", store=True)
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"),
         ("approved", "Approved"), ("rejected", "Rejected")],
        default="draft", required=True, tracking=True, index=True)
    submitted_on = fields.Datetime(readonly=True, tracking=True)
    approved_by = fields.Many2one("res.users", readonly=True, tracking=True)
    approved_on = fields.Datetime(readonly=True, tracking=True)
    comment = fields.Text(tracking=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)

    _sql_constraints = [
        ('week_user_uniq', "unique(user_id, date_start, company_id)", "A timesheet week already exists for this employee and this week."),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "timesheet.week") or "/"
            if vals.get("date_start"):
                vals["date_start"] = _monday(
                    fields.Date.to_date(vals["date_start"]))
        return super().create(vals_list)

    @api.depends("date_start")
    def _compute_date_end(self):
        for week in self:
            week.date_end = week.date_start + timedelta(days=6) \
                if week.date_start else False

    @api.depends("line_ids.unit_amount")
    def _compute_totals(self):
        for week in self:
            week.total_hours = sum(week.line_ids.mapped("unit_amount"))

    def action_generate(self):
        for week in self:
            lines = self.env["account.analytic.line"].search([
                ("user_id", "=", week.user_id.id),
                ("date", ">=", week.date_start),
                ("date", "<=", week.date_end),
                ("timesheet_week_id", "=", False),
                ("company_id", "=", week.company_id.id),
            ])
            if not lines:
                raise UserError(_(
                    "No timesheet line found for %(employee)s between "
                    "%(start)s and %(end)s.",
                    employee=week.user_id.display_name,
                    start=week.date_start, end=week.date_end))
            lines.write({"timesheet_week_id": week.id})
            week.message_post(body=_(
                "%s timesheet lines added to the week.", len(lines)))
        return True

    def action_submit(self):
        for week in self:
            if week.state not in ("draft", "rejected"):
                raise UserError(_("Only a draft or rejected week can be submitted."))
            if not week.line_ids:
                raise UserError(_("Generate the week before submitting it."))
            week.write({
                "state": "submitted",
                "submitted_on": fields.Datetime.now(),
            })
            week.message_post(body=_("Week submitted for approval."))
        return True

    def action_approve(self):
        for week in self:
            if week.state != "submitted":
                raise UserError(_("Only a submitted week can be approved."))
            week.write({
                "state": "approved",
                "approved_by": self.env.user.id,
                "approved_on": fields.Datetime.now(),
            })
            week.message_post(body=_(
                "%(hours).2f hours approved.", hours=week.total_hours))
        return True

    def action_reject(self):
        for week in self:
            if week.state != "submitted":
                raise UserError(_("Only a submitted week can be rejected."))
            if not week.comment:
                raise UserError(_(
                    "Add a comment explaining why the week is rejected."))
            week.write({"state": "rejected"})
            week.message_post(body=_("Week rejected: %s") % week.comment)
        return True

    def action_reopen(self):
        for week in self:
            if not self.env.user.has_group("base.group_system"):
                raise UserError(_(
                    "Only an administrator can reopen an approved week."))
            week.write({
                "state": "draft",
                "approved_by": False,
                "approved_on": False,
            })
        return True

    @api.model
    def _cron_remind(self):
        today = fields.Date.context_today(self)
        weeks = self.search([
            ("state", "in", ["draft", "submitted"]),
            ("date_end", "<", today),
        ])
        for week in weeks:
            week.activity_schedule(
                "mail.mail_activity_data_todo",
                summary=_("Timesheet week %s still not approved") % week.name,
                user_id=week.user_id.id,
            )
        return len(weeks)


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    timesheet_week_id = fields.Many2one(
        "timesheet.week", string="Timesheet Week", index=True, copy=False)
    week_state = fields.Selection(
        related="timesheet_week_id.state", string="Week Status")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            week_id = vals.get("timesheet_week_id")
            if week_id:
                self._check_week_lock(self.env["timesheet.week"].browse(week_id))
        return super().create(vals_list)

    def write(self, vals):
        if "timesheet_week_id" in vals and vals["timesheet_week_id"]:
            self._check_week_lock(
                self.env["timesheet.week"].browse(vals["timesheet_week_id"]))
        self._check_week_lock(self.mapped("timesheet_week_id"))
        return super().write(vals)

    def unlink(self):
        self._check_week_lock(self.mapped("timesheet_week_id"))
        return super().unlink()

    @api.model
    def _check_week_lock(self, weeks):
        if any(week.state == "approved" for week in weeks):
            raise UserError(_(
                "This timesheet belongs to an approved week and cannot be "
                "modified. Ask an administrator to reopen the week."))
