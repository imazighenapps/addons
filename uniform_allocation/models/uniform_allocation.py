# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class UniformItem(models.Model):
    _name = "uniform.item"
    _description = "Uniform / PPE Item"
    _order = "name, id"

    name = fields.Char(required=True)
    item_type = fields.Selection(
        [("uniform", "Uniform"), ("ppe", "PPE"), ("other", "Other")],
        default="uniform", string="Type", required=True)
    active = fields.Boolean(default=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)


class UniformAllocation(models.Model):
    _name = "uniform.allocation"
    _description = "Uniform Allocation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_issue desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, index=True, tracking=True)
    item_id = fields.Many2one(
        "uniform.item", string="Item", required=True, index=True, tracking=True)
    quantity = fields.Float(string="Quantity", required=True, default=1.0)
    size = fields.Char(string="Size")
    date_issue = fields.Date(
        string="Issue Date", required=True, default=fields.Date.context_today, tracking=True)
    date_return = fields.Date(string="Return Date", tracking=True)
    state = fields.Selection(
        [("issued", "Issued"), ("returned", "Returned"), ("replaced", "Replaced")],
        default="issued", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.constrains("quantity")
    def _check_quantity(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError(_("Quantity must be strictly positive."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("uniform.allocation")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Uniform Allocation",
                        "code": "uniform.allocation",
                        "prefix": "UNI/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_return(self):
        for rec in self:
            if rec.state != "issued":
                raise UserError(_("Only an issued allocation can be returned."))
            rec.write({
                "state": "returned",
                "date_return": rec.date_return or fields.Date.context_today(rec),
            })

    def action_replace(self):
        for rec in self:
            if rec.state != "issued":
                raise UserError(_("Only an issued allocation can be replaced."))
            rec.state = "replaced"

    def action_reset(self):
        for rec in self:
            if rec.state == "issued":
                raise UserError(_("An issued allocation cannot be reset."))
            rec.write({"state": "issued", "date_return": False})
