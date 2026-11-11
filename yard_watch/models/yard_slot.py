# -*- coding: utf-8 -*-
from odoo import api, fields, models


class YardSlot(models.Model):
    _name = "yard.slot"
    _description = "Yard Slot"
    _inherit = ["mail.thread"]
    _order = "dock, name"

    name = fields.Char(required=True, tracking=True)
    dock = fields.Char(
        required=True, tracking=True,
        help="Dock or gate this slot serves.")
    capacity = fields.Integer(
        default=1, required=True,
        help="Maximum number of trailers that can stand in this slot.")
    trailer_ids = fields.One2many(
        "yard.trailer", "slot_id", string="Trailers")
    waiting_count = fields.Integer(
        string="Waiting", compute="_compute_counts", store=True)
    docked_count = fields.Integer(
        string="Docked", compute="_compute_counts", store=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)
    note = fields.Text()

    @api.depends("trailer_ids.state")
    def _compute_counts(self):
        for slot in self:
            slot.waiting_count = len(slot.trailer_ids.filtered(
                lambda t: t.state == "waiting"))
            slot.docked_count = len(slot.trailer_ids.filtered(
                lambda t: t.state == "docked"))
