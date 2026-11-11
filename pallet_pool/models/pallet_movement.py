# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PalletMovement(models.Model):
    _name = "pallet.movement"
    _description = "Pallet Movement"
    _inherit = ["mail.thread"]
    _order = "movement_date desc, id desc"

    name = fields.Char(
        required=True, copy=False, default="New", tracking=True,
        help="Reference of the pallet movement.")
    account_id = fields.Many2one(
        "pallet.account", required=True, ondelete="cascade",
        tracking=True, index=True)
    partner_name = fields.Char(
        related="account_id.partner_name", store=True, readonly=True)
    direction = fields.Selection(
        [("lent", "Lent Out"), ("returned", "Returned")],
        required=True, default="lent", tracking=True,
        help="Whether pallets were lent out or returned.")
    quantity = fields.Integer(
        required=True, default=1, tracking=True,
        help="Number of pallets moved.")
    movement_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True,
        help="Date the movement happened.")
    reference = fields.Char(
        string="Document Reference",
        help="Delivery note or document linked to the movement.")
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed")],
        default="draft", required=True, tracking=True, index=True)
    confirmed_on = fields.Date(
        readonly=True, copy=False,
        help="Date the movement was confirmed.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "pallet.movement") or _("PM-%s") % fields.Date.context_today(self)
        return super().create(vals_list)

    @api.constrains("quantity")
    def _check_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError(_(
                    "The quantity of %s must be greater than zero.", record.name))

    def action_confirm(self):
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only draft movements can be confirmed."))
            record.write({
                "state": "confirmed",
                "confirmed_on": fields.Date.context_today(record),
            })
            record.message_post(body=_("Pallet movement confirmed."))
        return True

    def action_reset(self):
        for record in self:
            if record.state != "confirmed":
                raise UserError(_("Only confirmed movements can be reset."))
            record.write({"state": "draft", "confirmed_on": False})
            record.message_post(body=_("Pallet movement reset to draft."))
        return True
