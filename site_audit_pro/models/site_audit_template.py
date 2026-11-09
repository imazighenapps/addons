# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SiteAuditTemplate(models.Model):
    _name = "size.audit.template"
    _description = "Site Audit Template"
    _order = "name"

    name = fields.Char(required=True)
    line_ids = fields.One2many(
        "site.audit.template.line", "template_id", string="Points")
    point_count = fields.Integer(
        string="Points", compute="_compute_points")
    total_weight = fields.Float(
        string="Total Weight", compute="_compute_points",
        help="Sum of the weights of the points.")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)
    note = fields.Text()

    @api.depends("line_ids", "line_ids.points_max")
    def _compute_points(self):
        for template in self:
            template.point_count = len(template.line_ids)
            template.total_weight = sum(
                line.points_max for line in template.line_ids)


class SiteAuditTemplateLine(models.Model):
    _name = "site.audit.template.line"
    _description = "Site Audit Template Line"
    _order = "sequence, id"

    template_id = fields.Many2one(
        "size.audit.template", string="Template", required=True,
        ondelete="cascade", index=True)
    name = fields.Char(required=True)
    points_max = fields.Float(
        string="Weight", default=10.0, required=True,
        help="Best score a perfect visit obtains on this point.")
    category = fields.Selection(
        [("safety", "Safety"), ("cleanliness", "Cleanliness"),
         ("equipment", "Equipment"), ("compliance", "Compliance"),
         ("other", "Other")],
        default="other", required=True)
    sequence = fields.Integer(default=10)
