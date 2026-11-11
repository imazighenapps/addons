# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PriceShift(models.Model):
    _name = "price.shift"
    _description = "Price Change"
    _inherit = ["mail.thread"]
    _order = "effective_on desc, id desc"

    name = fields.Char(
        default="/", required=True, copy=False, tracking=True,
        help="Reference of the change, generated from the PSC/ sequence.")
    description = fields.Char(
        required=True, tracking=True,
        help="What this change is about, for example 2027 catalogue "
             "increase.")
    change_type = fields.Selection(
        [("increase", "Price Increase"), ("decrease", "Price Decrease")],
        default="increase", required=True, tracking=True)
    percent = fields.Float(
        string="Change (%)", default=5.0, required=True, tracking=True,
        help="Percentage applied to the current price of every line.")
    effective_on = fields.Date(
        string="Effective Date", required=True, tracking=True,
        help="Date from which the planned prices apply.")
    scope = fields.Char(
        help="Who the change covers, for example Retail segment or "
             "product family A.")
    state = fields.Selection(
        [("draft", "Draft"), ("scheduled", "Scheduled"),
         ("applied", "Applied"), ("cancelled", "Cancelled")],
        default="draft", required=True, copy=False, tracking=True,
        index=True)
    line_ids = fields.One2many(
        "price.shift.line", "shift_id", string="Customer Lines", copy=True)
    customer_count = fields.Integer(
        string="Customers", compute="_compute_customer_count", store=True,
        help="Number of customer lines carried by this change.")
    applied_on = fields.Datetime(
        string="Applied On", readonly=True, copy=False,
        help="Date and time the change was applied.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "price.shift") or "/"
        return super().create(vals_list)

    @api.depends("line_ids", "line_ids.current_price")
    def _compute_customer_count(self):
        for shift in self:
            shift.customer_count = len(shift.line_ids)

    @api.constrains("percent")
    def _check_percent(self):
        for shift in self:
            if not 0.0 < shift.percent <= 100.0:
                raise ValidationError(_(
                    "The change percentage of %s must be above 0 and at "
                    "most 100.", shift.name))

    def write(self, vals):
        if "percent" in vals or "change_type" in vals \
                or "effective_on" in vals:
            for shift in self:
                if shift.state != "draft":
                    raise UserError(_(
                        "The change %s is %s: its type, percentage and "
                        "effective date are locked. Reset it to draft "
                        "first.", shift.name, shift.state))
        return super().write(vals)

    def action_schedule(self):
        for shift in self:
            if shift.state != "draft":
                raise UserError(_(
                    "Only a draft change can be scheduled."))
            if not shift.line_ids:
                raise UserError(_(
                    "Add at least one customer line before scheduling "
                    "the change %s.", shift.name))
            shift.state = "scheduled"
            shift.message_post(body=_(
                "Change scheduled: %(type)s of %(percent).2f%% on "
                "%(date)s for %(count)s customer(s).",
                type=dict(shift._fields["change_type"].selection).get(
                    shift.change_type),
                percent=shift.percent,
                date=shift.effective_on.strftime("%Y-%m-%d"),
                count=len(shift.line_ids)))
        return True

    def action_apply(self):
        for shift in self:
            if shift.state != "scheduled":
                raise UserError(_(
                    "Only a scheduled change can be applied."))
            shift.write({
                "state": "applied",
                "applied_on": fields.Datetime.now(),
            })
            shift.message_post(body=_(
                "Change applied to %(count)s customer(s): their planned "
                "prices are now the recorded ones.",
                count=len(shift.line_ids)))
        return True

    def action_cancel(self):
        for shift in self:
            if shift.state not in ("draft", "scheduled"):
                raise UserError(_(
                    "Only a draft or scheduled change can be cancelled."))
            shift.state = "cancelled"
            shift.message_post(body=_(
                "Change cancelled before being applied: the trace is "
                "kept."))
        return True


class PriceShiftLine(models.Model):
    _name = "price.shift.line"
    _description = "Price Change Line"
    _inherit = ["mail.thread"]
    _order = "shift_id, partner_id, id"

    shift_id = fields.Many2one(
        "price.shift", string="Price Change", required=True,
        ondelete="cascade", index=True)
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True)
    current_price = fields.Monetary(
        string="Current Price", required=True,
        help="Price the customer pays before the effective date.")
    new_price = fields.Monetary(
        string="New Price", compute="_compute_new_price", store=True,
        help="Price computed from the current price and the change "
             "percentage.")
    currency_id = fields.Many2one(
        related="shift_id.company_id.currency_id", store=True,
        readonly=True)
    company_id = fields.Many2one(
        related="shift_id.company_id", store=True, readonly=True)
    note = fields.Text()

    @api.depends("current_price", "shift_id.percent",
                 "shift_id.change_type")
    def _compute_new_price(self):
        for line in self:
            factor = 1.0 + (line.shift_id.percent or 0.0) / 100.0
            if line.shift_id.change_type == "decrease":
                factor = 1.0 - (line.shift_id.percent or 0.0) / 100.0
            line.new_price = line.current_price * factor \
                if line.current_price else 0.0

    @api.constrains("current_price")
    def _check_current_price(self):
        for line in self:
            if line.current_price < 0:
                raise ValidationError(_(
                    "The current price of %s cannot be negative.",
                    line.partner_id.name))

    @api.model_create_multi
    def create(self, vals_list):
        shift_ids = {vals["shift_id"] for vals in vals_list
                     if vals.get("shift_id")}
        if shift_ids:
            applied = self.env["price.shift"].browse(
                sorted(shift_ids)).filtered(
                    lambda shift: shift.state == "applied")
            if applied:
                raise UserError(_(
                    "The price change %s is applied: no customer line "
                    "can be added to it.", applied[0].name))
        return super().create(vals_list)

    def write(self, vals):
        for line in self:
            if line.shift_id.state == "applied":
                raise UserError(_(
                    "The price change %s is applied: its customer lines "
                    "can no longer be changed.", line.shift_id.name))
        return super().write(vals)
