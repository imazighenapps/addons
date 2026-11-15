# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ItAssetLog(models.Model):
    _name = "it.asset.log"
    _description = "IT Asset"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name, id desc"

    name = fields.Char(
        string="Asset Tag", required=True, tracking=True, index=True)
    serial_no = fields.Char(string="Serial Number", tracking=True)
    asset_type = fields.Selection(
        [("laptop", "Laptop"), ("desktop", "Desktop"), ("phone", "Phone"),
         ("tablet", "Tablet"), ("monitor", "Monitor"), ("other", "Other")],
        default="other", required=True, tracking=True)
    model_name = fields.Char(string="Model")
    employee_id = fields.Many2one(
        "hr.employee", string="Assigned To", tracking=True)
    location = fields.Char(tracking=True)
    purchase_date = fields.Date(tracking=True)
    warranty_end = fields.Date(string="Warranty End", tracking=True)
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        tracking=True)
    note = fields.Text(string="Notes")
    state = fields.Selection(
        [("draft", "Draft"), ("in_use", "In Use"), ("repair", "In Repair"),
         ("spare", "Spare"), ("retired", "Retired")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    _sql_constraints = [
        ("name_company_uniq", "unique(name, company_id)",
         "The asset tag must be unique per company."),
    ]

    def action_assign(self):
        for record in self:
            if record.state not in ("draft", "spare"):
                raise UserError(_("Only a draft or spare asset can be assigned."))
            record.state = "in_use"
        return True

    def action_repair(self):
        for record in self:
            if record.state not in ("in_use", "spare"):
                raise UserError(_("Only an in-use or spare asset can be sent to repair."))
            record.state = "repair"
        return True

    def action_spare(self):
        for record in self:
            if record.state in ("retired", "spare"):
                raise UserError(_("This asset is already spare or retired."))
            record.state = "spare"
        return True

    def action_retire(self):
        for record in self:
            if record.state == "retired":
                raise UserError(_("This asset is already retired."))
            record.state = "retired"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state not in ("spare", "retired"):
                raise UserError(_("Only a spare or retired asset can be reset to draft."))
            record.state = "draft"
        return True
