# -*- coding: utf-8 -*-
from odoo import api, fields, models


class GatePoint(models.Model):
    _name = "gate.point"
    _description = "Gate Point"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        help="Short code of the gate, for example GATE-N.")
    location = fields.Char(
        help="Physical location or site of the gate.")
    entry_ids = fields.One2many(
        "gate.entry", "gate_id", string="Entries")
    entry_count = fields.Integer(
        string="Entries", compute="_compute_entry_counts", store=True)
    open_entry_count = fields.Integer(
        string="On Site", compute="_compute_entry_counts", store=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("entry_ids", "entry_ids.state")
    def _compute_entry_counts(self):
        for gate in self:
            entries = gate.entry_ids
            gate.entry_count = len(entries)
            gate.open_entry_count = len(entries.filtered(
                lambda entry: entry.state == "on_site"))
