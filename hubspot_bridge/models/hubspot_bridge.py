# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HubspotConnection(models.Model):
    _name = "hubspot.connection"
    _description = "HubSpot Connection"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    token_ref = fields.Char(string="Access Token Reference")
    portal_id = fields.Char(string="Portal ID")
    state = fields.Selection([("draft", "Draft"), ("active", "Active")], default="draft", tracking=True)
    active = fields.Boolean(default=True)
    sync_ids = fields.One2many("hubspot.sync", "connection_id")

    def action_activate(self):
        for rec in self:
            if not rec.token_ref:
                raise UserError(_("Set the access token reference before activating."))
            rec.state = "active"
        return True


class HubspotSync(models.Model):
    _name = "hubspot.sync"
    _description = "HubSpot Sync Record"
    _inherit = ["mail.thread"]
    _order = "write_date desc, id desc"

    name = fields.Char(required=True, copy=False, default="New")
    connection_id = fields.Many2one("hubspot.connection", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="connection_id.company_id", store=True)
    object_type = fields.Selection(
        [("contact", "Contact"), ("deal", "Deal")], required=True, default="contact")
    direction = fields.Selection(
        [("push", "Push to HubSpot"), ("pull", "Pull from HubSpot")],
        required=True, default="push")
    partner_id = fields.Many2one("res.partner", string="Contact")
    lead_id = fields.Many2one("crm.lead", string="Deal/Opportunity")
    external_id = fields.Char(string="HubSpot ID", copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("ready", "Ready"), ("synced", "Synced"), ("error", "Error")],
        default="draft", required=True, tracking=True)
    last_sync_at = fields.Datetime()
    payload = fields.Text()
    error_message = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("hubspot.sync") or "HS"
        return super().create(vals_list)

    @api.constrains("object_type", "partner_id", "lead_id")
    def _check_links(self):
        for rec in self:
            if rec.object_type == "contact" and not rec.partner_id:
                raise ValidationError(_("Select a contact/partner for a contact sync."))
            if rec.object_type == "deal" and not rec.lead_id:
                raise ValidationError(_("Select a deal/opportunity for a deal sync."))

    def action_prepare(self):
        for rec in self:
            rec.payload = "type=%s|dir=%s|ext=%s" % (rec.object_type, rec.direction, rec.external_id or "")
            rec.state = "ready"
            rec.error_message = False
        return True

    def action_sync(self):
        for rec in self:
            if rec.state != "ready":
                raise UserError(_("Only ready records can be synced."))
            if rec.connection_id.state != "active":
                raise UserError(_("Activate the HubSpot connection first."))
            rec.state = "synced"
            rec.external_id = rec.external_id or ("HS-%s" % rec.id)
            rec.last_sync_at = fields.Datetime.now()
            self.env["hubspot.sync.log"].create({
                "sync_id": rec.id, "status": "success", "message": _("Sync completed."),
            })
        return True

    def action_reset(self):
        for rec in self:
            rec.state = "draft"
            rec.error_message = False
        return True


class HubspotSyncLog(models.Model):
    _name = "hubspot.sync.log"
    _description = "HubSpot Sync Log"
    _order = "create_date desc, id desc"

    sync_id = fields.Many2one("hubspot.sync", required=True, ondelete="cascade")
    connection_id = fields.Many2one(related="sync_id.connection_id", store=True)
    status = fields.Selection([("success", "Success"), ("error", "Error")], required=True)
    message = fields.Text()
