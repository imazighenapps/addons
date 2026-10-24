# -*- coding: utf-8 -*-
import secrets

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class GiftCard(models.Model):
    _name = "gift.card"
    _description = "Gift Card"
    _inherit = ["mail.thread"]
    _order = "create_date desc, id desc"

    name = fields.Char(
        string="Card Code", required=True, copy=False, index=True,
        default=lambda self: self._generate_code())
    partner_id = fields.Many2one("res.partner", string="Customer")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True)
    initial_amount = fields.Monetary(
        currency_field="currency_id", tracking=True)
    balance = fields.Monetary(
        currency_field="currency_id", tracking=True)
    expiry_date = fields.Date(tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("used", "Used"),
         ("expired", "Expired"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    transaction_ids = fields.One2many(
        "gift.transaction", "card_id", string="Transactions")
    transaction_count = fields.Integer(compute="_compute_transaction_count")
    note = fields.Text()

    @api.model
    def _generate_code(self):
        for _attempt in range(20):
            code = "GC-%s-%s" % (
                secrets.token_hex(2).upper(), secrets.token_hex(2).upper())
            if not self.search_count([("name", "=", code)]):
                return code
        return "GC-%s" % secrets.token_hex(6).upper()

    @api.depends("transaction_ids")
    def _compute_transaction_count(self):
        for card in self:
            card.transaction_count = len(card.transaction_ids)

    @api.constrains("initial_amount")
    def _check_amount(self):
        for card in self:
            if card.initial_amount < 0:
                raise ValidationError(_("The amount cannot be negative."))

    @api.model_create_multi
    def create(self, vals_list):
        cards = super().create(vals_list)
        for card in cards:
            if card.initial_amount and not card.transaction_ids:
                card.balance = card.initial_amount
                card.state = "active"
                self.env["gift.transaction"].create({
                    "card_id": card.id,
                    "type": "issue",
                    "amount": card.initial_amount,
                    "reference": _("Initial issue"),
                })
        return cards

    def _check_usable(self, amount):
        self.ensure_one()
        if self.state in ("cancelled", "expired"):
            raise UserError(_("This card is not usable."))
        if self.state == "used":
            raise UserError(_("This card has no balance left."))
        if self.expiry_date and self.expiry_date < fields.Date.context_today(self):
            self.state = "expired"
            raise UserError(_("This card has expired."))
        if amount <= 0:
            raise UserError(_("The amount must be greater than zero."))
        if amount > self.balance:
            raise UserError(_(
                "The amount exceeds the available balance (%s).") % self.balance)

    def redeem(self, amount, reference=None):
        for card in self:
            card._check_usable(amount)
            card.balance -= amount
            card.state = "used" if card.balance <= 0.0 else "active"
            self.env["gift.transaction"].create({
                "card_id": card.id,
                "type": "redeem",
                "amount": -amount,
                "reference": reference or _("Redemption"),
            })
            card.message_post(body=_(
                "%(amount).2f redeemed. New balance: %(balance).2f.",
                amount=amount, balance=card.balance))
        return True

    def reload(self, amount, reference=None):
        for card in self:
            if card.state == "cancelled":
                raise UserError(_("A cancelled card cannot be reloaded."))
            if amount <= 0:
                raise UserError(_("The amount must be greater than zero."))
            card.balance += amount
            card.state = "active"
            self.env["gift.transaction"].create({
                "card_id": card.id,
                "type": "reload",
                "amount": amount,
                "reference": reference or _("Reload"),
            })
        return True

    def action_activate(self):
        for card in self:
            if card.state == "draft":
                card.balance = card.initial_amount
                card.state = "active" if card.balance else "draft"

    def action_cancel(self):
        self.write({"state": "cancelled"})

    @api.model
    def _cron_expire(self):
        today = fields.Date.context_today(self)
        cards = self.search([
            ("state", "in", ["active", "draft"]),
            ("expiry_date", "!=", False),
            ("expiry_date", "<", today),
        ])
        cards.write({"state": "expired"})
        return True


class GiftTransaction(models.Model):
    _name = "gift.transaction"
    _description = "Gift Card Transaction"
    _order = "date desc, id desc"

    card_id = fields.Many2one(
        "gift.card", required=True, ondelete="cascade", index=True)
    date = fields.Datetime(default=fields.Datetime.now, required=True)
    type = fields.Selection(
        [("issue", "Issue"), ("redeem", "Redemption"),
         ("reload", "Reload"), ("refund", "Refund")],
        required=True, default="issue")
    amount = fields.Monetary(currency_field="currency_id")
    reference = fields.Char()
    user_id = fields.Many2one(
        "res.users", default=lambda self: self.env.user, readonly=True)
    currency_id = fields.Many2one(
        related="card_id.currency_id", store=True, readonly=True)


class GiftRedeemWizard(models.TransientModel):
    _name = "gift.redeem.wizard"
    _description = "Redeem Gift Card"

    card_id = fields.Many2one(
        "gift.card", string="Card", required=True,
        domain=[("state", "in", ["active", "draft"])])
    amount = fields.Monetary(currency_field="currency_id", required=True)
    currency_id = fields.Many2one(
        related="card_id.currency_id", readonly=True)
    reference = fields.Char()
    available = fields.Monetary(
        related="card_id.balance", string="Available Balance",
        currency_field="currency_id", readonly=True)

    def action_redeem(self):
        self.ensure_one()
        self.card_id.redeem(self.amount, self.reference)
        return {"type": "ir.actions.act_window_close"}
