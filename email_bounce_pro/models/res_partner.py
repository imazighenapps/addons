# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    event_ids = fields.One2many(
        "bounce.event", "partner_id", string="Bounces")
    bounce_count = fields.Integer(compute="_compute_bounce")

    @api.depends()
    def _compute_bounce(self):
        events = self.env["bounce.event"].search([
            ("state", "=", "new"),
            ("partner_id", "in", self.ids),
        ])
        counts = {}
        for event in events:
            counts[event.partner_id.id] = counts.get(event.partner_id.id, 0) + 1
        for partner in self:
            partner.bounce_count = counts.get(partner.id, 0)
