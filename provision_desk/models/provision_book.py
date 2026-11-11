# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ProvisionBook(models.Model):
    _name = "provision.book"
    _description = "Provision"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    provision_type = fields.Selection(
        [("bad_debt", "Bad Debt"), ("warranty", "Warranty"),
         ("other", "Other")],
        default="bad_debt", required=True, tracking=True,
        help="Nature of the risk covered by this provision.")
    owner_id = fields.Many2one(
        "res.users", string="Owner", tracking=True,
        default=lambda self: self.env.user)
    opening_balance = fields.Monetary(
        string="Opening Balance", required=True, default=0.0, tracking=True)
    movement_ids = fields.One2many(
        "provision.movement", "provision_id", string="Movements", copy=True)
    current_balance = fields.Monetary(
        string="Current Balance", compute="_compute_balance", store=True,
        help="Opening balance plus all recorded movements.")
    movement_count = fields.Integer(
        string="Movements", compute="_compute_balance", store=True)
    state = fields.Selection(
        [("open", "Open"), ("closed", "Closed")],
        default="open", required=True, copy=False, tracking=True, index=True)
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("opening_balance", "movement_ids.amount",
                 "movement_ids.movement_type")
    def _compute_balance(self):
        for provision in self:
            total = provision.opening_balance
            for move in provision.movement_ids:
                if move.movement_type == "increase":
                    total += move.amount
                else:
                    total -= move.amount
            provision.current_balance = total
            provision.movement_count = len(provision.movement_ids)

    @api.constrains("opening_balance")
    def _check_opening(self):
        for provision in self:
            if provision.opening_balance < 0:
                raise ValidationError(_(
                    "The opening balance of %s cannot be negative.",
                    provision.name))

    def action_close(self):
        for provision in self:
            if provision.state == "closed":
                raise UserError(_(
                    "Provision %s is already closed.", provision.name))
            provision.state = "closed"
            provision.message_post(body=_(
                "Provision closed with a balance of %s.",
                provision.current_balance))
        return True

    def action_reopen(self):
        for provision in self:
            if provision.state != "closed":
                raise UserError(_(
                    "Only a closed provision can be reopened."))
            provision.state = "open"
            provision.message_post(body=_("Provision reopened."))
        return True
