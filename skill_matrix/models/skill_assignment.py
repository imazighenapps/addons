# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SkillAssignment(models.Model):
    _name = "skill.assignment"
    _description = "Skill Assignment"
    _inherit = ["mail.thread"]
    _order = "employee_id, skill_id, id desc"

    name = fields.Char(
        compute="_compute_name", store=True)
    skill_id = fields.Many2one(
        "skill.skill", string="Skill", required=True, ondelete="cascade",
        index=True, tracking=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, tracking=True,
        index=True)
    level = fields.Selection(
        [("basic", "Basic"), ("intermediate", "Intermediate"),
         ("expert", "Expert")],
        required=True, default="basic", tracking=True)
    certified_on = fields.Date(string="Certified On")
    expires_on = fields.Date(string="Expires On")
    state = fields.Selection(
        [("draft", "Draft"), ("certified", "Certified"),
         ("expired", "Expired"), ("revoked", "Revoked")],
        default="draft", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("skill_id.name", "employee_id.name")
    def _compute_name(self):
        for rec in self:
            skill = rec.skill_id.name or _("Skill")
            employee = rec.employee_id.name or _("Employee")
            rec.name = "%s - %s" % (employee, skill)

    @api.constrains("skill_id", "employee_id")
    def _check_unique_assignment(self):
        for rec in self:
            duplicates = self.search([
                ("id", "!=", rec.id),
                ("skill_id", "=", rec.skill_id.id),
                ("employee_id", "=", rec.employee_id.id),
            ], limit=1)
            if duplicates:
                raise ValidationError(_(
                    "Employee %s already has an assignment for skill %s.",
                    rec.employee_id.name, rec.skill_id.name))

    @api.constrains("certified_on", "expires_on")
    def _check_dates(self):
        for rec in self:
            if rec.certified_on and rec.expires_on \
                    and rec.expires_on < rec.certified_on:
                raise ValidationError(_(
                    "The expiry date for %s cannot be before the "
                    "certification date.", rec.name))

    @api.constrains("state", "certified_on")
    def _check_certified_date(self):
        for rec in self:
            if rec.state == "certified" and not rec.certified_on:
                raise ValidationError(_(
                    "A certification date is required for certified "
                    "assignment %s.", rec.name))

    def action_certify(self):
        for rec in self:
            if rec.state != "draft":
                raise ValidationError(_(
                    "Only draft assignments can be certified."))
            rec.write({
                "state": "certified",
                "certified_on": rec.certified_on or fields.Date.context_today(rec),
            })
            rec.message_post(body=_("Skill assignment certified."))
        return True

    def action_expire(self):
        for rec in self:
            if rec.state != "certified":
                raise ValidationError(_(
                    "Only certified assignments can be marked as expired."))
            rec.state = "expired"
            rec.message_post(body=_("Skill assignment marked as expired."))
        return True

    def action_revoke(self):
        for rec in self:
            if rec.state in ("revoked", "draft"):
                raise ValidationError(_(
                    "Only certified or expired assignments can be revoked."))
            rec.state = "revoked"
            rec.message_post(body=_("Skill assignment revoked."))
        return True
