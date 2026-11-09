# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SiteAudit(models.Model):
    _name = "site.audit"
    _description = "Site Audit"
    _inherit = ["mail.thread"]
    _order = "audit_date desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Site audit %s")
        % fields.Date.context_today(self),
        help="Reference of the audit, generated at creation.")
    template_id = fields.Many2one(
        "size.audit.template", string="Template", required=True,
        tracking=True,
        help="The inspection template the audit is built on.")
    site_name = fields.Char(
        string="Site", required=True, tracking=True,
        help="Name of the site visited, for example Site Lyon - Plant.")
    audit_date = fields.Date(
        default=fields.Date.context_today, required=True, tracking=True)
    auditor_id = fields.Many2one(
        "res.users", string="Auditor", required=True,
        default=lambda self: self.env.user)
    line_ids = fields.One2many(
        "site.audit.line", "audit_id", string="Scored Points")
    point_count = fields.Integer(
        string="Points", compute="_compute_score", store=True)
    failed_count = fields.Integer(
        string="Failed Points", compute="_compute_score", store=True)
    score_pct = fields.Float(
        string="Score", compute="_compute_score", store=True,
        help="Percentage of the best possible score, computed from the "
             "weights of the template.")
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done"), ("cancelled", "Cancelled")],
        default="draft", required=True, copy=False, tracking=True,
        index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)
    note = fields.Text()

    @api.depends("line_ids", "line_ids.score", "line_ids.points_max",
                 "line_ids.scored", "line_ids.state")
    def _compute_score(self):
        for audit in self:
            lines = audit.line_ids
            audit.point_count = len(lines)
            audit.failed_count = len(lines.filtered(
                lambda line: line.state == "failed"))
            best = sum(line.points_max for line in lines)
            got = sum(line.score for line in lines if line.scored)
            audit.score_pct = round(got / best * 100.0, 1) if best else 0.0

    @api.model_create_multi
    def create(self, vals_list):
        audits = super().create(vals_list)
        for audit in audits:
            if not audit.line_ids and audit.template_id:
                audit._apply_template()
        return audits

    def _apply_template(self):
        self.ensure_one()
        self.line_ids = [fields.Command.create({
            "name": line.name,
            "points_max": line.points_max,
            "category": line.category,
            "sequence": line.sequence,
        }) for line in self.template_id.line_ids]

    def action_reset(self):
        for audit in self:
            if not audit.template_id.exists():
                raise UserError(_(
                    "The template of this audit has been deleted."))
            audit.line_ids.unlink()
            audit._apply_template()
            audit.message_post(body=_(
                "The audit has been reset on its template."))
        return True

    def action_done(self):
        for audit in self:
            if audit.state == "done":
                raise UserError(_(
                    "Audit \"%s\" is already done.", audit.name))
            unscored = audit.line_ids.filtered(
                lambda line: not line.scored)
            if unscored:
                raise UserError(_(
                    "%s point(s) of audit \"%s\" are still unscored.",
                    len(unscored), audit.name))
            audit.state = "done"
            audit.message_post(body=_(
                "The audit is scored at %s%%.", audit.score_pct))
        return True

    def action_reopen(self):
        for audit in self:
            audit.state = "draft"
        return True

    def action_cancel(self):
        for audit in self:
            audit.state = "cancelled"
        return True
