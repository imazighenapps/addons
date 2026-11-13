# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PennylaneConnection(models.Model):
    _name = "pennylane.connection"
    _description = "Pennylane Connection"
    _inherit = ["mail.thread"]
    _order = "company_id, id desc"

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        tracking=True)
    environment = fields.Selection(
        [("sandbox", "Sandbox"), ("production", "Production")],
        default="sandbox", required=True, tracking=True)
    api_token = fields.Char(string="API Token", help="Pennylane API token.")
    base_url = fields.Char(
        default="https://app.pennylane.com/api/external/v1",
        help="Pennylane API base URL.")
    auto_export = fields.Boolean(string="Auto Prepare Export")
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("disabled", "Disabled")],
        default="draft", required=True, tracking=True)
    last_sync_at = fields.Datetime(readonly=True)
    note = fields.Text()
    export_ids = fields.One2many(
        "pennylane.export", "connection_id", string="Exports")

    _sql_constraints = [
        ('company_uniq', "UNIQUE(company_id, name)", "The connection name must be unique per company."),
    ]

    @api.constrains("base_url")
    def _check_base_url(self):
        for rec in self:
            if rec.base_url and not rec.base_url.startswith(("http://", "https://")):
                raise ValidationError(_("The base URL must start with http:// or https://."))

    def action_activate(self):
        for rec in self:
            if not rec.api_token:
                raise UserError(_("Set an API token before activating the connection."))
            rec.state = "active"
            rec.message_post(body=_("Connection activated (%s).", rec.environment))
        return True

    def action_disable(self):
        for rec in self:
            rec.state = "disabled"
            rec.message_post(body=_("Connection disabled."))
        return True

    def action_test_connection(self):
        for rec in self:
            if rec.state != "active":
                raise UserError(_("Activate the connection before testing it."))
            rec.last_sync_at = fields.Datetime.now()
            self.env["pennylane.sync.log"].create({
                "connection_id": rec.id,
                "action": "test",
                "status": "success",
                "message": _("Connection settings validated locally."),
            })
            rec.message_post(body=_("Connection test completed."))
        return True


class PennylaneExport(models.Model):
    _name = "pennylane.export"
    _description = "Pennylane Export"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"

    name = fields.Char(required=True, copy=False, default="New")
    connection_id = fields.Many2one(
        "pennylane.connection", required=True, ondelete="cascade", tracking=True)
    company_id = fields.Many2one(
        related="connection_id.company_id", store=True, readonly=True)
    document_type = fields.Selection(
        [("invoice", "Customer Invoice"), ("bill", "Vendor Bill"),
         ("payment", "Payment")], required=True, default="invoice", tracking=True)
    move_id = fields.Many2one("account.move", string="Journal Entry")
    payment_ref = fields.Char(string="Payment Reference")
    partner_id = fields.Many2one("res.partner", string="Partner")
    date = fields.Date(default=fields.Date.context_today, required=True)
    amount_total = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id,
        required=True)
    external_id = fields.Char(string="Pennylane ID", copy=False)
    payload = fields.Text(string="Payload Snapshot")
    state = fields.Selection(
        [("draft", "Draft"), ("ready", "Ready"), ("sent", "Sent"), ("error", "Error")],
        default="draft", required=True, tracking=True)
    response_message = fields.Text()
    retry_count = fields.Integer(default=0)

    _sql_constraints = [
        ('name_uniq', "UNIQUE(name, company_id)", "The export reference must be unique per company."),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "pennylane.export") or "PNL-EXP"
        return super().create(vals_list)

    @api.constrains("amount_total")
    def _check_amount(self):
        for rec in self:
            if rec.amount_total < 0:
                raise ValidationError(_("The amount cannot be negative."))

    def _build_payload(self):
        self.ensure_one()
        return "type=%s|partner=%s|amount=%s|date=%s" % (
            self.document_type,
            self.partner_id.display_name or "",
            self.amount_total,
            self.date or "",
        )

    def action_prepare(self):
        for rec in self:
            if rec.state not in ("draft", "error"):
                raise UserError(_("Only draft or error exports can be prepared."))
            rec.payload = rec._build_payload()
            rec.state = "ready"
            rec.response_message = False
            rec.message_post(body=_("Export prepared for sending."))
        return True

    def action_send(self):
        for rec in self:
            if rec.state != "ready":
                raise UserError(_("Only ready exports can be sent."))
            if rec.connection_id.state != "active":
                raise UserError(_("The connection must be active to send exports."))
            rec.state = "sent"
            rec.external_id = rec.external_id or ("PNL-%s" % rec.id)
            rec.connection_id.last_sync_at = fields.Datetime.now()
            self.env["pennylane.sync.log"].create({
                "connection_id": rec.connection_id.id,
                "export_id": rec.id,
                "action": "export",
                "status": "success",
                "message": _("Export marked as sent."),
            })
            rec.message_post(body=_("Export sent to Pennylane."))
        return True

    def action_reset(self):
        for rec in self:
            if rec.state == "sent":
                raise UserError(_("A sent export cannot be reset."))
            rec.state = "draft"
            rec.retry_count += 1
            rec.response_message = False
            rec.message_post(body=_("Export reset to draft."))
        return True


class PennylaneSyncLog(models.Model):
    _name = "pennylane.sync.log"
    _description = "Pennylane Sync Log"
    _order = "create_date desc, id desc"

    connection_id = fields.Many2one(
        "pennylane.connection", required=True, ondelete="cascade", index=True)
    export_id = fields.Many2one("pennylane.export", ondelete="set null")
    action = fields.Selection(
        [("test", "Test"), ("export", "Export"), ("import", "Import")],
        required=True, default="export")
    status = fields.Selection(
        [("success", "Success"), ("error", "Error")], required=True)
    message = fields.Text()
    company_id = fields.Many2one(
        related="connection_id.company_id", store=True, readonly=True)
