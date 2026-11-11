# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RecoverAction(models.Model):
    _name = "recover.action"
    _description = "Claim Chase Action"
    _inherit = ["mail.thread"]
    _order = "action_on desc, id desc"

    name = fields.Char(
        compute="_compute_name", store=True,
        help="Display name combining the claim and the chase date.")
    claim_id = fields.Many2one(
        "recover.claim", string="Claim", required=True,
        ondelete="cascade", index=True, tracking=True)
    action_on = fields.Date(
        string="Chased On", required=True, default=fields.Date.context_today,
        tracking=True)
    channel = fields.Selection(
        [("email", "Email"), ("phone", "Phone"),
         ("letter", "Letter"), ("other", "Other")],
        default="email", required=True)
    summary = fields.Char(
        required=True, help="Short note describing the chase action.")
    company_id = fields.Many2one(
        related="claim_id.company_id", store=True, readonly=True, index=True)
    state = fields.Selection(
        related="claim_id.state", store=True, readonly=True)

    @api.depends("claim_id.name", "action_on")
    def _compute_name(self):
        for action in self:
            if action.claim_id and action.action_on:
                action.name = "%s / %s" % (
                    action.claim_id.name, action.action_on)
            else:
                action.name = action.claim_id.name or _("Chase Action")

    @api.constrains("summary")
    def _check_summary(self):
        for action in self:
            if not (action.summary and action.summary.strip()):
                raise ValidationError(_(
                    "Describe the chase action before saving it."))
