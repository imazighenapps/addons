# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ReferCode(models.Model):
    _name = "refer.code"
    _description = "Referral Code"
    _inherit = ["mail.thread"]
    _order = "advocate_name"

    name = fields.Char(
        string="Code", required=True, tracking=True, copy=False,
        help="Unique code shared by the advocate.")
    advocate_name = fields.Char(
        string="Advocate", required=True, tracking=True,
        help="Customer who shares the referral code.")
    state = fields.Selection(
        [("active", "Active"), ("closed", "Closed")],
        default="active", required=True, tracking=True, index=True)
    referral_ids = fields.One2many(
        "refer.referral", "code_id", string="Referrals", copy=False)
    referral_count = fields.Integer(
        string="Referrals", compute="_compute_totals", store=True)
    credited_count = fields.Integer(
        string="Credited", compute="_compute_totals", store=True)
    total_reward = fields.Monetary(
        string="Total Reward", compute="_compute_totals",
        store=True, currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("referral_ids", "referral_ids.state",
                 "referral_ids.reward_amount")
    def _compute_totals(self):
        for code in self:
            refs = code.referral_ids
            credited = refs.filtered(lambda r: r.state == "credited")
            code.referral_count = len(refs)
            code.credited_count = len(credited)
            code.total_reward = sum(credited.mapped("reward_amount"))

    @api.constrains("name", "company_id")
    def _check_unique_code(self):
        for code in self:
            domain = [("id", "!=", code.id), ("name", "=", code.name),
                      ("company_id", "=", code.company_id.id)]
            if self.search_count(domain):
                raise ValidationError(_(
                    "The referral code %s already exists in this company.",
                    code.name))

    def action_close(self):
        for code in self:
            if code.state != "active":
                raise UserError(_("Only active codes can be closed."))
            code.state = "closed"
            code.message_post(body=_("The referral code was closed."))
        return True

    def action_reopen(self):
        for code in self:
            if code.state != "closed":
                raise UserError(_("Only closed codes can be reopened."))
            code.state = "active"
            code.message_post(body=_("The referral code was reopened."))
        return True
