# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class FireExtinguisherLog(models.Model):
    _name = "fire.extinguisher.log"
    _description = "Fire Extinguisher Inspection"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "next_inspection_date asc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    extinguisher_ref = fields.Char(
        string="Extinguisher ID", required=True, tracking=True)
    location = fields.Char(required=True, tracking=True)
    extinguisher_type = fields.Selection(
        [("water", "Water"), ("foam", "Foam"), ("co2", "CO2"),
         ("powder", "Dry Powder"), ("other", "Other")],
        required=True, default="powder", tracking=True)
    capacity_kg = fields.Float(string="Capacity (kg)")
    last_inspection_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    next_inspection_date = fields.Date(required=True, tracking=True)
    pressure_ok = fields.Boolean(string="Pressure OK", default=True, tracking=True)
    seal_ok = fields.Boolean(string="Seal OK", default=True, tracking=True)
    inspector_id = fields.Many2one(
        "hr.employee", string="Inspector", tracking=True)
    notes = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("validated", "Validated"),
         ("overdue", "Overdue"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("fire.extinguisher.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.constrains("capacity_kg")
    def _check_capacity(self):
        for record in self:
            if record.capacity_kg < 0:
                raise ValidationError(_("Capacity cannot be negative."))

    @api.constrains("last_inspection_date", "next_inspection_date")
    def _check_dates(self):
        for record in self:
            if record.next_inspection_date and record.last_inspection_date \
                    and record.next_inspection_date < record.last_inspection_date:
                raise ValidationError(
                    _("The next inspection date cannot be before the last one."))

    def action_validate(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft inspection can be validated."))
            if not record.pressure_ok or not record.seal_ok:
                raise UserError(
                    _("Pressure and seal must be OK before validation."))
            record.state = "validated"
        return True

    def action_mark_overdue(self):
        for record in self:
            if record.state != "validated":
                raise UserError(_("Only a validated inspection can become overdue."))
            record.state = "overdue"
        return True

    def action_cancel(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError(_("This inspection is already cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state != "cancelled":
                raise UserError(_("Only a cancelled inspection can be reset."))
            record.state = "draft"
        return True
