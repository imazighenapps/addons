# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

PASS_RATIO = 0.6


class SiteAuditLine(models.Model):
    _name = "site.audit.line"
    _description = "Site Audit Line"
    _order = "sequence, id"

    audit_id = fields.Many2one(
        "site.audit", string="Audit", required=True, ondelete="cascade",
        index=True)
    sequence = fields.Integer(default=10)
    name = fields.Char(string="Point", required=True)
    category = fields.Selection(
        [("safety", "Safety"), ("cleanliness", "Cleanliness"),
         ("equipment", "Equipment"), ("compliance", "Compliance"),
         ("other", "Other")],
        default="other", required=True)
    points_max = fields.Float(
        string="Weight", default=10.0, required=True,
        help="Best score this point could obtain.")
    score = fields.Float(
        help="What the auditor granted on this point, out of the weight.")
    scored = fields.Boolean(
        copy=False, default=False, index=True,
        help="Ticked when the point has actually been scored.")
    state = fields.Selection(
        [("pending", "Pending"), ("passed", "Passed"),
         ("failed", "Failed")],
        compute="_compute_state", store=True,
        help="Pending until the auditor scores it, then compared with the "
             "pass threshold of the weight.")
    company_id = fields.Many2one(
        related="audit_id.company_id", store=True, readonly=True)

    @api.depends("score", "scored", "points_max")
    def _compute_state(self):
        for line in self:
            if not line.scored:
                line.state = "pending"
            elif line.score >= line.points_max * PASS_RATIO:
                line.state = "passed"
            else:
                line.state = "failed"

    @api.constrains("score", "points_max")
    def _check_score(self):
        for line in self:
            if line.score < 0:
                raise ValidationError(_(
                    "The score of point \"%s\" cannot be negative.",
                    line.name))
            if line.score > line.points_max:
                raise ValidationError(_(
                    "The score of point \"%s\" cannot exceed its weight "
                    "of %s.", line.name, line.points_max))
