# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class DhlExpressShipConnection(models.Model):
    _name = "dhl_express.connection"
    _description = "DHL Express Shipping Connection"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company, index=True)
    active = fields.Boolean(default=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("active", "Active"),
        ("archived", "Archived"),
    ], default="draft", tracking=True, required=True)
    api_key = fields.Char(string="API Key / Token")
    endpoint = fields.Char(string="Endpoint / URL")
    note = fields.Text()
    record_ids = fields.One2many("dhl_express.record", "connection_id", string="Records")
    log_ids = fields.One2many("dhl_express.log", "connection_id", string="Logs")

    @api.constrains("endpoint")
    def _check_endpoint(self):
        for rec in self:
            if rec.endpoint and not rec.endpoint.startswith(("http://", "https://")):
                raise ValidationError(_("Endpoint must start with http:// or https://."))

    def action_activate(self):
        for rec in self:
            if not rec.api_key:
                raise UserError(_("Please set an API key/token before activating."))
            rec.state = "active"
            rec.message_post(body=_("Connection activated."))
        return True

    def action_archive_state(self):
        self.write({"state": "archived"})
        return True

    def action_reset(self):
        self.write({"state": "draft"})
        return True


class DhlExpressShipRecord(models.Model):
    _name = "dhl_express.record"
    _description = "DHL Express Shipping Record"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, tracking=True, default="New")
    connection_id = fields.Many2one("dhl_express.connection", required=True, ondelete="cascade", tracking=True)
    company_id = fields.Many2one(related="connection_id.company_id", store=True, readonly=True)
    external_ref = fields.Char(string="External Reference", tracking=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("ready", "Ready"),
        ("done", "Done"),
        ("error", "Error"),
    ], default="draft", tracking=True, required=True)
    payload = fields.Text(string="Payload / Notes")
    processed_at = fields.Datetime(readonly=True)
    log_ids = fields.One2many("dhl_express.log", "record_id", string="Logs")

    def action_prepare(self):
        for rec in self:
            if rec.connection_id.state != "active":
                raise UserError(_("Connection must be active before processing."))
            rec.state = "ready"
        return True

    def action_run(self):
        for rec in self:
            if rec.state not in ("ready", "error"):
                raise UserError(_("Record must be ready before running."))
            rec.state = "done"
            rec.processed_at = fields.Datetime.now()
            self.env["dhl_express.log"].create({
                "connection_id": rec.connection_id.id,
                "record_id": rec.id,
                "level": "info",
                "message": _("Record processed successfully."),
            })
        return True

    def action_reset(self):
        for rec in self:
            if rec.state == "done":
                raise UserError(_("Done records cannot be reset."))
            rec.state = "draft"
        return True

    def action_mark_error(self):
        self.write({"state": "error"})
        return True


class DhlExpressShipLog(models.Model):
    _name = "dhl_express.log"
    _description = "DHL Express Shipping Log"
    _order = "create_date desc, id desc"

    connection_id = fields.Many2one("dhl_express.connection", required=True, ondelete="cascade", index=True)
    record_id = fields.Many2one("dhl_express.record", ondelete="set null")
    level = fields.Selection([
        ("info", "Info"),
        ("warning", "Warning"),
        ("error", "Error"),
    ], default="info", required=True)
    message = fields.Text(required=True)


class res_company(models.Model):
    _inherit = "res.company"
