# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ClnPlan(models.Model):
    _name = "cln.plan"
    _description = "Cleaning Plan"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(
        required=True, tracking=True,
        help="Name of the cleaning plan or routine.")
    area = fields.Char(
        string="Area", required=True, tracking=True,
        help="Room, zone or equipment covered by this plan.")
    frequency = fields.Selection(
        [("daily", "Daily"), ("weekly", "Weekly"),
         ("monthly", "Monthly"), ("shift", "Per Shift")],
        default="daily", required=True, tracking=True)
    method = fields.Char(
        string="Method",
        help="Cleaning method or product to be used.")
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", tracking=True,
        default=lambda self: self.env.user)
    active = fields.Boolean(default=True)
    execution_ids = fields.One2many(
        "cln.execution", "plan_id", string="Executions")
    execution_count = fields.Integer(
        string="Executions", compute="_compute_counts", store=True)
    pending_count = fields.Integer(
        string="Pending", compute="_compute_counts", store=True)
    done_count = fields.Integer(
        string="Done", compute="_compute_counts", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True,
        default=lambda self: self.env.company)
    note = fields.Text()

    @api.depends("execution_ids", "execution_ids.state")
    def _compute_counts(self):
        for rec in self:
            rec.execution_count = len(rec.execution_ids)
            rec.pending_count = len(
                rec.execution_ids.filtered(lambda e: e.state == "planned"))
            rec.done_count = len(
                rec.execution_ids.filtered(lambda e: e.state == "done"))
