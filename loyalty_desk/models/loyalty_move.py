# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LoyaltyMove(models.Model):
    _name = "loyalty.move"
    _description = "Loyalty Point Movement"
    _inherit = ["mail.thread"]
    _order = "move_date desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Movement %s")
        % fields.Date.context_today(self))
    account_id = fields.Many2one(
        "loyalty.account", required=True, ondelete="cascade",
        index=True, tracking=True)
    move_type = fields.Selection(
        [("earn", "Earned"), ("redeem", "Redeemed")],
        required=True, default="earn", tracking=True)
    points = fields.Integer(required=True, default=1, tracking=True)
    move_date = fields.Date(
        string="Date", required=True, default=fields.Date.context_today,
        tracking=True)
    reference = fields.Char(
        help="Invoice, order or note that explains this movement.")
    state = fields.Selection(
        [("draft", "Draft"), ("posted", "Posted")],
        default="draft", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        related="account_id.company_id", store=True, readonly=True,
        index=True)
    note = fields.Text()

    @api.constrains("points")
    def _check_points(self):
        for move in self:
            if move.points <= 0:
                raise ValidationError(_(
                    "The points of movement %s must be above zero.",
                    move.name))

    def action_post(self):
        for move in self:
            if move.state != "draft":
                raise UserError(_("Only draft movements can be posted."))
            if move.account_id.state != "active":
                raise UserError(_(
                    "Points cannot be posted on a suspended account."))
            if move.move_type == "redeem":
                if move.points > move.account_id.balance_points:
                    raise UserError(_(
                        "Redeeming %s points would overdraw account %s.",
                        move.points, move.account_id.partner_name))
            move.state = "posted"
            move.message_post(body=_("The point movement was posted."))
        return True
