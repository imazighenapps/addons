# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PoAckFollowup(models.Model):
    _name = "po.ack.followup"
    _description = "PO Acknowledgement Follow-up"
    _inherit = ["mail.thread"]
    _order = "followup_date desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Follow-up %s")
        % fields.Date.context_today(self))
    ack_id = fields.Many2one(
        "po.ack.order", string="Purchase Order", required=True,
        ondelete="cascade", index=True, tracking=True)
    partner_id = fields.Many2one(
        related="ack_id.partner_id", store=True, readonly=True)
    followup_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    channel = fields.Selection(
        [("email", "Email"), ("phone", "Phone"), ("portal", "Portal")],
        default="email", required=True,
        help="How the supplier was chased for acknowledgement.")
    response = fields.Text(
        help="Supplier response or note from this follow-up.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.constrains("followup_date")
    def _check_followup_date(self):
        today = fields.Date.context_today(self)
        for followup in self:
            if followup.followup_date and followup.followup_date > today:
                raise ValidationError(_(
                    "The follow-up date of %s cannot be in the future.",
                    followup.name))
