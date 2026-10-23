# -*- coding: utf-8 -*-
from odoo import fields, models


class Nis2Sector(models.Model):
    _name = "nis2.sector"
    _description = "NIS2 Sector (Annex I / II)"

    name = fields.Char(required=True, translate=True)
    annex = fields.Selection(
        [("I", "Annex I - Highly Critical"), ("II", "Annex II - Other Critical")],
        required=True,
    )
    code = fields.Char(required=True)
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint(
        "UNIQUE(code)", "Sector code must be unique.")
