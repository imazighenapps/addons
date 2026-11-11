# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class LateFeeLine(models.Model):
    _name = "late.fee.line"
    _description = "Late Fee Line"
    _inherit = ["mail.thread"]
    _order = "due_date desc, id desc"

    name = fields.Char(
        string="Invoice Reference", required=True, tracking=True,
        help="Reference of the overdue invoice.")
    rule_id = fields.Many2one(
        "late.fee.rule", string="Interest Rule", required=True,
        ondelete="restrict", index=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True)
    due_date = fields.Date(required=True, tracking=True)
    base_amount = fields.Monetary(
        string="Overdue Amount", required=True, tracking=True)
    calculation_date = fields.Date(
        string="Calculated On", required=True,
        default=fields.Date.context_today, tracking=True,
        help="Date used to count the days late.")
    days_late = fields.Integer(
        compute="_compute_interest", store=True)
    interest_amount = fields.Monetary(
        string="Interest", compute="_compute_interest", store=True,
        help="Interest computed from the rule rate and the days late.")
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    state = fields.Selection(
        [("draft", "Draft"), ("issued", "Issued")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    issued_on = fields.Date(string="Issued On", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("base_amount", "due_date", "calculation_date",
                 "rule_id.annual_rate", "rule_id.fixed_fee")
    def _compute_interest(self):
        for line in self:
            days = 0
            if line.due_date and line.calculation_date:
                delta = (line.calculation_date - line.due_date).days
                days = max(delta, 0)
            line.days_late = days
            if days and line.base_amount and line.rule_id:
                interest = (
                    line.base_amount * line.rule_id.annual_rate / 100.0
                    * days / 365.0) + line.rule_id.fixed_fee
                line.interest_amount = max(interest, 0.0)
            else:
                line.interest_amount = 0.0

    @api.constrains("base_amount")
    def _check_amount(self):
        for line in self:
            if line.base_amount <= 0:
                raise ValidationError(_(
                    "The overdue amount of %s must be greater than zero.",
                    line.name))

    @api.constrains("due_date", "calculation_date")
    def _check_dates(self):
        for line in self:
            if line.calculation_date and line.due_date \
                    and line.calculation_date < line.due_date:
                raise ValidationError(_(
                    "The calculation date of %s cannot be before the due "
                    "date.", line.name))

    def action_recompute(self):
        for line in self:
            line._compute_interest()
        return True

    def action_issue(self):
        for line in self:
            if line.state != "draft":
                raise ValidationError(_(
                    "Only a draft interest line can be issued."))
            if line.interest_amount <= 0:
                raise ValidationError(_(
                    "The interest of %s must be greater than zero before "
                    "issuing it.", line.name))
            line.write({
                "state": "issued",
                "issued_on": fields.Date.context_today(line),
            })
            line.message_post(body=_("Interest line issued."))
        return True
