# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AssetCategory(models.Model):
    _name = "asset.category"
    _description = "Asset Category"
    _order = "name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char()
    method = fields.Selection(
        [("linear", "Linear"), ("declining", "Declining Balance")],
        default="linear", required=True)
    duration_months = fields.Integer(
        string="Duration (months)", default=60, required=True,
        help="Number of months over which the asset is depreciated.")
    declining_rate = fields.Float(
        string="Declining Rate (%)", default=20.0,
        help="Annual percentage applied to the net book value when the "
             "declining balance method is used.")
    account_asset_id = fields.Many2one(
        "account.account", string="Asset Account")
    account_depreciation_id = fields.Many2one(
        "account.account", string="Depreciation Account")
    account_expense_id = fields.Many2one(
        "account.account", string="Depreciation Expense Account")
    record_ids = fields.One2many("asset.record", "category_id")
    asset_count = fields.Integer(compute="_compute_asset_count")
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)

    @api.depends("record_ids")
    def _compute_asset_count(self):
        for category in self:
            category.asset_count = len(category.record_ids)

    @api.constrains("duration_months", "declining_rate", "method")
    def _check_parameters(self):
        for category in self:
            if category.duration_months <= 0:
                raise ValidationError(_(
                    "The duration must be strictly positive."))
            if category.method == "declining":
                if category.declining_rate <= 0 \
                        or category.declining_rate > 100:
                    raise ValidationError(_(
                        "The declining rate must be between 0 and 100."))


class AssetRecord(models.Model):
    _name = "asset.record"
    _description = "Fixed Asset"
    _inherit = ["mail.thread"]
    _order = "acquisition_date desc, id desc"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(string="Asset Code", tracking=True)
    category_id = fields.Many2one(
        "asset.category", string="Category", required=True,
        ondelete="restrict", tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Supplier", domain=[("supplier_rank", ">", 0)])
    location = fields.Char()
    responsible_id = fields.Many2one(
        "res.users", string="Responsible",
        default=lambda self: self.env.user)
    acquisition_date = fields.Date(
        default=fields.Date.context_today, required=True, tracking=True)
    in_service_date = fields.Date(
        default=fields.Date.context_today, tracking=True)
    gross_value = fields.Monetary(
        string="Acquisition Value", currency_field="currency_id",
        tracking=True)
    salvage_value = fields.Monetary(
        string="Salvage Value", currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    method = fields.Selection(
        related="category_id.method", store=True, readonly=True)
    duration_months = fields.Integer(
        related="category_id.duration_months", store=True, readonly=True)
    declining_rate = fields.Float(
        related="category_id.declining_rate", store=True, readonly=True)
    depreciation_line_ids = fields.One2many(
        "asset.depreciation.line", "asset_id", string="Depreciation Schedule")
    line_count = fields.Integer(compute="_compute_amounts")
    posted_depreciation = fields.Monetary(
        string="Posted Depreciation", currency_field="currency_id",
        compute="_compute_amounts")
    residual_value = fields.Monetary(
        string="Net Book Value", currency_field="currency_id",
        compute="_compute_amounts")
    remaining_depreciable = fields.Monetary(
        string="Remaining to Depreciate", currency_field="currency_id",
        compute="_compute_amounts")
    state = fields.Selection(
        [("draft", "Draft"), ("running", "Running"),
         ("closed", "Fully Depreciated"), ("disposed", "Disposed")],
        default="draft", required=True, tracking=True, index=True)
    disposal_date = fields.Date(tracking=True)
    disposal_value = fields.Monetary(
        string="Disposal Value", currency_field="currency_id", tracking=True)
    disposal_gain_loss = fields.Monetary(
        string="Gain / Loss", currency_field="currency_id", readonly=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    active = fields.Boolean(default=True)

    @api.depends("depreciation_line_ids.amount",
                 "depreciation_line_ids.posted",
                 "gross_value", "salvage_value")
    def _compute_amounts(self):
        for asset in self:
            lines = asset.depreciation_line_ids
            posted = sum(lines.filtered("posted").mapped("amount"))
            asset.line_count = len(lines)
            asset.posted_depreciation = posted
            asset.residual_value = asset.gross_value - posted
            asset.remaining_depreciable = (
                asset.gross_value - asset.salvage_value - posted)

    @api.constrains("gross_value", "salvage_value", "acquisition_date",
                    "in_service_date")
    def _check_values(self):
        for asset in self:
            if asset.gross_value < 0:
                raise ValidationError(_(
                    "The acquisition value cannot be negative."))
            if asset.salvage_value < 0:
                raise ValidationError(_(
                    "The salvage value cannot be negative."))
            if asset.salvage_value > asset.gross_value:
                raise ValidationError(_(
                    "The salvage value cannot exceed the acquisition value."))
            if asset.in_service_date and asset.acquisition_date \
                    and asset.in_service_date < asset.acquisition_date:
                raise ValidationError(_(
                    "The in-service date cannot be before the acquisition "
                    "date."))

    def _schedule_values(self):
        """Build the depreciation lines of one asset."""
        self.ensure_one()
        if self.duration_months <= 0:
            raise UserError(_("Set a positive duration on the category."))
        depreciable = self.gross_value - self.salvage_value
        if depreciable <= 0:
            raise UserError(_(
                "The acquisition value must exceed the salvage value."))
        start = self.in_service_date or self.acquisition_date \
            or fields.Date.context_today(self)
        total = self.duration_months
        values = []
        if self.method == "declining":
            rate = (self.declining_rate or 0.0) / 100.0
            if rate <= 0:
                raise UserError(_(
                    "Set a positive declining rate on the category."))
            monthly = rate / 12.0
            book = self.gross_value
            for index in range(1, total + 1):
                if index == total:
                    amount = round(book - self.salvage_value, 2)
                else:
                    amount = round(book * monthly, 2)
                    floor = round(book - self.salvage_value, 2)
                    if amount > floor:
                        amount = floor
                if amount <= 0:
                    break
                book = round(book - amount, 2)
                values.append({
                    "name": _("Depreciation %(index)02d/%(total)02d",
                              index=index, total=total),
                    "sequence": index,
                    "date": start + relativedelta(months=index),
                    "amount": amount,
                })
        else:
            amount = round(depreciable / total, 2)
            posted = 0.0
            for index in range(1, total + 1):
                if index == total:
                    current = round(depreciable - posted, 2)
                else:
                    current = amount
                posted = round(posted + current, 2)
                values.append({
                    "name": _("Depreciation %(index)02d/%(total)02d",
                              index=index, total=total),
                    "sequence": index,
                    "date": start + relativedelta(months=index),
                    "amount": current,
                })
        return values

    def action_validate(self):
        for asset in self:
            if asset.state != "draft":
                raise UserError(_("Only a draft asset can be validated."))
            if asset.gross_value <= 0:
                raise UserError(_(
                    "Set the acquisition value before validating the asset."))
            if not asset.depreciation_line_ids:
                values = asset._schedule_values()
                if not values:
                    raise UserError(_(
                        "The depreciation schedule is empty. Check the "
                        "duration and the values."))
                self.env["asset.depreciation.line"].create(
                    [dict(value, asset_id=asset.id) for value in values])
            asset.write({"state": "running"})
            asset.message_post(body=_("Asset validated and schedule generated."))
        return True

    def action_post_depreciation(self):
        today = fields.Date.context_today(self)
        for asset in self:
            if asset.state != "running":
                raise UserError(_(
                    "Depreciation can only be posted on a running asset."))
            due = asset.depreciation_line_ids.filtered(
                lambda line: not line.posted and line.date <= today)
            if not due:
                raise UserError(_(
                    "No depreciation period is due for \"%s\".", asset.name))
            due.write({"posted": True, "posted_date": today})
            if asset.remaining_depreciable <= 0.01:
                asset.write({"state": "closed"})
                asset.message_post(body=_(
                    "Asset fully depreciated."))
            else:
                asset.message_post(body=_(
                    "%s depreciation period(s) posted.", len(due)))
        return True

    def action_dispose(self):
        for asset in self:
            if asset.state not in ("running", "closed"):
                raise UserError(_(
                    "Only a running or closed asset can be disposed of."))
            if not asset.disposal_date:
                raise UserError(_("Set the disposal date."))
            if asset.disposal_value < 0:
                raise UserError(_("The disposal value cannot be negative."))
            gain_loss = asset.disposal_value - asset.residual_value
            asset.write({
                "disposal_gain_loss": gain_loss,
                "state": "disposed",
            })
            asset.message_post(body=_(
                "Asset disposed of for %(value)s. Gain / loss: %(gain)s.",
                value=asset.disposal_value, gain=gain_loss))
        return True

    def action_reset(self):
        for asset in self:
            if asset.state == "draft":
                continue
            if asset.posted_depreciation > 0 and asset.state == "closed":
                asset.write({"state": "running"})
            elif asset.posted_depreciation > 0:
                asset.write({
                    "state": "running",
                    "disposal_date": False,
                    "disposal_value": 0.0,
                    "disposal_gain_loss": 0.0,
                })
            else:
                asset.write({
                    "state": "draft",
                    "disposal_date": False,
                    "disposal_value": 0.0,
                    "disposal_gain_loss": 0.0,
                })
            asset.message_post(body=_("Asset reset."))
        return True


class AssetDepreciationLine(models.Model):
    _name = "asset.depreciation.line"
    _description = "Asset Depreciation Line"
    _order = "asset_id, sequence, id"

    asset_id = fields.Many2one(
        "asset.record", string="Asset", required=True,
        ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    date = fields.Date(required=True)
    amount = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        related="asset_id.currency_id", store=True, readonly=True)
    posted = fields.Boolean(default=False)
    posted_date = fields.Date(readonly=True)
    company_id = fields.Many2one(
        related="asset_id.company_id", store=True, readonly=True)

    _amount_positive = models.Constraint(
        "CHECK(amount >= 0)",
        "The depreciation amount cannot be negative.")
