# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class KeyItem(models.Model):
    _name = "key.item"
    _description = "Key or Badge"
    _inherit = ["mail.thread"]
    _order = "issued_on desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("KEY %s")
        % fields.Date.context_today(self),
        help="Reference of the key or badge record.")
    label = fields.Char(
        string="Key Label", required=True, tracking=True,
        help="Label printed on the key or badge.")
    key_type = fields.Selection(
        [("key", "Key"), ("badge", "Badge"), ("fob", "Fob"),
         ("other", "Other")],
        default="key", required=True, string="Type", tracking=True,
        help="Kind of access item being tracked.")
    holder = fields.Char(
        string="Holder", required=True, tracking=True,
        help="Person currently holding the key or badge.")
    issued_on = fields.Date(
        string="Issued On", required=True,
        default=fields.Date.context_today, tracking=True)
    returned_on = fields.Date(
        string="Returned On", readonly=True, copy=False, tracking=True)
    state = fields.Selection(
        [("issued", "Issued"), ("returned", "Returned")],
        default="issued", required=True, copy=False, tracking=True,
        index=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company, index=True)
    note = fields.Text()

    @api.constrains("issued_on", "returned_on")
    def _check_dates(self):
        for record in self:
            if record.returned_on and record.returned_on < record.issued_on:
                raise ValidationError(_(
                    "The return date of %s cannot come before the issue "
                    "date.", record.name))

    def action_return(self):
        for record in self:
            if record.state != "issued":
                raise ValidationError(_(
                    "The key %s is already returned.", record.label))
            record.write({
                "state": "returned",
                "returned_on": fields.Date.context_today(record),
            })
            record.message_post(body=_(
                "The key or badge was returned."))
        return True
