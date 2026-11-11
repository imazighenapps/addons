# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ExpediteEntry(models.Model):
    _name = "expedite.entry"
    _description = "Expedited Purchase Entry"
    _inherit = ["mail.thread"]
    _order = "request_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True,
        default=lambda self: _("EXP-%s") % fields.Date.context_today(self),
        help="Reference of the expedited purchase entry.")
    product_name = fields.Char(
        string="Product", required=True, tracking=True,
        help="Product or service purchased under urgency.")
    requester_name = fields.Char(
        string="Requester", required=True, tracking=True,
        help="Person or team who triggered the expedited purchase.")
    reason = fields.Char(
        string="Urgency Reason", required=True,
        help="Why the purchase had to be expedited.")
    urgency_type = fields.Selection(
        [("expedited", "Expedited"), ("emergency", "Emergency")],
        default="expedited", required=True, tracking=True,
        help="How urgent the purchase was.")
    request_date = fields.Date(
        string="Request Date", required=True,
        default=fields.Date.context_today, tracking=True)
    normal_cost = fields.Monetary(
        string="Normal Cost", currency_field="currency_id",
        required=True, tracking=True,
        help="Expected cost without the urgency premium.")
    actual_cost = fields.Monetary(
        string="Actual Cost", currency_field="currency_id",
        required=True, tracking=True,
        help="Actual cost paid for the expedited purchase.")
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    premium_amount = fields.Monetary(
        string="Premium", currency_field="currency_id",
        compute="_compute_premium", store=True,
        help="Extra cost paid because of urgency.")
    has_premium = fields.Boolean(
        string="Has Premium", compute="_compute_premium", store=True,
        help="True when the actual cost exceeds the normal cost.")
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed")],
        default="draft", required=True, copy=False, tracking=True,
        index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("normal_cost", "actual_cost")
    def _compute_premium(self):
        for rec in self:
            diff = (rec.actual_cost or 0.0) - (rec.normal_cost or 0.0)
            rec.premium_amount = diff if diff > 0 else 0.0
            rec.has_premium = bool(diff > 0)

    @api.constrains("normal_cost")
    def _check_normal_cost(self):
        for rec in self:
            if rec.normal_cost < 0:
                raise ValidationError(_(
                    "The normal cost of %s cannot be negative.",
                    rec.name))

    @api.constrains("actual_cost")
    def _check_actual_cost(self):
        for rec in self:
            if rec.actual_cost < 0:
                raise ValidationError(_(
                    "The actual cost of %s cannot be negative.",
                    rec.name))

    def action_confirm(self):
        for rec in self:
            if rec.state != "draft":
                raise ValidationError(_(
                    "Only draft entries can be confirmed: %s.", rec.name))
            rec.state = "confirmed"
            rec.message_post(body=_(
                "The expedited purchase was confirmed with a premium of %s.",
                rec.premium_amount))
        return True

    def action_reset_draft(self):
        for rec in self:
            if rec.state == "draft":
                raise ValidationError(_(
                    "The entry %s is already in draft.", rec.name))
            rec.state = "draft"
            rec.message_post(body=_("The entry was reset to draft."))
        return True
