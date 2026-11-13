# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PipedriveConnection(models.Model):
    _name = "pipedrive.connection"
    _description = "Pipedrive Connection"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    token_ref = fields.Char(string="API Token Reference")
    company_domain = fields.Char(string="Company Domain")
    state = fields.Selection([("draft", "Draft"), ("active", "Active")], default="draft", tracking=True)
    active = fields.Boolean(default=True)

    def action_activate(self):
        for rec in self:
            if not rec.token_ref:
                raise UserError(_("Set the API token reference before activating."))
            rec.state = "active"
        return True


class PipedriveSync(models.Model):
    _name = "pipedrive.sync"
    _description = "Pipedrive Sync Record"
    _inherit = ["mail.thread"]
    _order = "write_date desc, id desc"

    name = fields.Char(required=True, copy=False, default="New")
    connection_id = fields.Many2one("pipedrive.connection", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="connection_id.company_id", store=True)
    object_type = fields.Selection([("contact", "Contact"), ("deal", "Deal")], required=True, default="contact")
    direction = fields.Selection([("push", "Push to Pipedrive"), ("pull", "Pull from Pipedrive")], required=True, default="push")
    partner_id = fields.Many2one("res.partner")
    lead_id = fields.Many2one("crm.lead")
    external_id = fields.Char(string="Pipedrive ID", copy=False)
    state = fields.Selection([("draft", "Draft"), ("ready", "Ready"), ("synced", "Synced"), ("error", "Error")],
                             default="draft", required=True, tracking=True)
    last_sync_at = fields.Datetime()
    error_message = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("pipedrive.sync") or "PD"
        return super().create(vals_list)

    @api.constrains("object_type", "partner_id", "lead_id")
    def _check_links(self):
        for rec in self:
            if rec.object_type == "contact" and not rec.partner_id:
                raise ValidationError(_("Select a partner for a contact sync."))
            if rec.object_type == "deal" and not rec.lead_id:
                raise ValidationError(_("Select an opportunity for a deal sync."))

    def action_prepare(self):
        for rec in self:
            rec.state = "ready"; rec.error_message = False
        return True

    def action_sync(self):
        for rec in self:
            if rec.state != "ready":
                raise UserError(_("Only ready records can be synced."))
            if rec.connection_id.state != "active":
                raise UserError(_("Activate the Pipedrive connection first."))
            rec.state = "synced"
            rec.external_id = rec.external_id or ("PD-%s" % rec.id)
            rec.last_sync_at = fields.Datetime.now()
            self.env["pipedrive.sync.log"].create({"sync_id": rec.id, "status": "success", "message": _("Synced.")})
        return True

    def action_reset(self):
        for rec in self:
            rec.state = "draft"; rec.error_message = False
        return True


class PipedriveSyncLog(models.Model):
    _name = "pipedrive.sync.log"
    _description = "Pipedrive Sync Log"
    _order = "create_date desc, id desc"

    sync_id = fields.Many2one("pipedrive.sync", required=True, ondelete="cascade")
    status = fields.Selection([("success", "Success"), ("error", "Error")], required=True)
    message = fields.Text()
