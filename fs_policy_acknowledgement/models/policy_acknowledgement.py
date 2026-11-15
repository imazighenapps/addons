# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HrPolicy(models.Model):
    _name = "hr.policy"
    _description = "HR Policy"
    _order = "date_effective desc, id desc"

    name = fields.Char(string="Policy Title", required=True)
    version = fields.Char(string="Version")
    date_effective = fields.Date(string="Effective Date")
    active = fields.Boolean(default=True)
    description = fields.Text(string="Summary / Reference")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)


class PolicyAcknowledgement(models.Model):
    _name = "policy.acknowledgement"
    _description = "Policy Acknowledgement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_ack desc, id desc"

    policy_id = fields.Many2one(
        "hr.policy", string="Policy", required=True, index=True, tracking=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, index=True, tracking=True)
    date_ack = fields.Date(string="Acknowledged On", tracking=True)
    state = fields.Selection(
        [("pending", "Pending"), ("acknowledged", "Acknowledged")],
        default="pending", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    _sql_constraints = [
        ('policy_employee_uniq', "UNIQUE(policy_id, employee_id)", "An acknowledgement record already exists for this employee and policy."),
    ]

    def action_acknowledge(self):
        for rec in self:
            rec.write({
                "state": "acknowledged",
                "date_ack": rec.date_ack or fields.Date.context_today(rec),
            })

    def action_reset(self):
        for rec in self:
            rec.write({"state": "pending", "date_ack": False})
