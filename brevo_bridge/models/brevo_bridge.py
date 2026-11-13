# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class BrevoConnection(models.Model):
    _name = "brevo.connection"
    _description = "Brevo Connection"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)
    api_key = fields.Char(string="API Key")
    sender_name = fields.Char()
    sender_email = fields.Char()
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active")], default="draft", tracking=True)
    active = fields.Boolean(default=True)
    contact_ids = fields.One2many("brevo.contact.sync", "connection_id")
    list_ids = fields.One2many("brevo.list", "connection_id")

    @api.constrains("sender_email")
    def _check_sender_email(self):
        for rec in self:
            if rec.sender_email and "@" not in rec.sender_email:
                raise ValidationError(_("The sender email must be valid."))

    def action_activate(self):
        for rec in self:
            if not rec.api_key:
                raise UserError(_("Set the API key before activating."))
            rec.state = "active"
            rec.message_post(body=_("Brevo connection activated."))
        return True

    def action_test_connection(self):
        for rec in self:
            if rec.state != "active":
                raise UserError(_("Activate the connection before testing."))
            self.env["brevo.event.log"].create({
                "connection_id": rec.id, "event_type": "system",
                "message": _("Connection settings validated locally."),
            })
            rec.message_post(body=_("Connection test completed."))
        return True


class BrevoList(models.Model):
    _name = "brevo.list"
    _description = "Brevo Audience List"

    name = fields.Char(required=True)
    connection_id = fields.Many2one(
        "brevo.connection", required=True, ondelete="cascade")
    brevo_list_id = fields.Char(string="Brevo List ID")
    contact_count = fields.Integer(compute="_compute_count")
    contact_ids = fields.One2many("brevo.contact.sync", "list_id")
    company_id = fields.Many2one(related="connection_id.company_id", store=True)

    def _compute_count(self):
        for rec in self:
            rec.contact_count = len(rec.contact_ids)


class BrevoContactSync(models.Model):
    _name = "brevo.contact.sync"
    _description = "Brevo Contact Sync"
    _inherit = ["mail.thread"]
    _order = "write_date desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    connection_id = fields.Many2one(
        "brevo.connection", required=True, ondelete="cascade", tracking=True)
    partner_id = fields.Many2one("res.partner", required=True, tracking=True)
    email = fields.Char(related="partner_id.email", store=True, readonly=False)
    list_id = fields.Many2one("brevo.list", string="Audience List")
    brevo_contact_id = fields.Char(string="Brevo Contact ID", copy=False)
    opt_in = fields.Boolean(string="Opt-in", default=True)
    state = fields.Selection(
        [("draft", "Draft"), ("ready", "Ready"), ("synced", "Synced"), ("error", "Error")],
        default="draft", required=True, tracking=True)
    last_sync_at = fields.Datetime()
    error_message = fields.Text()
    company_id = fields.Many2one(related="connection_id.company_id", store=True)

    _sql_constraints = [
        ('partner_uniq', "UNIQUE(connection_id, partner_id)", "This partner is already linked to the connection."),
    ]

    @api.depends("partner_id", "email")
    def _compute_name(self):
        for rec in self:
            rec.name = rec.partner_id.name or rec.email or _("Contact")

    @api.constrains("email")
    def _check_email(self):
        for rec in self:
            if not rec.email or "@" not in rec.email:
                raise ValidationError(_("A valid email is required to sync a contact."))

    def action_prepare(self):
        for rec in self:
            rec.state = "ready"
            rec.error_message = False
        return True

    def action_sync(self):
        for rec in self:
            if rec.state != "ready":
                raise UserError(_("Only ready contacts can be synced."))
            if rec.connection_id.state != "active":
                raise UserError(_("Activate the Brevo connection first."))
            rec.state = "synced"
            rec.brevo_contact_id = rec.brevo_contact_id or ("BRV-%s" % rec.id)
            rec.last_sync_at = fields.Datetime.now()
            self.env["brevo.event.log"].create({
                "connection_id": rec.connection_id.id,
                "contact_sync_id": rec.id,
                "event_type": "synced",
                "message": _("Contact synced."),
            })
        return True

    def action_reset(self):
        for rec in self:
            rec.state = "draft"
            rec.error_message = False
        return True


class BrevoEventLog(models.Model):
    _name = "brevo.event.log"
    _description = "Brevo Event Log"
    _order = "create_date desc, id desc"

    connection_id = fields.Many2one(
        "brevo.connection", required=True, ondelete="cascade", index=True)
    contact_sync_id = fields.Many2one("brevo.contact.sync", ondelete="set null")
    event_type = fields.Selection(
        [("system", "System"), ("synced", "Synced"), ("delivered", "Delivered"),
         ("opened", "Opened"), ("clicked", "Clicked"), ("bounced", "Bounced")],
        required=True, default="system")
    message = fields.Text()
    company_id = fields.Many2one(related="connection_id.company_id", store=True)
