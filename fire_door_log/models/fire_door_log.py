# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class FireDoorLog(models.Model):
    _name = "fire.door.log"
    _description = "Fire Door Inspection"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "next_inspection_date asc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    door_ref = fields.Char(
        string="Door ID", required=True, tracking=True)
    location = fields.Char(required=True, tracking=True)
    door_type = fields.Selection(
        [("single", "Single"), ("double", "Double"),
         ("sliding", "Sliding"), ("other", "Other")],
        required=True, default="single", tracking=True)
    inspection_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    next_inspection_date = fields.Date(required=True, tracking=True)
    hinge_ok = fields.Boolean(string="Hinges OK", default=True, tracking=True)
    seal_ok = fields.Boolean(string="Seals OK", default=True, tracking=True)
    closer_ok = fields.Boolean(string="Closer OK", default=True, tracking=True)
    gap_ok = fields.Boolean(string="Gaps OK", default=True, tracking=True)
    inspector_id = fields.Many2one(
        "hr.employee", string="Inspector", tracking=True)
    notes = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("passed", "Passed"),
         ("defect", "Defect"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("fire.door.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.constrains("inspection_date", "next_inspection_date")
    def _check_dates(self):
        for record in self:
            if record.next_inspection_date and record.inspection_date \
                    and record.next_inspection_date < record.inspection_date:
                raise ValidationError(
                    _("The next inspection date cannot be before the inspection date."))

    def action_pass(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft inspection can be passed."))
            if not (record.hinge_ok and record.seal_ok
                    and record.closer_ok and record.gap_ok):
                raise UserError(
                    _("All checks must be OK before passing the inspection."))
            record.state = "passed"
        return True

    def action_flag_defect(self):
        for record in self:
            if record.state != "draft":
                raise UserError(
                    _("Only a draft inspection can be flagged as a defect."))
            record.state = "defect"
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
