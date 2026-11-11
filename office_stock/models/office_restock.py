# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class OfficeRestock(models.Model):
    _name = "office.restock"
    _description = "Office Restock Request"
    _inherit = ["mail.thread"]
    _order = "requested_on desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Restock %s")
        % fields.Date.context_today(self),
        help="Reference of the restock request, generated at creation.")
    supply_id = fields.Many2one(
        "office.supply", string="Supply", required=True,
        ondelete="cascade", index=True, tracking=True)
    requester_id = fields.Many2one(
        "res.partner", string="Requester", tracking=True)
    quantity = fields.Integer(
        string="Requested Quantity", default=1, required=True,
        help="Quantity requested to restock the supply.")
    requested_on = fields.Date(
        string="Requested On", required=True,
        default=fields.Date.context_today, tracking=True)
    ordered_on = fields.Date(string="Ordered On", readonly=True, copy=False)
    state = fields.Selection(
        [("pending", "Pending"), ("ordered", "Ordered")],
        default="pending", required=True, copy=False, tracking=True,
        index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.constrains("quantity")
    def _check_quantity(self):
        for req in self:
            if req.quantity <= 0:
                raise ValidationError(_(
                    "The requested quantity for %s must be above zero.",
                    req.supply_id.name))

    @api.constrains("requested_on", "ordered_on")
    def _check_dates(self):
        for req in self:
            if req.ordered_on and req.ordered_on < req.requested_on:
                raise ValidationError(_(
                    "The ordered date of %s cannot come before the requested "
                    "date.", req.name))

    def action_mark_ordered(self):
        for req in self:
            if req.state != "pending":
                raise ValidationError(_(
                    "The restock request %s is already ordered.", req.name))
            req.write({
                "state": "ordered",
                "ordered_on": fields.Date.context_today(req),
            })
            req.message_post(body=_(
                "The restock request was marked as ordered."))
        return True
