# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class GasCylinderLog(models.Model):
    _name = "gas.cylinder.log"
    _description = "Gas Cylinder"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "next_test_date asc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    cylinder_ref = fields.Char(
        string="Cylinder ID", required=True, tracking=True)
    gas_type = fields.Selection(
        [("oxygen", "Oxygen"), ("acetylene", "Acetylene"),
         ("co2", "CO2"), ("nitrogen", "Nitrogen"),
         ("propane", "Propane"), ("other", "Other")],
        required=True, default="other", tracking=True)
    capacity_l = fields.Float(string="Capacity (L)", default=0.0)
    supplier_id = fields.Many2one(
        "res.partner", string="Supplier", tracking=True)
    location = fields.Char(string="Storage Location")
    last_test_date = fields.Date(tracking=True)
    next_test_date = fields.Date(tracking=True)
    notes = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("in_use", "In Use"), ("empty", "Empty"),
         ("returned", "Returned"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("gas.cylinder.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.constrains("capacity_l")
    def _check_capacity(self):
        for record in self:
            if record.capacity_l < 0:
                raise ValidationError(_("The capacity cannot be negative."))

    @api.constrains("last_test_date", "next_test_date")
    def _check_dates(self):
        for record in self:
            if record.next_test_date and record.last_test_date \
                    and record.next_test_date < record.last_test_date:
                raise ValidationError(
                    _("The next test date cannot be before the last one."))

    def action_use(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft cylinder can be put in use."))
            record.state = "in_use"
        return True

    def action_empty(self):
        for record in self:
            if record.state != "in_use":
                raise UserError(_("Only a cylinder in use can become empty."))
            record.state = "empty"
        return True

    def action_return(self):
        for record in self:
            if record.state not in ("in_use", "empty"):
                raise UserError(
                    _("Only an in-use or empty cylinder can be returned."))
            record.state = "returned"
        return True

    def action_cancel(self):
        for record in self:
            if record.state in ("returned", "cancelled"):
                raise UserError(
                    _("A returned or cancelled cylinder cannot be cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state != "cancelled":
                raise UserError(_("Only a cancelled cylinder can be reset."))
            record.state = "draft"
        return True
