# -*- coding: utf-8 -*-
from odoo import api, fields, models


class DocControl(models.Model):
    _name = "doc.control"
    _description = "Controlled Document"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        string="Document Code", required=True, tracking=True,
        help="Unique code of the controlled document, for example SOP-001.")
    revision = fields.Char(
        default="A", required=True, tracking=True,
        help="Current revision of the document in force.")
    effective_on = fields.Date(
        string="Effective On", default=fields.Date.context_today,
        tracking=True,
        help="Date the current revision became effective.")
    distribution_ids = fields.One2many(
        "doc.distribution", "document_id", string="Distribution")
    distribution_count = fields.Integer(
        string="Recipients", compute="_compute_distribution")
    pending_count = fields.Integer(
        string="Pending", compute="_compute_distribution")
    acknowledged_count = fields.Integer(
        string="Acknowledged", compute="_compute_distribution")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)
    note = fields.Text()

    @api.depends("distribution_ids", "distribution_ids.state")
    def _compute_distribution(self):
        for doc in self:
            doc.distribution_count = len(doc.distribution_ids)
            doc.pending_count = len(doc.distribution_ids.filtered(
                lambda line: line.state == "pending"))
            doc.acknowledged_count = len(doc.distribution_ids.filtered(
                lambda line: line.state == "acknowledged"))
