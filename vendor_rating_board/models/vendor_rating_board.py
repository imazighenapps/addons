# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class VendorEvaluation(models.Model):
    _name = "vendor.evaluation"
    _description = "Vendor Evaluation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "evaluation_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    partner_id = fields.Many2one(
        "res.partner", string="Supplier", required=True, index=True,
        tracking=True, domain=[("supplier_rank", ">", 0)])
    evaluation_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    period = fields.Char(
        string="Period", help="Label such as 2026-Q1 or 2026-11.")
    user_id = fields.Many2one(
        "res.users", string="Evaluator", default=lambda self: self.env.user,
        tracking=True)
    delivery_score = fields.Integer(string="Delivery", default=3)
    quality_score = fields.Integer(string="Quality", default=3)
    price_score = fields.Integer(string="Price", default=3)
    service_score = fields.Integer(string="Service", default=3)
    overall_score = fields.Float(
        string="Overall Score", compute="_compute_overall", store=True,
        digits=(16, 2))
    state = fields.Selection(
        [("draft", "Draft"), ("validated", "Validated"),
         ("archived", "Archived")],
        default="draft", required=True, tracking=True, index=True)
    strengths = fields.Text()
    improvements = fields.Text(string="Improvement Actions")
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("vendor.evaluation")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.depends("delivery_score", "quality_score", "price_score", "service_score")
    def _compute_overall(self):
        for record in self:
            scores = [record.delivery_score, record.quality_score,
                      record.price_score, record.service_score]
            record.overall_score = sum(scores) / 4.0

    @api.constrains("delivery_score", "quality_score", "price_score", "service_score")
    def _check_scores(self):
        for record in self:
            for label, value in [
                ("Delivery", record.delivery_score),
                ("Quality", record.quality_score),
                ("Price", record.price_score),
                ("Service", record.service_score),
            ]:
                if value < 0 or value > 5:
                    raise ValidationError(
                        _("%s score must be between 0 and 5.") % label)

    def action_validate(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft evaluation can be validated."))
            record.state = "validated"
        return True

    def action_archive_eval(self):
        for record in self:
            if record.state != "validated":
                raise UserError(_("Only a validated evaluation can be archived."))
            record.state = "archived"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state == "draft":
                raise UserError(_("This evaluation is already a draft."))
            record.state = "draft"
        return True
