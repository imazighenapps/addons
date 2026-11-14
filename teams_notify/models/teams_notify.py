# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class TeamsChannel(models.Model):
    _name = "teams.channel"
    _description = "Teams Channel Webhook"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    webhook_url = fields.Char(string="Webhook URL", required=True, default="https://example.com/webhook")
    state = fields.Selection([("draft", "Draft"), ("active", "Active")], default="draft", tracking=True)
    active = fields.Boolean(default=True)
    rule_ids = fields.One2many("teams.rule", "channel_id")

    @api.constrains("webhook_url")
    def _check_url(self):
        for rec in self:
            if not rec.webhook_url.startswith(("http://", "https://")):
                raise ValidationError(_("Webhook URL must start with http:// or https://."))

    def action_activate(self):
        for rec in self:
            rec.state = "active"
        return True

    def action_test(self):
        for rec in self:
            if rec.state != "active":
                raise UserError(_("Activate the channel before testing."))
            self.env["teams.notification"].create({
                "channel_id": rec.id, "name": _("Test notification"),
                "event_type": "test", "payload": _("Teams webhook test from Odoo."),
                "state": "sent",
            })
            rec.message_post(body=_("Test notification recorded."))
        return True


class TeamsRule(models.Model):
    _name = "teams.rule"
    _description = "Teams Notification Rule"

    name = fields.Char(required=True)
    channel_id = fields.Many2one("teams.channel", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="channel_id.company_id", store=True)
    model_name = fields.Char(string="Model")
    event_type = fields.Selection(
        [("sale", "Sales"), ("invoice", "Invoicing"), ("stock", "Inventory"),
         ("approval", "Approval"), ("custom", "Custom")],
        default="custom", required=True)
    condition_text = fields.Char(string="Condition", help="Human-readable condition description.")
    active = fields.Boolean(default=True)


class TeamsNotification(models.Model):
    _name = "teams.notification"
    _description = "Teams Notification"
    _order = "create_date desc, id desc"

    name = fields.Char(required=True)
    channel_id = fields.Many2one("teams.channel", required=True, ondelete="cascade")
    rule_id = fields.Many2one("teams.rule", ondelete="set null")
    company_id = fields.Many2one(related="channel_id.company_id", store=True)
    event_type = fields.Char()
    payload = fields.Text(required=True)
    state = fields.Selection([("draft", "Draft"), ("sent", "Sent"), ("error", "Error")],
                             default="draft", required=True)
    error_message = fields.Text()

    def action_send(self):
        for rec in self:
            if rec.channel_id.state != "active":
                raise UserError(_("The Teams channel must be active."))
            rec.state = "sent"
        return True
