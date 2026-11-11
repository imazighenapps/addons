# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PackCheck(models.Model):
    _name = "pack.check"
    _description = "Packing Check"
    _inherit = ["mail.thread"]
    _order = "check_date desc, id desc"

    name = fields.Char(
        required=True, copy=False, default="New", tracking=True,
        help="Reference of the packing check.")
    reference = fields.Char(
        string="Shipment Reference", required=True, tracking=True,
        help="Shipment, order or box reference being checked.")
    packer = fields.Char(
        string="Packed By", tracking=True,
        help="Person who prepared the box.")
    checker = fields.Char(
        string="Checked By", tracking=True,
        help="Person who performed the control.")
    check_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True,
        help="Date the packing check was performed.")
    expected_weight = fields.Float(
        required=True, tracking=True,
        help="Expected total weight of the box.")
    actual_weight = fields.Float(
        required=True, tracking=True,
        help="Measured total weight of the box.")
    expected_count = fields.Integer(
        required=True, tracking=True,
        help="Expected number of pieces in the box.")
    actual_count = fields.Integer(
        required=True, tracking=True,
        help="Counted number of pieces in the box.")
    weight_variance = fields.Float(
        compute="_compute_results", store=True,
        help="Difference between actual and expected weight.")
    count_variance = fields.Integer(
        compute="_compute_results", store=True,
        help="Difference between actual and expected piece count.")
    result = fields.Selection(
        [("pass", "Pass"), ("fail", "Fail")],
        compute="_compute_results", store=True, index=True,
        help="Pass when weight and count match the expectation.")
    state = fields.Selection(
        [("draft", "Draft"), ("checked", "Checked"),
         ("approved", "Approved"), ("rejected", "Rejected")],
        default="draft", required=True, tracking=True, index=True)
    decision_date = fields.Date(
        readonly=True, copy=False,
        help="Date the check was approved or rejected.")
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    active = fields.Boolean(default=True)

    @api.depends("expected_weight", "actual_weight", "expected_count", "actual_count")
    def _compute_results(self):
        for record in self:
            weight_var = record.actual_weight - record.expected_weight
            count_var = record.actual_count - record.expected_count
            record.weight_variance = weight_var
            record.count_variance = count_var
            record.result = "pass" if (
                abs(weight_var) < 1e-6 and count_var == 0) else "fail"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "pack.check") or _("PC-%s") % fields.Date.context_today(self)
        return super().create(vals_list)

    @api.constrains("expected_weight", "actual_weight")
    def _check_weights(self):
        for record in self:
            if record.expected_weight < 0 or record.actual_weight < 0:
                raise ValidationError(_(
                    "Weights of %s cannot be negative.", record.name))

    @api.constrains("expected_count", "actual_count")
    def _check_counts(self):
        for record in self:
            if record.expected_count < 0 or record.actual_count < 0:
                raise ValidationError(_(
                    "Piece counts of %s cannot be negative.", record.name))

    def action_check(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only draft checks can be verified."))
            record.state = "checked"
            record.message_post(body=_("Packing check verified."))
        return True

    def action_approve(self):
        for record in self:
            if record.state != "checked":
                raise UserError(_("Only checked records can be approved."))
            record.write({
                "state": "approved",
                "decision_date": fields.Date.context_today(record),
            })
            record.message_post(body=_("Packing check approved."))
        return True

    def action_reject(self):
        for record in self:
            if record.state != "checked":
                raise UserError(_("Only checked records can be rejected."))
            record.write({
                "state": "rejected",
                "decision_date": fields.Date.context_today(record),
            })
            record.message_post(body=_("Packing check rejected."))
        return True

    def action_reset(self):
        for record in self:
            if record.state == "draft":
                raise UserError(_("Draft checks cannot be reset."))
            record.write({"state": "draft", "decision_date": False})
            record.message_post(body=_("Packing check reset to draft."))
        return True
