# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class GdprDpia(models.Model):
    _name = "gdpr.dpia"
    _description = "GDPR Data Protection Impact Assessment"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True, tracking=True)
    activity_id = fields.Many2one("gdpr.activity", string="Processing")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    crit_evaluation = fields.Boolean(string="Systematic extensive evaluation")
    crit_auto = fields.Boolean(string="Automated decision with legal effect")
    crit_monitoring = fields.Boolean(string="Systematic large-scale monitoring")
    crit_sensitive = fields.Boolean(string="Sensitive data at scale")
    crit_scale = fields.Boolean(string="Large scale")
    crit_matching = fields.Boolean(string="Dataset matching")
    crit_vulnerable = fields.Boolean(string="Vulnerable persons")
    crit_innovative = fields.Boolean(string="Innovative technology / AI")
    crit_hamper = fields.Boolean(string="Prevents exercising a right")
    score = fields.Integer(compute="_compute_score", store=True)
    need_dpia = fields.Boolean(compute="_compute_score", store=True)
    description = fields.Text(string="Description & Purposes")
    necessity = fields.Text(string="Necessity & Proportionality")
    risks = fields.Text(string="Risk Assessment")
    measures = fields.Text(string="Measures & Safeguards")
    residual = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="medium",
    )
    consultation = fields.Boolean(string="Prior Consultation (Art.36)")
    consultation_date = fields.Date()
    state = fields.Selection(
        [("screening", "Screening"), ("analysis", "Analysis"),
         ("decided", "Decided"), ("review", "Under Review")],
        default="screening",
        tracking=True,
    )

    @api.depends("crit_evaluation", "crit_auto", "crit_monitoring", "crit_sensitive",
                 "crit_scale", "crit_matching", "crit_vulnerable", "crit_innovative",
                 "crit_hamper")
    def _compute_score(self):
        for rec in self:
            n = sum(1 for f in (
                rec.crit_evaluation, rec.crit_auto, rec.crit_monitoring,
                rec.crit_sensitive, rec.crit_scale, rec.crit_matching,
                rec.crit_vulnerable, rec.crit_innovative, rec.crit_hamper) if f)
            rec.score = n
            rec.need_dpia = n >= 2

    def action_start_analysis(self):
        self.write({"state": "analysis"})

    def action_decide(self):
        for rec in self:
            if rec.residual == "high" and not rec.consultation:
                from odoo.exceptions import UserError
                raise UserError(_(
                    "High residual risk requires prior consultation (Art.36) or lower residual."))
            rec.state = "decided"
