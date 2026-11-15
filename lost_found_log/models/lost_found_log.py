# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class LostFoundItem(models.Model):
    _name = "lost.found.item"
    _description = "Lost and Found Item"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_found desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    description = fields.Text(string="Item Description", required=True)
    date_found = fields.Date(
        string="Date Found", required=True, default=fields.Date.context_today, tracking=True)
    location_found = fields.Char(string="Found Location", required=True)
    finder_name = fields.Char(string="Finder / Reported By")
    storage_location = fields.Char(string="Storage Location")
    claimant_name = fields.Char(string="Claimant Name")
    claimant_contact = fields.Char(string="Claimant Contact")
    date_returned = fields.Date(string="Return/Disposal Date")
    state = fields.Selection(
        [("found", "Found"), ("claimed", "Claimed"), ("returned", "Returned"), ("disposed", "Disposed")],
        default="found", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("lost.found.item")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Lost and Found Item",
                        "code": "lost.found.item",
                        "prefix": "LF/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_claim(self):
        for rec in self:
            if rec.state != "found":
                raise UserError(_("Only a found item can be marked claimed."))
            rec.state = "claimed"

    def action_return(self):
        for rec in self:
            if rec.state not in ("found", "claimed"):
                raise UserError(_("Only a found or claimed item can be returned."))
            rec.write({
                "state": "returned",
                "date_returned": rec.date_returned or fields.Date.context_today(rec),
            })

    def action_dispose(self):
        for rec in self:
            if rec.state in ("returned", "disposed"):
                raise UserError(_("This item cannot be disposed."))
            rec.write({
                "state": "disposed",
                "date_returned": rec.date_returned or fields.Date.context_today(rec),
            })

    def action_reset(self):
        for rec in self:
            if rec.state not in ("disposed", "returned"):
                raise UserError(_("Only a returned or disposed item can be reset."))
            rec.write({"state": "found", "date_returned": False})
