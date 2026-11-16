# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class EmergencyLightLog(models.Model):
    _name = "emergency.light.log"
    _description = "Emergency Lighting Test"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "next_test_date asc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    light_ref = fields.Char(
        string="Light ID", required=True, tracking=True)
    location = fields.Char(required=True, tracking=True)
    light_type = fields.Selection(
        [("maintained", "Maintained"), ("non_maintained", "Non-Maintained"),
         ("exit_sign", "Exit Sign")],
        required=True, default="non_maintained", tracking=True)
    test_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    next_test_date = fields.Date(required=True, tracking=True)
    duration_minutes = fields.Integer(default=5)
    battery_ok = fields.Boolean(string="Battery OK", default=True, tracking=True)
    lamp_ok = fields.Boolean(string="Lamp OK", default=True, tracking=True)
    tester_id = fields.Many2one(
        "hr.employee", string="Tester", tracking=True)
    notes = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("tested", "Tested"),
         ("failed", "Failed"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("emergency.light.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.constrains("duration_minutes")
    def _check_duration(self):
        for record in self:
            if record.duration_minutes < 0:
                raise ValidationError(_("Duration cannot be negative."))

    @api.constrains("test_date", "next_test_date")
    def _check_dates(self):
        for record in self:
            if record.next_test_date and record.test_date \
                    and record.next_test_date < record.test_date:
                raise ValidationError(
                    _("The next test date cannot be before the test date."))

    def action_test(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft test can be validated."))
            if not record.battery_ok or not record.lamp_ok:
                raise UserError(
                    _("Battery and lamp must be OK before validating the test."))
            record.state = "tested"
        return True

    def action_fail(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft test can be marked failed."))
            record.state = "failed"
        return True

    def action_cancel(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError(_("This test is already cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state != "cancelled":
                raise UserError(_("Only a cancelled test can be reset."))
            record.state = "draft"
        return True
