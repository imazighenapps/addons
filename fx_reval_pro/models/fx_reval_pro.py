# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class FxRevaluation(models.Model):
    _name = "fx.revaluation"
    _description = "Currency Revaluation"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"

    name = fields.Char(
        required=True, copy=False, default="/", tracking=True,
        help="Reference of the revaluation, taken from the FXR/ sequence.")
    date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True,
        help="Date of the revaluation, used as the date of the journal "
             "entry.")
    currency_id = fields.Many2one(
        "res.currency", string="Foreign Currency", required=True,
        tracking=True,
        help="Currency of the open items that are revalued.")
    company_currency_id = fields.Many2one(
        related="company_id.currency_id", string="Company Currency",
        store=True, readonly=True)
    rate = fields.Float(
        string="Closing Rate", digits=(12, 6), required=True, default=1.0,
        tracking=True,
        help="Closing rate: one unit of the foreign currency is worth this "
             "amount of company currency.")
    journal_id = fields.Many2one(
        "account.journal", string="Journal", tracking=True,
        help="Miscellaneous journal that receives the revaluation entry.")
    gain_account_id = fields.Many2one(
        "account.account", string="Gain Account", tracking=True,
        help="Income account that receives the unrealized exchange gains.")
    loss_account_id = fields.Many2one(
        "account.account", string="Loss Account", tracking=True,
        help="Expense account that receives the unrealized exchange "
             "losses.")
    state = fields.Selection(
        [("draft", "Draft"), ("posted", "Posted")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    line_ids = fields.One2many(
        "fx.revaluation.line", "revaluation_id", string="Open Items",
        copy=False)
    total_gain = fields.Monetary(
        string="Total Gain", currency_field="company_currency_id",
        compute="_compute_totals", store=True)
    total_loss = fields.Monetary(
        string="Total Loss", currency_field="company_currency_id",
        compute="_compute_totals", store=True)
    net_gain_loss = fields.Monetary(
        string="Net Unrealized Result", currency_field="company_currency_id",
        compute="_compute_totals", store=True,
        help="Total gain minus total loss: positive is a net gain, negative "
             "a net loss.")
    move_id = fields.Many2one(
        "account.move", string="Journal Entry", readonly=True, copy=False)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)

    _sql_constraints = [
        ('name_company_uniq', "UNIQUE(name, company_id)", "The revaluation reference must be unique per company."),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "fx.revaluation") or "/"
        return super().create(vals_list)

    def write(self, vals):
        locked = {"rate", "currency_id", "date", "journal_id",
                  "gain_account_id", "loss_account_id", "company_id"}
        if locked & set(vals):
            posted = self.filtered(lambda reval: reval.state == "posted")
            if posted:
                raise UserError(_(
                    "The posted revaluation \"%s\" can no longer be changed. "
                    "Reset it to draft first.", posted[0].name))
        return super().write(vals)

    @api.constrains("rate")
    def _check_rate(self):
        for reval in self:
            if reval.rate <= 0:
                raise ValidationError(_(
                    "The closing rate must be strictly positive: one unit of "
                    "the foreign currency must be worth a positive amount of "
                    "company currency."))

    @api.constrains("currency_id", "company_id")
    def _check_currency(self):
        for reval in self:
            if reval.currency_id and reval.company_id \
                    and reval.currency_id == reval.company_id.currency_id:
                raise ValidationError(_(
                    "The foreign currency must be different from the company "
                    "currency."))

    @api.depends("line_ids.gain_loss")
    def _compute_totals(self):
        for reval in self:
            gains = sum(
                line.gain_loss for line in reval.line_ids
                if line.gain_loss > 0)
            losses = -sum(
                line.gain_loss for line in reval.line_ids
                if line.gain_loss < 0)
            reval.total_gain = gains
            reval.total_loss = losses
            reval.net_gain_loss = gains - losses

    def _get_counterpart_account(self, line):
        """Return the balance sheet account that carries the adjustment."""
        self.ensure_one()
        partner = line.partner_id
        if line.balance_company > 0 and partner \
                and partner.property_account_receivable_id:
            return partner.property_account_receivable_id
        if line.balance_company < 0 and partner \
                and partner.property_account_payable_id:
            return partner.property_account_payable_id
        return self.journal_id.default_account_id

    def action_compute(self):
        for reval in self:
            if reval.state != "draft":
                raise UserError(_(
                    "The revaluation \"%s\" is posted: reset it to draft "
                    "before computing it again.", reval.name))
            reval.line_ids.unlink()
            move_lines = self.env["account.move.line"].search([
                ("parent_state", "=", "posted"),
                ("account_id.account_type", "in",
                 ["asset_receivable", "liability_payable"]),
                ("currency_id", "=", reval.currency_id.id),
                ("amount_residual_currency", "!=", 0.0),
                ("company_id", "=", reval.company_id.id),
            ], order="partner_id, date, id")
            vals_list = []
            for move_line in move_lines:
                vals_list.append({
                    "revaluation_id": reval.id,
                    "partner_id": move_line.partner_id.id,
                    "reference": move_line.move_id.name or move_line.name,
                    "amount_currency": move_line.amount_residual_currency,
                    "balance_company": move_line.amount_residual,
                })
            if vals_list:
                self.env["fx.revaluation.line"].create(vals_list)
            reval.message_post(body=_(
                "Revaluation computed: %(count)s open item(s) in "
                "%(currency)s at the closing rate of %(rate)s.",
                count=len(vals_list),
                currency=reval.currency_id.name,
                rate=reval.rate))
        return True

    def action_post(self):
        for reval in self:
            if reval.state != "draft":
                raise UserError(_(
                    "Only a draft revaluation can be posted."))
            if not reval.line_ids:
                raise UserError(_(
                    "Compute the revaluation before posting it: no open item "
                    "has been collected yet."))
            if not reval.journal_id:
                raise UserError(_(
                    "Select the journal that receives the revaluation entry "
                    "before posting."))
            if not reval.gain_account_id or not reval.loss_account_id:
                raise UserError(_(
                    "Set both the gain account and the loss account before "
                    "posting the revaluation."))
            move_lines = []
            for line in reval.line_ids:
                if reval.company_currency_id.is_zero(line.gain_loss):
                    continue
                account = reval._get_counterpart_account(line)
                if not account:
                    raise UserError(_(
                        "No receivable or payable account is set for the "
                        "partner \"%s\", and the journal \"%s\" has no "
                        "default account. Set one of them before posting.",
                        line.partner_id.display_name or _("Unknown"),
                        reval.journal_id.display_name))
                amount = abs(line.gain_loss)
                if line.gain_loss > 0:
                    debit_account = account
                    credit_account = reval.gain_account_id
                else:
                    debit_account = reval.loss_account_id
                    credit_account = account
                label = _(
                    "FX revaluation %(ref)s at %(rate)s",
                    ref=line.reference or reval.name, rate=reval.rate)
                move_lines.append((0, 0, {
                    "account_id": debit_account.id,
                    "partner_id": line.partner_id.id,
                    "name": label,
                    "debit": amount,
                    "credit": 0.0,
                }))
                move_lines.append((0, 0, {
                    "account_id": credit_account.id,
                    "partner_id": line.partner_id.id,
                    "name": label,
                    "debit": 0.0,
                    "credit": amount,
                }))
            if not move_lines:
                raise UserError(_(
                    "Every line of the revaluation is zero: there is nothing "
                    "to post."))
            move = self.env["account.move"].create({
                "move_type": "entry",
                "journal_id": reval.journal_id.id,
                "date": reval.date,
                "ref": _("FX revaluation %s", reval.name),
                "line_ids": move_lines,
            })
            move.action_post()
            reval.write({"state": "posted", "move_id": move.id})
            reval.message_post(body=_(
                "Revaluation posted on the journal entry %(move)s with a net "
                "unrealized result of %(net)s.",
                move=move.name, net=reval.net_gain_loss))
        return True

    def action_reset(self):
        for reval in self:
            if reval.state != "posted":
                raise UserError(_(
                    "Only a posted revaluation can be reset to draft."))
            move = reval.move_id
            if move:
                if move.state == "posted":
                    move.button_draft()
                try:
                    move.unlink()
                except UserError:
                    # An entry that has already been posted once may have to
                    # stay for the audit trail: cancel it instead.
                    move.button_cancel()
            reval.write({"state": "draft", "move_id": False})
            reval.message_post(body=_(
                "Revaluation reset to draft: its journal entry was removed "
                "or cancelled."))
        return True


class FxRevaluationLine(models.Model):
    _name = "fx.revaluation.line"
    _description = "Currency Revaluation Line"
    _order = "revaluation_id, partner_id, id"

    revaluation_id = fields.Many2one(
        "fx.revaluation", string="Revaluation", required=True,
        ondelete="cascade", index=True)
    partner_id = fields.Many2one("res.partner", string="Partner", index=True)
    reference = fields.Char(
        help="Number of the journal entry the open item comes from.")
    amount_currency = fields.Monetary(
        string="Balance in Currency", currency_field="currency_id",
        help="Open amount still due, expressed in the foreign currency.")
    balance_company = fields.Monetary(
        string="Book Value", currency_field="company_currency_id",
        help="Open amount as it is currently booked in the company "
             "currency.")
    new_balance = fields.Monetary(
        string="Revalued Balance", currency_field="company_currency_id",
        compute="_compute_gain_loss", store=True,
        help="Open amount converted at the closing rate of the "
             "revaluation.")
    gain_loss = fields.Monetary(
        string="Unrealized Gain/Loss", currency_field="company_currency_id",
        compute="_compute_gain_loss", store=True,
        help="Revalued balance minus book value: positive is an unrealized "
             "gain, negative an unrealized loss.")
    currency_id = fields.Many2one(
        related="revaluation_id.currency_id", store=True, readonly=True)
    company_currency_id = fields.Many2one(
        related="revaluation_id.company_currency_id", store=True,
        readonly=True)
    company_id = fields.Many2one(
        related="revaluation_id.company_id", store=True, readonly=True)

    @api.depends("amount_currency", "balance_company", "revaluation_id.rate")
    def _compute_gain_loss(self):
        for line in self:
            rate = line.revaluation_id.rate or 0.0
            line.new_balance = line.amount_currency * rate
            line.gain_loss = line.new_balance - line.balance_company
