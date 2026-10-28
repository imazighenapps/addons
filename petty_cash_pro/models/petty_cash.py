# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PettyCashFund(models.Model):
    _name = "petty.cash.fund"
    _description = "Petty Cash Fund"
    _inherit = ["mail.thread"]
    _order = "code, id"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        required=True, index=True, tracking=True,
        help="Short code of the cash box, for example PC-HQ.")
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", tracking=True,
        default=lambda self: self.env.user)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    float_amount = fields.Monetary(
        string="Initial Float", currency_field="currency_id", tracking=True)
    opened_date = fields.Date(
        default=fields.Date.context_today, required=True)
    state = fields.Selection(
        [("open", "Open"), ("closed", "Closed")],
        default="open", required=True, tracking=True, index=True)
    closed_date = fields.Date(readonly=True, tracking=True)
    transaction_ids = fields.One2many(
        "petty.cash.transaction", "fund_id", string="Transactions")
    reconciliation_ids = fields.One2many(
        "petty.cash.reconciliation", "fund_id", string="Reconciliations")
    balance = fields.Monetary(
        string="Balance", currency_field="currency_id",
        compute="_compute_balance")
    total_topups = fields.Monetary(
        string="Total Top-Ups", currency_field="currency_id",
        compute="_compute_balance")
    total_expenses = fields.Monetary(
        string="Total Expenses", currency_field="currency_id",
        compute="_compute_balance")
    transaction_count = fields.Integer(
        string="Transactions", compute="_compute_balance")
    note = fields.Text()

    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "The fund code must be unique per company.")

    @api.depends("float_amount", "transaction_ids.amount",
                 "transaction_ids.type", "transaction_ids.state")
    def _compute_balance(self):
        for fund in self:
            confirmed = fund.transaction_ids.filtered(
                lambda txn: txn.state == "confirmed")
            topups = sum(confirmed.filtered(
                lambda txn: txn.type == "top_up").mapped("amount"))
            expenses = sum(confirmed.filtered(
                lambda txn: txn.type == "expense").mapped("amount"))
            returns = sum(confirmed.filtered(
                lambda txn: txn.type == "return").mapped("amount"))
            fund.total_topups = topups
            fund.total_expenses = expenses
            fund.balance = (fund.float_amount or 0.0) + topups + returns \
                - expenses
            fund.transaction_count = len(fund.transaction_ids)

    def _check_difference(self, reconciliation):
        self.ensure_one()
        if not self.currency_id.is_zero(reconciliation.difference) \
                and not (reconciliation.note or "").strip():
            raise UserError(_(
                "The reconciliation shows a difference of %(difference).2f. "
                "Explain it in the reconciliation note before closing the "
                "fund.", difference=reconciliation.difference))

    def _close_from(self, reconciliation):
        self.ensure_one()
        if self.state == "closed":
            raise UserError(_("This fund is already closed."))
        if reconciliation.state != "validated":
            raise UserError(_(
                "Validate the reconciliation before closing the fund."))
        self._check_difference(reconciliation)
        self.write({
            "state": "closed",
            "closed_date": fields.Date.context_today(self),
        })
        self.message_post(body=_(
            "Fund closed. Counted cash: %(counted).2f, difference: "
            "%(difference).2f.",
            counted=reconciliation.counted_cash,
            difference=reconciliation.difference))
        return True

    def action_close(self):
        for fund in self:
            if fund.state == "closed":
                raise UserError(_("This fund is already closed."))
            reconciliations = self.env["petty.cash.reconciliation"].search([
                ("fund_id", "=", fund.id),
                ("state", "=", "validated"),
            ])
            if not reconciliations:
                raise UserError(_(
                    "Validate a reconciliation before closing the fund."))
            reconciliation = reconciliations.sorted(
                lambda rec: (rec.date or fields.Date.context_today(fund),
                             rec.id))[-1]
            fund._close_from(reconciliation)
        return True

    def action_reopen(self):
        for fund in self:
            if fund.state != "closed":
                raise UserError(_("Only a closed fund can be reopened."))
            fund.write({"state": "open", "closed_date": False})
            fund.message_post(body=_("Fund reopened."))
        return True

    def action_new_transaction(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Petty Cash Transaction"),
            "res_model": "petty.cash.transaction",
            "view_mode": "form",
            "target": "current",
            "context": {"default_fund_id": self.id},
        }

    def action_new_reconciliation(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Petty Cash Reconciliation"),
            "res_model": "petty.cash.reconciliation",
            "view_mode": "form",
            "target": "current",
            "context": {"default_fund_id": self.id},
        }


class PettyCashTransaction(models.Model):
    _name = "petty.cash.transaction"
    _description = "Petty Cash Transaction"
    _order = "date desc, id desc"

    fund_id = fields.Many2one(
        "petty.cash.fund", string="Fund", required=True,
        ondelete="cascade", index=True, domain=[("state", "=", "open")])
    date = fields.Date(
        default=fields.Date.context_today, required=True)
    type = fields.Selection(
        [("top_up", "Top-Up"), ("expense", "Expense"),
         ("return", "Return")],
        default="expense", required=True)
    name = fields.Char(string="Description", required=True)
    amount = fields.Monetary(
        currency_field="currency_id", required=True)
    category = fields.Selection(
        [("office", "Office"), ("travel", "Travel"),
         ("supplies", "Supplies"), ("meals", "Meals"),
         ("other", "Other")],
        default="other", required=True)
    partner_id = fields.Many2one("res.partner", string="Partner")
    receipt = fields.Binary(string="Receipt", attachment=True)
    note = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"),
         ("cancelled", "Cancelled")],
        default="draft", required=True, index=True)
    confirmed_by = fields.Many2one(
        "res.users", string="Confirmed By", readonly=True)
    confirmed_date = fields.Datetime(string="Confirmed On", readonly=True)
    currency_id = fields.Many2one(
        related="fund_id.currency_id", store=True, readonly=True)

    @api.constrains("amount")
    def _check_amount(self):
        for transaction in self:
            if transaction.amount <= 0:
                raise ValidationError(_(
                    "The transaction amount must be greater than zero."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            fund = self.env["petty.cash.fund"].browse(vals.get("fund_id"))
            if fund and fund.state == "closed":
                raise UserError(_(
                    "This fund is closed. Reopen it before adding "
                    "transactions."))
        return super().create(vals_list)

    def action_confirm(self):
        for transaction in self:
            if transaction.state != "draft":
                raise UserError(_(
                    "Only a draft transaction can be confirmed."))
            if transaction.fund_id.state != "open":
                raise UserError(_(
                    "This fund is closed. Reopen it before confirming "
                    "transactions."))
            transaction.write({
                "state": "confirmed",
                "confirmed_by": self.env.user.id,
                "confirmed_date": fields.Datetime.now(),
            })
        return True

    def action_cancel(self):
        for transaction in self:
            if transaction.state == "cancelled":
                raise UserError(_(
                    "This transaction is already cancelled."))
            if transaction.fund_id.state != "open":
                raise UserError(_(
                    "This fund is closed. Reopen it before cancelling "
                    "transactions."))
            transaction.write({
                "state": "cancelled",
                "confirmed_by": False,
                "confirmed_date": False,
            })
        return True

    def action_reset(self):
        for transaction in self:
            if transaction.state == "draft":
                raise UserError(_(
                    "This transaction is already in draft."))
            if transaction.fund_id.state != "open":
                raise UserError(_(
                    "This fund is closed. Reopen it before resetting "
                    "transactions."))
            transaction.write({
                "state": "draft",
                "confirmed_by": False,
                "confirmed_date": False,
            })
        return True


class PettyCashReconciliation(models.Model):
    _name = "petty.cash.reconciliation"
    _description = "Petty Cash Reconciliation"
    _order = "date desc, id desc"

    fund_id = fields.Many2one(
        "petty.cash.fund", string="Fund", required=True,
        ondelete="cascade", index=True)
    date = fields.Date(
        default=fields.Date.context_today, required=True)
    theoretical_balance = fields.Monetary(
        string="Theoretical Balance", currency_field="currency_id")
    counted_cash = fields.Monetary(
        string="Counted Cash", currency_field="currency_id", required=True)
    difference = fields.Monetary(
        string="Difference", currency_field="currency_id",
        compute="_compute_difference", store=True)
    state = fields.Selection(
        [("draft", "Draft"), ("validated", "Validated")],
        default="draft", required=True, index=True)
    validated_by = fields.Many2one(
        "res.users", string="Validated By", readonly=True)
    validated_date = fields.Datetime(string="Validated On", readonly=True)
    close_fund = fields.Boolean(string="Close the fund after validation")
    note = fields.Text()
    currency_id = fields.Many2one(
        related="fund_id.currency_id", store=True, readonly=True)

    @api.depends("counted_cash", "theoretical_balance")
    def _compute_difference(self):
        for reconciliation in self:
            reconciliation.difference = \
                (reconciliation.counted_cash or 0.0) \
                - (reconciliation.theoretical_balance or 0.0)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            fund = self.env["petty.cash.fund"].browse(vals.get("fund_id"))
            if fund and fund.state == "closed":
                raise UserError(_(
                    "This fund is closed. Reopen it before reconciling."))
            if fund and not vals.get("theoretical_balance"):
                vals["theoretical_balance"] = fund.balance
        return super().create(vals_list)

    def action_validate(self):
        for reconciliation in self:
            if reconciliation.state == "validated":
                raise UserError(_(
                    "This reconciliation is already validated."))
            if reconciliation.fund_id.state == "closed":
                raise UserError(_(
                    "This fund is closed. Reopen it before validating a "
                    "reconciliation."))
            if reconciliation.close_fund:
                reconciliation.fund_id._check_difference(reconciliation)
            reconciliation.write({
                "state": "validated",
                "validated_by": self.env.user.id,
                "validated_date": fields.Datetime.now(),
            })
            if reconciliation.close_fund:
                reconciliation.fund_id._close_from(reconciliation)
        return True
