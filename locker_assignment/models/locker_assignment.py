# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class Locker(models.Model):
    _name = "locker.locker"
    _description = "Locker"
    _order = "name, id"

    name = fields.Char(string="Locker ID", required=True)
    location = fields.Char(string="Location")
    active = fields.Boolean(default=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    _sql_constraints = [
        ('name_company_uniq', "UNIQUE(name, company_id)", "A locker with this identifier already exists for this company."),
    ]


class LockerAssignment(models.Model):
    _name = "locker.assignment"
    _description = "Locker Assignment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_issue desc, id desc"

    name = fields.Char(
        default=lambda self: _("New"), copy=False, readonly=True, index=True)
    locker_id = fields.Many2one(
        "locker.locker", string="Locker", required=True, index=True, tracking=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, index=True, tracking=True)
    date_issue = fields.Date(
        string="Issue Date", required=True, default=fields.Date.context_today, tracking=True)
    date_return = fields.Date(string="Return Date", tracking=True)
    state = fields.Selection(
        [("assigned", "Assigned"), ("returned", "Returned")],
        default="assigned", required=True, tracking=True, index=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.constrains("date_issue", "date_return")
    def _check_dates(self):
        for rec in self:
            if rec.date_issue and rec.date_return and rec.date_return < rec.date_issue:
                raise ValidationError(_("The return date cannot be before the issue date."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("locker.assignment")
                vals["name"] = seq or _("New")
                if vals.get("name", _("New")) == _("New"):
                    vals["name"] = self.env["ir.sequence"].sudo().create({
                        "name": "Locker Assignment",
                        "code": "locker.assignment",
                        "prefix": "LCK/%(year)s/",
                        "padding": 4,
                    }).next_by_id()
        return super().create(vals_list)

    def action_return(self):
        for rec in self:
            if rec.state != "assigned":
                raise UserError(_("Only an assigned locker can be returned."))
            rec.write({
                "state": "returned",
                "date_return": rec.date_return or fields.Date.context_today(rec),
            })

    def action_reset(self):
        for rec in self:
            if rec.state != "returned":
                raise UserError(_("Only a returned assignment can be reset."))
            rec.write({"state": "assigned", "date_return": False})
