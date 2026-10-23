# -*- coding: utf-8 -*-
from odoo import fields, models

ECO_ORGS = [
    ("citeo", "Citeo (household)"),
    ("leko", "Léko (household)"),
    ("citeo_pro", "Citeo Pro (professional)"),
    ("leko_pro", "Léko Pro (professional)"),
    ("twiice", "Twiice (professional)"),
]


class RepMaterial(models.Model):
    _name = "rep.material"
    _description = "REP Packaging Material"

    name = fields.Char(required=True, translate=True)
    family = fields.Selection(
        [("plastic", "Plastic"), ("cardboard", "Cardboard"), ("glass", "Glass"),
         ("steel", "Steel"), ("aluminium", "Aluminium"), ("wood", "Wood"),
         ("paper", "Paper"), ("other", "Other")],
        required=True,
    )
    resin = fields.Char(string="Resin (plastics)", help="e.g. PET, PE-HD, PP, PS, PVC")
    dangerous = fields.Boolean(string="Hazardous")
    recyclable_default = fields.Boolean(default=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("code_unique", "UNIQUE(name)", "Material name must be unique."),
    ]


class RepTariff(models.Model):
    _name = "rep.tariff"
    _description = "REP Eco-contribution Tariff (€/t)"
    _order = "year desc"

    material_id = fields.Many2one("rep.material", required=True, ondelete="cascade")
    eco_org = fields.Selection(ECO_ORGS, required=True)
    year = fields.Integer(required=True, default=2026)
    price_per_t = fields.Float(string="Price (€/t excl. tax)", required=True)
    active = fields.Boolean(default=True)
