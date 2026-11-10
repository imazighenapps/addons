# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SkillSkill(models.Model):
    _name = "skill.skill"
    _description = "Skill"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(help="Short reference of the skill.")
    required_count = fields.Integer(
        string="Required Holders", default=1, required=True,
        help="Number of people that should hold this skill.")
    certification_required = fields.Boolean(
        string="Certification Required", default=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    assignment_ids = fields.One2many(
        "skill.assignment", "skill_id", string="Assignments")
    holder_count = fields.Integer(
        string="Holders", compute="_compute_counts", store=True)
    certified_count = fields.Integer(
        string="Certified", compute="_compute_counts", store=True)
    note = fields.Text()

    @api.depends("assignment_ids", "assignment_ids.state")
    def _compute_counts(self):
        for skill in self:
            skill.holder_count = len(skill.assignment_ids)
            skill.certified_count = len(skill.assignment_ids.filtered(
                lambda a: a.state == "certified"))

    @api.constrains("required_count")
    def _check_required_count(self):
        for skill in self:
            if skill.required_count < 0:
                raise ValidationError(_(
                    "The required holders for %s cannot be negative.",
                    skill.name))
