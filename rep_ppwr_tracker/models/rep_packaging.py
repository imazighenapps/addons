# -*- coding: utf-8 -*-
from odoo import api, fields, models


class RepPackaging(models.Model):
    _name = "rep.packaging"
    _description = "Product Packaging Sheet (REP/PPWR)"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company)
    product_ids = fields.Many2many(
        "product.template", "product_template_rep_packaging_rel",
        "rep_packaging_id", "product_template_id", string="Products")
    material_id = fields.Many2one("rep.material", string="Material", required=True)
    weight_g = fields.Float(string="Weight (g/unit)", required=True)
    qty_per_unit = fields.Float(string="Units per Sale Unit", default=1.0, required=True)
    level = fields.Selection(
        [("primary", "Primary"), ("secondary", "Secondary"), ("tertiary", "Tertiary")],
        default="primary",
        required=True,
    )
    reuse = fields.Selection(
        [("single", "Single Use"), ("reusable", "Reusable"), ("reused", "Reused")],
        default="single",
        required=True,
    )
    deposit_id = fields.Many2one("rep.deposit", string="Deposit")
    recycled_pct = fields.Float(string="Recycled Content (%)", default=0.0)
    recyclability_class = fields.Selection(
        [("unknown", "Unknown"), ("A", "A"), ("B", "B"), ("C", "C"),
         ("D", "D - Banned 2030"), ("E", "E - Banned 2030")],
        default="unknown",
    )
    food_contact = fields.Boolean(string="Food Contact")
    soc_flag = fields.Boolean(string="Substance of Concern")
    active = fields.Boolean(default=True)
    eco_cost_unit = fields.Float(
        string="Eco-cost / Sale Unit (€)", compute="_compute_eco_cost", store=True)

    @api.depends("weight_g", "qty_per_unit", "reuse", "material_id")
    def _compute_eco_cost(self):
        for rec in self:
            rec.eco_cost_unit = rec._eco_cost_for_qty(rec.qty_per_unit)

    def _tariff(self, eco_org, year):
        self.ensure_one()
        tariff = self.env["rep.tariff"].search([
            ("material_id", "=", self.material_id.id),
            ("eco_org", "=", eco_org),
            ("year", "=", year),
            ("active", "=", True),
        ], limit=1)
        return tariff

    def _eco_cost_for_qty(self, qty_units, eco_org="citeo", year=2026):
        self.ensure_one()
        if self.reuse == "reused":
            return 0.0
        tariff = self._tariff(eco_org, year)
        price = tariff.price_per_t if tariff else 0.0
        weight_kg = self.weight_g * qty_units / 1000.0
        factor = 0.5 if self.reuse == "reusable" else 1.0
        return round(weight_kg * price / 1000.0 * factor, 4)

    def _ppwr_alerts(self):
        self.ensure_one()
        alerts = []
        if self.recyclability_class in ("D", "E"):
            alerts.append("PPWR: class %s banned from 2030." % self.recyclability_class)
        if self.soc_flag:
            alerts.append("PPWR: substance of concern to minimize.")
        if (self.material_id.family == "plastic" and self.weight_g >= 50
                and self.recycled_pct <= 0):
            alerts.append("PPWR: check recycled-content thresholds.")
        return alerts
