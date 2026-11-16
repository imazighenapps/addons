# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AssetDisposalLog(models.Model):
    _name = "asset.disposal.log"
    _description = "Asset Disposal Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "disposal_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    asset_ref = fields.Char(
        string="Asset Reference", required=True, tracking=True)
    asset_name = fields.Char(
        string="Asset Description", required=True, tracking=True)
    asset_category = fields.Selection(
        [("it", "IT Equipment"), ("vehicle", "Vehicle"),
         ("furniture", "Furniture"), ("machinery", "Machinery"),
         ("other", "Other")],
        required=True, default="it", tracking=True)
    disposal_method = fields.Selection(
        [("sale", "Sale"), ("scrap", "Scrap"), ("donation", "Donation"),
         ("return", "Return to Lessor")],
        required=True, default="scrap", tracking=True)
    disposal_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    acquisition_value = fields.Float(string="Acquisition Value")
    residual_value = fields.Float(string="Residual Value")
    requester_id = fields.Many2one(
        "res.users", string="Requested By", default=lambda self: self.env.user,
        tracking=True)
    approver_id = fields.Many2one(
        "res.users", string="Approved By", tracking=True)
    reason = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"),
         ("approved", "Approved"), ("disposed", "Disposed"),
         ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("asset.disposal.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    @api.constrains("acquisition_value", "residual_value")
    def _check_values(self):
        for record in self:
            if record.acquisition_value < 0:
                raise ValidationError(_("The acquisition value cannot be negative."))
            if record.residual_value < 0:
                raise ValidationError(_("The residual value cannot be negative."))

    def action_submit(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only a draft request can be submitted."))
            if not record.reason:
                raise UserError(_("A disposal reason is required before submission."))
            record.state = "submitted"
        return True

    def action_approve(self):
        for record in self:
            if record.state != "submitted":
                raise UserError(_("Only a submitted request can be approved."))
            record.write({"state": "approved", "approver_id": self.env.user.id})
        return True

    def action_dispose(self):
        for record in self:
            if record.state != "approved":
                raise UserError(_("Only an approved request can be disposed."))
            record.state = "disposed"
        return True

    def action_cancel(self):
        for record in self:
            if record.state in ("disposed", "cancelled"):
                raise UserError(
                    _("A disposed or cancelled request cannot be cancelled."))
            record.state = "cancelled"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state != "cancelled":
                raise UserError(_("Only a cancelled request can be reset."))
            record.state = "draft"
        return True
