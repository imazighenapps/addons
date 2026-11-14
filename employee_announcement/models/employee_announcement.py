# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class EmployeeAnnouncement(models.Model):
    _name = "employee.announcement"
    _description = "Employee Announcement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "priority desc, date_publish desc, id desc"

    name = fields.Char(string="Title", required=True, tracking=True)
    body = fields.Html(string="Content", required=True)
    author_id = fields.Many2one(
        "res.users", string="Author", default=lambda self: self.env.user,
        required=True, tracking=True)
    department_id = fields.Many2one(
        "hr.department", string="Department / Audience", tracking=True)
    date_publish = fields.Date(
        string="Publish Date", default=fields.Date.context_today, tracking=True)
    date_expiry = fields.Date(string="Expiry Date", tracking=True)
    priority = fields.Selection(
        [("0", "Normal"), ("1", "Important")], default="0", tracking=True)
    is_expired = fields.Boolean(compute="_compute_expired", string="Expired")
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("archived", "Archived")],
        default="draft", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True,
        index=True)

    @api.depends("date_expiry")
    def _compute_expired(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.is_expired = bool(rec.date_expiry and rec.date_expiry < today)

    @api.constrains("date_publish", "date_expiry")
    def _check_dates(self):
        for rec in self:
            if rec.date_publish and rec.date_expiry and rec.date_expiry < rec.date_publish:
                raise ValidationError(
                    _("The expiry date cannot be before the publish date."))

    def action_publish(self):
        for rec in self:
            if rec.state == "archived":
                raise UserError(_("An archived announcement cannot be published."))
            rec.state = "published"

    def action_archive_announcement(self):
        for rec in self:
            rec.state = "archived"

    def action_reset(self):
        for rec in self:
            rec.state = "draft"
