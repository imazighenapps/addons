# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ToolCribLoan(models.Model):
    _name = "tool.crib.loan"
    _description = "Tool Loan"
    _inherit = ["mail.thread"]
    _order = "issued_on desc, id desc"

    name = fields.Char(
        required=True, default=lambda self: _("Loan %s")
        % fields.Date.context_today(self),
        help="Reference of the loan, generated at creation.")
    tool_id = fields.Many2one(
        "tool.crib.tool", string="Tool", required=True,
        ondelete="cascade", index=True, tracking=True)
    borrower_name = fields.Char(
        string="Borrower", required=True, tracking=True,
        help="Name of the employee who borrowed the tool.")
    issued_on = fields.Date(
        string="Issued On", required=True,
        default=fields.Date.context_today, tracking=True)
    due_on = fields.Date(
        string="Due Back On", required=True, tracking=True,
        help="Date the tool is expected back in the crib.")
    is_late = fields.Boolean(
        string="Late", compute="_compute_is_late", store=True,
        help="True when the loan is still open after the due date.")
    state = fields.Selection(
        [("out", "Out"), ("returned", "Returned")],
        default="out", required=True, copy=False, tracking=True, index=True)
    returned_on = fields.Date(
        string="Returned On", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("due_on", "state")
    def _compute_is_late(self):
        today = fields.Date.context_today(self)
        for loan in self:
            loan.is_late = bool(
                loan.state == "out" and loan.due_on and loan.due_on < today)

    @api.constrains("issued_on", "due_on")
    def _check_due(self):
        for loan in self:
            if loan.due_on and loan.issued_on and loan.due_on < loan.issued_on:
                raise ValidationError(_(
                    "The due date of %s cannot come before the issue date.",
                    loan.name))

    @api.constrains("issued_on", "returned_on")
    def _check_return(self):
        for loan in self:
            if loan.returned_on and loan.returned_on < loan.issued_on:
                raise ValidationError(_(
                    "The return date of %s cannot come before the issue "
                    "date.", loan.name))

    def action_return(self):
        for loan in self:
            if loan.state != "out":
                raise ValidationError(_(
                    "The loan of %s to %s is already closed.",
                    loan.tool_id.name, loan.borrower_name))
            loan.write({
                "state": "returned",
                "returned_on": fields.Date.context_today(loan),
            })
            loan.message_post(body=_(
                "The tool has been returned to the crib."))
        return True
