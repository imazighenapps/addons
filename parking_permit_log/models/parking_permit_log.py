# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ParkingPermitLog(models.Model):
    _name = "parking.permit.log"
    _description = "Parking Permit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_end desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Contact / Visitor", tracking=True)
    holder_name = fields.Char(
        string="Holder", compute="_compute_holder_name", store=True)
    permit_type = fields.Selection(
        [("employee", "Employee"), ("visitor", "Visitor"),
         ("contractor", "Contractor"), ("other", "Other")],
        default="employee", required=True, tracking=True)
    vehicle_plate = fields.Char(string="Vehicle Plate", tracking=True)
    zone = fields.Char(string="Zone / Spot")
    date_start = fields.Date(string="Start Date", tracking=True)
    date_end = fields.Date(string="Expiry Date", tracking=True)
    user_id = fields.Many2one(
        "res.users", string="Issued By", default=lambda self: self.env.user,
        tracking=True)
    note = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"),
         ("expired", "Expired"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("parking.permit.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.depends("employee_id", "partner_id")
    def _compute_holder_name(self):
        for record in self:
            record.holder_name = (
                record.employee_id.name or record.partner_id.name or "")

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for record in self:
            if record.date_start and record.date_end \
                    and record.date_end < record.date_start:
                raise ValidationError(
                    _("The expiry date cannot be before the start date."))

    def action_activate(self):
        for record in self:
            if record.state not in ("draft", "expired"):
                raise UserError(_("Only a draft or expired permit can be activated."))
            record.state = "active"
        return True

    def action_expire(self):
        for record in self:
            if record.state != "active":
                raise UserError(_("Only an active permit can be marked expired."))
            record.state = "expired"
        return True

    def action_cancel(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError(_("This permit is already cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state not in ("cancelled", "expired"):
                raise UserError(_("Only a cancelled or expired permit can be reset to draft."))
            record.state = "draft"
        return True
