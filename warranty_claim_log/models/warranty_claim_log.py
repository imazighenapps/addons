# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class WarrantyClaimLog(models.Model):
    _name = "warranty.claim.log"
    _description = "Warranty Claim"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "claim_date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, tracking=True, index=True,
        default=lambda self: _("New"))
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, index=True,
        tracking=True)
    product_id = fields.Many2one(
        "product.product", string="Product", tracking=True)
    sale_order_id = fields.Many2one(
        "sale.order", string="Sale Order", tracking=True)
    claim_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    received_date = fields.Date(string="Received Date")
    planned_date = fields.Date(string="Planned Resolution")
    serial_ref = fields.Char(string="Serial / Lot")
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        tracking=True)
    description = fields.Text(string="Issue Description")
    resolution = fields.Text(string="Resolution Notes")
    state = fields.Selection(
        [("draft", "Draft"), ("review", "In Review"),
         ("approved", "Approved"), ("resolved", "Resolved"),
         ("rejected", "Rejected")],
        default="draft", required=True, tracking=True, index=True)
    count = fields.Integer(default=1)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                seq = self.env["ir.sequence"].next_by_code("warranty.claim.log")
                vals["name"] = seq or _("New")
        return super().create(vals_list)

    def action_review(self):
        for record in self:
            if record.state not in ("draft", "rejected"):
                raise UserError(_("Only a draft or rejected claim can be sent to review."))
            record.state = "review"
        return True

    def action_approve(self):
        for record in self:
            if record.state != "review":
                raise UserError(_("Only a claim in review can be approved."))
            record.state = "approved"
        return True

    def action_resolve(self):
        for record in self:
            if record.state != "approved":
                raise UserError(_("Only an approved claim can be resolved."))
            record.state = "resolved"
        return True

    def action_reject(self):
        for record in self:
            if record.state != "review":
                raise UserError(_("Only a claim in review can be rejected."))
            record.state = "rejected"
        return True

    def action_reset_draft(self):
        for record in self:
            if record.state not in ("rejected", "resolved"):
                raise UserError(_("Only a rejected or resolved claim can be reset to draft."))
            record.state = "draft"
        return True
