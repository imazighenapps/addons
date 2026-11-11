# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class QuoteAmendment(models.Model):
    _name = "quote.amendment"
    _description = "Quotation Amendment"
    _inherit = ["mail.thread"]
    _order = "revision_no desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Rev %s")
        % fields.Date.context_today(self),
        help="Reference of the amendment, generated at creation.")
    quote_ref = fields.Char(
        required=True, tracking=True,
        help="Reference of the quotation this amendment revises.")
    revision_no = fields.Integer(
        string="Revision", default=1, required=True, tracking=True,
        help="Version number of the quotation after this amendment.")
    reason = fields.Text(
        tracking=True, help="Why the quotation changes.")
    change_ids = fields.One2many(
        "quote.change.line", "amendment_id", string="Changes")
    change_count = fields.Integer(
        string="Changes", compute="_compute_change_count", store=True)
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"),
         ("approved", "Approved"), ("rejected", "Rejected")],
        default="draft", required=True, copy=False, tracking=True,
        index=True)
    submitted_on = fields.Date(
        string="Submitted On", readonly=True, copy=False)
    approved_user_id = fields.Many2one(
        "res.users", string="Approved By", readonly=True, copy=False)
    approved_on = fields.Date(
        string="Approved On", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("change_ids")
    def _compute_change_count(self):
        for amendment in self:
            amendment.change_count = len(amendment.change_ids)

    @api.constrains("revision_no")
    def _check_revision_no(self):
        for amendment in self:
            if amendment.revision_no <= 0:
                raise ValidationError(_(
                    "The revision number of %s must be above zero.",
                    amendment.quote_ref))

    @api.constrains("state", "approved_on", "approved_user_id")
    def _check_approval_stamp(self):
        for amendment in self:
            if amendment.state == "approved" and not (
                    amendment.approved_on and amendment.approved_user_id):
                raise ValidationError(_(
                    "The approved version of %s must carry its approval "
                    "date and approver.", amendment.quote_ref))

    def action_submit(self):
        for amendment in self:
            if amendment.state != "draft":
                raise UserError(_(
                    "Only a draft amendment of %s can be submitted.",
                    amendment.quote_ref))
            amendment.write({
                "state": "submitted",
                "submitted_on": fields.Date.context_today(amendment),
            })
            amendment.message_post(body=_(
                "The amendment was submitted for approval."))
        return True

    def action_approve(self):
        for amendment in self:
            if amendment.state != "submitted":
                raise UserError(_(
                    "Only a submitted amendment of %s can be approved.",
                    amendment.quote_ref))
            amendment.write({
                "state": "approved",
                "approved_user_id": self.env.user.id,
                "approved_on": fields.Date.context_today(amendment),
            })
            amendment.message_post(body=_(
                "Revision %s of %s became the approved version.",
                amendment.revision_no, amendment.quote_ref))
        return True

    def action_reject(self):
        for amendment in self:
            if amendment.state != "submitted":
                raise UserError(_(
                    "Only a submitted amendment of %s can be rejected.",
                    amendment.quote_ref))
            amendment.write({"state": "rejected"})
            amendment.message_post(body=_(
                "The amendment was rejected."))
        return True
