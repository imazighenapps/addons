# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class FrEreportLine(models.Model):
    _name = "fr.ereport.line"
    _description = "E-Reporting Register Line"
    _order = "create_date desc"

    name = fields.Char(string="Reference", required=True, default="/")
    move_id = fields.Many2one("account.move", string="Invoice", ondelete="cascade")
    partner_id = fields.Many2one("res.partner", string="Partner")
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    flow = fields.Selection(
        [
            ("einvoice_b2b", "E-Invoice B2B France"),
            ("ereport_b2c", "E-Reporting B2C"),
            ("ereport_intl", "E-Reporting International"),
            ("ereport_payment", "E-Reporting Payment"),
            ("chorus", "Chorus Pro"),
        ],
        string="Flow",
        required=True,
        default="einvoice_b2b",
    )
    amount_total = fields.Monetary(string="Amount", currency_field="currency_id")
    currency_id = fields.Many2one("res.currency", string="Currency")
    status = fields.Selection(
        [
            ("ready", "Ready"),
            ("sent", "Sent"),
            ("done", "Completed"),
            ("error", "Error"),
        ],
        string="Status",
        default="ready",
        required=True,
    )
    message = fields.Text(string="Details")
    sent_on = fields.Datetime(string="Transmitted On")

    def action_mark_sent(self):
        for line in self:
            line.write({"status": "sent", "sent_on": fields.Datetime.now()})

    def action_mark_done(self):
        self.write({"status": "done"})

    def action_reset_ready(self):
        self.write({"status": "ready", "message": False})

    @api.model
    def _cron_check_stale_lines(self):
        """Flag lines stuck in error so the accountant reviews them daily."""
        stale = self.search([("status", "=", "error")])
        for line in stale:
            line.message = (line.message or "") + "\n" + _(
                "Still in error at daily control: please review and resubmit."
            )
        return True
