# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SiteArea(models.Model):
    _name = "site.area"
    _description = "Site Area"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        help="Short code of the building or zone, for example HQ-B.")
    address = fields.Char(
        help="Address or internal location of the area.")
    ticket_ids = fields.One2many(
        "site.ticket", "area_id", string="Tickets")
    ticket_count = fields.Integer(
        string="Tickets", compute="_compute_ticket_counts", store=True)
    open_ticket_count = fields.Integer(
        string="Open Tickets", compute="_compute_ticket_counts", store=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("ticket_ids", "ticket_ids.state")
    def _compute_ticket_counts(self):
        for area in self:
            tickets = area.ticket_ids
            area.ticket_count = len(tickets)
            area.open_ticket_count = len(tickets.filtered(
                lambda ticket: ticket.state in ("new", "in_progress")))
