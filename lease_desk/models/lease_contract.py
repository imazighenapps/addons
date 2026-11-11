# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LeaseContract(models.Model):
    _name = "lease.contract"
    _description = "Lease Contract"
    _inherit = ["mail.thread"]
    _order = "date_start desc, id desc"

    name = fields.Char(required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Lessor", required=True, tracking=True)
    date_start = fields.Date(required=True, tracking=True)
    date_end = fields.Date(required=True, tracking=True)
    monthly_amount = fields.Monetary(required=True, tracking=True)
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    line_ids = fields.One2many(
        "lease.schedule", "lease_id", string="Schedule", copy=False)
    posted_amount = fields.Monetary(
        compute="_compute_totals", store=True)
    remaining_amount = fields.Monetary(
        compute="_compute_totals", store=True)
    schedule_count = fields.Integer(
        compute="_compute_totals", store=True)
    state = fields.Selection(
        [("draft", "Draft"), ("running", "Running"), ("closed", "Closed")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("monthly_amount", "line_ids.amount", "line_ids.state")
    def _compute_totals(self):
        for lease in self:
            total = sum(lease.line_ids.mapped("amount"))
            posted = sum(lease.line_ids.filtered(
                lambda l: l.state == "posted").mapped("amount"))
            lease.posted_amount = posted
            lease.remaining_amount = total - posted
            lease.schedule_count = len(lease.line_ids)

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for lease in self:
            if lease.date_end and lease.date_start \
                    and lease.date_end < lease.date_start:
                raise ValidationError(_(
                    "The end date of lease %s cannot be before its start "
                    "date.", lease.name))

    @api.constrains("monthly_amount")
    def _check_amount(self):
        for lease in self:
            if lease.monthly_amount <= 0:
                raise ValidationError(_(
                    "The monthly amount of lease %s must be greater than "
                    "zero.", lease.name))

    def action_generate_schedule(self):
        schedule = self.env["lease.schedule"]
        for lease in self:
            if lease.state == "closed":
                raise UserError(_(
                    "A closed lease cannot generate a schedule."))
            if lease.line_ids:
                raise UserError(_(
                    "Lease %s already has a schedule. Remove it before "
                    "generating a new one.", lease.name))
            current = lease.date_start
            seq = 1
            while current <= lease.date_end:
                schedule.create({
                    "lease_id": lease.id,
                    "sequence": seq,
                    "due_date": current,
                    "amount": lease.monthly_amount,
                })
                current = current + relativedelta(months=1)
                seq += 1
            lease.message_post(body=_(
                "Payment schedule generated with %s line(s).", seq - 1))
        return True

    def action_start(self):
        for lease in self:
            if lease.state != "draft":
                raise UserError(_("Only a draft lease can be started."))
            if not lease.line_ids:
                raise UserError(_(
                    "Generate the payment schedule before starting lease %s.",
                    lease.name))
            lease.state = "running"
            lease.message_post(body=_("Lease started."))
        return True

    def action_close(self):
        for lease in self:
            if lease.state != "running":
                raise UserError(_("Only a running lease can be closed."))
            lease.state = "closed"
            lease.message_post(body=_(
                "Lease closed with %s posted and %s remaining.",
                lease.posted_amount, lease.remaining_amount))
        return True
