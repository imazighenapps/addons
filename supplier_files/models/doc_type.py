# -*- coding: utf-8 -*-
from odoo import fields, models


class SupplierDocType(models.Model):
    _name = "supplier.document.type"
    _description = "Required Supplier Document"
    _order = "sequence"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    required = fields.Boolean(string="Mandatory", default=True)
    has_expiry = fields.Boolean(string="Expires?")
    expiry_warning_days = fields.Integer(string="Warn Before (days)", default=30)
    blocking = fields.Boolean(
        string="Block Payment",
        help="Prevent posting supplier bills while this document is missing or expired.")
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint(
        "UNIQUE(code)", "Document code must be unique.")