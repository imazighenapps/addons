# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VatCheck(models.Model):
    _name = "vat.check"
    _description = "VAT Cross Check"
    _inherit = ["mail.thread"]
    _order = "period_start desc, id desc"

    name = fields.Char(required=True, tracking=True)
    period_start = fields.Date(required=True, tracking=True)
    period_end = fields.Date(required=True, tracking=True)
    line_ids = fields.One2many("vat.check.line", "check_id", string="Boxes")
    line_count = fields.Integer(
        string="Boxes", compute="_compute_progress", store=True)
    open_line_count = fields.Integer(
        string="Open Boxes", compute="_compute_progress", store=True)
    state = fields.Selection(
        [("draft", "Draft"), ("review", "In Review"), ("closed", "Closed")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    closed_on = fields.Date(string="Closed On", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("line_ids", "line_ids.reviewed", "line_ids.difference_amount")
    def _compute_progress(self):
        for check in self:
            lines = check.line_ids
            check.line_count = len(lines)
            check.open_line_count = len(lines.filtered(
                lambda line: not line.reviewed or abs(
                    line.difference_amount) > 0.00001))

    @api.constrains("period_start", "period_end")
    def _check_period(self):
        for check in self:
            if check.period_end < check.period_start:
                raise ValidationError(_(
                    "The period end of %s cannot be before its start.",
                    check.name))

    def action_start_review(self):
        for check in self:
            if check.state != "draft":
                raise ValidationError(_(
                    "Only a draft VAT cross-check can move to review."))
            if not check.line_ids:
                raise ValidationError(_(
                    "Add at least one VAT box before reviewing %s.",
                    check.name))
            check.state = "review"
            check.message_post(body=_("The VAT cross-check entered review."))
        return True

    def action_close(self):
        for check in self:
            if check.state != "review":
                raise ValidationError(_(
                    "Only a VAT cross-check in review can be closed."))
            pending = check.line_ids.filtered(lambda line: not line.reviewed)
            if pending:
                raise ValidationError(_(
                    "Review every VAT box before closing %s.", check.name))
            check.write({
                "state": "closed",
                "closed_on": fields.Date.context_today(check),
            })
            check.message_post(body=_(
                "The VAT cross-check was closed and verified."))
        return True
