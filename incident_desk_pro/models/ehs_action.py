# -*- coding: utf-8 -*-
from odoo import fields, models, _


class EhsAction(models.Model):
    _name = "ehs.action"
    _description = "EHS Corrective Action"
    _order = "due_date, id"

    incident_id = fields.Many2one(
        "ehs.incident", string="Incident", required=True,
        ondelete="cascade", index=True)
    name = fields.Char(required=True)
    kind = fields.Selection(
        [("corrective", "Corrective"), ("preventive", "Preventive")],
        default="corrective", required=True,
        help="A corrective action fixes what failed, a preventive one "
             "stops it from happening again.")
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", required=True,
        default=lambda self: self.env.user)
    due_date = fields.Date(
        string="Due Date",
        help="Date the action must be finished by.")
    state = fields.Selection(
        [("todo", "To Do"), ("done", "Done")],
        default="todo", required=True, index=True)
    done_date = fields.Date(string="Done On", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    def action_done(self):
        for action in self:
            action.write({
                "state": "done",
                "done_date": fields.Date.context_today(action),
            })
        return True

    def action_reopen(self):
        for action in self:
            action.write({"state": "todo", "done_date": False})
        return True
