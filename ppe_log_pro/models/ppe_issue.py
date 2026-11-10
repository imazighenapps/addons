# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PpeIssue(models.Model):
    _name = "ppe.issue"
    _description = "PPE Issue"
    _inherit = ["mail.thread"]
    _order = "issued_on desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("PPE %s")
        % fields.Date.context_today(self),
        help="Reference of the issue, generated at creation.")
    item_id = fields.Many2one(
        "ppe.item", string="Equipment", required=True,
        ondelete="cascade", index=True, tracking=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, tracking=True)
    size = fields.Char(
        help="Size of the issued equipment, for example L or 42.")
    quantity = fields.Integer(default=1, required=True,
                              help="Number of pieces handed out.")
    issued_on = fields.Date(
        string="Issued On", required=True, default=fields.Date.context_today,
        tracking=True)
    expires_on = fields.Date(
        string="Renew On", compute="_compute_expires_on", store=True,
        help="Date the issue must be renewed, from the renewal period "
             "of the equipment.")
    signed = fields.Boolean(
        default=False, tracking=True,
        help="Ticked when the employee signed for the issue.")
    state = fields.Selection(
        [("issued", "In Service"), ("returned", "Returned")],
        default="issued", required=True, copy=False, tracking=True,
        index=True)
    returned_on = fields.Date(string="Returned On", readonly=True,
                              copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("item_id", "issued_on")
    def _compute_expires_on(self):
        for issue in self:
            if issue.item_id and issue.issued_on:
                issue.expires_on = issue.issued_on + relativedelta(
                    months=issue.item_id.validity_months)
            else:
                issue.expires_on = False

    @api.constrains("quantity")
    def _check_quantity(self):
        for issue in self:
            if issue.quantity <= 0:
                raise ValidationError(_(
                    "The quantity of %s issued to %s must be above zero.",
                    issue.item_id.name, issue.employee_id.name))

    @api.constrains("issued_on", "returned_on")
    def _check_dates(self):
        for issue in self:
            if issue.returned_on and issue.returned_on < issue.issued_on:
                raise ValidationError(_(
                    "The return date of %s cannot come before the issue "
                    "date.", issue.name))

    def action_return(self):
        for issue in self:
            if issue.state != "issued":
                raise ValidationError(_(
                    "The issue of %s to %s is already closed.",
                    issue.item_id.name, issue.employee_id.name))
            issue.write({
                "state": "returned",
                "returned_on": fields.Date.context_today(issue),
            })
            issue.message_post(body=_(
                "The equipment was returned to the cabinet."))
        return True
