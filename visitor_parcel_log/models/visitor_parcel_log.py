# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class VisitorParcelLog(models.Model):
    _name = "visitor.parcel.log"
    _description = "Parcel Delivery"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "arrival_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    employee_id = fields.Many2one(
        "hr.employee", string="Recipient", tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Sender / Carrier", tracking=True)
    carrier_name = fields.Char(string="Carrier")
    tracking_ref = fields.Char(string="Tracking Reference")
    description = fields.Char(string="Parcel Description")
    arrival_date = fields.Datetime(
        required=True, default=fields.Datetime.now, tracking=True)
    storage_location = fields.Char(string="Storage Location")
    received_by_id = fields.Many2one(
        "res.users", string="Received By", default=lambda self: self.env.user,
        tracking=True)
    collected_by = fields.Char(string="Collected By")
    collected_date = fields.Datetime()
    note = fields.Text()
    state = fields.Selection(
        [("received", "Received"), ("notified", "Notified"),
         ("collected", "Collected"), ("returned", "Returned")],
        default="received", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("visitor.parcel.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    def action_notify(self):
        for record in self:
            if record.state != "received":
                raise UserError(_("Only a received parcel can be marked notified."))
            record.state = "notified"
        return True

    def action_collect(self):
        for record in self:
            if record.state not in ("received", "notified"):
                raise UserError(_("Only a received or notified parcel can be collected."))
            values = {"state": "collected"}
            if not record.collected_date:
                values["collected_date"] = fields.Datetime.now()
            record.write(values)
        return True

    def action_return(self):
        for record in self:
            if record.state in ("collected", "returned"):
                raise UserError(_("A collected or returned parcel cannot be returned again."))
            record.state = "returned"
        return True

    def action_reset_received(self):
        for record in self:
            if record.state != "returned":
                raise UserError(_("Only a returned parcel can be reset to received."))
            record.write({"state": "received", "collected_date": False})
        return True
