# -*- coding: utf-8 -*-
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class RenewalContract(models.Model):
    _name = "renewal.contract"
    _description = "Renewal Contract"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "end_date, id"

    name = fields.Char(default="/", required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True,
        tracking=True, index=True)
    contract_type = fields.Selection(
        [("service", "Service"), ("subscription", "Subscription"),
         ("license", "License"), ("maintenance", "Maintenance"),
         ("lease", "Lease")],
        default="service", required=True, tracking=True)
    owner_id = fields.Many2one(
        "res.users", string="Owner", tracking=True,
        default=lambda self: self.env.user)
    start_date = fields.Date(
        required=True, tracking=True, default=fields.Date.context_today)
    end_date = fields.Date(required=True, tracking=True, index=True)
    notice_days = fields.Integer(
        string="Notice Period (days)", default=30, required=True,
        help="Number of days before the end date when the renewal "
             "process starts.")
    term_months = fields.Integer(
        string="Term (months)", default=12, required=True)
    amount = fields.Monetary(currency_field="currency_id", tracking=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)
    auto_renew = fields.Boolean(string="Automatic Renewal")
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"),
         ("to_renew", "To Renew"), ("renewed", "Renewed"),
         ("churned", "Churned"), ("expired", "Expired")],
        default="draft", required=True, tracking=True, index=True)
    renewal_date = fields.Date(
        string="Renewal Date", compute="_compute_renewal_date",
        store=True, readonly=True,
        help="End date minus the notice period.")
    days_left = fields.Integer(
        compute="_compute_days_left", search="_search_days_left")
    is_expiring = fields.Boolean(
        string="Expiring", compute="_compute_days_left",
        search="_search_is_expiring")
    churn_reason = fields.Text(tracking=True)
    last_renewal_date = fields.Date(readonly=True)
    renewal_count = fields.Integer(default=0, readonly=True)
    log_ids = fields.One2many(
        "renewal.log", "contract_id", string="Renewal History")
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    active = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "renewal.contract") or "/"
        return super().create(vals_list)

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        for contract in self:
            if contract.start_date and contract.end_date \
                    and contract.end_date < contract.start_date:
                raise ValidationError(_(
                    "The end date must be on or after the start date."))

    @api.constrains("term_months")
    def _check_term(self):
        for contract in self:
            if contract.term_months <= 0:
                raise ValidationError(_(
                    "The term must be at least one month."))

    @api.constrains("notice_days")
    def _check_notice(self):
        for contract in self:
            if contract.notice_days < 0:
                raise ValidationError(_(
                    "The notice period cannot be negative."))

    @api.depends("end_date", "notice_days")
    def _compute_renewal_date(self):
        for contract in self:
            if contract.end_date:
                contract.renewal_date = contract.end_date - timedelta(
                    days=contract.notice_days or 0)
            else:
                contract.renewal_date = False

    @api.depends("end_date", "notice_days", "state")
    def _compute_days_left(self):
        today = fields.Date.context_today(self)
        for contract in self:
            contract.days_left = (
                (contract.end_date - today).days if contract.end_date else 0)
            contract.is_expiring = bool(
                contract.state in ("active", "to_renew")
                and contract.end_date
                and contract.days_left <= contract.notice_days)

    def _search_days_left(self, operator, value):
        compare = {
            "=": lambda left, right: left == right,
            "!=": lambda left, right: left != right,
            ">": lambda left, right: left > right,
            ">=": lambda left, right: left >= right,
            "<": lambda left, right: left < right,
            "<=": lambda left, right: left <= right,
        }.get(operator)
        if not compare:
            return []
        ids = [contract.id for contract in self.search([])
               if compare(contract.days_left, value)]
        return [("id", "in", ids)]

    def _search_is_expiring(self, operator, value):
        positive = (operator == "=" and bool(value)) \
            or (operator == "!=" and not value)
        ids = [contract.id for contract in self.search([])
               if contract.is_expiring == positive]
        return [("id", "in", ids)]

    def _log(self, action, note=None):
        self.ensure_one()
        self.env["renewal.log"].create({
            "contract_id": self.id,
            "action": action,
            "note": note,
        })

    def action_activate(self):
        for contract in self:
            if contract.state != "draft":
                raise UserError(_("Only a draft contract can be activated."))
            contract.write({"state": "active"})
            contract._log("activated", _("Contract activated."))
        return True

    def action_mark_to_renew(self):
        for contract in self:
            if contract.state != "active":
                raise UserError(_(
                    "Only an active contract can be flagged for renewal."))
            contract.write({"state": "to_renew"})
            contract._log("reminder", _("Renewal notice period started."))
        return True

    def action_renew(self):
        for contract in self:
            if contract.state == "churned":
                raise UserError(_("A churned contract cannot be renewed."))
            if not contract.end_date:
                raise UserError(_(
                    "Set the end date before renewing the contract."))
            if contract.term_months <= 0:
                raise UserError(_("The term must be at least one month."))
            new_end = contract.end_date + relativedelta(
                months=contract.term_months)
            contract.write({
                "end_date": new_end,
                "last_renewal_date": fields.Date.context_today(contract),
                "renewal_count": contract.renewal_count + 1,
                "state": "active",
                "churn_reason": False,
            })
            contract._log(
                "renewed", _("Contract renewed until %s.", new_end))
            contract.message_post(body=_(
                "Contract renewed until %s.", new_end))
        return True

    def action_churn(self):
        for contract in self:
            if not contract.churn_reason:
                raise UserError(_(
                    "Enter the churn reason before churning the contract."))
            contract.write({"state": "churned"})
            contract._log("churned", contract.churn_reason)
        return True

    def action_expire(self):
        for contract in self:
            if contract.state == "churned":
                raise UserError(_(
                    "A churned contract cannot be expired."))
            contract.write({"state": "expired"})
            contract._log("note", _("Contract expired."))
        return True

    def action_reset(self):
        for contract in self:
            contract.write({"state": "draft"})
            contract._log("note", _("Contract reset to draft."))
        return True

    @api.model
    def _cron_mark_to_renew(self):
        today = fields.Date.context_today(self)
        contracts = self.search([
            ("state", "=", "active"),
            ("renewal_date", "<=", today),
        ])
        for contract in contracts:
            contract.write({"state": "to_renew"})
            contract._log("reminder", _(
                "Renewal notice period started on %s.", today))
        return len(contracts)


class RenewalLog(models.Model):
    _name = "renewal.log"
    _description = "Renewal History Line"
    _order = "date desc, id desc"

    contract_id = fields.Many2one(
        "renewal.contract", string="Contract", required=True,
        ondelete="cascade", index=True)
    date = fields.Date(
        default=fields.Date.context_today, required=True)
    action = fields.Selection(
        [("activated", "Activated"), ("reminder", "Reminder"),
         ("quote", "Quote Sent"), ("renewed", "Renewed"),
         ("churned", "Churned"), ("note", "Note")],
        default="note", required=True)
    user_id = fields.Many2one(
        "res.users", string="User", default=lambda self: self.env.user)
    note = fields.Text()
