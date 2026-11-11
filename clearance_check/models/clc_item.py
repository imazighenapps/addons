# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ClcItem(models.Model):
    _name = "clc.item"
    _description = "Clearance Checklist Item"
    _inherit = ["mail.thread"]
    _order = "sequence, id"

    check_id = fields.Many2one(
        "clc.check", string="Clearance", required=True,
        ondelete="cascade", index=True, tracking=True)
    sequence = fields.Integer(default=10)
    name = fields.Char(
        string="Item", required=True, tracking=True,
        help="What must be removed, cleaned or verified.")
    item_type = fields.Selection(
        [("remove", "Remove"), ("clean", "Clean"), ("verify", "Verify")],
        default="verify", required=True, tracking=True)
    signed_by_id = fields.Many2one(
        "res.users", string="Signed By", readonly=True, copy=False)
    signed_on = fields.Datetime(
        string="Signed On", readonly=True, copy=False)
    state = fields.Selection(
        [("todo", "To Do"), ("done", "Done")],
        default="todo", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True,
        default=lambda self: self.env.company)

    def action_done(self):
        for rec in self:
            if rec.state != "todo":
                raise ValidationError(_(
                    "Checklist item %s is already completed.", rec.name))
            rec.write({
                "state": "done",
                "signed_by_id": self.env.user.id,
                "signed_on": fields.Datetime.now(),
            })
        return True

    def action_reset(self):
        for rec in self:
            if rec.check_id.state == "released":
                raise ValidationError(_(
                    "Items of a released clearance cannot be reset."))
            rec.write({
                "state": "todo",
                "signed_by_id": False,
                "signed_on": False,
            })
        return True
