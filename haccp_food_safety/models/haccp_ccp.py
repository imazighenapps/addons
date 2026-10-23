# -*- coding: utf-8 -*-
from odoo import fields, models


class HaccpCcp(models.Model):
    _name = "haccp.ccp"
    _description = "HACCP Critical Control Point"
    _inherit = ["mail.thread"]
    _order = "code"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True)
    plan_id = fields.Many2one("haccp.plan", string="Plan", required=True,
                              ondelete="cascade")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True)
    step = fields.Char(string="Process Step")
    hazard_type = fields.Selection(
        [("bio", "Biological"), ("chem", "Chemical"),
         ("phys", "Physical"), ("allergen", "Allergen")],
        required=True,
        default="bio",
    )
    limit_min = fields.Float(string="Critical Limit Min")
    limit_max = fields.Float(string="Critical Limit Max")
    target = fields.Float(string="Target Value")
    uom_id = fields.Many2one("uom.uom", string="Unit")
    frequency = fields.Char(string="Monitoring Frequency", default="2x/day")
    method = fields.Text(string="Monitoring Method")
    equipment_ref = fields.Char(string="Equipment (probe, detector)")
    product_ids = fields.Many2many("product.template", string="Products")
    location_ids = fields.Many2many("stock.location", string="Locations")
    critical = fields.Boolean(default=True)
    active = fields.Boolean(default=True)
    reading_count = fields.Integer(compute="_compute_readings")

    def _compute_readings(self):
        groups = self.env["haccp.reading"]._read_group(
            [("ccp_id", "in", self.ids)], ["ccp_id"], ["__count"])
        counts = {ccp.id: n for ccp, n in groups}
        for rec in self:
            rec.reading_count = counts.get(rec.id, 0)
