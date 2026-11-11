# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HoldDeskReason(models.Model):
    _name = "hold.desk.reason"
    _description = "Hold Reason"
    _inherit = ["mail.thread"]
    _order = "sequence, name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        help="Short code used on the hold screens, for example CRED.")
    sequence = fields.Integer(default=10)
    description = fields.Text(
        help="When to use this reason: which rule triggers the hold.")
    request_ids = fields.One2many(
        "hold.desk.request", "reason_id", string="Holds")
    request_count = fields.Integer(
        string="Holds", compute="_compute_requests", store=True,
        help="Number of orders ever placed on hold with this reason.")
    open_count = fields.Integer(
        string="Active Holds", compute="_compute_requests", store=True,
        help="Orders still on hold with this reason.")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)

    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "The hold reason code must be unique per company.")

    @api.depends("request_ids", "request_ids.state")
    def _compute_requests(self):
        for reason in self:
            reason.request_count = len(reason.request_ids)
            reason.open_count = len(reason.request_ids.filtered(
                lambda request: request.state == "hold"))


class HoldDeskRequest(models.Model):
    _name = "hold.desk.request"
    _description = "Order Hold"
    _inherit = ["mail.thread"]
    _order = "hold_on desc, id desc"

    name = fields.Char(
        default="/", required=True, copy=False, tracking=True,
        help="Reference of the hold, generated from the HDS/ sequence.")
    reason_id = fields.Many2one(
        "hold.desk.reason", string="Reason", required=True, tracking=True,
        index=True)
    document = fields.Char(
        string="Order", required=True, tracking=True,
        help="Reference of the confirmed order placed on hold.")
    partner_id = fields.Many2one("res.partner", string="Customer")
    amount = fields.Monetary(tracking=True,
                             help="Amount of the order left waiting.")
    currency_id = fields.Many2one(
        "res.currency", string="Currency", required=True,
        default=lambda self: self.env.company.currency_id)
    state = fields.Selection(
        [("draft", "Draft"), ("hold", "On Hold"), ("released", "Released"),
         ("abandoned", "Cancelled")],
        default="draft", required=True, copy=False, tracking=True,
        index=True)
    hold_on = fields.Date(
        default=fields.Date.context_today, required=True, tracking=True,
        help="Date the order was placed on hold.")
    release_on = fields.Date(
        string="Released On", tracking=True, copy=False,
        help="Date the order was released, stamped by the release.")
    released_by = fields.Many2one(
        "res.users", string="Released By", copy=False, tracking=True,
        help="User who released the order.")
    hold_days = fields.Integer(
        string="Days On Hold", compute="_compute_hold_days", store=True,
        help="Days the order waited between its hold and its release.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "hold.desk.request") or "/"
        return super().create(vals_list)

    @api.depends("hold_on", "release_on")
    def _compute_hold_days(self):
        for request in self:
            if request.hold_on and request.release_on \
                    and request.release_on >= request.hold_on:
                request.hold_days = (
                    request.release_on - request.hold_on).days
            else:
                request.hold_days = 0

    @api.constrains("hold_on", "release_on")
    def _check_dates(self):
        for request in self:
            if request.release_on and request.release_on < request.hold_on:
                raise ValidationError(_(
                    "The release date of the hold %s cannot come before "
                    "the hold date.", request.name))

    @api.constrains("amount")
    def _check_amount(self):
        for request in self:
            if request.amount < 0:
                raise ValidationError(_(
                    "The amount of an order hold cannot be negative."))

    def action_hold(self):
        for request in self:
            if request.state != "draft":
                raise UserError(_(
                    "Only a draft hold can be placed on hold."))
            request.state = "hold"
            request.message_post(body=_(
                "The order %(order)s was placed on hold for reason "
                "%(reason)s.",
                order=request.document, reason=request.reason_id.name))
        return True

    def action_release(self):
        for request in self:
            if request.state != "hold":
                raise UserError(_(
                    "Only an order on hold can be released, not one in "
                    "status %s.", request.state))
            request.write({
                "state": "released",
                "release_on": fields.Date.context_today(request),
                "released_by": self.env.user.id,
            })
            request.message_post(body=_(
                "The order %s was released after %s day(s) on hold.",
                request.document, request.hold_days))
        return True

    def action_abandon(self):
        for request in self:
            if request.state not in ("draft", "hold"):
                raise UserError(_(
                    "Only a draft or on-hold request can be abandoned."))
            request.state = "abandoned"
            request.message_post(body=_(
                "The hold on the order %s was abandoned.", request.document))
        return True
