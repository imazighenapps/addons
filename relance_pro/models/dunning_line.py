# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class DunningLine(models.Model):
    _name = "dunning.line"
    _description = "Dunning Line"
    _inherit = ["mail.thread"]
    _order = "sent_date desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True)
    move_id = fields.Many2one(
        "account.move", string="Invoice", required=True)
    level_id = fields.Many2one(
        "dunning.level", string="Level", required=True)
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        related="move_id.currency_id", store=True, readonly=True)
    amount_residual = fields.Monetary(
        string="Amount Due", currency_field="currency_id",
        related="move_id.amount_residual", store=True, readonly=True)
    fee_amount = fields.Monetary(
        string="Late Fee", currency_field="currency_id")
    date_due = fields.Date(
        related="move_id.invoice_date_due", store=True, readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("sent", "Sent"), ("failed", "Failed"),
         ("paid", "Paid"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True, index=True)
    sent_date = fields.Datetime(readonly=True)
    mail_message_id = fields.Many2one(
        "mail.message", string="Message", readonly=True)

    _move_level_uniq = models.Constraint(
        "unique(move_id, level_id)",
        "This invoice was already chased at this level.")

    @api.depends("move_id", "level_id")
    def _compute_name(self):
        for line in self:
            parts = [
                line.move_id.name or "",
                line.level_id.name or "",
            ]
            line.name = " / ".join(part for part in parts if part) \
                or _("Dunning")

    def action_send(self):
        for line in self:
            if line.level_id.template_id:
                line.level_id.template_id.send_mail(
                    line.id, force_send=False)
            line.message_post(
                body=_("Dunning email sent at level %s.")
                % (line.level_id.name or ""))
            line.write({
                "state": "sent",
                "sent_date": fields.Datetime.now(),
                "mail_message_id": line.message_ids[:1].id,
            })
        return True

    def action_cancel(self):
        for line in self:
            line.state = "cancelled"
        return True
