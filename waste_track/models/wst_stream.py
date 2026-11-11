# -*- coding: utf-8 -*-
from odoo import api, fields, models


class WstStream(models.Model):
    _name = "wst.stream"
    _description = "Waste Stream"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(
        required=True, tracking=True,
        help="Name of the waste stream.")
    code = fields.Char(
        string="Waste Code", tracking=True,
        help="Internal or regulatory code of the waste stream.")
    hazard_class = fields.Selection(
        [("non_hazardous", "Non-Hazardous"), ("hazardous", "Hazardous"),
         ("special", "Special")],
        default="non_hazardous", required=True, tracking=True)
    contractor = fields.Char(
        string="Contractor", tracking=True,
        help="Collector or contractor handling this waste stream.")
    active = fields.Boolean(default=True)
    collection_ids = fields.One2many(
        "wst.collection", "stream_id", string="Collections")
    collection_count = fields.Integer(
        string="Collections", compute="_compute_counts", store=True)
    pending_receipt_count = fields.Integer(
        string="Pending Receipts", compute="_compute_counts", store=True)
    total_quantity = fields.Float(
        string="Collected Quantity", compute="_compute_counts", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True,
        default=lambda self: self.env.company)
    note = fields.Text()

    @api.depends("collection_ids", "collection_ids.state",
                 "collection_ids.quantity")
    def _compute_counts(self):
        for rec in self:
            rec.collection_count = len(rec.collection_ids)
            rec.pending_receipt_count = len(
                rec.collection_ids.filtered(lambda c: c.state != "filed"))
            rec.total_quantity = sum(
                rec.collection_ids.filtered(
                    lambda c: c.state in ("collected", "filed")
                ).mapped("quantity"))
