# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class QontoConnection(models.Model):
    _name = "qonto.connection"
    _description = "Qonto Connection"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)
    organization_slug = fields.Char(required=True, default="demo-org")
    iban = fields.Char(string="IBAN")
    token_ref = fields.Char(string="API Token Reference")
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active")], default="draft", tracking=True)
    active = fields.Boolean(default=True)
    last_sync_at = fields.Datetime(readonly=True)
    transaction_ids = fields.One2many("qonto.transaction", "connection_id")

    def action_activate(self):
        for rec in self:
            if not rec.token_ref:
                raise UserError(_("Set the API token reference before activating."))
            rec.state = "active"
            rec.message_post(body=_("Qonto connection activated."))
        return True

    def action_sync(self):
        for rec in self:
            if rec.state != "active":
                raise UserError(_("Activate the connection before syncing."))
            rec.last_sync_at = fields.Datetime.now()
            self.env["qonto.sync.log"].create({
                "connection_id": rec.id, "status": "success",
                "message": _("Sync completed (no external fetch in this environment)."),
            })
            rec.message_post(body=_("Sync executed."))
        return True


class QontoTransaction(models.Model):
    _name = "qonto.transaction"
    _description = "Qonto Transaction"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"

    name = fields.Char(required=True, copy=False, default="New")
    connection_id = fields.Many2one(
        "qonto.connection", required=True, ondelete="cascade", tracking=True)
    company_id = fields.Many2one(related="connection_id.company_id", store=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    label = fields.Char(required=True)
    counterpart = fields.Char(string="Counterparty")
    amount = fields.Monetary(currency_field="currency_id", required=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id,
        required=True)
    direction = fields.Selection(
        [("in", "Incoming"), ("out", "Outgoing")], required=True, default="out")
    external_id = fields.Char(string="Qonto ID", copy=False)
    attachment_ref = fields.Char(string="Attachment Reference")
    move_id = fields.Many2one("account.move", string="Matched Entry")
    state = fields.Selection(
        [("new", "New"), ("matched", "Matched"), ("ignored", "Ignored")],
        default="new", required=True, tracking=True)
    note = fields.Text()

    _ext_uniq = models.Constraint(
        "UNIQUE(connection_id, external_id)",
        "The Qonto transaction ID must be unique per connection.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "qonto.transaction") or "QTO"
        return super().create(vals_list)

    @api.constrains("amount")
    def _check_amount(self):
        for rec in self:
            if rec.amount == 0:
                raise ValidationError(_("The transaction amount cannot be zero."))

    def action_match(self):
        for rec in self:
            if rec.state == "ignored":
                raise UserError(_("Ignored transactions cannot be matched."))
            rec.state = "matched"
            rec.message_post(body=_("Transaction matched."))
        return True

    def action_ignore(self):
        for rec in self:
            if rec.state == "matched":
                raise UserError(_("Matched transactions cannot be ignored."))
            rec.state = "ignored"
        return True

    def action_reset(self):
        for rec in self:
            rec.state = "new"
            rec.move_id = False
        return True


class QontoSyncLog(models.Model):
    _name = "qonto.sync.log"
    _description = "Qonto Sync Log"
    _order = "create_date desc, id desc"

    connection_id = fields.Many2one(
        "qonto.connection", required=True, ondelete="cascade")
    status = fields.Selection([("success", "Success"), ("error", "Error")], required=True)
    message = fields.Text()
    company_id = fields.Many2one(related="connection_id.company_id", store=True)
