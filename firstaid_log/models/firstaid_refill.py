# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FirstaidRefill(models.Model):
    _name = "firstaid.refill"
    _description = "First Aid Refill"
    _inherit = ["mail.thread"]
    _order = "refill_date desc, id desc"

    name = fields.Char(
        required=True, default=lambda self: _("Refill %s")
        % fields.Date.context_today(self),
        help="Reference of the refill round.")
    kit_id = fields.Many2one(
        "firstaid.kit", string="Kit", required=True,
        ondelete="cascade", index=True, tracking=True)
    refill_date = fields.Date(
        string="Refill Date", required=True,
        default=fields.Date.context_today, tracking=True)
    refilled_by_id = fields.Many2one(
        "hr.employee", string="Refilled By", required=True, tracking=True,
        help="Employee who performed the refill round.")
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done")],
        default="draft", required=True, tracking=True, index=True)
    company_id = fields.Many2one(
        related="kit_id.company_id", store=True, readonly=True, index=True)
    note = fields.Text(help="What was restocked during the round.")

    def action_done(self):
        for refill in self:
            if refill.state != "draft":
                raise ValidationError(_(
                    "The refill round %s is already done.", refill.name))
            refill.write({"state": "done"})
            refill.message_post(body=_(
                "The refill round has been completed."))
        return True
