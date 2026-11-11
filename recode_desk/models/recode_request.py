# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class RecodeRequest(models.Model):
    _name = "recode.request"
    _description = "Product Recode Request"
    _inherit = ["mail.thread"]
    _order = "planned_on desc, id desc"

    name = fields.Char(
        string="Reference", required=True, copy=False,
        default=lambda self: _("New"), tracking=True)
    old_code = fields.Char(required=True, tracking=True)
    new_code = fields.Char(required=True, tracking=True)
    reason = fields.Char(required=True, tracking=True)
    planned_on = fields.Date(
        string="Planned On", required=True, default=fields.Date.context_today,
        tracking=True)
    applied_on = fields.Date(string="Applied On", readonly=True, copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Applied")],
        default="draft", required=True, copy=False, tracking=True, index=True)
    line_ids = fields.One2many(
        "recode.line", "request_id", string="References")
    line_count = fields.Integer(compute="_compute_counts", store=True)
    updated_count = fields.Integer(compute="_compute_counts", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    active = fields.Boolean(default=True)
    note = fields.Text()

    @api.depends("line_ids", "line_ids.updated")
    def _compute_counts(self):
        for request in self:
            request.line_count = len(request.line_ids)
            request.updated_count = len(
                request.line_ids.filtered(lambda l: l.updated))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "recode.request") or _("New")
        return super().create(vals_list)

    @api.constrains("old_code", "new_code")
    def _check_codes(self):
        for request in self:
            if (request.old_code or "").strip() == (request.new_code or "").strip():
                raise ValidationError(_(
                    "The new code must differ from the old code."))

    def action_apply(self):
        for request in self:
            if request.state != "draft":
                raise UserError(_("Only a draft request can be applied."))
            if not request.line_ids:
                raise UserError(_(
                    "Add at least one reference line before applying."))
            for line in request.line_ids:
                line.write({
                    "updated": True,
                    "new_value": line.new_value or request.new_code,
                })
            request.write({
                "state": "done",
                "applied_on": fields.Date.context_today(request),
            })
            request.message_post(body=_(
                "Recode applied: %s reference(s) updated from %s to %s.",
                len(request.line_ids), request.old_code, request.new_code))
        return True

    def action_reset_draft(self):
        for request in self:
            if request.state != "done":
                raise UserError(_("Only an applied request can be reset."))
            request.line_ids.write({"updated": False})
            request.write({"state": "draft", "applied_on": False})
        return True
