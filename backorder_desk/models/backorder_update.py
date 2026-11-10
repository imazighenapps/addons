# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BackorderUpdate(models.Model):
    _name = "backorder.update"
    _description = "Backorder Update"
    _inherit = ["mail.thread"]
    _order = "update_date desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Update %s") % fields.Date.context_today(self))
    case_id = fields.Many2one(
        "backorder.case", string="Case", required=True,
        ondelete="cascade", index=True, tracking=True)
    partner_id = fields.Many2one(
        related="case_id.partner_id", store=True, readonly=True)
    update_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    new_promised_date = fields.Date(
        string="New Promised Date",
        help="Set when this update changes the promised fulfilment date.")
    message = fields.Text(
        string="Message Sent",
        help="What was communicated to the customer in this update.")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)

    @api.constrains("update_date", "new_promised_date")
    def _check_dates(self):
        for update in self:
            if update.new_promised_date and update.update_date \
                    and update.new_promised_date < update.update_date:
                raise ValidationError(_(
                    "The new promised date of %s cannot come before the "
                    "update date.", update.name))
