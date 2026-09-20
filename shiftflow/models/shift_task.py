from odoo import api, fields, models, _

class ShiftFlowTask(models.Model):
    _name = "shiftflow.task"
    _description = "Shift Follow-up Task"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "deadline asc"

    name = fields.Char(required=True, translate=True)
    reference = fields.Char(readonly=True, copy=False, default=lambda self: _("New"))
    shift_id = fields.Many2one("shiftflow.shift", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="shift_id.company_id", store=True, index=True)
    responsible_id = fields.Many2one("res.users", default=lambda self: self.env.user)
    deadline = fields.Datetime(required=True)
    priority = fields.Selection([("low", "Low"), ("normal", "Normal"), ("high", "High"), ("urgent", "Urgent")], default="normal", required=True)
    state = fields.Selection([("open", "Open"), ("in_progress", "In Progress"), ("done", "Done"), ("cancelled", "Cancelled")], default="open", tracking=True)
    description = fields.Text(translate=True)
    carry_over = fields.Boolean(default=True)
    carried_from_id = fields.Many2one("shiftflow.task", readonly=True, copy=False)
    carried_to_id = fields.Many2one("shiftflow.task", readonly=True, copy=False)
    reminder_sent = fields.Boolean(copy=False, readonly=True)
    is_overdue = fields.Boolean(compute="_compute_is_overdue")

    @api.depends("deadline", "state")
    def _compute_is_overdue(self):
        now = fields.Datetime.now()
        for rec in self:
            rec.is_overdue = bool(rec.deadline and rec.deadline < now and rec.state not in ("done", "cancelled"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("reference", "New") == "New":
                vals["reference"] = self.env["ir.sequence"].next_by_code("shiftflow.task") or "New"
        return super().create(vals_list)
    def write(self, vals):
        if {"deadline", "responsible_id"} & set(vals):
            vals = dict(vals, reminder_sent=False)
        return super().write(vals)

    def action_start(self): self.write({"state": "in_progress"})
    def action_done(self): self.write({"state": "done"})
    def action_cancel(self): self.write({"state": "cancelled"})
    def action_reopen(self): self.write({"state": "open"})

    @api.model
    def _cron_overdue_task_reminders(self):
        tasks = self.search([("deadline", "<", fields.Datetime.now()), ("state", "not in", ["done", "cancelled"]), ("reminder_sent", "=", False), ("responsible_id", "!=", False)])
        template = self.env.ref("shiftflow.mail_template_overdue_task", raise_if_not_found=False)
        for task in tasks:
            if template and task.responsible_id.email:
                template.send_mail(task.id, force_send=False)
            if task.responsible_id:
                task.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=task.responsible_id.id,
                    summary=_("Overdue ShiftFlow task"),
                    note=_("Update overdue task %(reference)s: %(name)s") % {"reference": task.reference, "name": task.name},
                )
            task.reminder_sent = True
        return True
