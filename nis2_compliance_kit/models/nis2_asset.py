# -*- coding: utf-8 -*-
from odoo import fields, models


class Nis2Asset(models.Model):
    _name = "nis2.asset"
    _description = "NIS2 Information System Asset"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True
    )
    asset_type = fields.Selection(
        [
            ("hardware", "Hardware"),
            ("software", "Software"),
            ("data", "Data"),
            ("service", "Service"),
            ("ot", "OT / Industrial"),
            ("network", "Network"),
        ],
        required=True,
        default="software",
    )
    owner_id = fields.Many2one("res.users", string="Owner", tracking=True)
    confidentiality = fields.Selection(
        [("1", "1 - Low"), ("2", "2"), ("3", "3"), ("4", "4 - Critical")],
        default="2",
        required=True,
    )
    integrity = fields.Selection(
        [("1", "1 - Low"), ("2", "2"), ("3", "3"), ("4", "4 - Critical")],
        default="2",
        required=True,
    )
    availability = fields.Selection(
        [("1", "1 - Low"), ("2", "2"), ("3", "3"), ("4", "4 - Critical")],
        default="2",
        required=True,
    )
    hosting = fields.Selection(
        [("onprem", "On Premise"), ("cloud", "Cloud"), ("hybrid", "Hybrid"), ("third", "Third Party")],
        default="onprem",
    )
    supplier_id = fields.Many2one("res.partner", string="Supplier / Host")
    description = fields.Text()
    active = fields.Boolean(default=True)
