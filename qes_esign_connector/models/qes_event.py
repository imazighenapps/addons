# -*- coding: utf-8 -*-
from odoo import fields, models


class QesEvent(models.Model):
    _name = "qes.event"
    _description = "QES Audit Event (append-only)"
    _order = "create_date desc"

    envelope_id = fields.Many2one("qes.envelope", required=True, ondelete="cascade")
    etype = fields.Selection(
        [
            ("prepared", "Prepared"), ("sent", "Sent"), ("signed", "Signed"),
            ("status", "Status Check"), ("evidence", "Evidence"),
            ("finalized", "Finalized"), ("archived", "Archived"),
            ("webhook", "Webhook"), ("error", "Error"),
        ],
        string="Type",
        required=True,
    )
    actor = fields.Char()
    ip = fields.Char(string="IP")
    details = fields.Text()
    prev_hash = fields.Char(readonly=True)
    event_hash = fields.Char(readonly=True)
    provider_event_id = fields.Char(string="Provider Event ID", copy=False)

    _sql_constraints = [
        ("provider_event_unique", "UNIQUE(provider_event_id)", "Provider event already processed (idempotency)."),
    ]
