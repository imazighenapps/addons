# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PhotoAudit(models.Model):
    _name = "photo.audit"
    _description = "Photo Audit"
    _inherit = ["mail.thread"]
    _order = "due_date, id desc"

    name = fields.Char(
        required=True, tracking=True,
        default=lambda self: _("Photo Audit %s")
        % fields.Date.context_today(self))
    area = fields.Char(
        string="Catalog Area", required=True, tracking=True,
        help="Catalog section or channel covered by this audit.")
    owner_name = fields.Char(
        string="Owner", required=True, tracking=True)
    due_date = fields.Date(required=True, tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("in_progress", "In Progress"),
         ("done", "Done")],
        default="draft", required=True, tracking=True, index=True)
    issue_ids = fields.One2many(
        "photo.issue", "audit_id", string="Issues", copy=True)
    issue_count = fields.Integer(
        string="Issues", compute="_compute_stats", store=True)
    open_issue_count = fields.Integer(
        string="Open Issues", compute="_compute_stats", store=True)
    fixed_issue_count = fields.Integer(
        string="Fixed Issues", compute="_compute_stats", store=True)
    quality_score = fields.Float(
        string="Quality Score (%)", compute="_compute_stats", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("issue_ids", "issue_ids.state")
    def _compute_stats(self):
        for audit in self:
            issues = audit.issue_ids
            total = len(issues)
            fixed = len(issues.filtered(lambda i: i.state == "fixed"))
            audit.issue_count = total
            audit.fixed_issue_count = fixed
            audit.open_issue_count = total - fixed
            audit.quality_score = (fixed * 100.0 / total) if total else 0.0

    @api.constrains("due_date")
    def _check_due_date(self):
        for audit in self:
            if not audit.due_date:
                raise ValidationError(_(
                    "Audit %s must have a due date.", audit.name))

    def action_start(self):
        for audit in self:
            if audit.state != "draft":
                raise UserError(_("Only draft audits can be started."))
            if not audit.issue_ids:
                raise UserError(_(
                    "Audit %s must contain at least one issue before "
                    "starting.", audit.name))
            audit.state = "in_progress"
            audit.message_post(body=_("The photo audit was started."))
        return True

    def action_done(self):
        for audit in self:
            if audit.state != "in_progress":
                raise UserError(_("Only in-progress audits can be completed."))
            if audit.open_issue_count:
                raise UserError(_(
                    "All issues must be fixed before completing %s.",
                    audit.name))
            audit.state = "done"
            audit.message_post(body=_("The photo audit was completed."))
        return True
