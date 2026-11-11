# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MarginCheck(models.Model):
    _name = "margin.check"
    _description = "Discount Check"
    _inherit = ["mail.thread"]
    _order = "checked_on desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Check %s")
        % fields.Date.context_today(self),
        help="Reference of the check, generated at creation.")
    rule_id = fields.Many2one(
        "margin.rule", string="Rule", required=True, index=True,
        tracking=True, help="Floor the requested values collided with.")
    reference = fields.Char(
        required=True, tracking=True,
        help="Reference of the order line the check blocks.")
    requested_discount = fields.Float(
        string="Requested Discount (%)",
        help="Discount the rep wanted to apply.")
    requested_margin = fields.Float(
        string="Requested Margin (%)",
        help="Margin left on the line at the requested discount.")
    state = fields.Selection(
        [("pending", "Pending"), ("approved", "Approved"),
         ("rejected", "Rejected")],
        default="pending", required=True, copy=False, tracking=True,
        index=True)
    checked_on = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    decided_by = fields.Many2one(
        "res.users", string="Decided By", readonly=True, copy=False)
    decided_on = fields.Date(
        string="Decided On", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.constrains("requested_discount", "requested_margin")
    def _check_requested(self):
        for check in self:
            for value, label in (
                    (check.requested_discount, "discount"),
                    (check.requested_margin, "margin")):
                if value < 0.0 or value > 100.0:
                    raise ValidationError(_(
                        "The requested %s of %s must stay between 0 "
                        "and 100 percent.", label, check.reference))

    def action_approve(self):
        for check in self:
            if check.state != "pending":
                raise UserError(_(
                    "The check on %s is already decided.", check.reference))
            check.write({
                "state": "approved",
                "decided_by": self.env.user.id,
                "decided_on": fields.Date.context_today(check),
            })
            check.message_post(body=_(
                "The discount below the floor was approved."))
        return True

    def action_reject(self):
        for check in self:
            if check.state != "pending":
                raise UserError(_(
                    "The check on %s is already decided.", check.reference))
            check.write({
                "state": "rejected",
                "decided_by": self.env.user.id,
                "decided_on": fields.Date.context_today(check),
            })
            check.message_post(body=_(
                "The discount below the floor was refused."))
        return True
