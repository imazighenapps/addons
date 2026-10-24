# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CloseTemplate(models.Model):
    _name = "close.template"
    _description = "Month-End Close Template"
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    line_ids = fields.One2many(
        "close.template.line", "template_id", string="Tasks")
    line_count = fields.Integer(compute="_compute_line_count")
    active = fields.Boolean(default=True)
    note = fields.Text()

    @api.depends("line_ids")
    def _compute_line_count(self):
        for template in self:
            template.line_count = len(template.line_ids)

    def action_view_lines(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Template Tasks"),
            "res_model": "close.template.line",
            "view_mode": "list,form",
            "domain": [("template_id", "=", self.id)],
            "context": {"default_template_id": self.id},
        }


class CloseTemplateLine(models.Model):
    _name = "close.template.line"
    _description = "Close Template Task"
    _order = "template_id, sequence, id"

    template_id = fields.Many2one(
        "close.template", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    name = fields.Char(string="Task", required=True)
    user_id = fields.Many2one(
        "res.users", string="Default Owner",
        default=lambda self: self.env.user)
    due_day = fields.Integer(
        string="Due Day", default=5,
        help="Day of the month following the period end.")
    evidence_required = fields.Boolean(string="Evidence Required")
    instruction = fields.Text()
    dependency_ids = fields.Many2many(
        "close.template.line", "close_template_line_dependency_rel",
        "line_id", "dependency_id", string="Depends On")

    @api.constrains("dependency_ids")
    def _check_dependencies(self):
        for line in self:
            if line in line.dependency_ids:
                raise ValidationError(_(
                    "A task cannot depend on itself."))


class ClosePeriod(models.Model):
    _name = "close.period"
    _description = "Month-End Close Period"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_end desc, id desc"

    name = fields.Char(default="/", required=True, tracking=True)
    template_id = fields.Many2one(
        "close.template", string="Template", tracking=True)
    date_start = fields.Date(
        required=True, tracking=True,
        default=lambda self: fields.Date.context_today(self).replace(day=1))
    date_end = fields.Date(
        required=True, tracking=True,
        default=lambda self: fields.Date.context_today(self)
        + relativedelta(day=31))
    state = fields.Selection(
        [("draft", "Draft"), ("in_progress", "In Progress"),
         ("done", "Done"), ("locked", "Locked")],
        default="draft", required=True, tracking=True, index=True)
    task_ids = fields.One2many(
        "close.task", "period_id", string="Tasks")
    task_count = fields.Integer(compute="_compute_progress")
    done_count = fields.Integer(compute="_compute_progress")
    progress = fields.Float(
        string="Progress (%)", compute="_compute_progress")
    locked_on = fields.Datetime(readonly=True, tracking=True)
    locked_by = fields.Many2one("res.users", readonly=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "close.period") or "/"
        return super().create(vals_list)

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for period in self:
            if period.date_end < period.date_start:
                raise ValidationError(_(
                    "The end date must be after the start date."))

    @api.depends("task_ids", "task_ids.state")
    def _compute_progress(self):
        for period in self:
            total = len(period.task_ids)
            done = len(period.task_ids.filtered(
                lambda task: task.state == "done"))
            period.task_count = total
            period.done_count = done
            period.progress = (done / total * 100.0) if total else 0.0

    def _due_date(self, due_day):
        self.ensure_one()
        day = min(max(due_day or 1, 1), 28)
        return self.date_end + relativedelta(months=1, day=day)

    def action_generate(self):
        for period in self:
            if period.state == "locked":
                raise UserError(_("This period is locked."))
            if not period.template_id:
                raise UserError(_("Select a template first."))
            existing = {task.name: task for task in period.task_ids}
            mapping = {}
            lines = period.template_id.line_ids.sorted(
                lambda line: (line.sequence, line.id))
            for line in lines:
                task = existing.get(line.name)
                if not task:
                    task = self.env["close.task"].create({
                        "period_id": period.id,
                        "sequence": line.sequence,
                        "name": line.name,
                        "user_id": line.user_id.id or self.env.user.id,
                        "due_date": period._due_date(line.due_day),
                        "evidence_required": line.evidence_required,
                        "instruction": line.instruction,
                    })
                mapping[line.id] = task
            for line in lines:
                task = mapping.get(line.id)
                if not task:
                    continue
                dependency_tasks = [
                    mapping[dependency.id]
                    for dependency in line.dependency_ids
                    if dependency.id in mapping
                ]
                if dependency_tasks:
                    task.dependency_ids = [(6, 0, [d.id for d in dependency_tasks])]
            if period.state == "draft":
                period.state = "in_progress"
            period.message_post(body=_(
                "%s tasks generated from template %s.",
                len(period.task_ids), period.template_id.name))
        return True

    def action_start(self):
        for period in self:
            if period.state != "draft":
                raise UserError(_("Only a draft period can be started."))
            period.state = "in_progress"
        return True

    def action_done(self):
        for period in self:
            if period.state not in ("draft", "in_progress"):
                raise UserError(_(
                    "Only an open period can be marked as done."))
            if not period.task_ids:
                raise UserError(_("Generate the tasks before closing."))
            pending = period.task_ids.filtered(
                lambda task: task.state != "done")
            if pending:
                raise UserError(_(
                    "%s task(s) are still open. Complete them first.",
                    len(pending)))
            period.state = "done"
            period.message_post(body=_("Month-end close completed."))
        return True

    def action_lock(self):
        for period in self:
            if period.state != "done":
                raise UserError(_("Mark the period as done before locking it."))
            period.with_context(close_force=True).write({
                "state": "locked",
                "locked_on": fields.Datetime.now(),
                "locked_by": self.env.user.id,
            })
            period.message_post(body=_(
                "Period locked by %s.", self.env.user.name))
        return True

    def action_unlock(self):
        if not self.env.user.has_group("close_flow.group_closeflow_manager"):
            raise UserError(_(
                "Only a close manager can unlock a period."))
        for period in self:
            if period.state != "locked":
                raise UserError(_("This period is not locked."))
            period.with_context(close_force=True).write({
                "state": "in_progress",
                "locked_on": False,
                "locked_by": False,
            })
            period.message_post(body=_(
                "Period unlocked by %s.", self.env.user.name))
        return True

    def write(self, vals):
        if any(period.state == "locked" for period in self) \
                and not self.env.context.get("close_force"):
            raise UserError(_(
                "This period is locked. Ask a manager to unlock it."))
        return super().write(vals)


class CloseTask(models.Model):
    _name = "close.task"
    _description = "Month-End Close Task"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period_id desc, sequence, id"

    period_id = fields.Many2one(
        "close.period", required=True, ondelete="cascade", index=True,
        string="Period")
    sequence = fields.Integer(default=10)
    name = fields.Char(string="Task", required=True, tracking=True)
    user_id = fields.Many2one(
        "res.users", string="Owner", required=True, tracking=True,
        default=lambda self: self.env.user)
    due_date = fields.Date(tracking=True)
    state = fields.Selection(
        [("todo", "To Do"), ("in_progress", "In Progress"),
         ("done", "Done"), ("blocked", "Blocked")],
        default="todo", required=True, tracking=True, index=True)
    blocked_reason = fields.Text(tracking=True)
    evidence_required = fields.Boolean(string="Evidence Required")
    attachment_ids = fields.Many2many(
        "ir.attachment", "close_task_attachment_rel", "task_id",
        "attachment_id", string="Evidence")
    completed_on = fields.Datetime(readonly=True, tracking=True)
    completed_by = fields.Many2one(
        "res.users", readonly=True, tracking=True)
    instruction = fields.Text()
    dependency_ids = fields.Many2many(
        "close.task", "close_task_dependency_rel", "task_id",
        "dependency_id", string="Depends On")
    dependency_count = fields.Integer(compute="_compute_dependency_count")
    company_id = fields.Many2one(
        related="period_id.company_id", store=True, readonly=True)

    @api.depends("dependency_ids")
    def _compute_dependency_count(self):
        for task in self:
            task.dependency_count = len(task.dependency_ids)

    @api.constrains("dependency_ids", "period_id")
    def _check_dependencies(self):
        for task in self:
            if task in task.dependency_ids:
                raise ValidationError(_(
                    "A task cannot depend on itself."))
            wrong = task.dependency_ids.filtered(
                lambda dependency: dependency.period_id != task.period_id)
            if wrong:
                raise ValidationError(_(
                    "A task can only depend on a task of the same period."))

    def action_start(self):
        for task in self:
            if task.state not in ("todo", "blocked"):
                raise UserError(_("This task cannot be started."))
            task.write({
                "state": "in_progress",
                "blocked_reason": False,
            })
        return True

    def action_done(self):
        for task in self:
            if task.state == "done":
                raise UserError(_("This task is already done."))
            if task.evidence_required and not task.attachment_ids:
                raise UserError(_(
                    "Attach the evidence before completing \"%s\".",
                    task.name))
            pending = task.dependency_ids.filtered(
                lambda dependency: dependency.state != "done")
            if pending:
                raise UserError(_(
                    "\"%s\" cannot be completed before: %s",
                    task.name, ", ".join(pending.mapped("name"))))
            task.write({
                "state": "done",
                "completed_on": fields.Datetime.now(),
                "completed_by": self.env.user.id,
            })
            task.message_post(body=_("Task completed."))
        return True

    def action_block(self):
        for task in self:
            if not task.blocked_reason:
                raise UserError(_(
                    "Explain why the task is blocked."))
            task.write({"state": "blocked"})
        return True

    def action_reopen(self):
        for task in self:
            if task.period_id.state == "locked":
                raise UserError(_(
                    "The period is locked. Ask a manager to unlock it."))
            task.write({
                "state": "todo",
                "completed_on": False,
                "completed_by": False,
            })
        return True

    def write(self, vals):
        if any(task.period_id.state == "locked" for task in self) \
                and not self.env.context.get("close_force"):
            raise UserError(_(
                "This period is locked. Ask a manager to unlock it."))
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            period = self.env["close.period"].browse(vals.get("period_id"))
            if period.state == "locked" \
                    and not self.env.context.get("close_force"):
                raise UserError(_(
                    "This period is locked. Ask a manager to unlock it."))
        return super().create(vals_list)

    def unlink(self):
        if any(task.period_id.state == "locked" for task in self) \
                and not self.env.context.get("close_force"):
            raise UserError(_(
                "This period is locked. Ask a manager to unlock it."))
        return super().unlink()
