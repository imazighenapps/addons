# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DevdApproval(models.Model):
    _name = "devd.approval"
    _description = "Deviation Approval"
    _inherit = ["mail.thread"]
    _order = "decided_on desc, id desc"

    deviation_id = fields.Many2one(
        "devd.deviation", string="Deviation", required=True,
        ondelete="cascade", index=True, tracking=True)
    approver_id = fields.Many2one(
        "res.users", string="Approver", required=True,
        default=lambda self: self.env.user, tracking=True)
    decided_on = fields.Date(
        string="Decided On", required=True,
        default=fields.Date.context_today, tracking=True)
    decision = fields.Selection(
        [("granted", "Granted"), ("rejected", "Rejected")],
        default="granted", required=True, tracking=True)
    comment = fields.Text(string="Comment")
    company_id = fields.Many2one(
        "res.company", required=True, index=True,
        default=lambda self: self.env.company)

    @api.constrains("decided_on")
    def _check_decided_on(self):
        for rec in self:
            if rec.decided_on and rec.deviation_id.detected_on \
                    and rec.decided_on < rec.deviation_id.detected_on:
                raise ValidationError(_(
                    "The approval of %s cannot predate the deviation.",
                    rec.deviation_id.name))
