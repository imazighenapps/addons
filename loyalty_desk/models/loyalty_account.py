# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LoyaltyAccount(models.Model):
    _name = "loyalty.account"
    _description = "Loyalty Point Account"
    _inherit = ["mail.thread"]
    _order = "partner_name"

    name = fields.Char(
        required=True, tracking=True,
        default=lambda self: _("Points %s") % fields.Date.context_today(self))
    partner_name = fields.Char(
        string="Customer", required=True, tracking=True,
        help="Name of the customer who owns this point account.")
    state = fields.Selection(
        [("active", "Active"), ("suspended", "Suspended")],
        default="active", required=True, tracking=True, index=True)
    move_ids = fields.One2many(
        "loyalty.move", "account_id", string="Point Movements", copy=False)
    move_count = fields.Integer(
        string="Movements", compute="_compute_balance", store=True)
    points_earned = fields.Integer(
        string="Points Earned", compute="_compute_balance", store=True)
    points_redeemed = fields.Integer(
        string="Points Redeemed", compute="_compute_balance", store=True)
    balance_points = fields.Integer(
        string="Balance", compute="_compute_balance", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("move_ids", "move_ids.points", "move_ids.move_type",
                 "move_ids.state")
    def _compute_balance(self):
        for account in self:
            moves = account.move_ids.filtered(lambda m: m.state == "posted")
            earned = sum(m.points for m in moves if m.move_type == "earn")
            redeemed = sum(m.points for m in moves if m.move_type == "redeem")
            account.move_count = len(moves)
            account.points_earned = earned
            account.points_redeemed = redeemed
            account.balance_points = earned - redeemed

    def action_suspend(self):
        for account in self:
            if account.state != "active":
                raise UserError(_("Only active accounts can be suspended."))
            account.state = "suspended"
            account.message_post(body=_("The loyalty account was suspended."))
        return True

    def action_activate(self):
        for account in self:
            if account.state != "suspended":
                raise UserError(_("Only suspended accounts can be activated."))
            account.state = "active"
            account.message_post(body=_("The loyalty account was activated."))
        return True
