# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CustomerDeposit(models.Model):
    _name = "customer.deposit"
    _description = "Customer Deposit"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"

    name = fields.Char(
        string="Deposit", default="/", required=True, copy=False,
        tracking=True, index=True)
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True,
        index=True)
    date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    amount = fields.Monetary(
        currency_field="currency_id", required=True, tracking=True)
    currency_id = fields.Many2one(
        "res.currency", string="Currency", required=True,
        default=lambda self: self.env.company.currency_id)
    payment_method = fields.Selection(
        [("bank", "Bank Transfer"), ("cash", "Cash"),
         ("card", "Credit Card"), ("cheque", "Cheque")],
        string="Payment Method", default="bank", required=True, tracking=True)
    journal_id = fields.Many2one(
        "account.journal", string="Journal",
        domain=[("type", "in", ["bank", "cash"])])
    reference = fields.Char(string="Payment Reference")
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"),
         ("partial", "Partially Applied"), ("applied", "Fully Applied"),
         ("refunded", "Refunded"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    allocation_ids = fields.One2many(
        "deposit.allocation", "deposit_id", string="Allocations")
    allocated_amount = fields.Monetary(
        string="Allocated", currency_field="currency_id",
        compute="_compute_amounts", store=True)
    remaining_amount = fields.Monetary(
        string="Remaining", currency_field="currency_id",
        compute="_compute_amounts", store=True)
    allocation_count = fields.Integer(
        string="Allocations", compute="_compute_amounts")
    refund_amount = fields.Monetary(
        string="Refunded", currency_field="currency_id",
        tracking=True, copy=False)
    refund_date = fields.Date(tracking=True, copy=False)
    refund_reason = fields.Text(string="Refund Reason")
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)

    _name_uniq = models.Constraint(
        "UNIQUE(name)",
        "The deposit reference must be unique.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "customer.deposit") or "/"
        return super().create(vals_list)

    @api.depends("amount", "allocation_ids.amount", "refund_amount")
    def _compute_amounts(self):
        for deposit in self:
            allocated = sum(deposit.allocation_ids.mapped("amount"))
            refunded = deposit.refund_amount or 0.0
            deposit.allocated_amount = allocated
            deposit.remaining_amount = max(
                0.0, (deposit.amount or 0.0) - allocated - refunded)
            deposit.allocation_count = len(deposit.allocation_ids)

    @api.constrains("amount")
    def _check_amount(self):
        for deposit in self:
            if deposit.amount <= 0:
                raise ValidationError(_(
                    "The deposit amount must be greater than zero."))
            allocations = self.env["deposit.allocation"].search([
                ("deposit_id", "=", deposit.id)])
            total = sum(allocations.mapped("amount")) \
                + (deposit.refund_amount or 0.0)
            if total > deposit.amount + 0.005:
                raise ValidationError(_(
                    "The deposit amount cannot be lower than the allocated "
                    "and refunded amount (%s).", total))

    def write(self, vals):
        result = super().write(vals)
        if "amount" in vals:
            self._sync_state()
        return result

    def _sync_state(self):
        """Keep confirmed/partial/applied consistent with the allocations."""
        allocations = self.env["deposit.allocation"]
        for deposit in self.exists():
            if deposit.state in ("draft", "cancelled"):
                continue
            allocated = sum(allocations.search([
                ("deposit_id", "=", deposit.id)]).mapped("amount"))
            if deposit.refund_amount:
                deposit.state = "refunded"
            elif allocated <= 0.0:
                if deposit.state in ("partial", "applied"):
                    deposit.state = "confirmed"
            elif allocated + 0.005 < deposit.amount:
                deposit.state = "partial"
            else:
                deposit.state = "applied"

    def action_confirm(self):
        for deposit in self:
            if deposit.state != "draft":
                raise UserError(_(
                    "Only a draft deposit can be confirmed."))
            if deposit.amount <= 0:
                raise UserError(_(
                    "The deposit amount must be greater than zero."))
            deposit.state = "confirmed"
        return True

    def action_refund(self):
        for deposit in self:
            if deposit.state not in ("confirmed", "partial"):
                raise UserError(_(
                    "Only a confirmed deposit with a remaining balance can "
                    "be refunded."))
            remaining = deposit.remaining_amount
            if remaining <= 0:
                raise UserError(_(
                    "There is nothing left to refund on this deposit."))
            deposit.write({
                "refund_amount": (deposit.refund_amount or 0.0) + remaining,
                "refund_date": fields.Date.context_today(deposit),
                "state": "refunded",
            })
            deposit.message_post(body=_(
                "Remaining balance of %(amount).2f refunded.",
                amount=remaining))
        return True

    def action_cancel(self):
        for deposit in self:
            has_allocations = self.env["deposit.allocation"].search_count([
                ("deposit_id", "=", deposit.id)])
            if has_allocations or deposit.refund_amount:
                raise UserError(_(
                    "Remove the allocations and the refund before cancelling "
                    "this deposit."))
            deposit.write({"state": "cancelled"})
        return True

    def action_reset(self):
        for deposit in self:
            has_allocations = self.env["deposit.allocation"].search_count([
                ("deposit_id", "=", deposit.id)])
            if has_allocations or deposit.refund_amount:
                raise UserError(_(
                    "Remove the allocations and the refund before resetting "
                    "this deposit."))
            deposit.write({"state": "draft"})
        return True


class DepositAllocation(models.Model):
    _name = "deposit.allocation"
    _description = "Deposit Allocation"
    _order = "date desc, id desc"

    deposit_id = fields.Many2one(
        "customer.deposit", string="Deposit", required=True,
        ondelete="cascade", index=True)
    invoice_id = fields.Many2one(
        "account.move", string="Invoice", required=True,
        domain=[("move_type", "in", ["out_invoice", "out_refund"]),
                ("state", "=", "posted")])
    date = fields.Date(
        required=True, default=fields.Date.context_today)
    amount = fields.Monetary(
        currency_field="currency_id", required=True)
    note = fields.Char()
    currency_id = fields.Many2one(
        related="deposit_id.currency_id", store=True, readonly=True)

    @api.constrains("amount", "deposit_id", "invoice_id")
    def _check_allocation(self):
        for allocation in self:
            if allocation.amount <= 0:
                raise ValidationError(_(
                    "The allocated amount must be greater than zero."))
            deposit = allocation.deposit_id
            if not deposit:
                continue
            invoice = allocation.invoice_id
            if invoice:
                if invoice.state != "posted":
                    raise ValidationError(_(
                        "Only a posted invoice can receive a deposit "
                        "allocation."))
                if invoice.partner_id.commercial_partner_id \
                        != deposit.partner_id.commercial_partner_id:
                    raise ValidationError(_(
                        "The invoice must belong to the same customer as "
                        "the deposit."))
            total = sum(self.search([
                ("deposit_id", "=", deposit.id)]).mapped("amount")) \
                + (deposit.refund_amount or 0.0)
            if total > deposit.amount + 0.005:
                raise ValidationError(_(
                    "The allocated and refunded amount (%(total).2f) cannot "
                    "exceed the deposit amount (%(amount).2f).",
                    total=total, amount=deposit.amount))

    @api.model_create_multi
    def create(self, vals_list):
        deposits = self.env["customer.deposit"]
        for vals in vals_list:
            deposit = self.env["customer.deposit"].browse(
                vals.get("deposit_id"))
            if not deposit or deposit.state not in (
                    "confirmed", "partial", "applied"):
                raise UserError(_(
                    "Confirm the deposit before allocating it to an invoice."))
            deposits |= deposit
        allocations = super().create(vals_list)
        deposits.exists()._sync_state()
        return allocations

    def write(self, vals):
        deposits = self.mapped("deposit_id")
        if any(deposit.refund_amount for deposit in deposits):
            raise UserError(_(
                "Allocations cannot be changed after the deposit is "
                "refunded."))
        if vals.get("deposit_id"):
            target = self.env["customer.deposit"].browse(vals["deposit_id"])
            if target.refund_amount:
                raise UserError(_(
                    "Allocations cannot be added to a refunded deposit."))
        result = super().write(vals)
        deposits |= self.mapped("deposit_id")
        deposits.exists()._sync_state()
        return result

    def unlink(self):
        deposits = self.mapped("deposit_id")
        if any(deposit.refund_amount for deposit in deposits):
            raise UserError(_(
                "Allocations cannot be deleted after the deposit is "
                "refunded."))
        result = super().unlink()
        deposits.exists()._sync_state()
        return result
