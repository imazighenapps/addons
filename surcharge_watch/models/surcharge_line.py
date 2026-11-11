# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SurchargeLine(models.Model):
    _name = "surcharge.line"
    _description = "Applied Surcharge"
    _inherit = ["mail.thread"]
    _order = "period_start desc, id desc"

    name = fields.Char(
        required=True, copy=False,
        default=lambda self: _("Surcharge %s") % fields.Date.context_today(self))
    clause_id = fields.Many2one(
        "surcharge.clause", string="Clause", required=True, ondelete="cascade",
        tracking=True, index=True)
    partner_id = fields.Many2one(
        related="clause_id.partner_id", store=True, readonly=True, index=True)
    period_start = fields.Date(
        string="Period Start", required=True, default=fields.Date.context_today,
        tracking=True)
    period_end = fields.Date(
        string="Period End", required=True, tracking=True)
    current_index = fields.Float(
        required=True, digits=(16, 4),
        help="Index value observed for the billed period.")
    expected_amount = fields.Monetary(
        compute="_compute_amounts", store=True,
        help="Surcharge amount computed from the agreed clause.")
    billed_amount = fields.Monetary(
        required=True, default=0.0,
        help="Surcharge amount actually billed by the supplier.")
    variance_amount = fields.Monetary(
        compute="_compute_amounts", store=True,
        help="Difference between billed and expected surcharge.")
    currency_id = fields.Many2one(
        related="clause_id.currency_id", store=True, readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("to_review", "To Review"),
         ("accepted", "Accepted"), ("disputed", "Disputed")],
        default="draft", required=True, tracking=True, index=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("clause_id", "clause_id.base_index", "clause_id.factor",
                 "current_index", "billed_amount")
    def _compute_amounts(self):
        for line in self:
            clause = line.clause_id
            if clause and clause.base_index:
                movement = max(line.current_index - clause.base_index, 0.0)
                expected = movement * clause.factor
            else:
                expected = 0.0
            line.expected_amount = expected
            line.variance_amount = line.billed_amount - expected

    @api.constrains("period_start", "period_end")
    def _check_period(self):
        for line in self:
            if line.period_end < line.period_start:
                raise ValidationError(_(
                    "The period end of %s cannot come before its start.",
                    line.name))

    @api.constrains("current_index", "billed_amount")
    def _check_amounts(self):
        for line in self:
            if line.current_index <= 0:
                raise ValidationError(_(
                    "The current index of %s must be above zero.", line.name))
            if line.billed_amount < 0:
                raise ValidationError(_(
                    "The billed amount of %s cannot be negative.", line.name))

    def action_submit_review(self):
        for line in self:
            if line.state != "draft":
                raise UserError(_("Only draft surcharges can be sent to review."))
            line.state = "to_review"
            line.message_post(body=_("The surcharge was sent for review."))
        return True

    def action_accept(self):
        for line in self:
            if line.state != "to_review":
                raise UserError(_("Only surcharges to review can be accepted."))
            line.state = "accepted"
            line.message_post(body=_("The billed surcharge was accepted."))
        return True

    def action_dispute(self):
        for line in self:
            if line.state != "to_review":
                raise UserError(_("Only surcharges to review can be disputed."))
            line.state = "disputed"
            line.message_post(body=_("The billed surcharge was disputed."))
        return True

    def action_reset_draft(self):
        for line in self:
            if line.state not in ("to_review", "disputed"):
                raise UserError(_("Only review or disputed surcharges can be reset."))
            line.state = "draft"
            line.message_post(body=_("The surcharge was reset to draft."))
        return True
