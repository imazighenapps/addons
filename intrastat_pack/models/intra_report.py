# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class IntraReport(models.Model):
    _name = "intra.report"
    _description = "Intrastat Declaration"
    _inherit = ["mail.thread"]
    _order = "period_start desc, direction, id desc"

    name = fields.Char(
        required=True, copy=False, tracking=True,
        help="Reference of the declaration, for example 2026-11 Dispatch.")
    direction = fields.Selection(
        [("dispatch", "Dispatch"), ("arrival", "Arrival")],
        required=True, default="dispatch", tracking=True,
        help="Whether the declaration covers goods sent or goods received.")
    period_start = fields.Date(
        string="Period Start", required=True,
        default=lambda self: fields.Date.context_today(self).replace(day=1),
        tracking=True)
    period_end = fields.Date(
        string="Period End", required=True,
        default=fields.Date.context_today, tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("review", "In Review"), ("filed", "Filed")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    line_ids = fields.One2many(
        "intra.flow", "report_id", string="Flow Lines", copy=True)
    line_count = fields.Integer(
        string="Flow Lines", compute="_compute_totals", store=True)
    total_value = fields.Float(
        string="Total Value", compute="_compute_totals", store=True,
        help="Sum of the invoice values of all flow lines.")
    total_weight = fields.Float(
        string="Total Net Mass", compute="_compute_totals", store=True,
        help="Sum of the net mass of all flow lines, in kilograms.")
    filed_on = fields.Date(string="Filed On", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("line_ids", "line_ids.value", "line_ids.weight")
    def _compute_totals(self):
        for report in self:
            lines = report.line_ids
            report.line_count = len(lines)
            report.total_value = sum(lines.mapped("value"))
            report.total_weight = sum(lines.mapped("weight"))

    @api.constrains("period_start", "period_end")
    def _check_period(self):
        for report in self:
            if report.period_end < report.period_start:
                raise ValidationError(_(
                    "The period end of %s cannot be before its start.",
                    report.name))

    def _ensure_open(self):
        for report in self:
            if report.state == "filed":
                raise UserError(_(
                    "The filed declaration %s cannot be changed.", report.name))

    def write(self, vals):
        self._ensure_open()
        return super().write(vals)

    def action_review(self):
        for report in self:
            if report.state != "draft":
                raise UserError(_(
                    "Only a draft declaration can be sent to review."))
            if not report.line_ids:
                raise UserError(_(
                    "Add at least one flow line before reviewing %s.",
                    report.name))
            report.state = "review"
            report.message_post(body=_("Declaration sent to review."))
        return True

    def action_file(self):
        for report in self:
            if report.state != "review":
                raise UserError(_(
                    "Only a declaration in review can be filed."))
            report.write({
                "state": "filed",
                "filed_on": fields.Date.context_today(report),
            })
            report.message_post(body=_(
                "Declaration filed with %s flow line(s).", report.line_count))
        return True

    def action_reset(self):
        for report in self:
            if report.state != "review":
                raise UserError(_(
                    "Only a declaration in review can be reset to draft."))
            report.state = "draft"
            report.message_post(body=_("Declaration reset to draft."))
        return True
