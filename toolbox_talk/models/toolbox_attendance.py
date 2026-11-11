# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ToolboxAttendance(models.Model):
    _name = "toolbox.attendance"
    _description = "Toolbox Attendance"
    _inherit = ["mail.thread"]
    _order = "id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Attendance %s")
        % fields.Date.context_today(self),
        help="Reference of the attendance line, generated at creation.")
    talk_id = fields.Many2one(
        "toolbox.talk", string="Toolbox Talk", required=True,
        ondelete="cascade", index=True, tracking=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, tracking=True)
    signed = fields.Boolean(
        default=False, tracking=True,
        help="Ticked when the employee signed off the briefing.")
    signed_on = fields.Date(
        string="Signed On", readonly=True, copy=False,
        help="Date the employee confirmed attendance.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.constrains("talk_id")
    def _check_talk_open(self):
        for line in self:
            if line.talk_id and line.talk_id.state == "done":
                raise ValidationError(_(
                    "Attendance cannot be added to the completed talk %s.",
                    line.talk_id.name))

    @api.constrains("talk_id", "employee_id")
    def _check_unique_employee(self):
        for line in self:
            if not line.talk_id or not line.employee_id:
                continue
            duplicate = self.search_count([
                ("id", "!=", line.id),
                ("talk_id", "=", line.talk_id.id),
                ("employee_id", "=", line.employee_id.id),
            ])
            if duplicate:
                raise ValidationError(_(
                    "The employee %s is already listed on the talk %s.",
                    line.employee_id.name, line.talk_id.name))

    def action_sign(self):
        for line in self:
            if line.signed:
                raise ValidationError(_(
                    "The attendance of %s is already signed.",
                    line.employee_id.name))
            line.write({
                "signed": True,
                "signed_on": fields.Date.context_today(line),
            })
            line.message_post(body=_(
                "The employee signed off the toolbox talk."))
        return True
