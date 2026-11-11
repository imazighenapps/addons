# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DocDistribution(models.Model):
    _name = "doc.distribution"
    _description = "Document Distribution"
    _inherit = ["mail.thread"]
    _order = "sent_on desc, id desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Distribution %s")
        % fields.Date.context_today(self),
        help="Reference of the distribution line, generated at creation.")
    document_id = fields.Many2one(
        "doc.control", string="Document", required=True,
        ondelete="cascade", index=True, tracking=True)
    recipient_id = fields.Many2one(
        "res.partner", string="Recipient", required=True, tracking=True)
    sent_on = fields.Date(
        string="Sent On", required=True, default=fields.Date.context_today,
        tracking=True,
        help="Date the document revision was sent to the recipient.")
    acknowledged_on = fields.Date(
        string="Acknowledged On", readonly=True, copy=False,
        help="Date the recipient confirmed having read the document.")
    state = fields.Selection(
        [("pending", "Pending"), ("acknowledged", "Acknowledged")],
        default="pending", required=True, copy=False, tracking=True,
        index=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.constrains("sent_on", "acknowledged_on")
    def _check_dates(self):
        for line in self:
            if line.acknowledged_on and line.acknowledged_on < line.sent_on:
                raise ValidationError(_(
                    "The acknowledgement date of %s cannot come before the "
                    "sent date.", line.name))

    @api.constrains("document_id", "recipient_id")
    def _check_unique_recipient(self):
        for line in self:
            if not line.document_id or not line.recipient_id:
                continue
            duplicate = self.search_count([
                ("id", "!=", line.id),
                ("document_id", "=", line.document_id.id),
                ("recipient_id", "=", line.recipient_id.id),
            ])
            if duplicate:
                raise ValidationError(_(
                    "The recipient %s already appears on the distribution "
                    "list of %s.",
                    line.recipient_id.name, line.document_id.name))

    def action_acknowledge(self):
        for line in self:
            if line.state != "pending":
                raise ValidationError(_(
                    "The distribution line %s is already acknowledged.",
                    line.name))
            line.write({
                "state": "acknowledged",
                "acknowledged_on": fields.Date.context_today(line),
            })
            line.message_post(body=_(
                "The recipient acknowledged the controlled document."))
        return True
