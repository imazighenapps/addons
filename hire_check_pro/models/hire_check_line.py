# -*- coding: utf-8 -*-
from odoo import _, fields, models
from odoo.exceptions import UserError


class HireCheckLine(models.Model):
    _name = "hire.check.line"
    _description = "Hire and Exit Task"
    _order = "sequence, id"

    check_id = fields.Many2one(
        "hire.check", string="Checklist", required=True,
        ondelete="cascade", index=True)
    name = fields.Char(required=True)
    kind = fields.Selection(
        related="check_id.kind", store=True, readonly=True)
    category = fields.Selection(
        [("it", "IT"), ("admin", "Admin"), ("manager", "Manager"),
         ("other", "Other")],
        default="other", required=True,
        help="Which team owns the task: IT, admin, the manager or "
             "nobody in particular.")
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", required=True,
        default=lambda self: self.env.user)
    due_date = fields.Date(
        help="Date the task must be finished by.")
    state = fields.Selection(
        [("todo", "To Do"), ("done", "Done")],
        default="todo", required=True, index=True)
    done_date = fields.Date(string="Done On", readonly=True, copy=False)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        related="check_id.company_id", store=True, readonly=True)
    note = fields.Text()

    def action_done(self):
        for line in self:
            if line.check_id.state == "cancelled":
                raise UserError(_(
                    "The checklist is cancelled: its tasks cannot be "
                    "marked done."))
            line.write({
                "state": "done",
                "done_date": fields.Date.context_today(line),
            })
        return True

    def action_reopen(self):
        for line in self:
            line.write({"state": "todo", "done_date": False})
        return True
