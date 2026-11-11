# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CylinderType(models.Model):
    _name = "cylinder.type"
    _description = "Cylinder Type"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    gas = fields.Char(
        string="Gas",
        help="Gas contained in this cylinder type, for example oxygen or argon.")
    capacity_liters = fields.Float(
        string="Capacity (L)", default=0.0,
        help="Nominal capacity of one cylinder, in liters.")
    rental_rate = fields.Float(
        string="Rental Rate", default=0.0,
        help="Rental amount charged by the supplier for one cylinder.")
    custody_ids = fields.One2many(
        "cylinder.custody", "cylinder_type_id", string="Custody Movements")
    custody_count = fields.Integer(
        string="Custody Lines", compute="_compute_custody")
    open_custody_count = fields.Integer(
        string="Open Custody", compute="_compute_custody")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)
    note = fields.Text()

    @api.depends("custody_ids", "custody_ids.state")
    def _compute_custody(self):
        for cylinder in self:
            cylinder.custody_count = len(cylinder.custody_ids)
            cylinder.open_custody_count = len(cylinder.custody_ids.filtered(
                lambda line: line.state == "open"))
