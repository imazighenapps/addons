# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class LotoLockout(models.Model):
    _name = "loto.lockout"
    _description = "Lockout/Tagout Record"
    _inherit = ["mail.thread"]
    _order = "locked_on desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("LOTO %s")
        % fields.Date.context_today(self),
        help="Reference of the lockout, generated at creation.")
    equipment = fields.Char(
        required=True, tracking=True,
        help="Machine or asset that is isolated.")
    tag_holder = fields.Char(
        string="Tag Holder", required=True, tracking=True,
        help="Person who applied the lock and tag.")
    reason = fields.Text(
        required=True, tracking=True,
        help="Why the equipment must remain isolated.")
    locked_on = fields.Date(
        string="Locked On", required=True,
        default=fields.Date.context_today, tracking=True)
    restored_on = fields.Date(
        string="Restored On", readonly=True, copy=False, tracking=True)
    restored_by = fields.Char(
        string="Restored By", readonly=True, copy=False, tracking=True,
        help="Person who removed the lock and restored the equipment.")
    state = fields.Selection(
        [("locked", "Locked"), ("restored", "Restored")],
        default="locked", required=True, copy=False, tracking=True,
        index=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company, index=True)
    note = fields.Text()

    @api.constrains("locked_on", "restored_on")
    def _check_dates(self):
        for record in self:
            if record.restored_on and record.restored_on < record.locked_on:
                raise ValidationError(_(
                    "The restoration date of %s cannot come before the "
                    "lock date.", record.name))

    def action_restore(self):
        for record in self:
            if record.state != "locked":
                raise ValidationError(_(
                    "The lockout %s is already restored.", record.name))
            record.write({
                "state": "restored",
                "restored_on": fields.Date.context_today(record),
                "restored_by": self.env.user.name,
            })
            record.message_post(body=_(
                "The equipment was restored and the lock removed."))
        return True
