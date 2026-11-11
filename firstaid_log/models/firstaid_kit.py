# -*- coding: utf-8 -*-
from odoo import api, fields, models


class FirstaidKit(models.Model):
    _name = "firstaid.kit"
    _description = "First Aid Kit"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    location = fields.Char(
        required=True, tracking=True,
        help="Where the kit is installed on site.")
    responsible_id = fields.Many2one(
        "hr.employee", string="Responsible", required=True, tracking=True,
        help="Employee responsible for checking and refilling the kit.")
    item_ids = fields.One2many(
        "firstaid.item", "kit_id", string="Contents")
    refill_ids = fields.One2many(
        "firstaid.refill", "kit_id", string="Refill Rounds")
    item_count = fields.Integer(
        string="Items", compute="_compute_status", store=True)
    missing_count = fields.Integer(
        string="Missing", compute="_compute_status", store=True)
    expired_count = fields.Integer(
        string="Expired", compute="_compute_status", store=True)
    refill_count = fields.Integer(
        string="Refills", compute="_compute_status", store=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True)
    note = fields.Text()

    @api.depends("item_ids", "item_ids.qty_required", "item_ids.qty_on_hand",
                 "item_ids.expiry_date", "refill_ids")
    def _compute_status(self):
        today = fields.Date.context_today(self)
        for kit in self:
            items = kit.item_ids
            kit.item_count = len(items)
            kit.missing_count = len(items.filtered(
                lambda item: item.qty_on_hand < item.qty_required))
            kit.expired_count = len(items.filtered(
                lambda item: item.expiry_date and item.expiry_date < today))
            kit.refill_count = len(kit.refill_ids)
